---
name: Replit environment quirks
description: Platform behaviors that cost real debugging time — background process lifecycle in agent shell calls
---

# Replit environment quirks

**Background processes die when the shell call returns.** Launching
`nohup script > log 2>&1 &` inside an agent shell command does not survive the
command finishing — the process group is torn down, nohup notwithstanding, and
the script dies silently (log shows only its first lines, no error).

**Why:** a 400-item backfill launched this way died ~1 second in; the log
looked "stalled" but the process was simply gone. The foreground rerun took
only ~60s.

**How to apply:** run long scripts in the foreground of a shell call with an
adequate timeout; make them idempotent/resumable and invoke repeatedly if they
might exceed the 5-minute cap; use a workflow for anything genuinely
long-running.
