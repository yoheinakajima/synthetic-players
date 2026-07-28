#!/usr/bin/env bash
# Restore the sealed research data artifacts from the phase4-final release.
# No secrets required: the release assets are public. Verifies sha256s from
# DATA-SHA256SUMS.txt before installing anything.
set -euo pipefail
cd "$(dirname "$0")/.."
REL="https://github.com/yoheinakajima/synthetic-players/releases/download/phase4-final"
DEST="artifacts/api-server/engine/data"
mkdir -p "$DEST" /tmp/sp-restore
cd /tmp/sp-restore
for f in engine.db.xz budget.db.xz phase4-driver-state.json phase4-driver-plan.json DATA-SHA256SUMS.txt; do
  curl -fsSL -o "$f" "$REL/$f"
done
sha256sum -c DATA-SHA256SUMS.txt
xz -dk engine.db.xz budget.db.xz
cd - >/dev/null
for f in engine.db budget.db phase4-driver-state.json phase4-driver-plan.json; do
  if [ -e "$DEST/$f" ]; then echo "refusing to overwrite existing $DEST/$f — move it aside first"; exit 1; fi
  cp "/tmp/sp-restore/$f" "$DEST/$f"
done
echo "restored: $(ls -la $DEST)"
echo "Next: cd artifacts/api-server && uv run python engine/server.py  (port 8090; no secrets needed for replay)"
echo "Then:  cd artifacts/api-server/engine && uv run python phase4_step8_audit.py   # expect CLEAN"
