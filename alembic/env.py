# alembic/env.py
# TODO: Remove this import if not needed
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

import praxis.backend.database_models  # type: ignore
from alembic import context
from praxis.backend.utils.db import PRAXIS_DATABASE_URL as DATABASE_URL
from praxis.backend.utils.db import Base as PraxisBase

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# TODO: add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# --- MODIFICATION FOR PRAXIS ---

target_metadata = PraxisBase.metadata # Use the Base from your application
# --- END MODIFICATION ---

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# --- MODIFICATION FOR PRAXIS ---
# Set the SQLAlchemy URL from your application's config
# This ensures Alembic uses the same database URL as your application
config.set_main_option('sqlalchemy.url', DATABASE_URL)
# --- END MODIFICATION ---


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # --- MODIFICATION FOR PRAXIS ---
        # compare_type=True enables detection of column type changes.
        # include_schemas=True if you use multiple schemas (default is usually public)
        compare_type=True,
        # --- END MODIFICATION ---
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # --- MODIFICATION FOR PRAXIS ---
            compare_type=True, # For detecting column type changes
            # include_schemas=True, # If you use multiple schemas
            # --- END MODIFICATION ---
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

