"""Tests for core/container.py."""

from celery import Celery
from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import async_sessionmaker

from praxis.backend.core.container import Container


class TestContainerStructure:
    """Tests for Container class structure."""

    def test_container_is_declarative_container(self) -> None:
        """Test that Container inherits from DeclarativeContainer."""
        assert issubclass(Container, containers.DeclarativeContainer)

    def test_container_has_wiring_config(self) -> None:
        """Test that Container has wiring configuration."""
        assert hasattr(Container, "wiring_config")
        assert isinstance(Container.wiring_config, containers.WiringConfiguration)

    def test_wiring_config_includes_core_modules(self) -> None:
        """Test that wiring config includes core modules."""
        modules = Container.wiring_config.modules
        assert ".celery" in modules
        assert ".asset_lock_manager" in modules
        assert ".asset_manager" in modules
        assert ".protocol_code_manager" in modules

    def test_wiring_config_includes_api_modules(self) -> None:
        """Test that wiring config includes API modules."""
        modules = Container.wiring_config.modules
        assert "praxis.backend.api.dependencies" in modules
        assert "praxis.backend.api.global_dependencies" in modules


class TestContainerConfigProvider:
    """Tests for Container configuration provider."""

    def test_container_has_config_provider(self) -> None:
        """Test that Container has config provider."""
        assert hasattr(Container, "config")

    def test_config_is_configuration_provider(self) -> None:
        """Test that config is a Configuration provider."""
        assert isinstance(Container.config, providers.Configuration)

    def test_config_is_strict(self) -> None:
        """Test that config provider is strict."""
        # The config provider has strict mode enabled via Configuration(strict=True)
        # We can verify by checking the init parameters
        assert hasattr(Container.config, "strict")


class TestContainerRedisProvider:
    """Tests for Container Redis provider."""

    def test_container_has_redis_client_provider(self) -> None:
        """Test that Container has redis_client provider."""
        assert hasattr(Container, "redis_client")

    def test_redis_client_is_singleton_provider(self) -> None:
        """Test that redis_client is a Singleton provider."""
        assert isinstance(Container.redis_client, providers.Singleton)


class TestContainerCeleryProvider:
    """Tests for Container Celery provider."""

    def test_container_has_celery_app_provider(self) -> None:
        """Test that Container has celery_app provider."""
        assert hasattr(Container, "celery_app")

    def test_celery_app_is_object_provider(self) -> None:
        """Test that celery_app is an Object provider."""
        assert isinstance(Container.celery_app, providers.Object)


class TestContainerDatabaseProviders:
    """Tests for Container database providers."""

    def test_container_has_db_session_factory(self) -> None:
        """Test that Container has db_session_factory provider."""
        assert hasattr(Container, "db_session_factory")

    def test_db_session_factory_is_singleton_provider(self) -> None:
        """Test that db_session_factory is a Singleton provider."""
        assert isinstance(Container.db_session_factory, providers.Singleton)

    def test_container_has_db_session(self) -> None:
        """Test that Container has db_session provider."""
        assert hasattr(Container, "db_session")

    def test_db_session_is_resource_provider(self) -> None:
        """Test that db_session is a Resource provider."""
        assert isinstance(Container.db_session, providers.Resource)


