"""Machine type -> (module_path, symbol_name) mapping for supported PLR
machine types.

Extracted from ``web_bridge.py`` (was inline at :407-414, resolved at
:435) per ADR ``.praxia/docs/decisions/260817_repl-layout-and-delivery-mechanism.md``
Sec 4.3. This is an extraction, not a rewrite: every entry is carried over
verbatim except the ``"Incubator"`` row, corrected below.

THE INCUBATOR FIX: upstream renamed ``pylabrobot.incubator`` to
``pylabrobot.storage`` -- ``pylabrobot/incubator`` does not exist at the
pinned submodule sha (``d9651e2098cd269fc47e6aff80c9242a82d1b587``), and
``Incubator`` lives in ``pylabrobot/storage/incubator.py``. Verified the
target resolves before writing it: ``pylabrobot.storage``'s own
``__init__.py`` re-exports it at package level (``from .incubator import
Incubator``), so the package path below -- not the deeper submodule path --
is correct, matching every other entry in this map (all six are package-
level paths, not submodule paths).
"""

_MACHINE_CLASS_MAP = {
  "LiquidHandler": ("pylabrobot.liquid_handling", "LiquidHandler"),
  "PlateReader": ("pylabrobot.plate_reading", "PlateReader"),
  "HeaterShaker": ("pylabrobot.heating_shaking", "HeaterShaker"),
  "Shaker": ("pylabrobot.shaking", "Shaker"),
  "Centrifuge": ("pylabrobot.centrifuge", "Centrifuge"),
  "Incubator": ("pylabrobot.storage", "Incubator"),
}
