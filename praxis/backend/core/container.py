"""Dependency Injection container for the Praxis application.

This module defines the dependency injection (DI) container for the entire application.
It uses the `dependency-injector` library to manage object creation and wiring.

For more information on `dependency-injector`, see the documentation:
https://python-dependency-injector.ets-labs.org/
"""

import typing

from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

class Container(containers.DeclarativeContainer):

    """Main DI container for the application.

    This container holds the providers for all services, repositories, and configurations.
    Providers are configured with different lifetimes (scopes) depending on their use case.

    Lifetimes:
    - Singleton: A single instance is created and shared throughout the application's lifecycle.
                 Use for objects that are expensive to create or are stateless.
    - Factory: A new instance is created every time the provider is accessed.
               Use for lightweight, stateful objects. This is a "transient" scope.
    - Resource: Manages resources that need setup and teardown, like database sessions.
                This is a form of "scoped" provider.

    Interface Binding:
    To bind an interface (defined with `typing.Protocol`) to a concrete implementation,
    define the provider for the concrete class. Type hints in the dependent classes
    should use the Protocol to enforce the contract.

    Example:
        class IMyService(typing.Protocol):
            def do_something(self) -> str: ...

        class MyService:  # Implicitly implements IMyService
            def do_something(self) -> str:
                return "Hello"

        # In the container:
        my_service = providers.Factory(MyService)

        # In a dependent class:
        class MyConsumer:
            def __init__(self, service: IMyService = Provide[Container.my_service]):
                self.service = service

    """

    # Wiring configuration
    # This tells the container which modules to scan for `@inject` decorators.
    # It's crucial for making dependency injection work automatically.
    wiring_config = containers.WiringConfiguration(
        modules=[
            # Core modules
            ".celery",
            ".asset_lock_manager",
            ".asset_manager",
            ".protocol_code_manager",
            ".run_context",
            ".workcell",
            ".workcell_runtime",
            ".celery_tasks",
            ".protocol_execution_service",
            ".scheduler",
            ".orchestrator",
            # API layer dependencies
            "praxis.backend.api.dependencies",
            "praxis.backend.api.global_dependencies",
        ],
    )

    # --- Configuration ---
    # The config provider allows injecting configuration values from YAML, .env files, etc.
    config = providers.Configuration(strict=True)

    # --- Core Services (Example of different lifetimes) ---

    # Singleton provider: one instance for the entire app lifecycle.
    # discovery_service = providers.Singleton(DiscoveryService)

    # Factory provider: a new instance is created on each injection.
    # e.g. for a service that holds request-specific state.
    # transient_service = providers.Factory(MyTransientService)

    # --- Database ---
    # The db_session_factory creates the sessionmaker. It's a singleton.
    db_session_factory: providers.Singleton[async_sessionmaker[AsyncSession]] = providers.Singleton(
        async_sessionmaker,
        # autocommit=False, autoflush=False, bind=engine
        # these would be configured from config
        expire_on_commit=False,
    )

    # The db_session provider gives a single database session per scope (e.g., per request).
    # It uses a Resource provider, which will call the async_sessionmaker
    # as a context manager to create and close the session.
    # `pyright` struggles to infer the provided type from the Resource provider,
    # so we use `# type: ignore` to suppress the incorrect error.
    db_session: providers.Provider[AsyncSession] = providers.Resource(
        db_session_factory
    )  # type: ignore[assignment]

    # --- Service Providers ---
    # Services will be registered here as we refactor them.
    # For now, keeping the existing orchestrator provider as an example.
    orchestrator = providers.Factory(
        "praxis.backend.core.orchestrator.Orchestrator",
        db_session_factory=db_session_factory,
    )
