"""Capability Matcher Service for protocol-machine compatibility checking.

This service matches protocol hardware requirements against machine capabilities
to determine if a machine can execute a specific protocol.
"""

from typing import Any

from praxis.backend.models.domain.machine import (
  Machine as Machine,
)
from praxis.backend.models.domain.machine import (
  MachineDefinition as MachineDefinition,
)
from praxis.backend.models.domain.protocol import (
  FunctionProtocolDefinition as FunctionProtocolDefinition,
)
from praxis.backend.utils.plr_static_analysis.models import (
  CapabilityMatchResult,
  CapabilityRequirement,
  ProtocolRequirements,
)


class CapabilityMatcherService:
  """Service for matching protocol requirements to machine capabilities.

  This service checks if a machine has the necessary hardware capabilities
  to execute a protocol by comparing the protocol's inferred requirements
  against the machine's discovered and user-configured capabilities.
  """

  def match_protocol_to_machine(
    self,
    protocol: FunctionProtocolDefinition,
    machine: Machine,
    machine_definition: MachineDefinition | None = None,
  ) -> CapabilityMatchResult:
    """Check if a machine satisfies protocol requirements.

    Args:
      protocol: The protocol definition to check requirements for.
      machine: The machine instance to check capabilities against.
      machine_definition: Optional machine definition for discovered capabilities.

    Returns:
      CapabilityMatchResult indicating compatibility.

    """
    # Extract protocol requirements
    requirements = self._parse_requirements(protocol.hardware_requirements_json)

    if not requirements.requirements:
      # No requirements = compatible with anything
      return CapabilityMatchResult(
        is_compatible=True,
        machine_id=str(machine.accession_id),
        protocol_id=str(protocol.accession_id),
        warnings=["No hardware requirements found for protocol."],
      )

    # Merge machine capabilities
    capabilities = self._merge_machine_capabilities(machine, machine_definition)

    # Check each requirement
    missing: list[CapabilityRequirement] = []
    matched: list[str] = []

    for req in requirements.requirements:
      if self._check_requirement(req, capabilities):
        matched.append(req.capability_name)
      else:
        missing.append(req)

    return CapabilityMatchResult(
      is_compatible=len(missing) == 0,
      missing_capabilities=missing,
      matched_capabilities=matched,
      machine_id=str(machine.accession_id),
      protocol_id=str(protocol.accession_id),
    )

  def find_compatible_machines(
    self,
    protocol: FunctionProtocolDefinition,
    machines: list[tuple[Machine, MachineDefinition | None]],
  ) -> list[tuple[Machine, CapabilityMatchResult]]:
    """Find all machines compatible with a protocol.

    Args:
      protocol: The protocol definition to check requirements for.
      machines: List of (machine, machine_definition) tuples to check.

    Returns:
      List of (machine, match_result) tuples for all checked machines.

    """
    results: list[tuple[Machine, CapabilityMatchResult]] = []

    for machine, definition in machines:
      result = self.match_protocol_to_machine(protocol, machine, definition)
      results.append((machine, result))

    return results

  def get_compatible_machines(
    self,
    protocol: FunctionProtocolDefinition,
    machines: list[tuple[Machine, MachineDefinition | None]],
  ) -> list[Machine]:
    """Get only the machines that are compatible with a protocol.

    Args:
      protocol: The protocol definition to check requirements for.
      machines: List of (machine, machine_definition) tuples to check.

    Returns:
      List of machines that satisfy all protocol requirements.

    """
    results = self.find_compatible_machines(protocol, machines)
    return [machine for machine, result in results if result.is_compatible]

  def _parse_requirements(self, requirements_json: dict[str, Any] | None) -> ProtocolRequirements:
    """Parse requirements JSON into ProtocolRequirements model.

    Args:
      requirements_json: Raw JSON from ORM field.

    Returns:
      ProtocolRequirements model instance.

    """
    if not requirements_json:
      return ProtocolRequirements()

    try:
      return ProtocolRequirements.model_validate(requirements_json)
    except Exception:
      return ProtocolRequirements()

  def _merge_machine_capabilities(
    self,
    machine: Machine,
    machine_definition: MachineDefinition | None = None,
  ) -> dict[str, Any]:
    """Merge discovered and user-configured capabilities.

    User-configured capabilities take precedence over discovered capabilities.

    Args:
      machine: The machine instance with user_configured_capabilities.
      machine_definition: Optional definition with discovered capabilities.

    Returns:
      Merged capabilities dictionary.

    """
    capabilities: dict[str, Any] = {}

    # Start with discovered capabilities from definition
    if machine_definition and machine_definition.capabilities:
      capabilities.update(machine_definition.capabilities)

    # Override with user-configured capabilities
    if machine.user_configured_capabilities:
      capabilities.update(machine.user_configured_capabilities)

    return capabilities

  def _check_requirement(
    self,
    requirement: CapabilityRequirement,
    capabilities: dict[str, Any],
  ) -> bool:
    """Check if a single requirement is satisfied by capabilities.

    Args:
      requirement: The requirement to check.
      capabilities: Machine capabilities dictionary.

    Returns:
      True if requirement is satisfied, False otherwise.

    """
    cap_name = requirement.capability_name
    expected = requirement.expected_value
    operator = requirement.operator

    # Check if capability exists
    if cap_name not in capabilities:
      return False

    actual = capabilities[cap_name]

    # Apply operator comparison
    if operator == "eq":
      return actual == expected
    if operator == "gt":
      return actual > expected
    if operator == "gte":
      return actual >= expected
    if operator == "lt":
      return actual < expected
    if operator == "lte":
      return actual <= expected
    if operator == "in":
      # Expected value should be in actual (actual is a collection)
      return expected in actual
    if operator == "contains":
      # Actual should contain expected
      return expected in actual

    # Default to equality
    return actual == expected


# Singleton instance for convenience
capability_matcher = CapabilityMatcherService()
