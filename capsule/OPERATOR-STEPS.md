# Operator steps — publishing the capsule (~2 minutes)

> **SUPERSEDED (2026-07-29): the main repo is going public with capsule/ committed in-tree — no separate capsule repo is needed; kept for the record.**

The agent's credential proxy cannot create or push external repos, so
the final publish is manual:

1. Create the PUBLIC repo **yoheinakajima/synthetic-players-capsule**
   in the GitHub UI (empty — no README/license autogeneration).
2. From a checkout of the private repo:
   ```bash
   git clone capsule.bundle capsule-pub   # fresh history, single commit
   cd capsule-pub
   git remote add origin git@github.com:yoheinakajima/synthetic-players-capsule.git
   git push -u origin main
   ```
   (Or: unpack capsule.tar.gz into a new folder, git init + commit + push.)
3. Optional: create a release on the capsule repo and drag
   `capsule.tar.gz` onto it as a downloadable archive.
4. Tell the agent it is public — it will rerun the anonymous-clone
   verification (raw links included) and commit the transcript.

Built from private-repo commit `ddf4e8d55542db7fc3d766f17f0374835e63432c` by scripts/build-capsule.sh.
