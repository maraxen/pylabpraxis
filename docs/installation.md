# Installation

## Requirements

- Python >= 3.10
- PostgreSQL (v16 recommended)
- Redis
- `uv` (Universal Python Package Manager)

## Installation Steps

1. **Install `uv`**:
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2. **Clone the repository**:
    ```bash
    git clone https://github.com/maraxen/pylabpraxis.git
    cd pylabpraxis
    ```

3. **Install Dependencies**:
    `uv` handles virtual environment creation and dependency installation automatically.
    ```bash
    uv sync
    ```

4. **Environment Configuration**:
    Copy the example configuration:
    ```bash
    cp .env.example .env
    # Edit .env with your database/redis credentials
    ```

5. **Run the Application**:
    ```bash
    uv run uvicorn main:app --reload
    ```

## Development

- **Run Tests**: `uv run pytest`
- **Lint**: `uv run ruff check .`
- **Type Check**: `ty check`
