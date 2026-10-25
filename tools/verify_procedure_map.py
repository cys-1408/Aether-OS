"""Check the procedure(2).md required file map against the repo tree."""
import re, os, glob, sys

doc = open('documents/procedure (2).md', encoding='utf-8').read()

# Lines look like: -   `AetherOS->x->y->file.z` --- description
reqs = []
for m in re.finditer(r'`AetherOS->([^`]+)`', doc):
    p = m.group(1)
    if p not in reqs:
        reqs.append(p)

print(f"required entries: {len(reqs)}")

missing = []
for p in reqs:
    parts = p.split('->')
    last = parts[-1]
    dirs = parts[:-1]
    # wildcards: filename may end in .*
    if last.endswith('.*'):
        stem = last[:-2]
        # any file in dirs starting with stem + '.'
        base = os.path.join(*dirs)
        cands = glob.glob(os.path.join(base, stem + '.*'))
        if not cands:
            missing.append(p)
        continue
    # exact-ish: allow alternate extensions e.g. .yml vs .yaml, .h vs .py etc.
    def exists(name):
        return os.path.exists(os.path.join(*dirs, name))
    ok = exists(last)
    if not ok:
        # try slug alternates in any dir level handled only for final name
        stem, _, ext = last.rpartition('.')
        alt_exts = {'yaml':'yml','yml':'yaml','h':'hpp','c':'cc','json':'json'}
        cands = glob.glob(os.path.join(*dirs, '*'))
        # accept if some file shares the stem regardless of extension
        if stem and any(os.path.basename(c).rpartition('.')[0] == stem for c in cands):
            continue
        # accept if some existing file contains the full name as substring base
        if any(last in os.path.basename(c) for c in cands):
            continue
        missing.append(p)

print(f"missing: {len(missing)}")
for p in sorted(missing):
    print("  MISSING:", p)
