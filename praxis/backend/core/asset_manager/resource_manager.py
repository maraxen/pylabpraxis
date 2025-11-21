# pylint: disable=too-many-arguments,too-many-locals,too-many-branches,too-many-statements,logging-fstring-interpolation
# ruff: noqa: E501, FBT001, G004
"""Resource management logic for AssetManager."""

import importlib
import uuid
from typing import TYPE_CHECKING, Any

from pylabrobot.resources import Deck

from praxis.backend.models.orm.resource import (
    ResourceDefinitionOrm,
    ResourceOrm,
    ResourceStatusEnum,
)
from praxis.backend.models.pydantic_internals.asset import AcquireAsset
from praxis.backend.models.pydantic_internals.filters import SearchFilters
from praxis.backend.models.pydantic_internals.resource import ResourceUpdate
from praxis.backend.utils.errors import AssetAcquisitionError, AssetReleaseError
from praxis.backend.utils.logging import get_logger

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from praxis.backend.core.protocols.workcell_runtime import IWorkcellRuntime
    from praxis.backend.services.resource import ResourceService
    from praxis.backend.services.resource_type_definition import (
        ResourceTypeDefinitionService,
    )

logger = get_logger(__name__)


class ResourceManagerMixin:
    """Mixin for managing resource acquisition and release."""

    # Type hinting for dependencies expected on the main class
    db: "AsyncSession"
    workcell_runtime: "IWorkcellRuntime"
    resource_svc: "ResourceService"
    resource_type_definition_svc: "ResourceTypeDefinitionService"

    async def _find_resource_to_acquire(
        self,
        protocol_run_accession_id: uuid.UUID,
        fqn: str,
        user_choice_instance_accession_id: uuid.UUID | None,
        property_constraints: dict[str, Any] | None,
    ) -> ResourceOrm | None:
        if user_choice_instance_accession_id:
            instance_orm = await self.resource_svc.get(
                self.db,
                user_choice_instance_accession_id,
            )
            if not instance_orm:
                msg = f"Specified resource ID {user_choice_instance_accession_id} not found."
                raise AssetAcquisitionError(
                    msg,
                )
            if instance_orm.fqn != fqn:
                msg = (
                    f"Chosen instance {user_choice_instance_accession_id} (Def: {instance_orm.fqn}) "
                    f"mismatches constraint {fqn}."
                )
                raise AssetAcquisitionError(
                    msg,
                )
            if instance_orm.status == ResourceStatusEnum.IN_USE:
                if instance_orm.current_protocol_run_accession_id != uuid.UUID(
                    str(protocol_run_accession_id),
                ):
                    msg = f" {user_choice_instance_accession_id} IN_USE by another run."
                    raise AssetAcquisitionError(
                        msg,
                    )
            elif instance_orm.status not in [
                ResourceStatusEnum.AVAILABLE_IN_STORAGE,
                ResourceStatusEnum.AVAILABLE_ON_DECK,
            ]:
                msg = (
                    f"Chosen instance {user_choice_instance_accession_id} not available (Status: "
                    f"{instance_orm.status.name})."
                )
                raise AssetAcquisitionError(
                    msg,
                )
            return instance_orm
        filters = SearchFilters(
            search_filters={
                "fqn": fqn,
                "status": ResourceStatusEnum.IN_USE,
                "current_protocol_run_accession_id_filter": str(protocol_run_accession_id),
            },
            property_filters=property_constraints,
        )
        in_use_list = await self.resource_svc.get_multi(
            self.db,
            filters=filters,
        )
        if in_use_list:
            return in_use_list[0]
        filters = SearchFilters(
            search_filters={"fqn": fqn, "status": ResourceStatusEnum.AVAILABLE_ON_DECK},
            property_filters=property_constraints,
        )
        on_deck_list = await self.resource_svc.get_multi(
            self.db,
            filters=filters,
        )
        if on_deck_list:
            return on_deck_list[0]
        filters = SearchFilters(
            search_filters={
                "fqn": fqn,
                "status": ResourceStatusEnum.AVAILABLE_IN_STORAGE,
            },
            property_filters=property_constraints,
        )
        in_storage_list = await self.resource_svc.get_multi(
            self.db,
            filters=filters,
        )
        if in_storage_list:
            return in_storage_list[0]
        return None

    async def _update_resource_acquisition_status(
        self,
        resource_to_acquire: ResourceOrm,
        protocol_run_accession_id: uuid.UUID,
        target_deck_resource_accession_id: uuid.UUID | None,
        target_position_name: str | None,
        final_status_details: str,
    ) -> ResourceOrm:
        update_data = ResourceUpdate(
            status=ResourceStatusEnum.IN_USE,
            current_protocol_run_accession_id=protocol_run_accession_id,
            machine_location_accession_id=target_deck_resource_accession_id,
            current_deck_position_name=target_position_name,
            status_details=final_status_details,
        )
        updated_resource = await self.resource_svc.update(
            db=self.db,
            db_obj=resource_to_acquire,
            obj_in=update_data,
        )
        if not updated_resource:
            msg = f"CRITICAL: Failed to update DB status for resource '{resource_to_acquire.name}'."
            raise AssetAcquisitionError(
                msg,
            )
        return updated_resource

    async def acquire_resource(
        self,
        resource_data: AcquireAsset,
    ) -> tuple[Any, uuid.UUID, str]:
        """Acquire a resource instance that is available."""
        logger.info(
            "AM_ACQUIRE_RESOURCE: Acquiring '%s' (Def: '%s') for run '%s'. Loc: %s",
            resource_data.requested_asset_name_in_protocol,
            resource_data.fqn,
            resource_data.protocol_run_accession_id,
            resource_data.location_constraints,
        )

        resource_to_acquire = await self._find_resource_to_acquire(
            resource_data.protocol_run_accession_id,
            resource_data.fqn,
            resource_data.instance_accession_id,
            resource_data.property_constraints,
        )

        if not resource_to_acquire:
            msg = f"No instance found for definition '{resource_data.fqn}' matching criteria for run '{resource_data.protocol_run_accession_id}'."
            raise AssetAcquisitionError(
                msg,
            )

        resource_def_orm = await self.resource_type_definition_svc.get_by_name(
            self.db,
            name=resource_to_acquire.fqn,
        )
        if not resource_def_orm or not resource_def_orm.fqn:
            update_data = ResourceUpdate(
                status=ResourceStatusEnum.ERROR,
                status_details=f"FQN missing for def {resource_to_acquire.fqn}",
            )
            await self.resource_svc.update(
                db=self.db,
                db_obj=resource_to_acquire,
                obj_in=update_data,
            )
            msg = f"FQN not found for resource definition '{resource_to_acquire.fqn}'."
            raise AssetAcquisitionError(
                msg,
            )

        live_plr_resource = await self.workcell_runtime.create_or_get_resource(
            resource_orm=resource_to_acquire,
            resource_definition_fqn=resource_def_orm.fqn,
        )
        if not live_plr_resource:
            update_data = ResourceUpdate(
                status=ResourceStatusEnum.ERROR,
                status_details="PLR object creation failed.",
            )
            await self.resource_svc.update(
                db=self.db,
                db_obj=resource_to_acquire,
                obj_in=update_data,
            )
            msg = f"Failed to create/get PLR object for '{resource_to_acquire.name}'."
            raise AssetAcquisitionError(
                msg,
            )

        target_deck_resource_accession_id: uuid.UUID | None = None
        target_position_name: str | None = None
        final_status_details = f"In use by run {resource_data.protocol_run_accession_id}"
        is_acquiring_a_deck_resource = isinstance(live_plr_resource, Deck)

        (
            target_deck_resource_accession_id,
            target_position_name,
            final_status_details,
        ) = await self._handle_location_constraints(
            is_acquiring_a_deck_resource,
            resource_data.location_constraints,
            resource_to_acquire,
            resource_data.protocol_run_accession_id,
        )

        needs_db_update = not (
            resource_to_acquire.status == ResourceStatusEnum.IN_USE
            and resource_to_acquire.current_protocol_run_accession_id
            == uuid.UUID(str(resource_data.protocol_run_accession_id))
            and (
                is_acquiring_a_deck_resource
                or (
                    resource_to_acquire.machine_location_accession_id
                    == target_deck_resource_accession_id
                    and resource_to_acquire.current_deck_position_name == target_position_name
                )
            )
        )

        if needs_db_update:
            resource_to_acquire = await self._update_resource_acquisition_status(
                resource_to_acquire=resource_to_acquire,
                protocol_run_accession_id=resource_data.protocol_run_accession_id,
                target_deck_resource_accession_id=target_deck_resource_accession_id,
                target_position_name=target_position_name,
                final_status_details=final_status_details,
            )

        logger.info(
            "AM_ACQUIRE_RESOURCE: Resource '%s' (ID: %s) acquired. Status: IN_USE.",
            resource_to_acquire.name,
            resource_to_acquire.accession_id,
        )
        return live_plr_resource, resource_to_acquire.accession_id, "resource"

    def _is_deck_resource(self, resource_def_orm: ResourceDefinitionOrm | None) -> bool:
        if not resource_def_orm or not resource_def_orm.fqn:
            return False
        try:
            module_path, class_name = resource_def_orm.fqn.rsplit(".", 1)
            plr_class = getattr(importlib.import_module(module_path), class_name)
            return issubclass(plr_class, Deck)
        except (ImportError, AttributeError):
            return False

    async def _handle_resource_release_location(
        self,
        is_releasing_a_deck_resource: bool,
        resource_to_release: ResourceOrm,
        resource_orm_accession_id: uuid.UUID,
        clear_from_accession_id: uuid.UUID | None,
        clear_from_position_name: str | None,
    ) -> tuple[uuid.UUID | None, str | None]:
        if is_releasing_a_deck_resource:
            logger.info(
                "AM_RELEASE_RESOURCE: '%s' is a Deck resource. Clearing its WCR state.",
                resource_to_release.name,
            )
            await self.workcell_runtime.clear_resource(
                resource_orm_accession_id,
            )
            return None, None
        if clear_from_accession_id and clear_from_position_name:
            logger.info(
                "AM_RELEASE_RESOURCE: Clearing '%s' from deck ID %s, pos '%s'.",
                resource_to_release.name,
                clear_from_accession_id,
                clear_from_position_name,
            )
            await self.workcell_runtime.clear_deck_position(
                deck_orm_accession_id=clear_from_accession_id,
                position_name=clear_from_position_name,
                resource_orm_accession_id=resource_orm_accession_id,
            )
            return clear_from_accession_id, clear_from_position_name
        await self.workcell_runtime.clear_resource(
            resource_orm_accession_id,
        )
        return None, None

    async def release_resource(
        self,
        resource_orm_accession_id: uuid.UUID,
        final_status: ResourceStatusEnum,
        final_properties_json_update: dict[str, Any] | None = None,
        clear_from_accession_id: uuid.UUID | None = None,
        clear_from_position_name: str | None = None,
        status_details: str | None = "Released from run",
    ) -> None:
        """Release a resource instance."""
        resource_to_release = await self.resource_svc.get(
            self.db,
            resource_orm_accession_id,
        )
        if not resource_to_release:
            logger.warning(
                "AM_RELEASE_RESOURCE: Resource instance ID %s not found.",
                resource_orm_accession_id,
            )
            return
        logger.info(
            "AM_RELEASE_RESOURCE: Releasing '%s' (ID %s, Type %s), final status: %s.",
            resource_to_release.name,
            resource_orm_accession_id,
            resource_to_release.fqn,
            final_status.name,
        )

        resource_def_orm = await self.resource_type_definition_svc.get_by_name(
            self.db,
            name=resource_to_release.fqn,
        )
        is_releasing_a_deck_resource = self._is_deck_resource(resource_def_orm)

        (
            clear_from_accession_id,
            clear_from_position_name,
        ) = await self._handle_resource_release_location(
            is_releasing_a_deck_resource,
            resource_to_release,
            resource_orm_accession_id,
            clear_from_accession_id,
            clear_from_position_name,
        )

        final_loc_accession_id_for_ads: uuid.UUID | None = None
        final_pos_for_ads: str | None = None
        if (
            not is_releasing_a_deck_resource
            and final_status == ResourceStatusEnum.AVAILABLE_ON_DECK
        ):
            final_loc_accession_id_for_ads = clear_from_accession_id
            final_pos_for_ads = clear_from_position_name

        update_data = ResourceUpdate(
            status=final_status,
            machine_location_accession_id=final_loc_accession_id_for_ads,
            current_deck_position_name=final_pos_for_ads,
            current_protocol_run_accession_id=None,
            status_details=status_details,
        )
        if final_properties_json_update:
            update_data.properties_json = resource_to_release.properties_json or {}
            update_data.properties_json.update(final_properties_json_update)

        updated_resource = await self.resource_svc.update(
            db=self.db,
            db_obj=resource_to_release,
            obj_in=update_data,
        )
        if not updated_resource:
            msg = (
                f"Failed to update DB for resource ID {resource_orm_accession_id} on release."
            )
            raise AssetReleaseError(
                msg,
            )
        logger.info(
            "AM_RELEASE_RESOURCE: Resource '%s' released, status %s.",
            updated_resource.name,
            final_status.name,
        )
