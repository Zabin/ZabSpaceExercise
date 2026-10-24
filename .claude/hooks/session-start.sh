#!/bin/bash
# SessionStart hook: install SpaceSim's runtime and test dependencies so a cloud session can run
# `python3 -m pytest` from the start. The list is CLAUDE.md's "Build/test commands" install line.
# Idempotent: pip skips packages that are already installed.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

python3 -m pip install --quiet --disable-pip-version-check --root-user-action=ignore \
  pydantic numpy sgp4 pyyaml pytest hypothesis skyfield fastapi uvicorn httpx playwright
