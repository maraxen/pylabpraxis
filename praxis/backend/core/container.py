"""Dependency Injection container for the Praxis application.

This module defines the dependency injection (DI) container for the entire application.
It uses the `dependency-injector` library to manage object creation and wiring.

For more information on `dependency-injector`, see the documentation:
https://python-dependency-injector.ets-labs.org/
"""


import redis.asyncio as redis
from celery import Celery
from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from praxis.backend.services.deck import DeckService
from praxis.backend.services.machine import MachineService
from praxis.backend.services.protocol_definition import ProtocolDefinitionCRUDService
from praxis.backend.services.protocols import ProtocolRunService
from praxis.backend.services.resource import ResourceService
from praxis.backend.services.resource_type_definition import (
    ResourceTypeDefinitionService,
)

from .asset_lock_manager import AssetLockManager
from .asset_manager import AssetManager
from .celery import celery_app
from .protocol_code_manager import ProtocolCodeManager
from .protocols.asset_manager import IAssetManager
from .protocols.filesystem import IFileSystem
from .protocols.workcell import IWorkcell
from .protocols.workcell_runtime import IWorkcellRuntime
from .protocols.orchestrator import IOrchestrator
from .protocols.protocol_code_manager import IProtocolCodeManager
from .protocols.protocol_execution_service import IProtocolExecutionService
from .protocols.scheduler import IProtocolScheduler
from .scheduler import ProtocolScheduler
from .workcell import Workcell
from .workcell_runtime import WorkcellRuntime
from ..utils.filesystem import RealFileSystem


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

    # --- Redis ---
    redis_client: providers.Singleton[redis.Redis] = providers.Singleton(
        redis.Redis.from_url,
        url=config.redis.url,
        encoding="utf-8",
        decode_responses=True,
    )

    # --- Celery ---
    celery_app: providers.Object[Celery] = providers.Object(celery_app)

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
        db_session_factory,
    )  # type: ignore[assignment]

    # --- Service Providers ---
    # Services will be registered here as we refactor them.
    asset_lock_manager: providers.Singleton[AssetLockManager] = providers.Singleton(
        AssetLockManager,
        redis_client=redis_client,
    )

    protocol_code_manager: providers.Singleton[ProtocolCodeManager] = providers.Singleton(
        ProtocolCodeManager,
    )

    file_system: providers.Singleton[IFileSystem] = providers.Singleton(RealFileSystem)

    workcell: providers.Singleton[IWorkcell] = providers.Singleton(
        Workcell,
        name=config.workcell.name,
        save_file=config.workcell.save_file,
        file_system=file_system,
        backup_interval=config.workcell.backup_interval.as_int(),
        num_backups=config.workcell.num_backups.as_int(),
    )

    workcell_runtime: providers.Singleton[IWorkcellRuntime] = providers.Singleton(
        WorkcellRuntime,
        db_session_factory=db_session_factory,
        workcell=workcell,
        deck_service=providers.Factory(DeckService),
        machine_service=providers.Factory(MachineService),
        resource_service=providers.Factory(ResourceService),
        deck_type_definition_service=providers.Factory(DeckTypeDefinitionCRUDService),
        workcell_service=providers.Factory(WorkcellService),
    )

    deck_service: providers.Singleton[DeckService] = providers.Singleton(DeckService)
    machine_service: providers.Singleton[MachineService] = providers.Singleton(MachineService)
    resource_service: providers.Singleton[ResourceService] = providers.Singleton(ResourceService)
    resource_type_definition_service: providers.Singleton[ResourceTypeDefinitionService] = providers.Singleton(
        ResourceTypeDefinitionService,
        db=db_session,
    )

    protocol_run_service: providers.Singleton[ProtocolRunService] = providers.Singleton(ProtocolRunService)
    protocol_definition_service: providers.Singleton[ProtocolDefinitionCRUDService] = providers.Singleton(ProtocolDefinitionCRUDService)

    scheduler: providers.Singleton[IProtocolScheduler] = providers.Singleton(
        ProtocolScheduler,
        db_session_factory=db_session_factory,
        celery_app=celery_app,
        protocol_run_service=protocol_run_service,
        protocol_definition_service=protocol_definition_service,
    )

    orchestrator: providers.Factory[IOrchestrator] = providers.Factory(
        "praxis.backend.core.orchestrator.Orchestrator",
        db_session_factory=db_session_factory,
        asset_manager=asset_manager,
        workcell_runtime=workcell_runtime,
        protocol_code_manager=protocol_code_manager,
    )

    protocol_execution_service: providers.Factory[IProtocolExecutionService] = providers.Factory(
        "praxis.backend.core.protocol_execution_service.ProtocolExecutionService",
        db_session_factory=db_session_factory,
        asset_manager=asset_manager,
        workcell_runtime=workcell_runtime,
        scheduler=scheduler,
        orchestrator=orchestrator,
        protocol_run_service=protocol_run_service,
        protocol_definition_service=protocol_definition_service,
    )

    asset_manager: providers.Factory[IAssetManager] = providers.Factory(
        AssetManager,
        db_session=db_session,
        workcell_runtime=workcell_runtime,
        deck_service=deck_service,
        machine_service=machine_service,
        resource_service=resource_service,
        resource_type_definition_service=resource_type_definition_service,
        asset_lock_manager=asset_lock_manager,
    )

    # For now, keeping the existing orchestrator provider as an example.
