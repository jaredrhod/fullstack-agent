# fullstack-kimi voice bridge: agent backend with tool use.

import json
import os
import subprocess
from pathlib import Path

from openai import OpenAI

# Import memory tools if the vault is bundled.
try:
    import memory
    MEMORY_AVAILABLE = True
except Exception:
    MEMORY_AVAILABLE = False


class Agent:
    def __init__(self, cfg, approve_callback=None):
        self.cfg = cfg
        self.llm_cfg = cfg.get("llm", {})
        self.approve_callback = approve_callback or (lambda _n, _d: True)
        backend = self.llm_cfg.get("backend", "kimi_api")
        if backend != "kimi_api":
            raise ValueError(f"unknown llm backend: {backend}")

        api_key = self.llm_cfg.get("api_key")
        if not api_key:
            raise RuntimeError("llm backend 'kimi_api' requires an api_key or MOONSHOT_API_KEY env var")

        self.client = OpenAI(
            api_key=api_key,
            base_url=self.llm_cfg.get("base_url", "https://api.moonshot.ai/v1"),
        )
        self.model = self.llm_cfg.get("model", "kimi-k3")
        self.name = cfg.get("name", "Kimi")
        self.messages = []
        self.tools = []
        self.tool_map = {}
        self._load_identity()
        self._load_tools()

    def _load_identity(self):
        agent_dir = Path(self.cfg.get("agent_dir", "~")).expanduser()
        identity_text = f"You are {self.name}, a helpful AI assistant.\n"
        identity_text += "You have tools. Use them when they help answer the user.\n"
        identity_text += "When you write files, prefer Markdown. Keep replies concise when speaking.\n"
        for filename in ("AGENTS.md", "KIMI.md", "SYSTEM.md"):
            path = agent_dir / filename
            if path.exists():
                identity_text += f"\n--- {filename} ---\n" + path.read_text(encoding="utf-8")
        self.messages.append({"role": "system", "content": identity_text})

    def _load_tools(self):
        tool_files = [Path(__file__).parent / "tools" / "system_tools.json"]
        if MEMORY_AVAILABLE:
            tool_files.append(Path(__file__).parent.parent / "kimi-memory-vault" / "tools" / "memory_tools.json")

        for tf in tool_files:
            if tf.exists():
                defs = json.loads(tf.read_text(encoding="utf-8"))
                self.tools.extend(defs)

        self.tool_map = {
            "bash": self._tool_bash,
            "read_file": self._tool_read_file,
            "write_file": self._tool_write_file,
            "memory_search": self._tool_memory_search,
            "memory_read": self._tool_memory_read,
            "memory_write": self._tool_memory_write,
            "memory_inbox": self._tool_memory_inbox,
            "memory_session": self._tool_memory_session,
        }

    def _resolve_path(self, path: str) -> Path:
        p = Path(path).expanduser()
        if not p.is_absolute():
            p = Path(self.cfg.get("agent_dir", "~")).expanduser() / p
        return p.resolve()

    def _tool_bash(self, args: dict) -> str:
        cmd = args.get("command", "")
        if not cmd:
            return "no command provided"
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            out = result.stdout
            if result.stderr:
                out += "\n" + result.stderr
            if result.returncode != 0:
                out += f"\n[exit code {result.returncode}]"
            return out[:4000]
        except Exception as exc:
            return f"error: {exc}"

    def _tool_read_file(self, args: dict) -> str:
        p = self._resolve_path(args.get("path", ""))
        try:
            return p.read_text(encoding="utf-8")[:8000]
        except Exception as exc:
            return f"error reading {p}: {exc}"

    def _tool_write_file(self, args: dict) -> str:
        p = self._resolve_path(args.get("path", ""))
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(args.get("content", ""), encoding="utf-8")
            return f"wrote {p}"
        except Exception as exc:
            return f"error writing {p}: {exc}"

    def _tool_memory_search(self, args: dict) -> str:
        if not MEMORY_AVAILABLE:
            return "memory vault not available"
        results = memory.search_notes(args.get("query", ""), args.get("limit", 10))
        return json.dumps(results, ensure_ascii=False)

    def _tool_memory_read(self, args: dict) -> str:
        if not MEMORY_AVAILABLE:
            return "memory vault not available"
        return memory.read_note(args.get("path", ""))

    def _tool_memory_write(self, args: dict) -> str:
        if not MEMORY_AVAILABLE:
            return "memory vault not available"
        return memory.write_note(args.get("path", ""), args.get("content", ""))

    def _tool_memory_inbox(self, args: dict) -> str:
        if not MEMORY_AVAILABLE:
            return "memory vault not available"
        return memory.append_to_inbox(args.get("text", ""))

    def _tool_memory_session(self, args: dict) -> str:
        if not MEMORY_AVAILABLE:
            return "memory vault not available"
        return memory.add_session_note(args.get("text", ""))

    def _needs_approval(self, name: str) -> bool:
        return name in ("bash", "write_file", "memory_write", "memory_inbox", "memory_session")

    def _execute_tool(self, call) -> dict:
        name = call.function.name
        args = json.loads(call.function.arguments or "{}")
        description = f"{name}({json.dumps(args)})"

        if self._needs_approval(name):
            if not self.approve_callback(name, description):
                return {"role": "tool", "tool_call_id": call.id, "content": "user denied permission"}

        handler = self.tool_map.get(name)
        if not handler:
            return {"role": "tool", "tool_call_id": call.id, "content": f"unknown tool: {name}"}
        try:
            result = handler(args)
        except Exception as exc:
            result = f"error: {exc}"
        return {"role": "tool", "tool_call_id": call.id, "content": str(result)[:8000]}

    def respond(self, text: str) -> str:
        self.messages.append({"role": "user", "content": text})

        for _ in range(8):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=self.tools,
                tool_choice="auto",
                max_completion_tokens=1024,
            )
            message = response.choices[0].message
            self.messages.append(message)

            if not message.tool_calls:
                reply = message.content or ""
                return reply.strip()

            for call in message.tool_calls:
                result = self._execute_tool(call)
                self.messages.append(result)

        return "I ran too many tool calls. Please rephrase your request."
