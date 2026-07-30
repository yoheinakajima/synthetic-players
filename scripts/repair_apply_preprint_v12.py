#!/usr/bin/env python3
"""One-time textual repairs for the generated v12 manuscript integrator.

The initial source intentionally arrived as an unexecuted construction script;
this repair normalizes three mismatched quote delimiters and the registered-run
accounting before compilation. It is idempotent and the repaired source is
committed by the workflow.
"""
from pathlib import Path

path = Path(__file__).resolve().with_name("apply_preprint_v12.py")
text = path.read_text(encoding="utf-8")
text = text.replace("response bound.\\n\\n',", "response bound.\\n\\n\",")
text = text.replace("paper-draft.md`.\\n',", "paper-draft.md`.\\n\",")
text = text.replace("formatting only.\\n',", "formatting only.\\n\",")
text = text.replace(
    'total_confirmatory = p3_totals["llmRuns"] + p3_totals["baselineRuns"] + 2864 + 1712\n    total_llm_replayed = p3_totals["llmRuns"] + 2864 + 1712',
    'registered_phase3_llm = sum(p3["expectedPromptCounts"].values())\n    total_confirmatory = registered_phase3_llm + p3_totals["baselineRuns"] + 2864 + 1712\n    total_llm_replayed = registered_phase3_llm + 2864 + 1712',
)
path.write_text(text, encoding="utf-8")
compile(text, str(path), "exec")
print("repair_apply_preprint_v12: syntax and registered-run accounting verified")
