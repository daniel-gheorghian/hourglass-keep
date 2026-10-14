#!/usr/bin/env python3
"""Point the dev tools at this checkout.

The tools in dev/tools were written in a cloud session where the game source lived at
/home/claude/hourglass-keep.html and the tools sat in a scratch folder. Run this once on a
new machine (from anywhere): it rewrites those absolute paths in dev/tools to this
checkout's own paths. Running it again changes nothing. macOS, Linux or WSL.
"""
import pathlib

DEV = pathlib.Path(__file__).resolve().parent
REPO = DEV.parent
OLD = [  # longest first
    ('/tmp/claude-0/-home-claude-hourglass-keep/f01bc65f-8e08-5e8f-8f80-4fcb704e8720/scratchpad', (DEV / 'tools').as_posix()),
    ('/home/claude/hourglass-keep.html', (DEV / 'hourglass-keep.html').as_posix()),
    ('/home/claude/hourglass-keep/', REPO.as_posix() + '/'),
]
TEXT = {'.py', '.js', '.html', '.json', '.txt', '.md', '.sh'}

changed = 0
for p in (DEV / 'tools').rglob('*'):
    if not p.is_file() or p.suffix not in TEXT:
        continue
    s = p.read_text(encoding='utf-8', errors='surrogateescape')
    t = s
    for a, b in OLD:
        t = t.replace(a, b)
    if t != s:
        p.write_text(t, encoding='utf-8', errors='surrogateescape')
        changed += 1
print(f'{changed} files now point at {REPO.as_posix()}')
