#!/usr/bin/env python3
"""Freeze review candidate file hashes; self-excludes manifest, not evidence."""
from pathlib import Path
import hashlib,json
J=Path(__file__).resolve().parents[1]
files=[p for p in sorted(J.rglob('*')) if p.is_file() and p.name!='package-manifest.json' and '__pycache__' not in p.parts]
out={'schema_version':1,'source_base':'62ab90beff1d291b069c87f13b6b6b3495171ddd','branch':'codex/jesa-prep-20261102','status':'review candidate, not approved submission','self_exclusion':'package-manifest.json; Git commit pins this manifest','files':[{'path':str(p.relative_to(J)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]}
(J/'package-manifest.json').write_text(json.dumps(out,indent=2)+'\n')
print('manifest files:',len(files))
