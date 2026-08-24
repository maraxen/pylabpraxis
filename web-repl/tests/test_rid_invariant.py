"""R-ID negative test (ADR Sec 2.2, ``260817_repl-layout-and-delivery-mechanism.md``):
the single-class-object invariant that ``web-repl/bootstrap/stages.py`` implements
(``apply()``, ``assert_identity()``, ``import_shim_class()``, ``install_native_stubs()``)
must be *observed* failing, not just observed passing.

RV1 flagged the gap this file closes: those functions existed with no test at all,
which is exactly the state the historical bug shipped in -- a fail-closed check nobody
had ever seen fail is not known to be closed. Four things are proven here, matching the
task brief's four numbered requirements:

1. **Positive path** -- after ``apply()``, all four of
   ``pylabrobot.io.{serial.Serial, usb.USB, hid.HID, ftdi.FTDI}`` are the SAME OBJECTS
   (``is``, never by name) as their ``builtins.Web*`` counterparts.
2. **Negative path** -- a synthetic double-``exec`` scenario (two distinct class objects
   sharing ``__name__ == "WebSerial"``) is fed to ``assert_identity()`` directly, and its
   ``PraxisDriftError`` is observed firing. This is the test that matters most: per
   ``apply()``'s own docstring, ``apply()`` does ``setattr`` immediately before its
   identity check, so calling ``apply()`` alone can only ever pass trivially -- the real
   negative case requires ``assert_identity()`` in isolation, against a pair it did not
   just construct itself.
3. **The seven native stubs** install as real ``types.ModuleType`` objects, register in
   ``sys.modules``, and wire correctly (``serial.tools.list_ports`` reachable through the
   ``serial`` module attribute chain, not just via a ``sys.modules`` dict lookup) -- and
   ``import serial`` after installation is provably NOT a ``unittest.mock`` object, which
   is exactly what a downstream check inspects.
4. **The capability-flag consequence**, exercised against the REAL PyLabRobot import path
   in this repo's pinned ``external/pylabrobot`` submodule, in CPython, not faked. PLR's
   four flags (``pylabrobot.io.serial.HAS_SERIAL``, ``pylabrobot.io.usb.USE_USB``,
   ``pylabrobot.io.hid.USE_HID``, ``pylabrobot.io.ftdi.HAS_PYLIBFTDI`` -- plus
   ``pylabrobot.io.ftdi.HAS_PYUSB``, a second, independent ``try: import usb.core`` in the
   same file) are module-scope ``try: import X / except ImportError: HAS_X = False``
   booleans evaluated ONCE at import time. What ``install_native_stubs()`` covers
   (``NATIVE_STUB_MODULES``: ``ssl``, ``usb``, ``usb.core``, ``usb.util``, ``serial``,
   ``serial.tools``, ``serial.tools.list_ports``) is PROVEN here to flip ``HAS_SERIAL``
   and ``HAS_PYUSB`` True. What it deliberately does NOT cover -- ``libusb_package``
   (needed by ``pylabrobot.io.usb``'s ``USE_USB``) and ``hid`` (``USE_HID``) -- is PROVEN
   here to stay False, and is called out explicitly rather than silently glossed over:
   both flags are read only inside the ORIGINAL ``pylabrobot.io.usb.USB`` /
   ``pylabrobot.io.hid.HID`` classes' own ``setup()`` methods, which ``apply()`` replaces
   wholesale with ``WebUSB``/``WebHID`` -- so the flags gate no code path the browser REPL
   reaches, and stubbing two more native modules just to flip two dead flags True would be
   pure overclaim-chasing. ``pylibftdi``/``HAS_PYLIBFTDI`` is a THIRD, DIFFERENT case, not
   grouped with the other two here: it is proven False in THIS file's in-repo-bootstrap-dir
   subprocess (the ``pylibftdi`` stub package's source is not on this test's ``sys.path`` at
   all) but proven True, by genuine import with no forcing, against the real built
   ``pylibftdi`` stub wheel in ``test_has_pylibftdi_is_true_with_real_pylibftdi_stub_on_path``
   below -- ``apply()`` no longer forces ``HAS_PYLIBFTDI = True`` (F-STAGES, 260818: a forced
   flag over what was, before the stub fix, a genuinely failed import is exactly the
   pathology ADR 260817 exists to abolish).

Isolation strategy (ADR Sec 2.4 constraint): this file NEVER appends
``web-repl/overlay/assets/python`` to ``sys.path`` -- that subtree's ``praxis/`` package
shadows the repo's real top-level ``praxis`` package. Requirements 1, 3, and 4 all mutate
process-global state (``sys.modules``, ``builtins.Web*``) that ``stages.py``'s own
functions are specified to mutate, and requirement 4 specifically needs a *fresh*
interpreter per scenario (PLR's flags are evaluated once, at first import, and this venv
happens to have a real ``pyserial`` installed as an unrelated dependency -- see
``test_capability_flags_are_all_false_without_native_stubs`` for why that matters and how
it is neutralized). Both are handled by running each such scenario in its own ``subprocess``
with an explicit ``PYTHONPATH`` (bootstrap dir, plus a ``tmp_path`` COPY of
``overlay/assets/shims`` -- never the live tree, never ``overlay/assets/python``), per the
task brief's sanctioned alternative to a fixture-copied import. Requirement 2 (the
negative path) needs no such isolation: ``assert_identity()`` is a pure read-only
function with no side effects on ``sys.modules`` or ``builtins``.

A companion guard test, ``test_praxis_namespace_not_shadowed_by_overlay``, asserts that
importing ``praxis`` from THIS process resolves to the repo's real top-level package (or
is absent), never to the ``web-repl`` overlay copy -- cheap insurance for every later test
author in this directory, per ADR Sec 2.4's explicit request.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import textwrap
import types
from pathlib import Path

import pytest

_WEB_REPL_DIR = Path(__file__).resolve().parents[1]
_BOOTSTRAP_DIR = _WEB_REPL_DIR / "bootstrap"
_SHIMS_DIR = _WEB_REPL_DIR / "overlay" / "assets" / "shims"
_OVERLAY_PYTHON_DIR = _WEB_REPL_DIR / "overlay" / "assets" / "python"  # NEVER on sys.path here
_PYLIBFTDI_STUB_DIR = _WEB_REPL_DIR / "scripts" / "pylibftdi_stub"  # contains pylibftdi/

if str(_BOOTSTRAP_DIR) not in sys.path:
    sys.path.insert(0, str(_BOOTSTRAP_DIR))

import stages  # noqa: E402 -- path setup must precede this import


# ---------------------------------------------------------------------------
# Requirement 2: the negative path. Pure, no subprocess needed.
# ---------------------------------------------------------------------------


def test_assert_identity_passes_when_object_matches_itself() -> None:
    """Sanity companion to the negative test below: the trivially-true case
    (comparing an object against itself) must NOT raise. Without this, a
    vacuously-broken ``assert_identity`` that always raises would make the
    negative test below pass for the wrong reason.
    """
    cls = type("WebSerial", (), {})
    module = types.ModuleType("fake_pylabrobot_io_serial")
    module.Serial = cls
    stages.assert_identity(module, "Serial", cls, "WebSerial")  # must not raise


def test_assert_identity_fails_on_reintroduced_double_exec() -> None:
    """THE negative test ADR Sec 2.2 mandates: re-introducing the double-``exec``
    must be *observed* failing this stage.

    Reproduces the historical bug's exact shape (ADR Sec 2.2 point 1): the same
    source text ``exec``'d into two separate throwaway namespaces produces two
    distinct class objects that share ``__name__`` and even compare equal by
    source/repr, but are NOT the same object. ``class_a`` stands in for what
    ``pylabrobot.io.serial.Serial`` was patched to by an earlier boot stage;
    ``class_b`` stands in for what ``builtins.WebSerial`` was later REBOUND to by
    the now-deleted ``web_bridge.bootstrap_playground()`` shim re-injection.
    """
    source = "class WebSerial:\n    pass\n"

    ns_a: dict[str, object] = {}
    exec(source, ns_a)  # noqa: S102 -- deliberately reproducing the historical bug's mechanism
    class_a = ns_a["WebSerial"]

    ns_b: dict[str, object] = {}
    exec(source, ns_b)  # noqa: S102 -- second, independent exec -> a second, distinct class object
    class_b = ns_b["WebSerial"]

    # Precondition: this really is the double-exec bug shape, not a trivial mismatch.
    assert class_a is not class_b
    assert class_a.__name__ == class_b.__name__ == "WebSerial"

    module = types.ModuleType("fake_pylabrobot_io_serial")
    module.Serial = class_a  # what an earlier stage patched pylabrobot.io.serial.Serial to

    with pytest.raises(stages.PraxisDriftError) as exc_info:
        # builtins.WebSerial is now class_b (the rebind) -- assert_identity must
        # catch that module.Serial (class_a) is NOT builtins.WebSerial (class_b).
        stages.assert_identity(module, "Serial", class_b, "WebSerial")

    message = str(exc_info.value)
    assert "single-class-object invariant" in message
    assert "fake_pylabrobot_io_serial.Serial" in message
    assert "WebSerial" in message


def test_apply_raises_when_a_builtin_shim_is_missing() -> None:
    """``apply()``'s own fail-closed precondition check: it must name the
    missing shim rather than silently skipping a target. This is the
    "silent partial patch" shape the whole redesign exists to close.
    """
    import builtins

    # Ensure none of the four are staged (defensive -- they should not be,
    # since nothing in this test module staples them onto builtins).
    for name in ("WebSerial", "WebUSB", "WebHID", "WebFTDI"):
        assert not hasattr(builtins, name), (
            f"builtins.{name} unexpectedly already set -- a prior test in this "
            "process leaked global state onto builtins"
        )

    with pytest.raises(stages.PraxisDriftError, match="WebSerial"):
        stages.apply()


# ---------------------------------------------------------------------------
# Requirements 1, 3, 4: subprocess-isolated, real-PLR-import-path scenarios.
# ---------------------------------------------------------------------------

_BASELINE_NO_STUBS_SCRIPT = textwrap.dedent(
    """
    # Simulates the browser's true starting condition -- NONE of serial, usb,
    # usb.core, usb.util, hid, libusb_package, pylibftdi exist -- even though
    # this dev venv happens to have a REAL pyserial installed as an unrelated
    # dependency of something else in the repo. `sys.modules[name] = None` is
    # the documented CPython mechanism for forcing `import name` to raise
    # ImportError, and is the only way to make this baseline reproducible
    # regardless of what happens to be installed locally.
    import sys
    for _blocked in ("serial", "usb", "hid", "libusb_package", "pylibftdi"):
        sys.modules[_blocked] = None

    import pylabrobot.io.serial as plr_serial
    import pylabrobot.io.usb as plr_usb
    import pylabrobot.io.hid as plr_hid
    import pylabrobot.io.ftdi as plr_ftdi

    flags = {
        "HAS_SERIAL": plr_serial.HAS_SERIAL,
        "USE_USB": plr_usb.USE_USB,
        "USE_HID": plr_hid.USE_HID,
        "HAS_PYLIBFTDI": plr_ftdi.HAS_PYLIBFTDI,
        "HAS_PYUSB": plr_ftdi.HAS_PYUSB,
    }
    assert flags == {
        "HAS_SERIAL": False,
        "USE_USB": False,
        "USE_HID": False,
        "HAS_PYLIBFTDI": False,
        "HAS_PYUSB": False,
    }, f"baseline (no stubs) flags were not all False: {flags!r}"
    print("BASELINE_OK", flags)
    """
)


def test_capability_flags_are_all_false_without_native_stubs() -> None:
    """Baseline half of requirement 4: reproduces, against the real PLR import
    path in this repo's pinned submodule, the premise ``install_native_stubs()``
    exists to fix -- with nothing stubbed, all five PLR capability booleans
    that gate WebSerial/WebUSB/WebHID/WebFTDI usability are False.
    """
    result = subprocess.run(
        [sys.executable, "-c", _BASELINE_NO_STUBS_SCRIPT],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, (
        f"baseline (no-stubs) subprocess failed:\nstdout={result.stdout}\nstderr={result.stderr}"
    )
    assert "BASELINE_OK" in result.stdout


_WITH_STUBS_SCRIPT = textwrap.dedent(
    """
    import sys
    sys.path.insert(0, {bootstrap_dir!r})
    sys.path.insert(0, {shims_copy_dir!r})

    import stages

    # Real callers (the JupyterLite kernel) always have asyncio imported long
    # before boot stages run. Import it here too, BEFORE stubbing ssl: CPython
    # 3.14's asyncio.base_events imports asyncio.sslproto unconditionally,
    # which reads real attributes off the `ssl` module -- if ssl is stubbed
    # first, any *later*, first-time `import asyncio` (e.g. transitively, from
    # `web_serial_shim.py`'s own `import asyncio`) breaks on a bare stub ssl
    # module. That is a precondition of install_native_stubs(), not something
    # this test exists to fix.
    import asyncio  # noqa: F401

    # install_native_stubs() MUST run before any `import pylabrobot` --
    # PLR's flags are evaluated once, at first import, and never re-checked.
    freshly_installed = stages.install_native_stubs()
    # ssl's freshly-installed value is environment-dependent (True if this bare
    # `-c` interpreter had not yet imported stdlib ssl by the time this ran,
    # False if it had) -- install_native_stubs()'s own idempotence guard (`if
    # mod_name not in sys.modules`) is what matters, not which branch fired
    # here, so only the other six (never real, in this venv -- see the
    # module-level docstring) are asserted freshly installed.
    for name in ("usb", "usb.core", "usb.util", "serial", "serial.tools", "serial.tools.list_ports"):
        assert freshly_installed[name] is True, f"{{name}} was not freshly installed: {{freshly_installed!r}}"

    # --- Requirement 3: real ModuleType, sys.modules-registered, correctly wired ---
    import types
    for name in stages.NATIVE_STUB_MODULES:
        mod = sys.modules[name]
        assert type(mod) is types.ModuleType, f"{{name}} is not a real ModuleType: {{type(mod)!r}}"

    assert sys.modules["usb"].core is sys.modules["usb.core"]
    assert sys.modules["usb"].util is sys.modules["usb.util"]
    assert sys.modules["serial"].tools is sys.modules["serial.tools"]
    assert sys.modules["serial"].tools.list_ports is sys.modules["serial.tools.list_ports"]
    # Reachable through the attribute chain starting from a plain `import serial`,
    # not merely via a sys.modules dict lookup -- this is the shape a downstream
    # caller (e.g. `import serial.tools.list_ports; serial.tools.list_ports.comports()`)
    # actually uses.
    import serial as serial_via_plain_import
    assert serial_via_plain_import.tools.list_ports.comports() == []
    assert "unittest.mock" not in type(sys.modules["serial"]).__module__, (
        "serial stub is (or wraps) a MagicMock -- this is directly checked downstream "
        "and load-bearing per install_native_stubs()'s own docstring"
    )
    assert sys.modules["serial"].__class__.__name__ == "module", (
        f"serial stub's class is {{sys.modules['serial'].__class__.__name__!r}}, not "
        "the real 'module' type -- MagicMock's class name would be 'MagicMock', not this"
    )

    # --- Requirement 1: import the four REAL shim classes exactly once each ---
    builtins.WebSerial = stages.import_shim_class("web_serial_shim", "WebSerial")
    builtins.WebUSB = stages.import_shim_class("web_usb_shim", "WebUSB")
    builtins.WebHID = stages.import_shim_class("web_hid_shim", "WebHID")
    builtins.WebFTDI = stages.import_shim_class("web_ftdi_shim", "WebFTDI")

    # A second import_shim_class call for the same module must hit the
    # sys.modules cache and hand back the IDENTICAL object -- this is R-ID's
    # entire mechanism (no `exec`, ever).
    again = stages.import_shim_class("web_serial_shim", "WebSerial")
    assert again is builtins.WebSerial, "import_shim_class is not idempotent by identity"

    results = stages.apply()
    assert all(results.values()), f"apply() reported a non-True result: {{results!r}}"

    import pylabrobot.io.serial as plr_serial
    import pylabrobot.io.usb as plr_usb
    import pylabrobot.io.hid as plr_hid
    import pylabrobot.io.ftdi as plr_ftdi

    assert plr_serial.Serial is builtins.WebSerial
    assert plr_usb.USB is builtins.WebUSB
    assert plr_hid.HID is builtins.WebHID
    assert plr_ftdi.FTDI is builtins.WebFTDI
    # HAS_PYLIBFTDI is NOT apply()'s side effect (F-STAGES, 260818 -- the old
    # forced `ftdi_mod.HAS_PYLIBFTDI = True` was deleted). It reflects PLR's
    # own real `try: import pylibftdi.driver` at pylabrobot.io.ftdi import
    # time; the pylibftdi stub package's source is not on THIS subprocess's
    # sys.path, so it is genuinely False here -- proven True elsewhere, by
    # real import, in test_has_pylibftdi_is_true_with_real_pylibftdi_stub_on_path.
    assert plr_ftdi.HAS_PYLIBFTDI is False, (
        f"HAS_PYLIBFTDI was True with no pylibftdi on sys.path -- something "
        f"is forcing it again: {{plr_ftdi.HAS_PYLIBFTDI!r}}"
    )

    # --- Requirement 4: the capability-flag consequence, WITH stubs installed ---
    flags = {{
        "HAS_SERIAL": plr_serial.HAS_SERIAL,
        "USE_USB": plr_usb.USE_USB,
        "USE_HID": plr_hid.USE_HID,
        "HAS_PYLIBFTDI": plr_ftdi.HAS_PYLIBFTDI,
        "HAS_PYUSB": plr_ftdi.HAS_PYUSB,
    }}
    assert flags["HAS_SERIAL"] is True, f"HAS_SERIAL did not flip True: {{flags!r}}"
    assert flags["HAS_PYUSB"] is True, f"HAS_PYUSB did not flip True: {{flags!r}}"
    # NOT covered by NATIVE_STUB_MODULES (libusb_package, hid are not stubbed,
    # deliberately -- they gate no code path apply()'s WebUSB/WebHID
    # replacement reaches) -- stays False here. Documented, not silently
    # glossed over.
    assert flags["USE_USB"] is False, f"USE_USB unexpectedly True: {{flags!r}}"
    assert flags["USE_HID"] is False, f"USE_HID unexpectedly True: {{flags!r}}"
    assert flags["HAS_PYLIBFTDI"] is False, f"HAS_PYLIBFTDI unexpectedly True: {{flags!r}}"

    # --- F-STAGES: verify_identity() positive path -- non-vacuous re-check ---
    # after apply(), with no corruption yet: must succeed.
    verify_results = stages.verify_identity()
    assert all(verify_results.values()), (
        f"verify_identity() reported a non-True result on the clean post-apply() "
        f"state: {{verify_results!r}}"
    )

    # --- F-STAGES: verify_identity() negative path -- THE proof it is not
    # vacuous in its real call position. Reproduces the historical bug shape
    # directly: something (e.g. the now-deleted web_bridge.bootstrap_playground()
    # shim re-injection) rebinds builtins.WebSerial to a SECOND, distinct class
    # object AFTER apply() already patched pylabrobot.io.serial.Serial with the
    # FIRST. apply()'s own post-write assert cannot see this -- it already ran,
    # before this rebind happened. verify_identity(), called again later (as
    # praxis_bootstrap.py now does, immediately before praxis:ready), must.
    _original_web_serial = builtins.WebSerial
    _rebound_web_serial = type("WebSerial", (), {{}})
    assert _rebound_web_serial is not _original_web_serial
    builtins.WebSerial = _rebound_web_serial
    try:
        stages.verify_identity()
    except stages.PraxisDriftError as exc:
        print("VERIFY_IDENTITY_CAUGHT_DRIFT", str(exc))
    else:
        raise AssertionError(
            "verify_identity() did NOT raise after builtins.WebSerial was "
            "rebound to a second, distinct class object -- the check is "
            "vacuous in its real call position"
        )
    finally:
        builtins.WebSerial = _original_web_serial

    print("WITH_STUBS_OK", flags)
    """
)


@pytest.fixture
def _shims_copy(tmp_path: Path) -> Path:
    """Copy ``overlay/assets/shims`` to ``tmp_path`` so the subprocess imports
    from a scratch copy, never the live ``overlay/`` tree, and (per ADR Sec 2.4)
    never anywhere near ``overlay/assets/python``.
    """
    dest = tmp_path / "shims_copy"
    shutil.copytree(_SHIMS_DIR, dest)
    return dest


def test_apply_produces_true_identity_with_real_shims_and_native_stubs(_shims_copy: Path) -> None:
    """Requirements 1, 3, and 4 together, against the real PLR import path in
    this repo's pinned ``external/pylabrobot`` submodule, in a fresh
    interpreter with an explicit PYTHONPATH (bootstrap dir + a tmp_path COPY
    of the shims -- never ``overlay/assets/python``, per ADR Sec 2.4).

    Also (F-STAGES, 260818) proves ``verify_identity()`` is non-vacuous: after
    a clean ``apply()`` it must pass, and after ``builtins.WebSerial`` gets
    rebound to a second, distinct class object (the historical bug shape) it
    must raise -- unlike ``apply()``'s own post-write assert, which cannot see
    a rebind that happens after it already ran.
    """
    script = "import builtins\n" + _WITH_STUBS_SCRIPT.format(
        bootstrap_dir=str(_BOOTSTRAP_DIR),
        shims_copy_dir=str(_shims_copy),
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, (
        f"with-stubs subprocess failed:\nstdout={result.stdout}\nstderr={result.stderr}"
    )
    assert "WITH_STUBS_OK" in result.stdout
    assert "VERIFY_IDENTITY_CAUGHT_DRIFT" in result.stdout, (
        f"verify_identity() did not report catching the simulated rebind -- "
        f"stdout={result.stdout}"
    )


_HAS_PYLIBFTDI_SCRIPT = textwrap.dedent(
    """
    import sys
    sys.path.insert(0, {pylibftdi_stub_dir!r})

    # No install_native_stubs() call needed here -- HAS_PYLIBFTDI does not
    # depend on any of the seven NATIVE_STUB_MODULES names, only on
    # `pylibftdi` itself being importable (see stages.install_native_stubs's
    # docstring, F-STAGES 260818).
    import pylabrobot.io.ftdi as plr_ftdi

    assert plr_ftdi.HAS_PYLIBFTDI is True, (
        "HAS_PYLIBFTDI is False with the real pylibftdi stub package on "
        "sys.path -- either the stub regressed or something about the "
        "import chain broke: _FTDI_ERROR={{}}".format(getattr(plr_ftdi, "_FTDI_ERROR", None))
    )
    print("HAS_PYLIBFTDI_TRUE_OK")
    """
)


def test_has_pylibftdi_is_true_with_real_pylibftdi_stub_on_path() -> None:
    """F-STAGES (260818): durable regression test for the ``apply()`` FIX 2
    finding -- ``stages.py`` used to force
    ``pylabrobot.io.ftdi.HAS_PYLIBFTDI = True`` unconditionally, papering over
    a genuinely-failed ``import pylibftdi.driver`` before the stub package was
    fixed to actually provide a ``driver`` submodule. Now that the forced
    assignment is deleted, this proves the flag comes out True on its own
    merits: with ONLY the real ``pylibftdi`` stub package
    (``web-repl/scripts/pylibftdi_stub/``, the same source the wheel-building
    pipeline packages into ``pylibftdi-0.0.0-py3-none-any.whl``) on
    ``sys.path`` -- no ``install_native_stubs()``, no forcing -- PLR's own
    ``try: import pylibftdi.driver; from pylibftdi import Device, FtdiError``
    at ``pylabrobot.io.ftdi`` import time succeeds and sets ``HAS_PYLIBFTDI =
    True`` genuinely. Isolated in a subprocess (fresh interpreter) because
    PLR's flags are evaluated once, at first import, same reason every other
    capability-flag scenario in this file uses ``subprocess``.
    """
    result = subprocess.run(
        [sys.executable, "-c", _HAS_PYLIBFTDI_SCRIPT.format(pylibftdi_stub_dir=str(_PYLIBFTDI_STUB_DIR))],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(_WEB_REPL_DIR),  # never a scratch dir that could shadow `pylibftdi`
    )
    assert result.returncode == 0, (
        f"HAS_PYLIBFTDI-with-real-stub subprocess failed:\nstdout={result.stdout}\nstderr={result.stderr}"
    )
    assert "HAS_PYLIBFTDI_TRUE_OK" in result.stdout


# ---------------------------------------------------------------------------
# ADR Sec 2.4 guard: `web-repl/tests/` must never resolve `praxis` to the
# overlay shadow copy. Cheap, and protects every later test author here.
# ---------------------------------------------------------------------------


def test_praxis_namespace_not_shadowed_by_overlay() -> None:
    """FAILS if ``praxis.__file__`` (or any ``praxis.__path__`` entry)
    resolves under ``web-repl/`` -- i.e. if this process's ``sys.path`` has
    been polluted with ``overlay/assets/python``, which shadows the repo's
    real top-level ``praxis`` package (ADR Sec 2.4).

    This module never appends that directory to ``sys.path`` -- if this test
    fails, some OTHER test collected in the same run did.
    """
    overlay_python_dir = str(_OVERLAY_PYTHON_DIR.resolve())
    assert overlay_python_dir not in sys.path, (
        "web-repl/overlay/assets/python is on sys.path in this test process -- "
        "this is exactly what ADR Sec 2.4 forbids; it shadows the repo's real "
        "top-level `praxis` package"
    )

    import praxis  # the repo's real top-level package (or absent) -- never the overlay shadow

    resolved_file = getattr(praxis, "__file__", None)
    if resolved_file is not None:
        assert "web-repl" not in str(Path(resolved_file).resolve()), (
            f"praxis.__file__ ({resolved_file!r}) resolves under web-repl/ -- "
            "sys.path was polluted with the overlay shadow copy"
        )

    for entry in getattr(praxis, "__path__", []):
        # Only real directories can shadow a package. An editable install puts a
        # NON-PATH marker on __path__ -- setuptools' finder hook, e.g.
        # '__editable__.praxis-0.0.1.finder.__path_hook__' -- and feeding that to
        # Path.resolve() anchors it to the CURRENT WORKING DIRECTORY. These tests run
        # from web-repl/, so the marker resolved to
        # <repo>/web-repl/__editable__.praxis-0.0.1.finder.__path_hook__ and tripped
        # the "web-repl" substring check, reporting overlay shadowing that was not
        # happening (the real entry, <repo>/praxis, was correct all along). Skipping
        # non-directories loses no coverage: something that is not a directory cannot
        # shadow anything.
        if not Path(entry).is_dir():
            continue
        assert "web-repl" not in str(Path(entry).resolve()), (
            f"praxis.__path__ entry ({entry!r}) resolves under web-repl/ -- "
            "sys.path was polluted with the overlay shadow copy"
        )
