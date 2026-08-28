# kimi-memory-vault

Persistent memory for fullstack-kimi. A folder of plain Markdown files that the agent reads and writes.

## Vault layout

```
vault/
├── identity.md        # Agent personality and role
├── inbox.md           # Quick captures
├── sessions/          # Daily conversation logs
├── people/            # People the user mentions
├── projects/          # Active projects
└── topics/            # Topics, lessons, reference notes
```

## Tools

The agent receives these tools in `tools/memory_tools.json`:

- `memory_search(query)` — find notes
- `memory_read(path)` — read a note
- `memory_write(path, content)` — write a note
- `memory_inbox(text)` — quick capture
- `memory_session(text)` — append to today's log

## Setup

Run once to create the vault:

```bash
python3 memory.py
```

## Config

Edit `kimi-memory-vault.json`:

```json
{
  "vault_dir": "~/my-kimi-agent/vault",
  "agent_name": "Kimi",
  "daily_note_format": "sessions/%Y-%m-%d.md"
}
```

## License

AGPL-3.0-or-later. See root `LICENSE`.
