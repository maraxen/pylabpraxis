# filepath: praxis/backend/api/function_data_outputs.py
#
# This file contains the FastAPI router for all function data output endpoints,
# including data outputs from protocol function calls and plate visualization data.

from functools import partial
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

# Import the service layer, aliased as 'svc' for convenience
import praxis.backend.services as svc

# Import dependencies from the local 'api' package
from praxis.backend.api.dependencies import get_db

# Import all necessary Pydantic models from the central models package
from praxis.backend.models import (
    DataOutputTypeEnum,
    FunctionDataOutputCreate,
    FunctionDataOutputFilters,
    FunctionDataOutputResponse,
    FunctionDataOutputUpdate,
    PlateDataVisualization,
    WellDataOutputCreate,
    WellDataOutputFilters,
    WellDataOutputResponse,
    WellDataOutputUpdate,
)
from praxis.backend.utils.errors import PraxisAPIError
from praxis.backend.utils.logging import get_logger, log_async_runtime_errors

logger = get_logger(__name__)

# Initialize the FastAPI router
router = APIRouter()

log_data_output_api_errors = partial(
    log_async_runtime_errors,
    logger_instance=logger,
    raises_exception=PraxisAPIError,
)


@log_data_output_api_errors(
    exception_type=HTTPException,
    raises=True,
    prefix="Failed to create function data output: ",
    suffix="",
)
@router.post(
    "/outputs",
    response_model=FunctionDataOutputResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_function_data_output(
    data_output: FunctionDataOutputCreate,
    db: AsyncSession = Depends(get_db),
) -> FunctionDataOutputResponse:
    """Create a new function data output."""
    # Service layer returns ORM model
    orm_result = await svc.create_function_data_output(db, data_output)
    # Explicit conversion to Pydantic model
    return FunctionDataOutputResponse.model_validate(orm_result)


@log_data_output_api_errors(
    exception_type=HTTPException,
    raises=True,
    prefix="Failed to get function data outputs: ",
    suffix="",
)
@router.get(
    "/outputs",
    response_model=list[FunctionDataOutputResponse],
)
async def list_function_data_outputs(
    filters: FunctionDataOutputFilters = Depends(),
    db: AsyncSession = Depends(get_db),
) -> list[FunctionDataOutputResponse]:
    """Get function data outputs with optional filtering."""
    result = await svc.list_function_data_outputs(
        db=db,
        filters=filters.search_filters,
        data_types=filters.data_types,
        spatial_contexts=filters.spatial_contexts,
        has_numeric_data=filters.has_numeric_data,
        has_file_data=filters.has_file_data,
        min_quality_score=filters.min_quality_score,
    )
    return [FunctionDataOutputResponse.model_validate(item) for item in result]


@log_data_output_api_errors(
    exception_type=HTTPException,
    raises=True,
    prefix="Failed to get function data output: ",
    suffix="",
)
@router.get(
    "/outputs/{output_id}",
    response_model=FunctionDataOutputResponse,
)
async def read_function_data_output(
    output_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> FunctionDataOutputResponse:
    """Get a specific function data output by ID."""
    result = await svc.read_function_data_output(db, output_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Function data output with ID {output_id} not found",
        )
    return FunctionDataOutputResponse.model_validate(result)


@log_data_output_api_errors(
    exception_type=HTTPException,
    raises=True,
    prefix="Failed to update function data output: ",
    suffix="",
)
@router.put(
    "/outputs/{output_id}",
    response_model=FunctionDataOutputResponse,
)
async def update_function_data_output(
    output_id: UUID,
    data_output: FunctionDataOutputUpdate,
    db: AsyncSession = Depends(get_db),
) -> FunctionDataOutputResponse:
    """Update a function data output."""
    result = await svc.update_function_data_output(db, output_id, data_output)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Function data output with ID {output_id} not found",
        )
    return FunctionDataOutputResponse.model_validate(result)


@log_data_output_api_errors(
    exception_type=HTTPException,
    raises=True,
    prefix="Failed to delete function data output: ",
    suffix="",
)
@router.delete(
    "/outputs/{output_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_function_data_output(
    output_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a function data output."""
    success = await svc.delete_function_data_output(db, output_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Function data output with ID {output_id} not found",
        )


# Well Data Output endpoints
@log_data_output_api_errors(
    exception_type=HTTPException,
    raises=True,
    prefix="Failed to create well data output: ",
    suffix="",
)
@router.post(
    "/well-outputs",
    response_model=WellDataOutputResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_well_data_output(
    well_data_output: WellDataOutputCreate,
    db: AsyncSession = Depends(get_db),
) -> WellDataOutputResponse:
    """Create a new well data output."""
    result = await svc.create_well_data_output(db, well_data_output)
    return WellDataOutputResponse.model_validate(result)


@log_data_output_api_errors(
    exception_type=HTTPException,
    raises=True,
    prefix="Failed to get well data outputs: ",
    suffix="",
)
@router.get(
    "/well-outputs",
    response_model=list[WellDataOutputResponse],
)
async def read_well_data_outputs(
    filters: WellDataOutputFilters = Depends(),
    db: AsyncSession = Depends(get_db),
) -> list[WellDataOutputResponse]:
    """Get well data outputs with optional filtering."""
    result = await svc.read_well_data_outputs(
        db=db,
        plate_resource_id=filters.plate_resource_id,
        function_call_id=filters.function_call_id,
        protocol_run_id=filters.protocol_run_id,
        data_type=filters.data_type,
        well_row=filters.well_row,
        well_column=filters.well_column,
        skip=filters.skip,
        limit=filters.limit,
    )
    return [WellDataOutputResponse.model_validate(item) for item in result]


@log_data_output_api_errors(
    exception_type=HTTPException,
    raises=True,
    prefix="Failed to get well data output: ",
    suffix="",
)
@router.get(
    "/well-outputs/{output_id}",
    response_model=WellDataOutputResponse,
)
async def read_well_data_output(
    output_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> WellDataOutputResponse:
    """Get a specific well data output by ID."""
    result = await svc.read_well_data_output(db, output_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Well data output with ID {output_id} not found",
        )
    return WellDataOutputResponse.model_validate(result)


@log_data_output_api_errors(
    exception_type=HTTPException,
    raises=True,
    prefix="Failed to update well data output: ",
    suffix="",
)
@router.put(
    "/well-outputs/{output_id}",
    response_model=WellDataOutputResponse,
)
async def update_well_data_output(
    output_id: UUID,
    well_data_output: WellDataOutputUpdate,
    db: AsyncSession = Depends(get_db),
) -> WellDataOutputResponse:
    """Update a well data output."""
    result = await svc.update_well_data_output(db, output_id, well_data_output)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Well data output with ID {output_id} not found",
        )
    return WellDataOutputResponse.model_validate(result)


@log_data_output_api_errors(
    exception_type=HTTPException,
    raises=True,
    prefix="Failed to delete well data output: ",
    suffix="",
)
@router.delete(
    "/well-outputs/{output_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_well_data_output(
    output_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a well data output."""
    success = await svc.delete_well_data_output(db, output_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Function data output with ID {output_id} not found",
        )


# Plate visualization endpoints
@log_data_output_api_errors(
    exception_type=HTTPException,
    raises=True,
    prefix="Failed to get plate visualization data: ",
    suffix="",
)
@router.get(
    "/plate-visualization/{plate_resource_id}",
    response_model=PlateDataVisualization,
)
async def read_plate_visualization_data(
    plate_resource_id: UUID,
    data_type: DataOutputTypeEnum | None = Query(None),
    function_call_id: UUID | None = Query(None),
    protocol_run_id: UUID | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> PlateDataVisualization:
    """Get plate visualization data for a specific plate resource."""
    if data_type is None:
        data_type = DataOutputTypeEnum.GENERIC_MEASUREMENT
    result = await svc.read_plate_data_visualization(
        db=db,
        plate_resource_instance_accession_id=plate_resource_id,
        data_type=data_type,
        function_call_log_accession_id=function_call_id,
        protocol_run_accession_id=protocol_run_id,
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No data found for plate resource {plate_resource_id}",
        )
    return result
