#!/usr/bin/env bash
# One-command zero-credential verifier for the synthetic-players capsule.
# Run from the capsule root: ./verify.sh
# Requires: bash, sha256sum, xz, python3, uv (https://docs.astral.sh/uv/).
# No credentials, no API keys, no live provider calls. `uv` may fetch packages;
# use an offline cache when network-free package installation is required.
set -euo pipefail
cd "$(dirname "$0")"

echo "== 1/5 capsule integrity: SHA256SUMS.capsule"
sha256sum -c SHA256SUMS.capsule --quiet
echo "OK"

echo "== 2/5 stage archived databases"
mkdir -p artifacts/api-server/engine/data
for f in engine.db budget.db; do
  [ -e "artifacts/api-server/engine/data/$f" ] || xz -dkc "data/$f.xz" > "artifacts/api-server/engine/data/$f"
done
cp data/phase4-driver-plan.json data/phase4-driver-state.json \
   data/phase5-driver-plan.json data/phase5-driver-state.json \
   artifacts/api-server/engine/data/ 2>/dev/null || true

echo "== 3/5 zero-credential guard"
for v in $(env | grep -oE '^AI_INTEGRATIONS[A-Z_]*' || true); do unset "$v"; done
unset OPENAI_API_KEY ANTHROPIC_API_KEY GEMINI_API_KEY 2>/dev/null || true
echo "OK (no provider variables set for the audits below)"

echo "== 4/5 Phase 3 replay audit (320 LLM runs + 20 deterministic baselines)"
cd artifacts/api-server
uv run --with numpy --with scipy python engine/phase3_replay_audit.py

echo "== 5/5 Phase 4-5 byte-exact replay audits"
# Start a LOCAL engine server against THIS capsule's data (never a pre-existing
# service on the default port). Phase 3 above is in-process and needs no server.
export ENGINE_PORT=8123 ENGINE_URL="http://127.0.0.1:8123"
uv run --with fastapi --with uvicorn --with pydantic --with numpy --with scipy \
  python engine/server.py & SRV=$!
trap 'kill $SRV 2>/dev/null || true' EXIT
for i in $(seq 1 60); do
  curl -fsS "$ENGINE_URL/docs" >/dev/null 2>&1 && break
  sleep 1
done
# Phase 4 audit (2,864 runs; Phase 5 runs are audited by the next step).
STEP8_PHASE4_ONLY=1 uv run --with numpy --with scipy python engine/phase4_step8_audit.py
# Phase 5 audit (1,712 runs, in-process).
uv run --with fastapi --with uvicorn --with pydantic --with numpy --with scipy \
  python engine/phase5_replay_audit.py
kill $SRV 2>/dev/null || true
trap - EXIT

echo "CAPSULE VERIFICATION PASS — 4,916 Phase 3-5 runs verified"
