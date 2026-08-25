"""Deck construction for the P2.2 verify harness.

Wraps DeckFactory.create_setup from
praxis/backend/core/simulation/chatterbox_runner.py (loaded standalone,
SQLAlchemy-free -- see verifier.py) with:

* a declarative, serializable DeckLayout (resources by name + seeded well
  volumes + optional parking holders for gripper/move examples),
* layout INFERENCE from a call sequence (tiny decks by default: one tip rack
  plus exactly the resources the calls reference),
* state snapshotting used by the post-condition checks.

DeckFactory always builds the Hamilton carrier deck (TIP_CAR at rails=1,
PLT_CAR at rails=9) and names resources after their param entries; this
module keeps that behavior and only EXTENDS the returned setup.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from pylabrobot.resources import ResourceHolder

__all__ = [
    "DeckLayout",
    "SetupHandle",
    "build_setup",
    "infer_layout",
    "load_chatterbox_runner",
]

#: Resource type vocabulary accepted in DeckLayout.resources. Values mirror
#: chatterbox_runner's _DECK_PLACEABLE_TYPES.
RESOURCE_TYPES = ("Plate", "TipRack", "Trough", "TubeRack", "Container")

#: Rails used for harness-added parking holders (plate carrier spans ~rails
#: 9-12; tip carrier 1-2; troughs go to rails=21; keep clear of those).
_PARK_RAILS = (5, 7, 13, 15, 17, 23)

_RUNNER_PATH = (
    Path(__file__).resolve().parents[2]
    / "praxis" / "backend" / "core" / "simulation" / "chatterbox_runner.py"
)


def load_chatterbox_runner():
    """Load chatterbox_runner.py standalone by file path.

    Deliberately NOT ``import praxis.backend.core.simulation``: that package's
    __init__ pulls method_contracts/pipeline/simulator and, transitively, the
    SQLAlchemy stack.  The runner module itself is SQLAlchemy-free (verified);
    loading it by path keeps the harness import-light and honors the
    never-modify-praxis/backend constraint (we only read it).
    """
    name = "_p22_chatterbox_runner"
    if name in sys.modules:
        return sys.modules[name]
    if not _RUNNER_PATH.is_file():
        raise ImportError(
            f"chatterbox runner not found at {_RUNNER_PATH} (repo layout change?)"
        )
    spec = importlib.util.spec_from_file_location(name, _RUNNER_PATH)
    if spec is None or spec.loader is None:  # pragma: no cover - packaging bug
        raise ImportError(f"cannot load {_RUNNER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # required before exec for dataclass resolution
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(name, None)  # don't cache a broken half-module
        raise
    return module


@dataclass
class DeckLayout:
    """Declarative tiny-deck description for one verification."""

    #: name -> resource kind ("Plate", "Trough", ...). "TipRack" aliases the
    #: factory-built default rack named "tip_rack".
    resources: dict[str, str] = field(default_factory=dict)
    #: "<name>.<well>" -> initial uL seeded via tracker.set_volume().
    seed_volumes: dict[str, float] = field(default_factory=dict)
    #: Extra empty ResourceHolders placed directly on the deck (move/plate
    #: parking destinations), addressable by bare name in refs.
    holders: list[str] = field(default_factory=list)

    def merged(self, other: "DeckLayout | None") -> "DeckLayout":
        if other is None:
            return self
        return DeckLayout(
            resources={**self.resources, **other.resources},
            seed_volumes={**self.seed_volumes, **other.seed_volumes},
            holders=[*self.holders, *other.holders],
        )


@dataclass
class SetupHandle:
    """Everything the dispatcher and checks need about one built deck."""

    machine: Any  # LiquidHandler
    deck: Any
    backend_name: str
    #: param/resource name -> PLR object (plates, tip_rack, holders, ...)
    resources: dict[str, Any] = field(default_factory=dict)
    runner_module: Any = None

    def mounted_tip_count(self) -> int:
        return sum(1 for t in self.machine.get_mounted_tips() if t is not None)

    def iter_tracked(self):
        """Yield every object carrying a VolumeTracker (wells, tip spots,
        containers) in stable deck order."""
        stack = [self.deck]
        while stack:
            node = stack.pop()
            tracker = getattr(node, "tracker", None)
            if tracker is not None and hasattr(tracker, "get_free_volume"):
                yield node
            stack.extend(getattr(node, "children", []))

    def well_index(self) -> dict[str, Any]:
        return {
            obj.name: obj
            for obj in self.iter_tracked()
            if getattr(obj, "name", None)
        }

    def snapshot(self) -> dict[str, Any]:
        """Full observable state: per-resource tracker state + topology +
        free-volume readings per tracked object (AC-2.2.2 measurement)."""
        return {
            "backend": self.backend_name,
            "mounted_tips": self.mounted_tip_count(),
            "resources": self.deck.serialize_all_state(),
            "topology": self.deck.serialize(),
            "free_volume": {
                obj.name: float(obj.tracker.get_free_volume())
                for obj in self.iter_tracked()
                if getattr(obj, "name", None)
            },
        }

    def free_volume(self, obj: Any) -> float:
        """Free volume of a well/container per AC-2.2.2 measurement rule."""
        return float(obj.tracker.get_free_volume())


def infer_layout(calls: Sequence[Mapping[str, Any]],
                 exclude: set[str] | None = None) -> DeckLayout:
    """Derive a minimal DeckLayout from a call sequence.

    Every referenced resource name gets a Plate unless its name suggests tips
    ("tip*" -> TipRack) or liquid supply ("*trough*" -> Trough).  Names in
    ``exclude`` (typically explicit-layout resources/holders) are skipped so
    an explicit DeckLayout fully owns them.
    """
    resources: dict[str, str] = {}
    skip = exclude or set()
    for call in calls:
        for value in (call or {}).get("params", {}).values():
            for name in _names_in(value):
                if name in skip:
                    continue
                if name in ("tip_rack",) or name.startswith("tip"):
                    resources.setdefault("tip_rack", "TipRack")
                elif name.endswith("trough"):
                    resources.setdefault(name, "Trough")
                else:
                    resources.setdefault(name, "Plate")
    return DeckLayout(resources=resources)


def _names_in(value: Any) -> list[str]:
    """Collect base resource names out of ref strings/lists/dicts."""
    names: list[str] = []
    if isinstance(value, str):
        names.append(_base_name(value))
    elif isinstance(value, Mapping):
        # structured Coordinate payload {"x":..} etc. carries no resource ref
        if set(("x", "y", "z")) & set(value.keys()):
            return []
        for v in value.values():
            names.extend(_names_in(v))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for v in value:
            names.extend(_names_in(v))
    return [n for n in names if n]


def _base_name(ref: str) -> str:
    head = ref.split(".", 1)[0]
    return head.split("[", 1)[0].strip()


def build_setup(
    backend_name: str,
    layout: DeckLayout,
) -> SetupHandle:
    """Build machine + deck via DeckFactory.create_setup, then extend.

    Extension covers what the shared factory deliberately does not know
    about: named parking holders and seeded starting volumes.
    """
    runner = load_chatterbox_runner()

    # TipRack entries alias the factory default; drop them from resource_needs
    # so create_setup does not double-place a rack.
    needs: dict[str, str] = {}
    has_tips = False
    for res_name, kind in layout.resources.items():
        if kind == "TipRack":
            has_tips = True
            continue
        needs[res_name] = kind
    if not has_tips:
        # Pipetting calls need SOME rack; factory always builds one anyway.
        has_tips = True

    setup = runner.DeckFactory().create_setup(backend_name, needs)

    handle = SetupHandle(
        machine=setup["machine"],
        deck=setup["deck"],
        backend_name=backend_name,
        runner_module=runner,
    )
    handle.resources["tip_rack"] = setup["tip_rack"]
    for res_name in needs:
        handle.resources[res_name] = setup[res_name]

    # Parking holders for move-verb destinations. Rails footprints depend on
    # what DeckFactory already placed, so walk candidates until one fits.
    deck = handle.deck
    candidates = [r for r in range(1, 28)]
    used_rail = 0
    for holder_name in layout.holders:
        holder = ResourceHolder(
            name=holder_name, size_x=127.76, size_y=85.48, size_z=14.5
        )
        placed = False
        last_err: Exception | None = None
        for rails in candidates[used_rail:]:
            try:
                deck.assign_child_resource(holder, rails=rails)
                used_rail = candidates.index(rails) + 1
                placed = True
                break
            except ValueError as e:  # location occupied -> next candidate
                last_err = e
        if not placed:
            raise RuntimeError(
                f"no free rails for parking holder {holder_name!r}: {last_err}"
            )
        handle.resources[holder_name] = holder

    # Seed volumes AFTER all assignment (trackers exist from construction).
    for ref, volume_ul in layout.seed_volumes.items():
        wells = ground_ref(ref, handle)
        for well in wells:
            well.tracker.set_volume(float(volume_ul))

    return handle


# Imported late to avoid a circular import (grounding needs SetupHandle-typed
# objects only duck-typed, but build_setup seeds volumes through grounding).
from verify.grounding import ground_ref  # noqa: E402
