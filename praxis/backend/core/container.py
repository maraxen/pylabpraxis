from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import async_sessionmaker


class Container(containers.DeclarativeContainer):
  # Configuration
  config = providers.Configuration()

  # Database
  db_session_factory = providers.Factory(async_sessionmaker)

  # Services
  orchestrator = providers.Factory(
    "praxis.backend.core.orchestrator.Orchestrator",
    db_session_factory=db_session_factory,
  )
