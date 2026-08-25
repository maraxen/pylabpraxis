"""Teacher backends (task deliverable 3; spec rev2 F6 amendment).

Two sanctioned backends:

(a) ``OxAlphaBatchWriter`` -- writes self-contained prompt-batch files with
    expected-response-shape instructions so an orchestrator can later fan
    them to spawned ox-alpha jcode workers (ambiguity-injection / golden
    authoring lane). No network, fully offline.

(b) ``TitanixTeacher`` -- DIRECT HTTP to the verified-live localhost vLLM
    endpoint (OpenAI-compatible ``/v1/chat/completions``, model
    ``titanix-vllm-primary``), implemented end-to-end now for bulk
    mechanical passes. stdlib urllib only: no new dependencies.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable, Final, Protocol

from floor_gen.prompts import response_shape_instructions
from floor_gen.versions import TITANIX_BASE_URL, TITANIX_MODEL

__all__ = ["FakeTeacher", "OxAlphaBatchWriter", "TeacherBackend", "TitanixError", "TitanixTeacher"]


class TeacherBackend(Protocol):
    """Minimal backend surface the corpus driver consumes."""

    @property
    def teacher_model_version(self) -> str: ...

    def complete(self, system: str, user: str) -> str:
        """Return the RAW assistant text verbatim."""
        ...


class TitanixError(RuntimeError):
    """Loud transport/shape failure against the titanix vLLM endpoint."""


class TitanixTeacher:
    """Direct OpenAI-compatible chat-completions client for localhost:8020/v1."""

    def __init__(
        self,
        base_url: str = TITANIX_BASE_URL,
        model: str = TITANIX_MODEL,
        timeout_s: float = 180.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout_s = timeout_s
        self._resolved_version: str | None = None

    @property
    def teacher_model_version(self) -> str:
        if self._resolved_version is None:
            self._resolved_version = self._resolve_model_version()
        return self._resolved_version

    def _resolve_model_version(self) -> str:
        payload = self._request_json("GET", "/models")
        for entry in payload.get("data", []):
            if entry.get("id") == self._model:
                root = entry.get("root") or entry.get("id")
                return f"{self._model}@{root}"
        raise TitanixError(f"model {self._model!r} not served at {self._base_url}")

    def complete(self, system: str, user: str) -> str:
        body = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            # Greedy decode for reproducibility-on-regeneration intent; the
            # cache is what guarantees byte-identity across teacher drift.
            "temperature": 0,
            # Thinking-capable served models can spend budget before answering;
            # 1024 leaves ample room for the small mandated JSON object.
            "max_tokens": 1024,
            "stream": False,
            # Qwen3-family served models: disable chain-of-thought so the
            # budget goes to the mandated JSON object (verified against the
            # live titanix endpoint; ignored by non-thinking templates).
            "chat_template_kwargs": {"enable_thinking": False},
        }
        last_error: TitanixError | None = None
        for _attempt in range(2):  # one bounded retry on empty content
            payload = self._request_json("POST", "/chat/completions", body)
            try:
                message = payload["choices"][0]["message"]
                content = message["content"]
            except (KeyError, IndexError, TypeError) as exc:
                raise TitanixError(f"unexpected completion shape: {json.dumps(payload)[:400]}") from exc
            if isinstance(content, str) and content.strip():
                return content
            reasoning = str(message.get("reasoning") or message.get("reasoning_content") or "")[:200]
            last_error = TitanixError(
                f"empty completion content from titanix (finish={payload['choices'][0].get('finish_reason')!r}, reasoning={reasoning!r})"
            )
        raise last_error  # type: ignore[misc]

    def _request_json(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        data = json.dumps(body).encode("utf-8") if body is not None else None
        request = urllib.request.Request(url, data=data, method=method)
        request.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(request, timeout=self._timeout_s) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            snippet = exc.read().decode("utf-8", errors="replace")[:300]
            raise TitanixError(f"{method} {url} -> HTTP {exc.code}: {snippet}") from exc
        except urllib.error.URLError as exc:
            raise TitanixError(f"{method} {url} failed: {exc.reason}") from exc
        except TimeoutError as exc:
            raise TitanixError(f"{method} {url} timed out after {self._timeout_s}s") from exc


class FakeTeacher:
    """Offline scripted backend for tests + offline pipeline checks."""

    def __init__(
        self,
        responder: Callable[[str, str], str] | None = None,
        model_version: str = "fake-teacher@test",
    ) -> None:
        self._responder = responder or self._default_responder
        self._model_version = model_version
        self.call_count = 0

    @property
    def teacher_model_version(self) -> str:
        return self._model_version

    def complete(self, system: str, user: str) -> str:
        self.call_count += 1
        return self._responder(system, user)

    @staticmethod
    def _default_responder(system: str, user: str) -> str:
        if '"clarification"' in user and "OUTSIDE" in user:
            return json.dumps(
                {
                    "utterance": "Can you do this off-list request for me?",
                    "clarification": "I can't do that with the tools I have, but I can help with pipetting, deck moves, or plate reads.",
                },
                sort_keys=True,
            )
        return json.dumps(
            {"utterance": "Aspirate 50 microliters from plate_1_A1.", "clarification": None},
            sort_keys=True,
        )


class OxAlphaBatchWriter:
    """Write fan-out-ready prompt batch files for ox-alpha jcode workers."""

    HEADER: Final[str] = """# ox-alpha NL-ification batch {batch_no} ({n_items} items)

prompt_version={prompt_version}

You are one of several spawned ox-alpha workers producing teacher text for the
Coxswain P2.3 coverage floor. For EACH item below, read `system` and `user`,
compose the assistant reply exactly per the output contract, then APPEND one
line to `responses.jsonl` next to your batch file:

{{"input_hash": "<item input_hash>", "response": <your reply as a JSON string>}}

Rules:
- `response` is the EXACT assistant text (a single JSON object per the
  contract) serialized as a JSON string. No markdown fences around it.
- One line per item, keyed by `input_hash`. Do not reorder, do not merge.
- Do not edit any other field or file.

Output contract (verbatim):
{shape}
"""

    def write_batches(
        self,
        items: list[dict[str, str]],
        out_dir: Path,
        *,
        prompt_version: str,
        batch_size: int = 8,
    ) -> list[Path]:
        out_dir.mkdir(parents=True, exist_ok=True)
        paths: list[Path] = []
        for start in range(0, len(items), batch_size):
            chunk = items[start : start + batch_size]
            batch_no = start // batch_size
            lines = [
                self.HEADER.format(
                    batch_no=batch_no,
                    n_items=len(chunk),
                    prompt_version=prompt_version,
                    shape=response_shape_instructions(),
                )
            ]
            for offset, item in enumerate(chunk):
                lines.append(
                    "\n--- ITEM {no} (input_hash={ih}) ---\nsystem:\n{system}\n\nuser:\n{user}\n".format(
                        no=start // batch_size * batch_size + offset,
                        ih=item["input_hash"],
                        system=item["system"],
                        user=item["user"],
                    )
                )
            path = out_dir / f"batch_{batch_no:04d}.md"
            path.write_text("\n".join(lines), encoding="utf-8")
            paths.append(path)
        return paths
