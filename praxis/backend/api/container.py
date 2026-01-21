from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from praxis.backend.core.container import Container
from praxis.backend.core.protocol_execution_service import ProtocolExecutionService


@inject
def get_protocol_execution_service(
  service: ProtocolExecutionService = Depends(Provide[Container.protocol_execution_service]),
) -> ProtocolExecutionService:
  return service