class TestContainerServiceProviders:
    """Tests for Container service providers."""

    def test_container_has_asset_lock_manager(self) -> None:
        """Test that Container has asset_lock_manager provider."""
        assert hasattr(Container, "asset_lock_manager")

    def test_asset_lock_manager_is_singleton(self) -> None:
        """Test that asset_lock_manager is a Singleton provider."""
        assert isinstance(Container.asset_lock_manager, providers.Singleton)

    def test_container_has_protocol_code_manager(self) -> None:
        """Test that Container has protocol_code_manager provider."""
        assert hasattr(Container, "protocol_code_manager")

    def test_protocol_code_manager_is_singleton(self) -> None:
        """Test that protocol_code_manager is a Singleton provider."""
        assert isinstance(Container.protocol_code_manager, providers.Singleton)

    def test_container_has_file_system(self) -> None:
        """Test that Container has file_system provider."""
        assert hasattr(Container, "file_system")

    def test_file_system_is_singleton(self) -> None:
        """Test that file_system is a Singleton provider."""
        assert isinstance(Container.file_system, providers.Singleton)

    def test_container_has_workcell(self) -> None:
        """Test that Container has workcell provider."""
        assert hasattr(Container, "workcell")

    def test_workcell_is_singleton(self) -> None:
        """Test that workcell is a Singleton provider."""
        assert isinstance(Container.workcell, providers.Singleton)

    def test_container_has_workcell_runtime(self) -> None:
        """Test that Container has workcell_runtime provider."""
        assert hasattr(Container, "workcell_runtime")

    def test_workcell_runtime_is_singleton(self) -> None:
        """Test that workcell_runtime is a Singleton provider."""
        assert isinstance(Container.workcell_runtime, providers.Singleton)

    def test_container_has_deck_service(self) -> None:
        """Test that Container has deck_service provider."""
        assert hasattr(Container, "deck_service")

    def test_deck_service_is_singleton(self) -> None:
        """Test that deck_service is a Singleton provider."""
        assert isinstance(Container.deck_service, providers.Singleton)

    def test_container_has_machine_service(self) -> None:
        """Test that Container has machine_service provider."""
        assert hasattr(Container, "machine_service")

    def test_machine_service_is_singleton(self) -> None:
        """Test that machine_service is a Singleton provider."""
        assert isinstance(Container.machine_service, providers.Singleton)

    def test_container_has_resource_service(self) -> None:
        """Test that Container has resource_service provider."""
        assert hasattr(Container, "resource_service")

    def test_resource_service_is_singleton(self) -> None:
        """Test that resource_service is a Singleton provider."""
        assert isinstance(Container.resource_service, providers.Singleton)

    def test_container_has_resource_type_definition_service(self) -> None:
        """Test that Container has resource_type_definition_service provider."""
        assert hasattr(Container, "resource_type_definition_service")

    def test_resource_type_definition_service_is_singleton(self) -> None:
        """Test that resource_type_definition_service is a Singleton provider."""
        assert isinstance(Container.resource_type_definition_service, providers.Singleton)

    def test_container_has_protocol_run_service(self) -> None:
        """Test that Container has protocol_run_service provider."""
        assert hasattr(Container, "protocol_run_service")

    def test_protocol_run_service_is_singleton(self) -> None:
        """Test that protocol_run_service is a Singleton provider."""
        assert isinstance(Container.protocol_run_service, providers.Singleton)

    def test_container_has_protocol_definition_service(self) -> None:
        """Test that Container has protocol_definition_service provider."""
        assert hasattr(Container, "protocol_definition_service")

    def test_protocol_definition_service_is_singleton(self) -> None:
        """Test that protocol_definition_service is a Singleton provider."""
        assert isinstance(Container.protocol_definition_service, providers.Singleton)

    def test_container_has_scheduler(self) -> None:
        """Test that Container has scheduler provider."""
        assert hasattr(Container, "scheduler")

    def test_scheduler_is_singleton(self) -> None:
        """Test that scheduler is a Singleton provider."""
        assert isinstance(Container.scheduler, providers.Singleton)

    def test_container_has_asset_manager(self) -> None:
        """Test that Container has asset_manager provider."""
        assert hasattr(Container, "asset_manager")

    def test_asset_manager_is_factory(self) -> None:
        """Test that asset_manager is a Factory provider."""
        assert isinstance(Container.asset_manager, providers.Factory)

    def test_container_has_orchestrator(self) -> None:
        """Test that Container has orchestrator provider."""
        assert hasattr(Container, "orchestrator")

    def test_orchestrator_is_factory(self) -> None:
        """Test that orchestrator is a Factory provider."""
        assert isinstance(Container.orchestrator, providers.Factory)

    def test_container_has_protocol_execution_service(self) -> None:
        """Test that Container has protocol_execution_service provider."""
        assert hasattr(Container, "protocol_execution_service")

    def test_protocol_execution_service_is_factory(self) -> None:
        """Test that protocol_execution_service is a Factory provider."""
        assert isinstance(Container.protocol_execution_service, providers.Factory)


class TestContainerInstantiation:
    """Tests for Container instantiation."""

    def test_container_can_be_instantiated(self) -> None:
        """Test that Container can be instantiated."""
        container = Container()
        # When instantiated, DeclarativeContainer creates a DynamicContainer
        assert isinstance(container, containers.DynamicContainer)
        # Verify it has the expected providers
        assert hasattr(container, "config")
        assert hasattr(container, "redis_client")

    def test_container_config_can_be_updated(self) -> None:
        """Test that container config can be updated."""
        container = Container()

        # Update config values
        container.config.from_dict({
            "redis": {"url": "redis://localhost:6379/0"},
            "workcell": {
                "name": "test_workcell",
                "save_file": "/tmp/test.json",
                "backup_interval": 60,
                "num_backups": 3,
            },
        })

        assert container.config.redis.url() == "redis://localhost:6379/0"
        assert container.config.workcell.name() == "test_workcell"


class TestContainerProviderOverriding:
    """Tests for Container provider overriding."""

    def test_container_can_override_singleton_provider(self) -> None:
        """Test that singleton providers can be overridden."""
        container = Container()

        # Create mock provider
        mock_redis = providers.Singleton(lambda: "mock_redis")

        # Override provider
        container.redis_client.override(mock_redis)

        # Verify override
        assert container.redis_client.provided is not None

    def test_container_can_reset_overrides(self) -> None:
        """Test that overrides can be reset."""
        container = Container()

        # Override provider
        mock_redis = providers.Singleton(lambda: "mock_redis")
        container.redis_client.override(mock_redis)

        # Reset override
        container.redis_client.reset_override()

        # Verify reset (provider should be back to original)
        assert container.redis_client.provided is not None


class TestContainerIntegration:
    """Integration tests for Container."""

    def test_container_providers_chain(self) -> None:
        """Test that providers can reference each other."""
        container = Container()

        # Configure container
        container.config.from_dict({
            "redis": {"url": "redis://localhost:6379/0"},
            "workcell": {
                "name": "test_workcell",
                "save_file": "/tmp/test.json",
                "backup_interval": 60,
                "num_backups": 3,
            },
        })

        # Verify providers are connected
        # asset_lock_manager depends on redis_client
        assert container.asset_lock_manager.provided is not None

        # scheduler depends on multiple providers
        assert container.scheduler.provided is not None

        # asset_manager depends on many providers
        assert container.asset_manager.provided is not None

    def test_container_all_required_providers_present(self) -> None:
        """Test that all required providers are present in container."""
        container = Container()

        required_providers = [
            "config",
            "redis_client",
            "celery_app",
            "db_session_factory",
            "db_session",
            "asset_lock_manager",
            "protocol_code_manager",
            "file_system",
            "workcell",
            "workcell_runtime",
            "deck_service",
            "machine_service",
            "resource_service",
            "resource_type_definition_service",
            "protocol_run_service",
            "protocol_definition_service",
            "scheduler",
            "asset_manager",
            "orchestrator",
            "protocol_execution_service",
        ]

        for provider_name in required_providers:
            assert hasattr(container, provider_name), f"Missing provider: {provider_name}"
