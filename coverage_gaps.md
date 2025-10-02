# Coverage Gaps

This document lists the modules with the lowest test coverage, based on the latest `pytest --cov=praxis` run.

## Core Layer (`praxis/backend/core`)

| Module                      | Coverage |
| --------------------------- | -------- |
| `celery_base.py`            | 0%       |
| `asset_lock_manager.py`     | 15%      |
| `orchestrator.py`           | 20%      |
| `asset_manager.py`          | 21%      |
| `workcell_runtime.py`       | 22%      |

## Service Layer (`praxis/backend/services`)

| Module                      | Coverage |
| --------------------------- | -------- |
| `scheduler.py`              | 0%       |
| `type_definition_base.py`   | 0%       |
| `utils/plr_type_base.py`    | 0%       |
| `plate_parsing.py`          | 12%      |
| `discovery_service.py`      | 16%      |