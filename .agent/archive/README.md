# Agent Archive

This directory manages the long-term storage of project artifacts, completed prompts, and historical logs. To keep the workspace clean, older content is consolidated into a compressed archive.

## Contents

- **`archive.tar.gz`**: The master archive file containing all historical data.
- **`COMPRESSED_ARCHIVE.md`**: A high-level manifest of what is inside the tarball.
- **`UPDATE_ARCHIVE.md`**: A reusable prompt for agents to perform the archiving process.
- **`artifacts/`**: Loose artifacts currently slated for the next archive update.

## How to Archive

To move current loose folders (like `prompts/`, `backlog/`, `artifacts/`, etc.) into the archive:

1. Read the instructions in `UPDATE_ARCHIVE.md`.
2. Execute the steps described there (or ask an agent to "Update the archive using the instructions in .agent/archive/UPDATE_ARCHIVE.md").

This process will:

1. Unpack `archive.tar.gz`.
2. Merge the current loose directories into the unpacked content.
3. Update the `COMPRESSED_ARCHIVE.md` manifest.
4. Re-compress everything into `archive.tar.gz`.
5. Clean up the loose directories.
