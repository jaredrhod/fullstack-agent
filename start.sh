#!/bin/bash
# fullstack-agent (ChatGPT fork): memory, chat, face, hands.
# Copyright (C) 2026 Jared Rhodenizer — ChatGPT adaptations by contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
#   ./start.sh          face (if installed)
#   ./start.sh chat     ChatGPT typed chat
#   ./start.sh hands    barehands board
#   ./start.sh voice    same as chat (ChatGPT; no Claude backtalk)

HERE="$(cd "$(dirname "$0")" && pwd)"
HOME_DIR="$(dirname "$HERE")"
MODE="${1:-all}"
PIDS=()

cleanup() {
  trap - EXIT INT TERM
  for p in "${PIDS[@]}"; do kill "$p" 2>/dev/null; done
  echo
  echo "agent stopped."
}
trap cleanup EXIT INT TERM

echo "fullstack-agent (ChatGPT): starting from $HOME_DIR"

if [ "$MODE" = "chat" ] || [ "$MODE" = "voice" ]; then
  echo "  chatgpt: typed chat"
  cd "$HERE/chatgpt"
  python3 -c "import certifi" 2>/dev/null || python3 -m pip install -r requirements.txt
  exec python3 chat.py
fi

if [ -d "$HOME_DIR/ai-visualizer" ] && [ "$MODE" != "hands" ]; then
  (cd "$HOME_DIR/ai-visualizer" && exec python3 server.py) &
  PIDS+=($!)
  echo "  face:  starting"
fi

if [ -d "$HOME_DIR/barehands" ] && [ "$MODE" = "hands" ]; then
  (cd "$HOME_DIR/barehands" && exec python3 server.py) &
  PIDS+=($!)
  echo "  hands: starting (open the printed URL in Chrome)"
fi

if [ "$MODE" = "all" ] && [ ! -d "$HOME_DIR/ai-visualizer" ]; then
  echo "  no face installed — starting ChatGPT chat"
  cd "$HERE/chatgpt"
  python3 -c "import certifi" 2>/dev/null || python3 -m pip install -r requirements.txt
  exec python3 chat.py
fi

echo "  For ChatGPT chat: ./start.sh chat"
wait
