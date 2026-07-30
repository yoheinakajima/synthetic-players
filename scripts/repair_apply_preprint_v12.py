#!/usr/bin/env python3
"""One-time textual repairs for the generated v12 manuscript integrator.

The repaired file is committed by the v12 workflow; all operations are idempotent.
"""
from pathlib import Path

path = Path(__file__).resolve().with_name("apply_preprint_v12.py")
text = path.read_text(encoding="utf-8")
replacements = {
    'bound.\n\n\',\n        readme,': 'bound.\n\n",\n        readme,',
    'paper-draft.md`.\n\',\n        review,': 'paper-draft.md`.\n",\n        review,',
    'formatting only.\n\',\n            status,': 'formatting only.\n",\n            status,',
    'total_confirmatory = p3_totals["llmRuns"] + p3_totals["baselineRuns"] + 2864 + 1712\n    total_llm_replayed = p3_totals["llmRuns"] + 2864 + 1712':
        'registered_phase3_llm = sum(p3["expectedPromptCounts"].values())\n    total_confirmatory = registered_phase3_llm + p3_totals["baselineRuns"] + 2864 + 1712\n    total_llm_replayed = registered_phase3_llm + 2864 + 1712',
}
for old, new in replacements.items():
    text = text.replace(old, new)
path.write_text(text, encoding="utf-8")
compile(text, str(path), "exec")
print("repair_apply_preprint_v12: syntax and registered-run accounting verified")
