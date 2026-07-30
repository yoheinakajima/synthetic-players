#!/usr/bin/env python3
"""One-time textual repair for three quote delimiters in apply_preprint_v12.py.

The repaired file is committed by the v12 workflow; the operation is idempotent.
"""
from pathlib import Path

path = Path(__file__).resolve().with_name("apply_preprint_v12.py")
text = path.read_text(encoding="utf-8")
replacements = {
    'bound.\n\n\',\n        readme,': 'bound.\n\n",\n        readme,',
    'paper-draft.md`.\n\',\n        review,': 'paper-draft.md`.\n",\n        review,',
    'formatting only.\n\',\n            status,': 'formatting only.\n",\n            status,',
}
for old, new in replacements.items():
    text = text.replace(old, new)
path.write_text(text, encoding="utf-8")
compile(text, str(path), "exec")
print("repair_apply_preprint_v12: syntax verified")
