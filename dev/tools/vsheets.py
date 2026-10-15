# vsheets.py: join the manifest fragments (parts/*.json), draw the contact sheets and write manifest.json / manifest.md.
# A sheet is every entry sharing a `sheet` key (grids of up to 9 cells, 3 columns, 2400 px wide; strips run the full width).
# Hand-written lines (gaps, visual problems noticed) live in notes.json next to the manifest: {"gaps":[...],"problems":[...]}.
import os, json, glob
from PIL import Image, ImageDraw
from vlib import OUT, font

parts = {}
for p in sorted(glob.glob(os.path.join(OUT, 'parts', '*.json'))):
    for e in json.load(open(p)):
        e['group'] = os.path.basename(p)[:-5]
        parts[e['id']] = e
ents = list(parts.values())
# drop entries whose image is gone
ents = [e for e in ents if os.path.exists(os.path.join(OUT, e['file']))]
json.dump(ents, open(os.path.join(OUT, 'manifest.json'), 'w'), indent=1)

# fold the small Classic comparison sheets of a family into one, and a few small sheets into their neighbours
MERGE = {'chamber-a': 'chamber-1', 'chamber-b': 'chamber-1', 'chamber-c': 'chamber-2', 'chamber-d': 'chamber-2', 'ui-portrait': 'ui-menus', 'fx-gradeoff': 'fx-misc', 'trap-lift': 'trap-snake'}
for e in ents:
    sh = e.get('sheet')
    if not sh:
        continue
    if e.get('light') == 'classic':
        for pre in ('trap-', 'fx-', 'arch-', 'guard-'):
            if sh.startswith(pre):
                e['sheet'] = pre + 'classic'
                break
    e['sheet'] = MERGE.get(e['sheet'], e['sheet'])
sheets = {}
for e in ents:
    if e.get('sheet'):
        sheets.setdefault(e['sheet'], []).append(e)
for f in glob.glob(os.path.join(OUT, 'sheets', '*.png')):
    os.remove(f)
made = []
F = font(24)
def chunk(grid):
    n = len(grid)
    k = max(1, -(-n // 12))
    per = -(-n // k) if n else 0
    return [grid[i * per:(i + 1) * per] for i in range(k)] if n else [[]]
jobs = []  # (name, entries, strips)
for key, lst in sheets.items():
    strips = [e for e in lst if e.get('kind') == 'strip']
    grid = [e for e in lst if e.get('kind') != 'strip']
    modes = [m for m in ('torch', 'classic') if any(e.get('light') == m for e in grid)]
    groups = [(m, [e for e in grid if e.get('light') == m]) for m in modes] if len(modes) > 1 else [('', grid)]
    other = [e for e in grid if e.get('light') not in ('torch', 'classic')]
    if len(modes) > 1 and other:
        groups.append(('x', other))
    for gi, (m, g) in enumerate(groups):
        cs = chunk(g)
        for ci, c in enumerate(cs):
            nm = key + ('-' + m if m else '') + ('' if len(cs) == 1 else '-%d' % (ci + 1))
            jobs.append((nm, c, strips if (gi == len(groups) - 1 and ci == len(cs) - 1) else []))
for name, ch, strips in jobs:
    if 1:
        ci = 0
        n = len(ch)
        cols = 4 if n > 9 else 2 if n in (2, 4) else 3 if n else 1
        cw = 2400 // cols if n else 2400
        rows = (n + cols - 1) // cols if n else 0
        cells = []
        for e in ch:
            im = Image.open(os.path.join(OUT, e['file'])).convert('RGB')
            ch_ = int(im.height * cw / im.width)
            cells.append((e, im.resize((cw, ch_), Image.LANCZOS)))
        rh = max([c[1].height for c in cells] or [0])
        sl = []
        if 1:
            for e in strips:
                im = Image.open(os.path.join(OUT, e['file'])).convert('RGB')
                sl.append((e, im.resize((2400, int(im.height * 2400 / im.width)), Image.LANCZOS)))
        H_ = rows * rh + sum(i.height for _, i in sl)
        S = Image.new('RGB', (2400, max(H_, 10)), (12, 10, 18))
        d = ImageDraw.Draw(S)
        for i, (e, im) in enumerate(cells):
            x, y = (i % cols) * cw, (i // cols) * rh
            S.paste(im, (x, y))
            cap = e['id']
            tw = d.textlength(cap, font=F)
            d.rectangle([x, y + im.height - 34, x + tw + 20, y + im.height], fill=(0, 0, 0))
            d.text((x + 8, y + im.height - 30), cap, fill=(255, 226, 140), font=F)
            d.rectangle([x, y, x + cw - 1, y + im.height - 1], outline=(40, 34, 52))
        y = rows * rh
        for e, im in sl:
            S.paste(im, (0, y)); y += im.height
        fn = os.path.join('sheets', name + '.png')
        S.save(os.path.join(OUT, fn), optimize=False)
        made.append((name, fn, [e['id'] for e in ch] + [e['id'] for e in strips]))

# ---- manifest.md
notes = json.load(open(os.path.join(OUT, 'notes.json'))) if os.path.exists(os.path.join(OUT, 'notes.json')) else {'gaps': [], 'problems': []}
nshots = sum(1 for e in ents if e.get('kind') == 'shot')
nstrips = sum(1 for e in ents if e.get('kind') == 'strip')
L = ['# Hourglass Keep: visual review manifest', '',
     'Phone landscape 844x390 CSS px at device scale 3 (2532x1170 images), touch controls and HUD in view unless an entry says "closeup".',
     'Themes: dungeon = The Cistern (floors 1-4), palace = Sandstone Halls (5-8), tile = Lapis Gallery (9-12), forge = Ember Forge (13-16), crypt = Jade Crypt (17-20); then they repeat (21+: "II").',
     'Lighting: torch = Torchlight (the default since v42), classic = the older lighting. Files: `shots/<id>.png`, `strips/<id>.png`, `sheets/<sheet>.png`.',
     'Regenerate: `cd dev/tools && python3 vshots.py <group> [id ...]` then `python3 vsheets.py` (group = vs_<group>.py; the repro column names it).', '',
     '**%d images (%d single shots, %d frame strips), %d contact sheets.**' % (len(ents), nshots, nstrips, len(made)), '']
L += ['## Contact sheets (read these first)', '', '| sheet | cells |', '|---|---|']
for name, fn, ids in made:
    L.append('| `%s` | %s |' % (fn, ', '.join(ids)))
L += ['', '## Gaps (checklist items not captured)', ''] + ['- ' + g for g in notes.get('gaps', [])]
L += ['', '## Visual problems noticed (not fixed)', ''] + ['- ' + g for g in notes.get('problems', [])]
topics = {}
for e in ents:
    topics.setdefault(e.get('topic', '?'), []).append(e)
L += ['', '## All images', '']
for t, lst in topics.items():
    L += ['### ' + t, '', '| id | file | floor | seed | theme | light | prince | what | reproduce |', '|---|---|---|---|---|---|---|---|---|']
    for e in lst:
        L.append('| %s | `%s` | %s | %s | %s | %s | %s%s | %s | `%s` |' % (e['id'], e['file'], e.get('floor', ''), e.get('seed', ''), e.get('theme', ''),
                 e.get('light', ''), e.get('state', ''), ('/' + e['jk']) if e.get('jk') else '', e.get('what', '').replace('|', '/'), e.get('repro', '')))
    L.append('')
open(os.path.join(OUT, 'manifest.md'), 'w').write('\n'.join(L))
print(len(ents), 'images', len(made), 'sheets')
