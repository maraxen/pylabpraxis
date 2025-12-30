# PLR Capability Update Prompt

Use this prompt when PyLabRobot adds new machine types or capabilities.

## When to Use This

- PyLabRobot releases a new version with additional machine types
- New backends are added for existing machine types
- New capability patterns need detection

## Step-by-Step Update Process

### 1. Identify New Machine Types

```bash
# Check what machine types PLR currently exports
cd /path/to/pylabrobot
grep -r "class.*Backend\|class.*Machine" --include="*.py" pylabrobot/
```

### 2. Update Class Discovery (`class_discovery.py`)

Add new base class sets:

```python
# In praxis/backend/utils/plr_static_analysis/visitors/class_discovery.py

# Add frontend base set
NEW_MACHINE_BASES: frozenset[str] = frozenset({
  "NewMachine",  # The base class name from PLR
})

# Add backend base set
NEW_MACHINE_BACKEND_BASES: frozenset[str] = frozenset({
  "NewMachineBackend",
})

# Add to combined sets
ALL_MACHINE_FRONTEND_BASES = (
  ...
  | NEW_MACHINE_BASES
)

ALL_MACHINE_BACKEND_BASES = (
  ...
  | NEW_MACHINE_BACKEND_BASES
)
```

Add classification checks in `_classify_class()`:

```python
if base_set_with_self & NEW_MACHINE_BACKEND_BASES:
  return PLRClassType.NEW_MACHINE_BACKEND

if base_set_with_self & NEW_MACHINE_BASES:
  return PLRClassType.NEW_MACHINE
```

### 3. Update PLRClassType Enum (`models.py`)

```python
# In praxis/backend/utils/plr_static_analysis/models.py

class PLRClassType(str, Enum):
  # Add frontend type
  NEW_MACHINE = "new_machine"
  # Add backend type
  NEW_MACHINE_BACKEND = "new_machine_backend"

# Update type sets at bottom of file
_frontend_types = frozenset({
  ...
  PLRClassType.NEW_MACHINE,
})

_backend_types = frozenset({
  ...
  PLRClassType.NEW_MACHINE_BACKEND,
})

_frontend_to_backend = {
  ...
  PLRClassType.NEW_MACHINE: PLRClassType.NEW_MACHINE_BACKEND,
}
```

### 4. Add Capability Schema (`models.py`)

```python
class NewMachineCapabilities(BaseModel):
  """Capabilities specific to the new machine type."""

  # Add fields based on what the machine supports
  some_capability: bool = False
  max_value: float | None = None

# Update union type
MachineCapabilities = (
  ...
  | NewMachineCapabilities
)
```

### 5. Update Capability Extractor (`capability_extractor.py`)

Add method detection patterns:

```python
def _detect_capabilities_from_method_name(self, func_name: str) -> None:
  # === NewMachine specific ===
  if "new_machine_method" in func_lower:
    self._signals["some_capability"] = True
```

Add capability builder case:

```python
def build_machine_capabilities(self) -> MachineCapabilities | None:
  if self.class_type in (PLRClassType.NEW_MACHINE, PLRClassType.NEW_MACHINE_BACKEND):
    return NewMachineCapabilities(
      some_capability=self._signals.get("some_capability", False),
      max_value=self._signals.get("max_value"),
    )
```

### 6. Add Tests

```python
# In tests/utils/test_plr_static_analysis.py

def test_new_machine_capabilities(self):
  """Test NewMachineCapabilities model."""
  from praxis.backend.utils.plr_static_analysis.models import NewMachineCapabilities

  caps = NewMachineCapabilities(some_capability=True)
  assert caps.some_capability is True
```

### 7. Run Verification

```bash
# Run static analysis tests
uv run pytest tests/utils/test_plr_static_analysis.py -v --no-cov

# Type check the module
uv run pyright praxis/backend/utils/plr_static_analysis/

# Verify discovery finds new types
uv run python -c "
from praxis.backend.utils.plr_static_analysis import PLRSourceParser, find_plr_source_root
parser = PLRSourceParser(find_plr_source_root())
machines = parser.discover_machine_classes()
new_machines = [m for m in machines if 'new_machine' in m.class_type.value]
print(f'Found {len(new_machines)} new machine classes')
for m in new_machines[:5]:
  print(f'  - {m.name}: {m.class_type}')
"
```

## Key Files

| File | Purpose |
|------|---------|
| `models.py` | `PLRClassType` enum, capability Pydantic schemas |
| `class_discovery.py` | Base class sets, classification logic |
| `capability_extractor.py` | Signal detection, capability building |
| `parser.py` | Orchestrates discovery and extraction |
| `test_plr_static_analysis.py` | Unit tests |

## Tips

- **Classification order matters**: Check backends before frontends, and machine types before resources
- **Use `base_set_with_self`**: Include the class name itself when classifying base classes
- **Capability signals**: Look for method names, attribute names, and `__init__` parameters
- **Test with real PLR**: Always verify against actual PyLabRobot source
