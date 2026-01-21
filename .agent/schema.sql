-- Agent Infrastructure SQLite Schema
-- Version: 1.0.0
-- Created: 2026-01-20
--
-- DEVIATIONS FROM PLAN:
-- 1. Added triggers to automatically update 'updated_at' fields on changes.
-- 2. Added explicit foreign key support pragma check comment (pragma must be enabled per connection).
-- 3. Ensured JSON fields validation is handled at application layer (TEXT storage).

-- Core metadata
CREATE TABLE schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT (datetime('now')),
    description TEXT
);

-- Tasks (replaces DEVELOPMENT_MATRIX.md)
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,                    -- 6-char hex ID
    status TEXT NOT NULL DEFAULT 'TODO',    -- TODO, IN_PROGRESS, DONE, BLOCKED, ARCHIVED
    priority TEXT NOT NULL DEFAULT 'P2',    -- P1, P2, P3
    difficulty TEXT NOT NULL DEFAULT 'med', -- easy, med, hard
    mode TEXT NOT NULL DEFAULT 'manual',    -- manual, orchestrator, fixer, etc.
    description TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    archived_at TEXT,
    CONSTRAINT valid_status CHECK (status IN ('TODO', 'IN_PROGRESS', 'DONE', 'BLOCKED', 'ARCHIVED')),
    CONSTRAINT valid_priority CHECK (priority IN ('P1', 'P2', 'P3'))
);

-- Task-Skill associations (many-to-many)
CREATE TABLE task_skills (
    task_id TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    skill TEXT NOT NULL,
    PRIMARY KEY (task_id, skill)
);

-- Task-Research associations
CREATE TABLE task_research (
    task_id TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    research_path TEXT NOT NULL,
    PRIMARY KEY (task_id, research_path)
);

-- Task-Workflow associations
CREATE TABLE task_workflows (
    task_id TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    workflow TEXT NOT NULL,
    PRIMARY KEY (task_id, workflow)
);

-- Task-Agent assignments
CREATE TABLE task_agents (
    task_id TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    agent TEXT NOT NULL,
    PRIMARY KEY (task_id, agent)
);

-- Technical Debt (replaces TECHNICAL_DEBT.md)
CREATE TABLE tech_debt (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    category TEXT NOT NULL,               -- infrastructure, schema, ux, etc.
    status TEXT NOT NULL DEFAULT 'open',  -- open, in_progress, resolved
    description TEXT NOT NULL,
    impact TEXT,
    proposed_solution TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    resolved_at TEXT,
    related_task_id TEXT REFERENCES tasks(id),
    CONSTRAINT valid_debt_status CHECK (status IN ('open', 'in_progress', 'resolved'))
);

-- Dispatch Log (replaces dispatch.log)
CREATE TABLE dispatches (
    id TEXT PRIMARY KEY,                  -- DISP-YYMMDDHHMMSS-XXXX
    target TEXT NOT NULL,                 -- cli, jules
    task_id TEXT REFERENCES tasks(id),
    model TEXT,
    prompt_hash TEXT NOT NULL,            -- SHA256 of prompt (for dedup)
    prompt_preview TEXT NOT NULL,         -- First 200 chars
    prompt_full TEXT NOT NULL,            -- Full prompt (sanitized)
    status TEXT NOT NULL DEFAULT 'pending', -- pending, running, completed, failed
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at TEXT,
    CONSTRAINT valid_dispatch_status CHECK (status IN ('pending', 'running', 'completed', 'failed'))
);

-- Reusable Prompts (replaces prompts/reuse/*.md)
CREATE TABLE prompts (
    name TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    content TEXT NOT NULL,                -- Full markdown content
    placeholders TEXT,                    -- JSON array of placeholder definitions
    tags TEXT,                            -- JSON array of tags
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    CONSTRAINT valid_placeholders CHECK (placeholders IS NULL OR json_valid(placeholders)),
    CONSTRAINT valid_tags CHECK (tags IS NULL OR json_valid(tags))
);

-- Skills (metadata only - SKILL.md files stay on disk)
CREATE TABLE skills (
    name TEXT PRIMARY KEY,
    description TEXT,
    source TEXT NOT NULL,                 -- 'global' or 'local'
    path TEXT NOT NULL,                   -- Path to SKILL.md
    synced_at TEXT
);

-- Orchestration Lessons (replaces ORCHESTRATION.md table)
CREATE TABLE lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    context TEXT NOT NULL,
    outcome TEXT NOT NULL,                -- success, partial, failure
    lesson TEXT NOT NULL,
    action TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    CONSTRAINT valid_outcome CHECK (outcome IN ('success', 'partial', 'failure'))
);

-- Research Reports (JSON-structured findings)
CREATE TABLE research (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    task_id TEXT REFERENCES tasks(id),
    summary TEXT NOT NULL,
    findings TEXT NOT NULL,               -- JSON object with structured findings
    sources TEXT,                         -- JSON array of source references
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    CONSTRAINT valid_research_findings CHECK (json_valid(findings)),
    CONSTRAINT valid_sources CHECK (sources IS NULL OR json_valid(sources))
);

-- Recon Reports (JSON-structured reconnaissance)
CREATE TABLE recon (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target TEXT NOT NULL,                 -- What was investigated (file, feature, etc.)
    task_id TEXT REFERENCES tasks(id),
    status TEXT NOT NULL,                 -- found, not_found, partial
    summary TEXT NOT NULL,
    findings TEXT NOT NULL,               -- JSON object with structured findings
    recommendations TEXT,                 -- JSON array of next steps
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    CONSTRAINT valid_recon_status CHECK (status IN ('found', 'not_found', 'partial')),
    CONSTRAINT valid_recon_findings CHECK (json_valid(findings)),
    CONSTRAINT valid_recommendations CHECK (recommendations IS NULL OR json_valid(recommendations))
);

-- Create indexes for common queries
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_mode ON tasks(mode);
CREATE INDEX idx_dispatches_task ON dispatches(task_id);
CREATE INDEX idx_dispatches_status ON dispatches(status);
CREATE INDEX idx_tech_debt_status ON tech_debt(status);
CREATE INDEX idx_research_task ON research(task_id);
CREATE INDEX idx_recon_task ON recon(task_id);

-- TRIGGERS (Auto-update updated_at)

CREATE TRIGGER update_tasks_timestamp 
AFTER UPDATE ON tasks
BEGIN
    UPDATE tasks SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER update_prompts_timestamp 
AFTER UPDATE ON prompts
BEGIN
    UPDATE prompts SET updated_at = datetime('now') WHERE name = NEW.name;
END;

CREATE TRIGGER update_research_timestamp 
AFTER UPDATE ON research
BEGIN
    UPDATE research SET updated_at = datetime('now') WHERE id = NEW.id;
END;
