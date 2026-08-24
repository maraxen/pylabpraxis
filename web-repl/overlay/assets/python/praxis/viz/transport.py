"""Transport layer for the browser visualizer (P6.4, Phase 6 slice 2).

This module deliberately does **not** ``import js``. Per ADR
``.praxia/docs/decisions/260817_repl-layout-and-delivery-mechanism.md`` Sec 2.1 --
the same rule ``web-repl/bootstrap/transport.py`` follows -- the browser object is
*injected* as a plain callable. That is what makes the ordered-event assertions in
``web-repl/tests/test_browser_visualizer.py`` runnable under CPython with no
Pyodide, no Chromium, and no kernel.

Channel separation: visualizer traffic rides ``praxis_viz``, NOT ``praxis_repl``.
``praxis_repl`` carries the device-authorization request/response protocol
(``web_bridge.request_user_interaction``); mixing a high-volume state-update
stream into it would put deck repaints and device grants on one channel. Spike S-D
established the split and it is preserved here.

Note BroadcastChannel is **origin-scoped** (S-D finding): the visualizer page and
the kernel must be served from the same origin or messages are silently dropped --
no error, no delivery. ``web-repl``'s single-origin layout satisfies this.
"""

from __future__ import annotations

import json
from typing import Any, Callable, Dict, List, Protocol, runtime_checkable

#: The visualizer's BroadcastChannel. Deliberately distinct from ``praxis_repl``.
VIZ_CHANNEL = "praxis_viz"


@runtime_checkable
class VizTransport(Protocol):
    """What :class:`~praxis.viz.browser.BrowserVisualizer` requires of a sink.

    ``send`` takes the **already-serialized** command string produced by PLR's
    ``Visualizer._assemble_command``. It is deliberately not handed a dict: that
    method is where ``_sanitize_floats`` runs, and routing around it would
    reintroduce the defect S-D found (``max_volume = float('inf')`` on
    ``trash``/``trash_core96`` emits a bare ``Infinity`` token that browser
    ``JSON.parse`` rejects, failing the initial 65 KB deck paint while every
    subsequent delta parses fine).
    """

    def send(self, serialized: str) -> None: ...

    def stats(self) -> Dict[str, int]: ...


class RecordingTransport:
    """In-memory transport for browserless tests (P6.5).

    Keeps every serialized payload so tests can assert the **ordered event
    sequence** rather than byte-exact payloads -- payload bytes differ across PLR
    pins (S-D measured 485 KB / 164 KB / 137 KB for the same operation across the
    three candidate pins), so byte comparison would be a pin-coupled false alarm.
    Event order is the stable contract.
    """

    def __init__(self) -> None:
        self.messages: List[str] = []

    def send(self, serialized: str) -> None:
        self.messages.append(serialized)

    def stats(self) -> Dict[str, int]:
        return {"sent": len(self.messages)}

    @property
    def events(self) -> List[str]:
        """Ordered event names, e.g. ``["set_root_resource", "set_state", ...]``."""
        return [self.decoded(i)["event"] for i in range(len(self.messages))]

    def decoded(self, index: int) -> Dict[str, Any]:
        """The parsed payload at ``index``.

        Parsing here is itself meaningful: it fails loudly on a non-finite float
        that ``json.dumps`` let through, which is precisely the S-D defect. A test
        that only counted messages would not notice.
        """
        return json.loads(self.messages[index])

    def clear(self) -> None:
        self.messages.clear()


class BroadcastChannelTransport:
    """Posts serialized commands onto a BroadcastChannel via an injected poster.

    ``post`` is supplied by the caller (in the kernel,
    ``praxis.viz.browser.make_broadcast_poster``) so this class stays importable
    and testable outside Pyodide. It is called with the serialized string.
    """

    def __init__(
        self,
        post: Callable[[str], None],
        channel_name: str = VIZ_CHANNEL,
    ) -> None:
        self._post = post
        self.channel_name = channel_name
        self._sent = 0
        self._failed = 0

    def send(self, serialized: str) -> None:
        try:
            self._post(serialized)
        except Exception:
            # Count and re-raise. A silently-swallowed post would present exactly
            # as "the deck never painted" with no diagnostic -- the failure shape
            # this project has already been burned by twice.
            self._failed += 1
            raise
        self._sent += 1

    def stats(self) -> Dict[str, int]:
        return {"sent": self._sent, "failed": self._failed}
