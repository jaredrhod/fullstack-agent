# fullstack-kimi memory vault: persistent notes for your agent.
# Copyright (C) 2026 Jared Rhodenizer
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Core memory operations for the fullstack-kimi memory vault.

The vault is a folder of plain Markdown files. The agent reads and writes
these files to remember the user, projects, and conversations across sessions.
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path


def load_config():
    cfg_path = Path(__file__).parent / "kimi-memory-vault.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    cfg["vault_dir"] = str(Path(cfg["vault_dir"]).expanduser())
    return cfg


def ensure_vault():
    cfg = load_config()
    vault = Path(cfg["vault_dir"])
    for sub in ("sessions", "people", "projects", "topics"):
        (vault / sub).mkdir(parents=True, exist_ok=True)
    inbox = vault / "inbox.md"
    if not inbox.exists():
        inbox.write_text("# Inbox\n\nQuick captures go here.\n", encoding="utf-8")
    identity = vault / "identity.md"
    if not identity.exists():
        identity.write_text(
            f"# {cfg.get('agent_name', 'Agent')}\n\n"
            "Role and personality for the agent go here.\n",
            encoding="utf-8",
        )
    return vault


def _vault_dir():
    return Path(load_config()["vault_dir"])


def search_notes(query: str, limit: int = 10):
    """Search all markdown notes for a query string."""
    vault = _vault_dir()
    results = []
    query_lower = query.lower()
    for path in vault.rglob("*.md"):
        try:
            text = path.read_text(encoding="utf-8")
            if query_lower in text.lower():
                # Return a snippet around the match.
                idx = text.lower().find(query_lower)
                start = max(0, idx - 120)
                end = min(len(text), idx + 240)
                snippet = text[start:end].replace("\n", " ")
                results.append({
                    "file": str(path.relative_to(vault)),
                    "snippet": snippet,
                })
        except Exception:
            continue
    return results[:limit]


def read_note(path: str) -> str:
    """Read a single note by vault-relative path."""
    vault = _vault_dir()
    note_path = vault / path
    note_path = note_path.resolve()
    if not str(note_path).startswith(str(vault.resolve())):
        raise ValueError("path escapes vault")
    if not note_path.exists():
        return ""
    return note_path.read_text(encoding="utf-8")


def write_note(path: str, content: str) -> str:
    """Write a note at a vault-relative path. Creates parent folders."""
    vault = _vault_dir()
    note_path = vault / path
    note_path = note_path.resolve()
    if not str(note_path).startswith(str(vault.resolve())):
        raise ValueError("path escapes vault")
    note_path.parent.mkdir(parents=True, exist_ok=True)
    note_path.write_text(content, encoding="utf-8")
    return str(note_path.relative_to(vault))


def append_to_inbox(text: str):
    """Append a quick capture to inbox.md."""
    vault = _vault_dir()
    inbox = vault / "inbox.md"
    inbox.write_text(
        inbox.read_text(encoding="utf-8") + f"\n- {datetime.now().isoformat()}: {text}\n",
        encoding="utf-8",
    )
    return str(inbox.relative_to(vault))


def add_session_note(text: str):
    """Append a summary to today's session note."""
    vault = _vault_dir()
    cfg = load_config()
    date_path = datetime.now().strftime(cfg.get("daily_note_format", "sessions/%Y-%m-%d.md"))
    note_path = vault / date_path
    note_path.parent.mkdir(parents=True, exist_ok=True)
    header = f"# Session {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    if not note_path.exists():
        note_path.write_text(header, encoding="utf-8")
    note_path.write_text(
        note_path.read_text(encoding="utf-8") + f"\n{text}\n",
        encoding="utf-8",
    )
    return str(note_path.relative_to(vault))


def list_notes(folder: str = ""):
    """List notes in a vault-relative folder."""
    vault = _vault_dir()
    target = vault / folder if folder else vault
    notes = []
    for path in target.rglob("*.md"):
        notes.append(str(path.relative_to(vault)))
    return sorted(notes)


if __name__ == "__main__":
    ensure_vault()
    print(f"vault ready at {_vault_dir()}")
