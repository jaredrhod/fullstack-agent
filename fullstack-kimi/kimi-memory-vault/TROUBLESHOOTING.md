# Troubleshooting

## The agent says it can't find memory tools

Make sure `kimi-voice/agent.py` is loading `tools/memory_tools.json` and passing the tool definitions to the Kimi API.

## Notes are not being saved

Check that `vault_dir` in `kimi-memory-vault.json` points to a writable path. The default is `~/my-kimi-agent/vault`.

## The agent reads stale notes

The agent searches the vault on demand. If a note was updated recently, the next search will see it.

## Vault path errors

All note paths are vault-relative and must stay inside the vault. Paths with `..` are rejected.
