# Update Archive Workflow

**Trigger**: When `.agents/archive/` becomes cluttered with loose folders (e.g., `prompts/`, `summaries/`, `backlog/`) that are no longer active.
**Goal**: Merge these loose folders into `archive.tar.gz` and update the manifest.

---

## Agent Instructions

Follow these steps to update the archive.

### 1. Setup

Initialize a temporary workspace.

```bash
# Create a temp directory for unpacking
mkdir -p .agents/archive/.temp_pack
```

### 2. Unpack Existing Archive

If `archive.tar.gz` exists, unpack it.

```bash
if [ -f .agents/archive/archive.tar.gz ]; then
  tar -xzf .agents/archive/archive.tar.gz -C .agents/archive/.temp_pack
  echo "Unpacked existing archive."
else
  echo "No existing archive found. Starting fresh."
fi
```

### 3. Merge Content

Move candidate directories into the temp location. Use `rsync` to merge contents if directories already exist, then remove the source.

**Candidates to archive**:

- `.agents/archive/prompts`
- `.agents/archive/summaries`
- `.agents/archive/backlog`
- `.agents/archive/artifacts`
- *(Add any other dated or completed folders found in .agents/archive)*

**Exclusions**:

- `archive.tar.gz`
- `README.md`
- `UPDATE_ARCHIVE.md`
- `COMPRESSED_ARCHIVE.md`

**Command Template**:
For each candidate directory (e.g., `prompts`):

```bash
# Example for 'prompts'
if [ -d .agents/archive/prompts ]; then
  # Snyc contents to temp/prompts, creating it if needed
  rsync -av .agents/archive/prompts/ .agents/archive/.temp_pack/prompts/
  # Remove the source directory after successful sync
  rm -rf .agents/archive/prompts
  echo "Archived prompts."
fi
```

*Repeat this logic for all candidates.*

### 4. Optimize and Index

1. **Generate Tree**: Run `tree` or `ls -R` on `.agents/archive/.temp_pack` to analyze contents.
2. **Update Manifest**: Write a summary to `.agents/archive/COMPRESSED_ARCHIVE.md`.
    - List top-level directories.
    - Note the range of dates or prompt IDs (e.g., "Contains prompts from 260101 to 260115").
    - Append a log entry with today's date and what was added.

### 5. Repack and Cleanup

Compress the consolidated content back to the tarball.

```bash
# Compress
tar -czf .agents/archive/archive.tar.gz -C .agents/archive/.temp_pack .

# Cleanup temp
rm -rf .agents/archive/.temp_pack

# Report
ls -lh .agents/archive/archive.tar.gz
```

### 6. Validation

- Verify `archive.tar.gz` is non-empty.
- Verify `COMPRESSED_ARCHIVE.md` is updated.
- Verify loose folders are gone.
