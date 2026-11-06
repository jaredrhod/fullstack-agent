# Troubleshooting

Between-piece issues for this **ChatGPT fork**. Component guides still live in each installed repo (`ai-memory-vault`, `ai-visualizer`, `barehands`).

## I closed the window in the middle of setup

Nothing is lost. Open this toolbox folder in Cursor again and say: **we got cut off, keep going with the setup** (or **set me up**). The wizard finds what is already there and continues.

## Chat says missing OPENAI_API_KEY

Copy `.env.example` to `.env` in the toolbox folder and paste your key from https://platform.openai.com/api-keys. Never commit `.env`.

## Chat fails with SSL / certificate errors

Use a real Python from python.org (or `uv`), not the Microsoft Store `python` stub. Then:

```
cd chatgpt
python -m pip install -r requirements.txt
python chat.py
```

## start.bat chat cannot find Python

Install Python 3 from https://www.python.org/downloads/ and tick **Add python.exe to PATH**. Open a **new** terminal and try again.

## The face sits idle

This fork’s ChatGPT chat does not drive the face signal bus the way upstream backtalk did. The face still runs as a visualizer; typed ChatGPT chat is separate. If you later add a voice line that writes `.voice_*` files, point `ai-visualizer.json` `bus_dir` at that folder.

## My agent forgot who it is

Identity lives in `AGENTS.md` / `CLAUDE.md` in the **agent home** (parent of this toolbox). Open Cursor in that home folder. `chatgpt/chat.py` reads those files from the home folder.

## Updates

`./update.sh` pulls installed upstream pieces. Your `.env`, identity files, and vault stay outside tracked files.
