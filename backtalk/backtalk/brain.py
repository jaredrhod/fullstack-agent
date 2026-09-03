# backtalk: talk to your agent out loud.
# Copyright (C) 2026 Akhil
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""The warm brain — a persistent Ollama session via the OpenAI-compatible API,
streaming.

One OllamaBrain lives for the whole voice session. History is maintained
as a Python list (Ollama is stateless per request). Partial-message
streaming means sentences are yielded the moment they are complete, so
the mouth starts speaking while the rest of the thought is still forming.

The system prompt is read from the agent_dir's AGENTS.md (or CLAUDE.md
for compatibility), falling back to an inline default. backtalk adds
only the spoken-delivery discipline (config.DISCIPLINE): the medium,
never the character.

Drop-in replacement for the original claude-agent-sdk brain: all public
methods (ask_stream, start, stop, interrupt, reset_turn, command,
set_permission_mode, context_usage) are preserved with identical
signatures so main.py requires zero changes.
"""
import asyncio
import os
import re
from pathlib import Path

from openai import AsyncOpenAI

from backtalk import signals
from backtalk.config import CFG, DISCIPLINE
from backtalk.vlog import log

_SENTENCE_END = re.compile(r"(?<=[.!?])\s")

SESSION_FILE = os.path.join(CFG["signals_dir"], ".backtalk_session")

# ------------------------------------------------------------------ #
#  System-prompt loader                                                #
# ------------------------------------------------------------------ #

def _load_system_prompt() -> str:
    """Read the agent identity from AGENTS.md or CLAUDE.md in agent_dir,
    then append the spoken-delivery discipline."""
    agent_dir = Path(CFG["agent_dir"]).expanduser()
    for name in ("AGENTS.md", "CLAUDE.md"):
        p = agent_dir / name
        if p.exists():
            try:
                identity = p.read_text(encoding="utf-8").strip()
                log(f"[brain] loaded identity from {p.name}")
                return identity + "\n\n" + DISCIPLINE
            except OSError:
                pass
    # Fallback: no identity file found — use name from config
    name = CFG.get("name", "Assistant")
    log("[brain] no AGENTS.md or CLAUDE.md found — using built-in default")
    return (
        f"You are {name}, a helpful, warm voice assistant. "
        f"You are knowledgeable, concise, and personable.\n\n" + DISCIPLINE
    )


# ------------------------------------------------------------------ #
#  WarmBrain                                                           #
# ------------------------------------------------------------------ #

class WarmBrain:
    """Ollama-backed voice brain. Drop-in for the original ClaudeSDKClient
    brain: same public interface, zero changes required in main.py."""

    def __init__(self, model: str | None = None,
                 can_use_tool=None,       # accepted, not used (no tool gate)
                 resume_id: str | None = None):  # accepted, not used
        self.model = model or CFG["model"]
        # Session usage (spoken on "usage report")
        self.session = {"turns": 0, "out_tokens": 0, "in_tokens": 0,
                        "cost": 0.0}
        # Conversation history maintained in-process (Ollama is stateless)
        self._history: list[dict] = []
        self._system_prompt: str = ""
        self._client: AsyncOpenAI | None = None
        # Interrupt flag: set True to abort the current stream
        self._interrupted: bool = False

    # ---- lifecycle ------------------------------------------------- #

    async def start(self):
        """Initialise the Ollama client and load the system prompt."""
        ollama_url = CFG.get("ollama_url", "http://localhost:11434/v1")
        self._client = AsyncOpenAI(
            base_url=ollama_url,
            api_key="ollama",   # required by SDK, value is ignored by Ollama
        )
        self._system_prompt = _load_system_prompt()
        log(f"[brain] connected to Ollama at {ollama_url}, model={self.model}")

    async def stop(self):
        """Shut down (no-op for Ollama — no persistent connection)."""
        self._client = None

    # ---- interrupt / reset ----------------------------------------- #

    async def interrupt(self):
        """Signal the current stream to abort at the next sentence boundary."""
        self._interrupted = True

    async def reset_turn(self, timeout: float = 8.0):
        """Re-align after a cancelled turn. For Ollama this is a no-op:
        history is only appended on *complete* turns, so a cancelled stream
        leaves history consistent automatically."""
        self._interrupted = False

    # ---- console commands ------------------------------------------ #

    async def command(self, cmd: str) -> str:
        """Handle voice-console slash commands.

        Claude Code commands (/clear, /compact, /model X, /effort X) are
        translated to their Ollama equivalents where possible.
        """
        cmd = cmd.strip()
        if cmd.startswith("/clear"):
            self._history.clear()
            log("[brain] /clear — history reset")
            return "Cleared."
        if cmd.startswith("/compact"):
            # Compact: summarise history into a single message, shrink context
            if self._history:
                summary = await self._summarise_history()
                self._history = [{"role": "user",
                                   "content": "[Previous session summary] " + summary},
                                  {"role": "assistant",
                                   "content": "Understood. I have the summary."}]
                log("[brain] /compact — history compacted")
            return "Compacted."
        if cmd.startswith("/model "):
            new_model = cmd[7:].strip()
            if new_model:
                self.model = new_model
                log(f"[brain] /model — switched to {self.model}")
                return f"Model switched to {self.model}."
        if cmd.startswith("/effort "):
            # Ollama doesn't have effort levels; acknowledge gracefully
            level = cmd[8:].strip()
            log(f"[brain] /effort {level} — no-op for Ollama")
            return f"Effort noted (Ollama doesn't use effort levels)."
        return ""

    async def _summarise_history(self) -> str:
        """Ask the model to summarise conversation history (for /compact)."""
        if not self._client or not self._history:
            return "No history to summarise."
        messages = [{"role": "system",
                     "content": "Summarise the following conversation "
                                "in 3-5 sentences, preserving all key "
                                "facts, decisions, and context."},
                    *self._history]
        try:
            resp = await self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False,
            )
            return resp.choices[0].message.content or ""
        except Exception as e:
            log(f"[brain] compact summary failed: {e}")
            return "Summary unavailable."

    # ---- permission mode ------------------------------------------- #

    async def set_permission_mode(self, backtalk_mode: str):
        """Live permission-mode flip. Ollama has no permission gate;
        acknowledged gracefully so main.py's console verb handler works."""
        log(f"[brain] set_permission_mode({backtalk_mode!r}) — no-op for Ollama")

    # ---- usage ----------------------------------------------------- #

    async def context_usage(self):
        """Return context-window usage info. Ollama doesn't expose this
        as a structured object; return None so the spoken usage report
        skips the context-window line."""
        return None

    # ---- core stream ----------------------------------------------- #

    async def ask_stream(self, utterance: str):
        """Send an utterance and yield complete sentences as they stream out."""
        if not self._client:
            log("[brain] ask_stream called before start()")
            return

        self._interrupted = False

        messages = [
            {"role": "system", "content": self._system_prompt},
            *self._history,
            {"role": "user", "content": utterance},
        ]

        buf = ""
        full_response = ""

        try:
            stream = await self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
            )
            async for chunk in stream:
                if self._interrupted:
                    # User interrupted — close the stream and bail
                    try:
                        await stream.close()
                    except Exception:
                        pass
                    break

                delta = chunk.choices[0].delta if chunk.choices else None
                if delta and delta.content:
                    text = delta.content
                    buf += text
                    full_response += text
                    # emit complete sentences immediately
                    while True:
                        m = _SENTENCE_END.search(buf)
                        if not m:
                            break
                        sentence, buf = (buf[:m.end()].strip(),
                                         buf[m.end():])
                        if sentence:
                            yield sentence

                # Tally usage from the final chunk if available
                if (chunk.usage and not self._interrupted):
                    self.session["out_tokens"] += (chunk.usage.completion_tokens or 0)
                    self.session["in_tokens"] += (chunk.usage.prompt_tokens or 0)

        except asyncio.CancelledError:
            self._interrupted = True
            raise
        except Exception as e:
            log(f"[brain] stream error: {e}")
            yield "Sorry, I hit an error. Check the log for details."
            return

        # Flush any remaining text
        if not self._interrupted:
            tail = buf.strip()
            if tail:
                yield tail

        # Commit to history only on a complete (non-interrupted) turn
        if not self._interrupted and full_response:
            self._history.append({"role": "user", "content": utterance})
            self._history.append({"role": "assistant",
                                   "content": full_response})
            self.session["turns"] += 1

        self._interrupted = False


# ------------------------------------------------------------------ #
#  Smoke-test                                                          #
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    import time

    async def demo():
        b = WarmBrain()
        await b.start()
        for prompt in ("Voice check: greet me in one sentence.",
                       "And what's two plus two, spoken like yourself?"):
            t0 = time.time()
            async for s in b.ask_stream(prompt):
                print(f"  ({time.time()-t0:4.1f}s) {s}", flush=True)
        await b.stop()

    asyncio.run(demo())
