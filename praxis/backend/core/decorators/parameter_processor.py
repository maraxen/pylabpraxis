import inspect
from typing import Any, Union, get_args, get_origin

from praxis.backend.models.pydantic_internals.protocol import (
    AssetRequirementModel,
    ParameterMetadataModel,
    UIHint,
)
from praxis.backend.utils.type_inspection import (
    fqn_from_hint,
    is_pylabrobot_resource,
    serialize_type_hint,
)
from praxis.backend.utils.uuid import uuid7

from .models import CreateProtocolDefinitionData


def _process_parameter(
    param_name_sig: str,
    param_obj: inspect.Parameter,
    data: CreateProtocolDefinitionData,
    parameters_list: list[ParameterMetadataModel],
    assets_list: list[AssetRequirementModel],
    *,
    found_deck_param: bool,
    found_state_param_details: dict[str, Any] | None,
) -> tuple[list[ParameterMetadataModel], list[AssetRequirementModel], bool, dict[str, Any] | None]:
    param_type_hint = param_obj.annotation
    is_optional_param = (
        get_origin(param_type_hint) is Union and type(None) in get_args(param_type_hint)
    ) or (param_obj.default is not inspect.Parameter.empty)
    fqn = fqn_from_hint(param_type_hint)
    param_meta_entry = data.param_metadata.get(param_name_sig, {})
    p_description = param_meta_entry.get("description")
    p_constraints = param_meta_entry.get("constraints", {})
    p_ui_hints_dict = param_meta_entry.get("ui_hints")
    p_ui_hints = UIHint(**p_ui_hints_dict) if isinstance(p_ui_hints_dict, dict) else None

    type_for_plr_check = param_type_hint
    origin_check = get_origin(param_type_hint)
    args_check = get_args(param_type_hint)
    if origin_check is Union and type(None) in args_check:
        non_none_args = [arg for arg in args_check if arg is not type(None)]
        if len(non_none_args) == 1:
            type_for_plr_check = non_none_args[0]

    if is_pylabrobot_resource(type_for_plr_check):
        asset_args = {
            "accession_id": uuid7(),
            "name": param_name_sig,
            "type_hint_str": serialize_type_hint(param_type_hint),
            "actual_type_str": serialize_type_hint(type_for_plr_check),
            "fqn": fqn,
            "optional": is_optional_param,
            "default_value_repr": repr(param_obj.default)
            if param_obj.default is not inspect.Parameter.empty
            else None,
            "description": p_description,
            "constraints_json": p_constraints if isinstance(p_constraints, dict) else {},
            "ui_hints": p_ui_hints,
        }
        assets_list.append(AssetRequirementModel(**asset_args))
    else:
        param_args = {
            "name": param_name_sig,
            "type_hint": serialize_type_hint(param_type_hint),
            "fqn": fqn,
            "optional": is_optional_param,
            "default_value_repr": repr(param_obj.default)
            if param_obj.default is not inspect.Parameter.empty
            else None,
            "description": p_description,
            "constraints": p_constraints if isinstance(p_constraints, dict) else {},
            "ui_hint": p_ui_hints,
        }
        if data.preconfigure_deck and param_name_sig == data.deck_param_name:
            param_args["is_deck_param"] = True
            found_deck_param = True
        elif param_name_sig == data.state_param_name:
            is_state_type_match = fqn in {
                "PraxisState",
                "praxis.backend.core.definitions.PraxisState",
            }
            is_dict_type_match = fqn == "dict"
            found_state_param_details = {
                "name": param_name_sig,
                "expects_praxis_state": is_state_type_match,
                "expects_dict": is_dict_type_match,
            }
        parameters_list.append(ParameterMetadataModel(**param_args))

    return parameters_list, assets_list, found_deck_param, found_state_param_details
