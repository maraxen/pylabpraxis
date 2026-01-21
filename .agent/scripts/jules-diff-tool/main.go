package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strings"
	"time"
)

type Session struct {
	ID          string `json:"id"`
	Description string `json:"description"`
	Repo        string `json:"repo"`
	LastActive  string `json:"last_active"`
	Status      string `json:"status"`
}

type SessionMetadata struct {
	SessionID   string    `json:"session_id"`
	TaskName    string    `json:"task_name"`
	Status      string    `json:"status"`
	LastActive  string    `json:"last_active"`
	ExtractedAt time.Time `json:"extracted_at"`
	FilesCount  int       `json:"files_count"`
}

func main() {
	outputDir := flag.String("output", ".agent/reports/jules_diffs", "Output directory for diffs")
	statusFilter := flag.String("status", "", "Filter by status (comma-separated: Completed,Paused,Awaiting)")
	all := flag.Bool("all", false, "Extract from all sessions regardless of status")
	flag.Parse()

	date := time.Now().Format("2006-01-02")
	baseDir := filepath.Join(*outputDir, date)

	if err := os.MkdirAll(baseDir, 0755); err != nil {
		fmt.Fprintf(os.Stderr, "Error creating output directory: %v\n", err)
		os.Exit(1)
	}

	// Get session list
	sessions, err := listSessions()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error listing sessions: %v\n", err)
		os.Exit(1)
	}

	// Filter sessions
	filtered := filterSessions(sessions, *all, *statusFilter)
	fmt.Printf("Found %d sessions to extract (total: %d)\n", len(filtered), len(sessions))

	// Create summary file
	summaryPath := filepath.Join(baseDir, "SUMMARY.md")
	summaryFile, err := os.Create(summaryPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error creating summary: %v\n", err)
		os.Exit(1)
	}
	defer summaryFile.Close()

	fmt.Fprintf(summaryFile, "# Jules Diff Extraction - %s\n\n", date)
	fmt.Fprintf(summaryFile, "| Session ID | Task | Status | Files |\n")
	fmt.Fprintf(summaryFile, "|------------|------|--------|-------|\n")

	successCount := 0
	for i, session := range filtered {
		fmt.Printf("[%d/%d] Extracting %s (%s)...\n", i+1, len(filtered), session.ID, session.Status)

		sessionDir := filepath.Join(baseDir, session.ID)
		if err := os.MkdirAll(sessionDir, 0755); err != nil {
			fmt.Fprintf(os.Stderr, "  Error creating dir: %v\n", err)
			continue
		}

		// Pull diff
		diff, err := pullDiff(session.ID)
		if err != nil {
			fmt.Fprintf(os.Stderr, "  Error pulling diff: %v\n", err)
			writeErrorFile(sessionDir, err)
			fmt.Fprintf(summaryFile, "| %s | %s | %s | ERROR |\n", session.ID, truncate(session.Description, 50), session.Status)
			continue
		}

		// Write diff file
		diffPath := filepath.Join(sessionDir, "changes.diff")
		if err := os.WriteFile(diffPath, []byte(diff), 0644); err != nil {
			fmt.Fprintf(os.Stderr, "  Error writing diff: %v\n", err)
			continue
		}

		// Extract file list
		files := extractFileList(diff)
		filesPath := filepath.Join(sessionDir, "files_changed.txt")
		os.WriteFile(filesPath, []byte(strings.Join(files, "\n")), 0644)

		// Write metadata
		meta := SessionMetadata{
			SessionID:   session.ID,
			TaskName:    session.Description,
			Status:      session.Status,
			LastActive:  session.LastActive,
			ExtractedAt: time.Now(),
			FilesCount:  len(files),
		}
		metaBytes, _ := json.MarshalIndent(meta, "", "  ")
		metaPath := filepath.Join(sessionDir, "metadata.json")
		os.WriteFile(metaPath, metaBytes, 0644)

		fmt.Fprintf(summaryFile, "| %s | %s | %s | %d |\n", session.ID, truncate(session.Description, 50), session.Status, len(files))
		successCount++
		fmt.Printf("  ✓ Extracted %d files\n", len(files))
	}

	fmt.Printf("\nDone! Extracted %d/%d sessions to %s\n", successCount, len(filtered), baseDir)
	fmt.Printf("Summary: %s\n", summaryPath)
}

func listSessions() ([]Session, error) {
	cmd := exec.Command("jules", "remote", "list", "--session")
	output, err := cmd.CombinedOutput()
	if err != nil {
		return nil, fmt.Errorf("jules list failed: %w\nOutput: %s", err, string(output))
	}

	return parseSessionList(string(output)), nil
}

func parseSessionList(output string) []Session {
	var sessions []Session
	lines := strings.Split(output, "\n")

	// Skip header lines
	for _, line := range lines {
		line = strings.TrimSpace(line)
		if line == "" || strings.HasPrefix(line, "ID") || strings.Contains(line, "---") {
			continue
		}

		// Parse columnar output - handle variable spacing
		parts := regexp.MustCompile(`\s{2,}`).Split(line, -1)
		if len(parts) >= 5 {
			sessions = append(sessions, Session{
				ID:          strings.TrimSpace(parts[0]),
				Description: strings.TrimSpace(parts[1]),
				Repo:        strings.TrimSpace(parts[2]),
				LastActive:  strings.TrimSpace(parts[3]),
				Status:      strings.TrimSpace(parts[4]),
			})
		}
	}
	return sessions
}

func filterSessions(sessions []Session, all bool, statusFilter string) []Session {
	if all {
		return sessions
	}

	var filters []string
	if statusFilter != "" {
		filters = strings.Split(statusFilter, ",")
	} else {
		// Default: include sessions with work to extract
		filters = []string{"Completed", "Paused", "Awaiting"}
	}

	var filtered []Session
	for _, s := range sessions {
		for _, f := range filters {
			if strings.Contains(s.Status, strings.TrimSpace(f)) {
				filtered = append(filtered, s)
				break
			}
		}
	}
	return filtered
}

func pullDiff(sessionID string) (string, error) {
	cmd := exec.Command("jules", "remote", "pull", "--session", sessionID)
	output, err := cmd.CombinedOutput()
	if err != nil {
		return "", fmt.Errorf("pull failed: %w", err)
	}
	return string(output), nil
}

func extractFileList(diff string) []string {
	var files []string
	seen := make(map[string]bool)

	re := regexp.MustCompile(`diff --git a/(.+?) b/`)
	matches := re.FindAllStringSubmatch(diff, -1)
	for _, m := range matches {
		if len(m) > 1 && !seen[m[1]] {
			files = append(files, m[1])
			seen[m[1]] = true
		}
	}
	return files
}

func writeErrorFile(dir string, err error) {
	errPath := filepath.Join(dir, "ERROR.txt")
	os.WriteFile(errPath, []byte(err.Error()), 0644)
}

func truncate(s string, max int) string {
	s = strings.ReplaceAll(s, "|", "/")
	s = strings.ReplaceAll(s, "\n", " ")
	if len(s) > max {
		return s[:max-3] + "..."
	}
	return s
}
