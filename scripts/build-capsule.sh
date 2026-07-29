#!/usr/bin/env bash
# R2 item 9 — build the public reproduction capsule (capsule/) from the
# private working repo. Zero credentials, zero live calls. Regenerable.
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$PWD"
CAP="$ROOT/capsule"
ENG="$ROOT/artifacts/api-server/engine"

rm -rf "$CAP"
mkdir -p "$CAP"/{data,docs,verify} "$CAP"/artifacts/api-server/{engine,prompts}

# --- 1. sanitized event-store exports (WAL-checkpointed snapshots) -----
python3 - <<'EOF'
import sqlite3, os
for name in ("engine.db", "budget.db"):
    src = os.path.join("artifacts/api-server/engine/data", name)
    dst = os.path.join("capsule/data", name)
    db = sqlite3.connect(src)
    db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    db.execute(f"VACUUM INTO '{dst}'")
    db.close()
    print("exported", dst, os.path.getsize(dst))
EOF
# secret scan of the exports (patterns, not values): fail closed
if strings capsule/data/engine.db capsule/data/budget.db \
    | grep -E -m1 "sk-[A-Za-z0-9]{20}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN( RSA)? PRIVATE KEY|xox[baprs]-" ; then
  echo "SECRET PATTERN FOUND IN EXPORT — refusing to build capsule"; exit 1
fi
xz -9 -T0 capsule/data/engine.db capsule/data/budget.db
cp "$ENG/data/phase4-driver-plan.json" "$ENG/data/phase4-driver-state.json" \
   "$ENG/data/phase5-driver-plan.json" "$ENG/data/phase5-driver-state.json" \
   capsule/data/

# --- 2. registries, seals, ledgers, adjudication records --------------
cp -r docs/phase3-preregistration.md docs/phase3-report.md \
      docs/phase3-layer2.md docs/phase3-layer2.json \
      docs/substitution-estimand-preregistration.md \
      docs/phase4 docs/phase4-close docs/phase5 docs/phase5-close \
      docs/paper docs/analysis docs/instance-ledger.md \
      docs/dead-predictions.md docs/close-out-verification.md \
      capsule/docs/
cp artifacts/api-server/prompts/registry.json capsule/artifacts/api-server/prompts/

# --- 3. adjudication + analysis code with pinned environment ----------
cp "$ENG"/*.py capsule/artifacts/api-server/engine/
cat > capsule/artifacts/api-server/requirements.lock <<'REQ'
# exact versions used by the working environment (uv run --with ...)
REQ
cd artifacts/api-server && uv run --with numpy --with scipy --with pandas \
  python -c "import numpy,scipy,pandas,sys;print(f'numpy=={numpy.__version__}\nscipy=={scipy.__version__}\npandas=={pandas.__version__}\n# python {sys.version.split()[0]}')" \
  >> "$CAP/artifacts/api-server/requirements.lock"
cd "$ROOT"

# --- 4. verifier + OTS proofs ------------------------------------------
cp docs/phase5-close/SHA256SUMS-final.txt docs/phase5-close/SHA256SUMS-final.txt.ots \
   docs/phase5-close/SHA256SUMS.txt docs/phase5-close/SHA256SUMS.txt.ots \
   capsule/verify/
cp scripts/capsule-verify.sh capsule/verify.sh
chmod +x capsule/verify.sh

cp capsule-README.md capsule/README.md
SRC_COMMIT=$(git rev-parse HEAD 2>/dev/null || echo unknown)
sed -i "s/at a recorded commit/at commit \`$SRC_COMMIT\`/" capsule/README.md

cat > capsule/OPERATOR-STEPS.md <<EOF
# Operator steps — publishing the capsule (~2 minutes)

The agent's credential proxy cannot create or push external repos, so
the final publish is manual:

1. Create the PUBLIC repo **yoheinakajima/synthetic-players-capsule**
   in the GitHub UI (empty — no README/license autogeneration).
2. From a checkout of the private repo:
   \`\`\`bash
   git clone capsule.bundle capsule-pub   # fresh history, single commit
   cd capsule-pub
   git remote add origin git@github.com:yoheinakajima/synthetic-players-capsule.git
   git push -u origin main
   \`\`\`
   (Or: unpack capsule.tar.gz into a new folder, git init + commit + push.)
3. Optional: create a release on the capsule repo and drag
   \`capsule.tar.gz\` onto it as a downloadable archive.
4. Tell the agent it is public — it will rerun the anonymous-clone
   verification (raw links included) and commit the transcript.

Built from private-repo commit \`$SRC_COMMIT\` by scripts/build-capsule.sh.
EOF

# --- 5. capsule-wide sums -----------------------------------------------
( cd capsule && find . -type f ! -name SHA256SUMS.capsule -print0 \
    | sort -z | xargs -0 sha256sum > SHA256SUMS.capsule )

# --- 6. fresh-history bundle + tarball ------------------------------------
rm -rf /tmp/capsule-git capsule.bundle capsule.tar.gz
cp -r capsule /tmp/capsule-git
( cd /tmp/capsule-git && git init -q -b main \
    && git -c user.name="synthetic-players" -c user.email="capsule@localhost" \
       add -A \
    && git -c user.name="synthetic-players" -c user.email="capsule@localhost" \
       commit -q -m "synthetic-players public reproduction capsule (from private commit $SRC_COMMIT)" \
    && git bundle create "$ROOT/capsule.bundle" main )
tar -czf capsule.tar.gz capsule
sha256sum capsule.bundle capsule.tar.gz > capsule-SHA256SUMS.txt

echo "capsule built: $(du -sh capsule | cut -f1); bundle $(du -h capsule.bundle | cut -f1); tar $(du -h capsule.tar.gz | cut -f1)"
