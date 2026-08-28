# fullstack-kimi voice bridge: agent backend.

from pathlib import Path

from openai import OpenAI


class Agent:
    def __init__(self, cfg):
        self.cfg = cfg
        self.llm_cfg = cfg.get("llm", {})
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
        self._load_identity()

    def _load_identity(self):
        agent_dir = Path(self.cfg.get("agent_dir", "~")).expanduser()
        identity_text = ""
        for filename in ("AGENTS.md", "KIMI.md", "SYSTEM.md"):
            path = agent_dir / filename
            if path.exists():
                identity_text += f"\n\n--- {filename} ---\n" + path.read_text(encoding="utf-8")
        if not identity_text:
            identity_text = f"You are {self.name}, a helpful AI assistant."
        self.messages.append({"role": "system", "content": identity_text})

    def respond(self, text: str) -> str:
        self.messages.append({"role": "user", "content": text})
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            max_completion_tokens=1024,
        )
        reply = response.choices[0].message.content.strip()
        self.messages.append({"role": "assistant", "content": reply})
        # Keep context window bounded roughly.
        if len(self.messages) > 20:
            self.messages = [self.messages[0]] + self.messages[-18:]
        return reply
