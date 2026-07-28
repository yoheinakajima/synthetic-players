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

**`setsid nohup … &` does not fix it.** The double-detached process survives
the launching shell call by ~10–40 seconds, then is reaped anyway (cgroup-level
cleanup): the log freezes mid-stream with no error line and `ps` shows nothing.
The reliable detachment mechanism is a **console workflow** wrapping a one-shot
command: `node runner.mjs 2>&1 | tee -a /tmp/x.log; tail -f /dev/null`. The
`tail -f` hold keeps the workflow "running" after the runner exits, so the
platform never auto-restarts it — critical when a crashed runner's retry loop
could re-spend real API budget. Remove the workflow when the job is done.

**Resumable runners must also handle orphaned `pending` rows.** A runner dying
between "create row" and "start run" leaves a pending row that no server-side
work will ever advance. Treat pending (created-but-never-executed) as
re-runnable via the idempotent create → run path; only actively `running` rows
stay claimed as in-flight.

**Server-side work outlives a killed client.** When a shell-call timeout kills
a script mid-HTTP-request, the Express handler keeps running and usually
completes (rows land minutes later). A resumable runner that only checks
"completed" state will re-create the in-flight item → duplicate data.

**Why:** a study runner killed at the 5-min cap left one run in flight; the
next invocation saw it "not completed", created a second experiment for the
same design slot, and both finished — a duplicate replicate needing an
outcome-blind exclusion rule after the fact.

**How to apply:** resumable scripts must treat any non-failed row (pending/
running/completed) as claiming its slot; only a failed row frees it. Log
in-flight items instead of retrying them.

**`gitPush` requires a remote named `origin`.** Repls whose GitHub repo was
connected via the git pane get a `subrepl-<id>` remote; the push callback fails
with NO_REMOTE / UNKNOWN_REMOTE even though a valid GitHub remote exists.

**How to apply:** `git remote add origin <same URL>` — the callback then pushes
with platform-injected credentials (no PAT, no token handling in scripts).

**The whole container can restart under you mid-run.** All workflows die
simultaneously and the active shell call fails with "SERVER unexpectedly
disconnected"; anything dispatched by a workflow at that instant is killed
mid-flight (server-side too — unlike the shell-timeout case above, the engine
dies with the client, leaving a partial run with no terminal event).

**How to apply:** workflow-hosted dispatch loops must persist resume state
before every request (at-most-once marker + append-only event store +
reconcile path); treat "killable at any instant" as the design contract.

**AI-proxy gemini RPM binds on sustained multi-round bursts.** Back-to-back
multi-call episodes at ~190 calls/min drew terminal 429s (proxy retries 3×
then fails); ~30–40 calls/min with a 6 s inter-run gap runs clean. gpt-4.1
traffic at the same volumes never bound. Pace gemini dispatch and use a single
bounded backoff-retry (~120 s) on rate-limit refusals — the failed attempt is
terminal server-side once an HTTP response arrives, so one re-dispatch is safe
under at-most-once bookkeeping.

**Connector credentials from agent contexts.** For a freshly-attached
connection, sandbox `listConnections('<slug>')` can return `[]`. The shell-side
credential proxy (`$REPLIT_CONNECTORS_HOSTNAME/api/v2/connection`,
`X_REPLIT_TOKEN: "repl $REPL_IDENTITY"`) works instead — but its
`connector_names=` filter can return 0 items while the unfiltered list returns
the connection.

**How to apply:** fetch unfiltered with `include_secrets=true`, filter
client-side on `connector_name`. Keep the token inside the script process;
print only ids/urls/shas. The GitHub API can then create annotated tag objects,
releases, and upload assets directly — a release is the clean external
timestamp anchor for research artifacts.

**OpenTimestamps stamping works via `uvx --from opentimestamps-client ots
stamp <file>` with `LD_LIBRARY_PATH` pointed at a real openssl lib dir**
(find it via `ldd` on python's `_ssl` module — /nix/store globbing times
out). `python -m otsclient.ots` fails silently; python-bitcoinlib's ctypes
needs libssl.so.3 on the path. Four public calendars respond in seconds.

**Registering a workflow rewrites `.replit`**, which trips clean-worktree
gates in dispatch drivers and then a head-moved gate after you commit it.
**How to apply:** register workflows and commit `.replit` BEFORE starting a
clean-tree-gated driver; expect one unfreeze cycle otherwise.
