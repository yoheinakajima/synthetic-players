"""Close-seal gate — mechanizes "review first, seal last".

The Phase 5 close-out had to re-seal after an architect review found defects
in already-sealed files. This gate makes that failure mode impossible going
forward: the seal step REFUSES to run unless a review artifact exists and is
newer than every file being sealed.

Usage:
    uv run python engine/close_seal.py --files <list.txt> \
        --review <docs/reviews/xxx.md> --out <SHA256SUMS.txt> [--selftest]

  <list.txt>  one repo-relative path per line (# comments allowed)
  --review    the architect-review artifact covering the sealed set
  --out       the sums file to write (only written if the gate passes)

Gate predicate (all must hold, else exit 1 and nothing is written):
  G1  the review artifact exists and is non-empty;
  G2  every sealed file exists;
  G3  the review artifact's content-time is strictly newer than every sealed
      file's content-time. Content-time = last git commit time when the file
      is committed and unmodified in the worktree, else filesystem mtime —
      so a post-review edit to any sealed file (committed or not) re-opens
      the gate.
  G4  the review artifact is not itself in the sealed set.

After the gate passes, SHA256 sums are written in `sha256sum` format.
OTS stamping remains a separate, subsequent step.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(_HERE, "..", "..", ".."))


def content_time(path: str) -> float:
    """Git commit time if committed & clean in the worktree, else mtime."""
    rel = os.path.relpath(path, REPO)
    try:
        dirty = subprocess.run(
            ["git", "status", "--porcelain", "--", rel],
            cwd=REPO, capture_output=True, text=True, check=True).stdout.strip()
        if not dirty:
            out = subprocess.run(
                ["git", "log", "-1", "--format=%ct", "--", rel],
                cwd=REPO, capture_output=True, text=True, check=True).stdout.strip()
            if out:
                return float(out)
    except Exception:
        pass
    return os.path.getmtime(path)


def gate(files: list[str], review: str) -> list[str]:
    """Return list of violations (empty = gate passes)."""
    v: list[str] = []
    rpath = os.path.join(REPO, review)
    if not os.path.exists(rpath) or os.path.getsize(rpath) == 0:
        return [f"G1: review artifact missing or empty: {review} — no seal "
                f"without a review that covers the sealed set"]
    if review in files:
        v.append("G4: the review artifact is inside the sealed set — a review "
                 "cannot attest to itself")
    rt = content_time(rpath)
    for f in files:
        p = os.path.join(REPO, f)
        if not os.path.exists(p):
            v.append(f"G2: sealed file missing: {f}")
            continue
        ft = content_time(p)
        if ft >= rt:
            v.append(f"G3: {f} is newer than the review artifact "
                     f"({ft:.0f} >= {rt:.0f}) — it changed after review; "
                     f"re-review before sealing")
    return v


def write_sums(files: list[str], out: str) -> None:
    lines = []
    for f in sorted(files):
        h = hashlib.sha256(open(os.path.join(REPO, f), "rb").read()).hexdigest()
        lines.append(f"{h}  {f}")
    with open(os.path.join(REPO, out), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"sealed {len(files)} files -> {out}")


def selftest() -> int:
    import tempfile, time
    ok = True
    with tempfile.TemporaryDirectory(dir=REPO) as td:
        rel = os.path.relpath(td, REPO)
        sealed = os.path.join(td, "sealed.md")
        review = os.path.join(td, "review.md")
        open(sealed, "w").write("sealed content\n")
        # T1: no review artifact -> refuse
        r = gate([f"{rel}/sealed.md"], f"{rel}/review.md")
        t1 = bool(r) and r[0].startswith("G1")
        # T2: review OLDER than sealed file -> refuse (the Phase 5 incident)
        open(review, "w").write("review\n")
        os.utime(review, (time.time() - 3600,) * 2)
        r = gate([f"{rel}/sealed.md"], f"{rel}/review.md")
        t2 = any(x.startswith("G3") for x in r)
        # T3: review newer than every sealed file -> pass
        os.utime(review, None)
        os.utime(sealed, (time.time() - 3600,) * 2)
        r = gate([f"{rel}/sealed.md"], f"{rel}/review.md")
        t3 = not r
        # T4: post-review edit to a sealed file re-opens the gate
        time.sleep(0.01)
        open(sealed, "a").write("edited after review\n")
        r = gate([f"{rel}/sealed.md"], f"{rel}/review.md")
        t4 = any(x.startswith("G3") for x in r)
        # T5: review inside the sealed set -> refuse
        os.utime(sealed, (time.time() - 3600,) * 2)
        r = gate([f"{rel}/sealed.md", f"{rel}/review.md"], f"{rel}/review.md")
        t5 = any(x.startswith("G4") for x in r)
        for name, t in [("T1 no-review refuses", t1),
                        ("T2 stale review refuses (the incident)", t2),
                        ("T3 fresh review passes", t3),
                        ("T4 post-review edit re-opens gate", t4),
                        ("T5 self-attestation refuses", t5)]:
            print(("PASS  " if t else "FAIL  ") + name)
            ok = ok and t
    print("close_seal selftest:", "ALL PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--files")
    ap.add_argument("--review")
    ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if not (args.files and args.review and args.out):
        ap.print_help()
        return 2
    files = [ln.strip() for ln in open(os.path.join(REPO, args.files))
             if ln.strip() and not ln.strip().startswith("#")]
    violations = gate(files, args.review)
    if violations:
        print("SEAL REFUSED:")
        for v in violations:
            print(" -", v)
        return 1
    write_sums(files, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
