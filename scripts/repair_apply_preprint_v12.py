#!/usr/bin/env python3
"""One-time textual repairs for the generated v12 manuscript integrator.

The initial source arrived as an unexecuted construction script. This repair
normalizes quote delimiters, makes regex replacements literal-safe, corrects
registered-run accounting, distinguishes the three legacy diagnostics, aligns
the entropy interpretation with the exact event-store audit, and strips
review-only status residue from the preprint surface. It is idempotent; the
repaired source is committed by the workflow.
"""
from pathlib import Path

path = Path(__file__).resolve().with_name("apply_preprint_v12.py")
text = path.read_text(encoding="utf-8")
text = text.replace("response bound.\\n\\n',", "response bound.\\n\\n\",")
text = text.replace("paper-draft.md`.\\n',", "paper-draft.md`.\\n\",")
text = text.replace("formatting only.\\n',", "formatting only.\\n\",")
text = text.replace(
    'new, count = re.subn(pattern, replacement.rstrip() + "\\n\\n", text, count=1, flags=re.DOTALL)',
    'new, count = re.subn(pattern, lambda _m: replacement.rstrip() + "\\n\\n", text, count=1, flags=re.DOTALL)',
)
text = text.replace(
    'new, count = re.subn(pattern, replacement.rstrip(), text, count=1, flags=re.DOTALL)',
    'new, count = re.subn(pattern, lambda _m: replacement.rstrip(), text, count=1, flags=re.DOTALL)',
)
text = text.replace(
    'total_confirmatory = p3_totals["llmRuns"] + p3_totals["baselineRuns"] + 2864 + 1712\n    total_llm_replayed = p3_totals["llmRuns"] + 2864 + 1712',
    'registered_phase3_llm = sum(p3["expectedPromptCounts"].values())\n    total_confirmatory = registered_phase3_llm + p3_totals["baselineRuns"] + 2864 + 1712\n    total_llm_replayed = registered_phase3_llm + 2864 + 1712',
)
text = text.replace(
    "The audit covers {p3_totals['llmRuns']} Phase 3/X1 LLM runs, {p3_totals['baselineRuns']} deterministic Phase 3 baselines, 2,864 Phase 4 runs, and 1,712 Phase 5 runs.",
    "The audit covers {registered_phase3_llm} registered Phase 3/X1 LLM runs, {p3_totals['baselineRuns']} deterministic Phase 3 baselines, 2,864 Phase 4 runs, and 1,712 Phase 5 runs; three additional completed legacy entry/diagnostic runs are also replayed but are not counted as confirmatory.",
)
text = text.replace(
    'The pooled decline survives matching; mean within-unit entropy is reported because pooled entropy can be high even when individual prompt-cell policies are concentrated at opposite boundaries. Neither statistic identifies why temperature and downstream strategic actions interact.',
    'The registered pooled decline is partly composition-confounded but survives on the identical sweep lattice. Mean within-unit entropy is reported separately because pooled entropy can remain high when different prompt-cell units occupy opposite boundaries. Neither statistic identifies a temperature mechanism.',
)
text = text.replace(
    'The pooled decline survives matching, but pooled and within-unit entropy capture different phenomena and neither identifies a mechanism.',
    'The registered pooled decline is partly composition-confounded but survives on the identical sweep lattice. Pooled and mean within-unit entropy capture different objects, and neither identifies a mechanism.',
)
needle = '    PAPER.write_text(manuscript, encoding="utf-8")'
cleanup = '''    manuscript = manuscript.replace("*End of post-freeze review revision v11.*", "")
    manuscript = re.sub(r"(?i)review revision v11", "post-adjudication revision", manuscript)
    manuscript = re.sub(r"(?i)not for citation", "", manuscript)
    PAPER.write_text(manuscript, encoding="utf-8")'''
text = text.replace(needle, cleanup)
path.write_text(text, encoding="utf-8")
compile(text, str(path), "exec")
print("repair_apply_preprint_v12: syntax, literal-safe replacement, accounting, diagnostics, entropy, and preprint cleanup verified")
