#!/bin/bash
export TEST_DATABASE_URL=postgresql+asyncpg://test_user:test_password@localhost:5433/test_db
rm -f logs/orm_test_failures.txt
touch logs/orm_test_failures.txt

# List of failing test files
TESTS=(
    "tests/models/test_orm/test_asset_requirement_orm.py"
    "tests/models/test_orm/test_file_system_protocol_source_orm.py"
    "tests/models/test_orm/test_function_call_log_orm.py"
    "tests/models/test_orm/test_function_data_output_orm.py"
    "tests/models/test_orm/test_function_protocol_definition_orm.py"
    "tests/models/test_orm/test_machine_definition_orm.py"
    "tests/models/test_orm/test_parameter_definition_orm.py"
    "tests/models/test_orm/test_protocol_run_orm.py"
    "tests/models/test_orm/test_protocol_source_repository_orm.py"
    "tests/models/test_orm/test_resource_definition_orm.py"
    "tests/models/test_orm/test_user_orm.py"
    "tests/models/test_orm/test_well_data_output_orm.py"
)

for t in "${TESTS[@]}"; do
    echo "Running $t..."
    uv run pytest "$t" >> logs/orm_test_failures.txt 2>&1 || true
done
