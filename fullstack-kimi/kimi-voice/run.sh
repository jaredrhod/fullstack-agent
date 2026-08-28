#!/bin/bash
# fullstack-kimi voice bridge launcher.
# Copyright (C) 2026 Jared Rhodenizer
# SPDX-License-Identifier: AGPL-3.0-or-later

HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE" || exit 1

# Prefer a local virtual environment if it exists.
if [ -d "$HERE/.venv" ]; then
  source "$HERE/.venv/bin/activate"
fi

exec python3 bridge.py
