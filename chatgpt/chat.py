#!/usr/bin/env python3
# ChatGPT chat for fullstack-agent (replaces the Claude Code typed session).
# Copyright (C) 2026 contributors — AGPL-3.0-or-later (same license as upstream)
"""Minimal OpenAI chat that reads your agent identity from AGENTS.md / CLAUDE.md."""

from __future__ import annotations

import json
import os
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path

try:
    import certifi

    def _ssl_context() -> ssl.SSLContext:
        return ssl.create_default_context(cafile=certifi.where())
except ImportError:
    def _ssl_context() -> ssl.SSLContext:
        return ssl.create_default_context()


HERE = Path(__file__).resolve().parent
TOOLBOX = HERE.parent
HOME = TOOLBOX.parent


def load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def agent_dir() -> Path:
    env = os.environ.get("AGENT_DIR")
    if env:
        return Path(env).expanduser().resolve()
    # Standard layout: <agent-home>/<toolbox>/chatgpt/chat.py
    markers = ("ai-memory-vault", "ai-visualizer", "barehands")
    home_looks_like_agent = any((HOME / m).is_dir() for m in markers)
    # Do not treat the OS user profile as the agent home just because a CLAUDE.md exists there.
    if home_looks_like_agent and HOME != Path.home():
        return HOME
    if HOME != Path.home() and (
        (HOME / "AGENTS.md").is_file() or (HOME / "CLAUDE.md").is_file()
    ):
        return HOME
    # Repo opened directly (this ChatGPT fork): identity lives in the toolbox until setup creates a home.
    return TOOLBOX


def identity_text(root: Path) -> str:
    for name in ("AGENTS.md", "CLAUDE.md", "JARVIS.md"):
        p = root / name
        if p.is_file():
            return p.read_text(encoding="utf-8", errors="replace")[:12000]
    return (
        f"You are a helpful desktop assistant. Your home folder is {root}."
    )


def chat_completion(messages: list[dict], model: str, api_key: str) -> str:
    body = json.dumps(
        {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, context=_ssl_context(), timeout=90) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")[:400]
        raise SystemExit(f"OpenAI HTTP {e.code}: {detail}") from e
    except urllib.error.URLError as e:
        raise SystemExit(f"Network error talking to OpenAI: {e}") from e
    return data["choices"][0]["message"]["content"]


def main() -> int:
    load_dotenv(TOOLBOX / ".env")
    load_dotenv(HOME / ".env")
    load_dotenv(Path.cwd() / ".env")

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print(
            "Missing OPENAI_API_KEY. Copy .env.example to .env and paste your key.",
            file=sys.stderr,
        )
        return 1

    root = agent_dir()
    model = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
    system = identity_text(root)
    messages = [{"role": "system", "content": system}]

    print(f"ChatGPT agent  model={model}")
    print(f"home={root}")
    print("Type a message (Ctrl-C to quit).\n")

    oneshot = " ".join(sys.argv[1:]).strip()
    if oneshot:
        messages.append({"role": "user", "content": oneshot})
        print(chat_completion(messages, model, api_key))
        return 0

    try:
        while True:
            user = input("you> ").strip()
            if not user:
                continue
            messages.append({"role": "user", "content": user})
            reply = chat_completion(messages, model, api_key)
            messages.append({"role": "assistant", "content": reply})
            print(f"\n{reply}\n")
    except (KeyboardInterrupt, EOFError):
        print("\nbye.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
