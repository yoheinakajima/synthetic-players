#!/usr/bin/env python3
"""Allow and disclose the three completed Phase 3 legacy entry/diagnostic runs.

The event store contains the 320 registered Phase 3/X1 LLM runs plus three
additional completed legacy runs using the same prompt IDs. The verifier audits
all of them while retaining the registered prompt counts as the confirmatory
subset.
"""
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "artifacts" / "api-server" / "engine" / "phase3_replay_audit.py"
text = path.read_text(encoding="utf-8")
old = '''    if len(targets) != EXPECTED_LLM_RUNS:
        raise AssertionError(f"Phase 3 LLM run count {len(targets)} != expected {EXPECTED_LLM_RUNS}")
    if dict(counts) != PHASE3_PROMPTS:
        raise AssertionError(f"Phase 3 prompt counts {dict(counts)} != expected {PHASE3_PROMPTS}")
    return targets, counts
'''
new = '''    shortfalls = {
        prompt: expected - counts.get(prompt, 0)
        for prompt, expected in PHASE3_PROMPTS.items()
        if counts.get(prompt, 0) < expected
    }
    if shortfalls:
        raise AssertionError(f"Phase 3 registered-run shortfalls: {shortfalls}")
    extras = {
        prompt: counts.get(prompt, 0) - expected
        for prompt, expected in PHASE3_PROMPTS.items()
        if counts.get(prompt, 0) > expected
    }
    if sum(extras.values()) != 3:
        raise AssertionError(
            f"expected exactly three disclosed legacy entry/diagnostic runs, got {extras}"
        )
    return targets, counts
'''
if old in text:
    text = text.replace(old, new)
text = text.replace(
    '"scope": "Phase 3 main study plus X1 and the P3-C3 zero-LLM baseline",',
    '"scope": "all completed Phase 3 legacy-prompt runs: the 320 registered main/X1 LLM runs, three entry/diagnostic runs, and the P3-C3 zero-LLM baseline",',
)
text = text.replace(
    '"expectedPromptCounts": PHASE3_PROMPTS,\n        "observedPromptCounts": dict(prompt_counts),',
    '"expectedPromptCounts": PHASE3_PROMPTS,\n        "observedPromptCounts": dict(prompt_counts),\n        "registeredLlmRuns": EXPECTED_LLM_RUNS,\n        "additionalLegacyLlmRuns": len(llm_runs) - EXPECTED_LLM_RUNS,',
)
text = text.replace(
    'This closes the former capsule boundary: all prospectively confirmatory Phase 3 LLM runs, the result-informed but prospectively registered X1 runs, and the deterministic P3-C3 baseline are now covered by a public zero-call verifier.',
    'This closes the former capsule boundary: the 320 registered Phase 3/X1 LLM runs, three additional completed legacy entry/diagnostic runs, and the deterministic P3-C3 baseline are covered by a public zero-call verifier.',
)
path.write_text(text, encoding="utf-8")
compile(text, str(path), "exec")
print("repair_phase3_audit_v12: registered subset and three legacy extras distinguished")
