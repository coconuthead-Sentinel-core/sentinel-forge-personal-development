#!/usr/bin/env python3
"""
ai_brain.py — onboard local AI assistant for Sentinel Forge.

A self-contained "wiring harness": one class wrapping a LOCAL language model via
Ollama. 100% offline — the only network touch is the loopback to the Ollama
daemon on this machine. No cloud, no API key, no per-token cost.

Pulled out of the Strata Console prototype and installed here as a pluggable
module. If Ollama or the model isn't present, `.available` is False and `ask()`
returns None, so callers degrade gracefully (the app keeps working without AI).

Smoke test from this folder:
    python ai_brain.py "What can you help me with?"

Optional env overrides:
    SENTINEL_AI_MODEL      (default: llama3.2:3b)
    SENTINEL_AI_NUM_CTX    (default: 2048 — keep small on low-RAM machines)
    SENTINEL_AI_KEEP_ALIVE (default: 10m — keep the model warm between calls)
"""
from __future__ import annotations
import os
import sys
from typing import Optional

# Optional dependency: importing must never break the app when Ollama is absent.
try:
    import ollama
    _OLLAMA_IMPORTED = True
except Exception:
    _OLLAMA_IMPORTED = False

DEFAULT_MODEL = os.environ.get("SENTINEL_AI_MODEL", "llama3.2:3b")

DEFAULT_SYSTEM = (
    "You are the onboard assistant inside Sentinel Forge, a local, offline "
    "personal-development and reading workspace. You help with reading, study, "
    "journaling, planning, and focus. Be accurate, concise, and encouraging. "
    "If something isn't in the provided context or you are unsure, say so plainly "
    "instead of inventing details. When asked for code, return clean, working code."
)


class LocalBrain:
    """Local Ollama-backed assistant. Offline, graceful, dependency-optional.

    The KV cache is bounded by num_ctx (the 128K default OOMs on small machines);
    keep_alive keeps the model resident so only the first call pays the cold load.
    """

    def __init__(self, model: Optional[str] = None,
                 num_ctx: Optional[int] = None,
                 keep_alive: Optional[str] = None):
        self.model = model or DEFAULT_MODEL
        self.num_ctx = int(num_ctx or os.environ.get("SENTINEL_AI_NUM_CTX", "2048"))
        self.keep_alive = keep_alive or os.environ.get("SENTINEL_AI_KEEP_ALIVE", "10m")
        self.available = False
        self.last_error: Optional[str] = None
        if not _OLLAMA_IMPORTED:
            self.last_error = "ollama package not installed"
            return
        try:
            self.available = any(
                self.model.split(":")[0] in n for n in self._installed_models()
            )
            if not self.available:
                self.last_error = f"model '{self.model}' not pulled (run: ollama pull {self.model})"
        except Exception as e:
            self.last_error = f"Ollama daemon not reachable: {type(e).__name__}"

    @staticmethod
    def _installed_models():
        """Installed model names, tolerant of ollama library version differences."""
        data = ollama.list()
        models = getattr(data, "models", None)
        if models is None and isinstance(data, dict):
            models = data.get("models", [])
        names = []
        for m in (models or []):
            n = getattr(m, "model", None)
            if n is None and isinstance(m, dict):
                n = m.get("model") or m.get("name")
            if n:
                names.append(n)
        return names

    def ask(self, prompt: str, system: Optional[str] = None,
            context: str = "", temperature: float = 0.5) -> Optional[str]:
        """Return the model's reply, or None if the backend is unavailable / errors."""
        if not self.available:
            return None
        sys_text = system or DEFAULT_SYSTEM
        if context:
            sys_text += f"\n\nContext:\n{context}"
        try:
            resp = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": sys_text},
                    {"role": "user", "content": prompt},
                ],
                keep_alive=self.keep_alive,
                options={
                    "temperature": temperature,
                    "num_ctx": self.num_ctx,
                    "num_predict": 512,
                },
            )
            return resp["message"]["content"].strip()
        except Exception as e:
            self.last_error = f"{type(e).__name__}: {e}"
            return None


# Shared lazy singleton so the whole app talks to one warm model instance.
_BRAIN: Optional[LocalBrain] = None


def get_brain() -> LocalBrain:
    global _BRAIN
    if _BRAIN is None:
        _BRAIN = LocalBrain()
    return _BRAIN


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "In one sentence, what can you help me with?"
    brain = get_brain()
    print(f"[brain available: {brain.available} | model: {brain.model}]")
    if not brain.available:
        print(f"[offline: {brain.last_error}]")
    else:
        print(brain.ask(question))
