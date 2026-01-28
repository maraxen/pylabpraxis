CREATE TABLE schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT (datetime('now')),
    description TEXT
);
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,                    -- 6-char hex ID
    status TEXT NOT NULL DEFAULT 'TODO',    -- TODO, IN_PROGRESS, DONE, BLOCKED, ARCHIVED
    priority TEXT NOT NULL DEFAULT 'P2',    -- P1, P2, P3
    difficulty TEXT NOT NULL DEFAULT 'med', -- easy, med, hard
    mode TEXT NOT NULL DEFAULT 'manual',    -- manual, orchestrator, fixer, etc.
    description TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    archived_at TEXT, batch_id TEXT, worktree_target TEXT,
    CONSTRAINT valid_status CHECK (status IN ('TODO', 'IN_PROGRESS', 'DONE', 'BLOCKED', 'ARCHIVED')),
    CONSTRAINT valid_priority CHECK (priority IN ('P1', 'P2', 'P3'))
);
CREATE TABLE task_skills (
    task_id TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    skill TEXT NOT NULL,
    PRIMARY KEY (task_id, skill)
);
CREATE TABLE task_research (
    task_id TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    research_path TEXT NOT NULL,
    PRIMARY KEY (task_id, research_path)
);
CREATE TABLE task_workflows (
    task_id TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    workflow TEXT NOT NULL,
    PRIMARY KEY (task_id, workflow)
);
CREATE TABLE task_agents (
    task_id TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    agent TEXT NOT NULL,
    PRIMARY KEY (task_id, agent)
);
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
CREATE TABLE sqlite_sequence(name,seq);
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
    completed_at TEXT, mode TEXT, depends_on TEXT, dispatch_type TEXT DEFAULT 'pull', claimed_by TEXT, claimed_at TEXT, result TEXT, batch_id TEXT, worktree_path TEXT, worktree_cleanup INTEGER DEFAULT 0, last_ping_at TEXT, priority TEXT DEFAULT 'P2', max_steps INTEGER DEFAULT 25, retry_count INTEGER DEFAULT 0, max_retries INTEGER DEFAULT 3, error_message TEXT, execution_backend TEXT, jules_session_id TEXT, agent_mode TEXT, output_format TEXT, can_dispatch BOOLEAN DEFAULT 0, parent_dispatch_id TEXT, depth INTEGER DEFAULT 0, output_schema TEXT, profile TEXT, compatible_models TEXT, fallback_index INTEGER DEFAULT 0, worker_pid INTEGER, cdp_port INTEGER,
    CONSTRAINT valid_dispatch_status CHECK (status IN ('pending', 'running', 'completed', 'failed'))
);
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
CREATE TABLE skills (
    name TEXT PRIMARY KEY,
    description TEXT,
    source TEXT NOT NULL,                 -- 'global' or 'local'
    path TEXT NOT NULL,                   -- Path to SKILL.md
    synced_at TEXT
);
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
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_mode ON tasks(mode);
CREATE INDEX idx_dispatches_task ON dispatches(task_id);
CREATE INDEX idx_dispatches_status ON dispatches(status);
CREATE INDEX idx_tech_debt_status ON tech_debt(status);
CREATE INDEX idx_research_task ON research(task_id);
CREATE INDEX idx_recon_task ON recon(task_id);
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
CREATE INDEX idx_tasks_batch_id ON tasks(batch_id);
CREATE TABLE staging (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_text TEXT NOT NULL,
    source TEXT NOT NULL,                 -- manual, dispatch, conversation
    category TEXT,                        -- feature, bug, idea, plan
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    triaged_at TEXT,
    triaged_to TEXT,                      -- task_id, backlog_id, or 'deleted'
    CONSTRAINT valid_source CHECK (source IN ('manual', 'dispatch', 'conversation', 'import'))
);
CREATE TABLE backlog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,                        -- feature, refactor, research, debt
    source_type TEXT,                     -- tech_debt, roadmap, staging
    source_ref TEXT,                      -- ID of source item
    target_sprint TEXT,                   -- e.g., '2026-W04', 'Q1'
    status TEXT NOT NULL DEFAULT 'open',  -- open, in_progress, promoted, cancelled
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    promoted_at TEXT,
    CONSTRAINT valid_backlog_status CHECK (status IN ('open', 'in_progress', 'promoted', 'cancelled'))
);
CREATE TABLE roadmap_refs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section_anchor TEXT NOT NULL,         -- e.g., 'v2-features', 'q1-goals'
    title TEXT NOT NULL,
    description TEXT,
    path TEXT NOT NULL DEFAULT 'ROADMAP.md',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX idx_staging_triaged ON staging(triaged_at);
CREATE INDEX idx_backlog_status ON backlog(status);
CREATE INDEX idx_backlog_sprint ON backlog(target_sprint);
CREATE TABLE orch_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,      -- UUID
    started_at TEXT NOT NULL,
    ended_at TEXT,
    expires_at TEXT NOT NULL,
    focus TEXT NOT NULL,                  -- tasks, debt, staging, research, dispatches
    pid INTEGER,
    status TEXT NOT NULL DEFAULT 'running', -- running, completed, expired, killed
    summary TEXT,                          -- AI-generated session summary
    handoff_written BOOLEAN DEFAULT 0
);
CREATE INDEX idx_orch_sessions_status ON orch_sessions(status);
CREATE TABLE orch_mailbox (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    source TEXT NOT NULL,                  -- user, dispatch, workflow, cross-project
    source_ref TEXT,                       -- Dispatch ID, project name, etc.
    priority TEXT DEFAULT 'P3',
    type TEXT NOT NULL,                    -- review, action, info, question
    title TEXT NOT NULL,
    body TEXT,
    status TEXT DEFAULT 'pending',         -- pending, read, actioned, dismissed
    actioned_at TEXT,
    actioned_by TEXT,                      -- Session ID that handled it
    CONSTRAINT valid_mailbox_priority CHECK (priority IN ('P1', 'P2', 'P3')),
    CONSTRAINT valid_mailbox_type CHECK (type IN ('review', 'action', 'info', 'question', 'handoff')),
    CONSTRAINT valid_mailbox_status CHECK (status IN ('pending', 'read', 'actioned', 'dismissed'))
);
CREATE INDEX idx_orch_mailbox_status ON orch_mailbox(status);
CREATE INDEX idx_orch_mailbox_priority ON orch_mailbox(priority);
CREATE TABLE orch_workflows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    cron_expression TEXT NOT NULL,
    prompt TEXT NOT NULL,
    enabled BOOLEAN DEFAULT 1,
    last_run TEXT,
    next_run TEXT,
    run_count INTEGER DEFAULT 0
);
CREATE INDEX idx_orch_workflows_next ON orch_workflows(next_run);
CREATE TABLE orch_activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL DEFAULT (datetime('now')),
    event TEXT NOT NULL,
    session_id TEXT,
    data TEXT                              -- JSON blob for extra data
);
CREATE INDEX idx_orch_activity_event ON orch_activity(event);
CREATE INDEX idx_orch_activity_ts ON orch_activity(ts);
CREATE TABLE agent_presets (
    name TEXT PRIMARY KEY,
    mode TEXT NOT NULL,                    -- @fixer, @explorer, etc.
    output_format TEXT DEFAULT 'markdown',
    can_dispatch BOOLEAN DEFAULT 0,
    max_steps INTEGER DEFAULT 25,
    output_schema TEXT,                    -- JSON schema (nullable)
    description TEXT
);
