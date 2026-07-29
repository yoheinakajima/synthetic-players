# Operator steps — publishing the capsule (~2 minutes)

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

Built from private-repo commit `694aba1f36a0d68e0e9759679a2698b748c530ad` by scripts/build-capsule.sh.
