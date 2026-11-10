#!/bin/bash
# SessionStart hook: install SpaceSim's dependencies so a cloud session can run `python3 -m pytest`
# from the start. It installs the exact versions in requirements.lock, so a session tests on the
# same versions as the release and as CI. If the lock cannot be installed (no network, a pin that
# is unavailable for this interpreter), it falls back to the unpinned list so the session still starts.
set -uo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
PIP="python3 -m pip install --quiet --disable-pip-version-check --root-user-action=ignore"

if [ -f requirements.lock ] && $PIP -r requirements.lock; then
  exit 0
fi

echo "session-start: could not install requirements.lock; installing unpinned packages instead" >&2
$PIP pydantic numpy sgp4 pyyaml pytest hypothesis skyfield fastapi uvicorn httpx playwright || true
