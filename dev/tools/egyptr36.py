# egyptr36.py [png|gif|all] [html]: round 36a's pictures, the Crossing (owner: an interlude at each change of theme; research in
# dev/INTERLUDE_RESEARCH.md). Run from dev/tools; writes into egypt_themes/ (untracked):
#   r36a_dunes.png  the dune crossings (The Blue Chambers, The Foggaras of Garama, The Pyramids of Napata) at every hour they come in
#                   floors 1-180, three moments each (the start, the gust, at the doorway), Torchlight over Classic
#   r36a_all.png    every theme's crossing (the nine not yet built play the plain stub), one frame each, Torchlight | Classic
#   r36a_cross.gif  one crossing played through the game's own input (Right held: the walk, then the run; the gust; into the doorway;
#                   the entry), Torchlight
# Round 36b (dunes revised, the oasis):
#   r36b_dunes.png  before | after: every dune theme and hour, round 36a's page (git show 250c213, written to egypt_themes/r36b_base36a.html)
#                   against this one, at the start and in the gust, Torchlight and Classic rows
#   r36b_oasis.png  every oasis theme (Meroë's hafir, Kerma's Nile, Siwa's spring) at every hour it comes in floors 1-180, three moments
#                   (the start, the geese lifting off, at the doorway), Torchlight and Classic rows
#   r36b_oasis.gif  one oasis crossing (floor 13, Meroë at dusk) played through the game's own input, Torchlight
#   arguments: dunes36b | oasis | oasisgif | r36b (all three)
# Round 36c (the garden: West's pool, Osiris's Field of Reeds, Hawara's lake shore, Nun's papyrus marsh; fixes from the review of 36b):
#   r36c_garden.png  every garden theme at every hour it comes in floors 1-180, three moments (the start, the beat, at the doorway),
#                    Torchlight and Classic rows
#   r36c_garden.gif  one garden crossing (floor 5, the Halls of the West at dusk: the heron) played through the game's own input, Torchlight
#   r36c_fixes.png   before (round 36b's page, 87ab266, written to egypt_themes/r36c_base36b.html) | after, at twice the scale: the geese
#                    on Meroe's hafir and Kerma's Nile, resting and lifting off; Siwa's mudbrick garden walls
#   arguments: garden | gardengif | fixes36c | r36c (all three)
# The scene is stepped by hand (crossStep at 60 Hz, frozen clock) so the pictures are the same every run.
import io, os, subprocess, sys
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
KW = ('png', 'gif', 'all', 'dunes36b', 'oasis', 'oasisgif', 'r36b', 'garden', 'gardengif', 'fixes36c', 'r36c')
WHAT = a[0] if a and a[0] in KW else 'all'
a = [x for x in a if x not in KW]
SRC = os.path.abspath(a[0] if a else os.path.join(HERE, '..', 'hourglass-keep.html'))
OUT = os.path.join(HERE, 'egypt_themes'); os.makedirs(OUT, exist_ok=True)
VP = {'width': 852, 'height': 393}
INK = (20, 16, 24)

BEGIN = r'''([n,mode])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;H.S.set.lightMode=mode;H.S.set.cross=true;H.S.started=true;
  H.startLevel(n-1,-1,true);H.levelComplete();document.getElementById('bNext').click();const c=H.CR;if(!c)return {err:'no crossing on '+n};
  if(H.GLP)H.GLP.pipe=false;return {name:H.themeName(n),set:c.set,look:c.look,tod:c.tod,ov:c.ov||''};}'''
# put him at x (world px), with the clock at t; held: the walk's phase as if walking there; gust: seconds into the gust (or -1)
AT = r'''([x,t,gust,run])=>{const H=__HK,c=H.CR;c.x=x;c.t=t;c.gust=gust<0?-1:t-gust;c.hold=run?3:0;H.setKey('kb','r',true);
  for(let i=0;i<24;i++){H.crossStep(1/60);c.x=x;c.t=t;}H.setKey('kb','r',false);for(let k=0;k<16;k++)H.render();return {x:c.x,cx:c.cx,phase:c.phase};}'''
CSS = '.ctl,#bPause{visibility:hidden!important}'

def shot(pg):
    return Image.open(io.BytesIO(pg.screenshot())).convert('RGB')

def sheet(rows, labels, out, scale=0.5):
    w, h = rows[0][0].size; w2, h2 = int(w * scale), int(h * scale); n = max(len(r) for r in rows)
    S = Image.new('RGB', (n * (w2 + 4) + 4, len(rows) * (h2 + 18) + 4), INK); d = ImageDraw.Draw(S)
    for j, (r, lab) in enumerate(zip(rows, labels)):
        y = 4 + j * (h2 + 18); d.text((6, y), lab, fill=(230, 220, 200))
        for i, im in enumerate(r): S.paste(im.resize((w2, h2), Image.LANCZOS), (4 + i * (w2 + 4), y + 14))
    S.save(out); print('wrote', out)

def run():
    with sync_playwright() as p:
        b = p.chromium.launch(); errs = []
        def page():
            pg = b.new_page(viewport=VP, device_scale_factor=1)
            pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.goto('file://' + SRC); pg.wait_for_timeout(300); pg.add_style_tag(content=CSS); return pg
        if WHAT in ('png', 'all'):
            pg = page()
            fl = pg.evaluate('''()=>{const H=__HK,o={};for(let n=2;n<=180;n++){if(!H.crossDue(n))continue;const th=H.themeOf(n),k=th.look+':'+H.progOf(n).tod;if(!o[k])o[k]=n;}return o;}''')
            dunes = sorted([(k, n) for k, n in fl.items() if k.split(':')[0] in ('blue', 'foggara', 'napata')], key=lambda q: q[1])
            rows, labels = [], []
            for k, n in dunes:
                for mode in ('torch', 'classic'):
                    r = pg.evaluate(BEGIN, [n, mode]); row = []
                    for x, t, g in [(70, 1.2, -1), (340, 4.0, 1.2), (657, 8.0, -1)]:
                        pg.evaluate(AT, [x, t, g, 0]); row.append(shot(pg))
                    pg.evaluate('()=>__HK.crossEnd()'); rows.append(row); labels.append('floor %d  %s  (%s, %s)  %s' % (n, r['name'], r['set'], ['dusk', 'night', 'dawn'][r['tod']], mode))
            sheet(rows, labels, os.path.join(OUT, 'r36a_dunes.png'))
            firsts = {}
            for k, n in sorted(fl.items(), key=lambda q: q[1]):
                lk = k.split(':')[0]
                if lk not in firsts: firsts[lk] = n
            rows, labels = [], []
            for lk, n in sorted(firsts.items(), key=lambda q: q[1]):
                row = []
                for mode in ('torch', 'classic'):
                    r = pg.evaluate(BEGIN, [n, mode]); pg.evaluate(AT, [300, 3.0, -1, 0]); row.append(shot(pg)); pg.evaluate('()=>__HK.crossEnd()')
                rows.append(row); labels.append('floor %d  %s  (%s, %s)' % (n, r['name'], r['set'], ['dusk', 'night', 'dawn'][r['tod']]))
            sheet(rows, labels, os.path.join(OUT, 'r36a_all.png'), 0.4)
            pg.close()
        if WHAT in ('gif', 'all'):
            pg = page(); frames = []
            pg.evaluate(BEGIN, [21, 'torch'])
            # the game's own input, stepped by hand: 0.8 s waiting (the pad's cue), then Right held to the doorway, then the entry
            for i in range(900):
                held = i >= 48
                st = pg.evaluate('''(held)=>{const H=__HK;H.setKey('kb','r',held);if(H.CR){H.crossStep(1/60);H.crossStep(1/60);}else{H.tick(2);}
                  return {cr:!!H.CR,mode:H.mode,state:H.P.state};}''', held)
                if i % 3 == 0:
                    pg.evaluate('()=>__HK.render()'); frames.append(shot(pg).resize((426, 196), Image.LANCZOS))
                if not st['cr'] and st['state'] != 'enter': break
            out = os.path.join(OUT, 'r36a_cross.gif')
            frames[0].save(out, save_all=True, append_images=frames[1:], duration=100, loop=0); print('wrote', out, len(frames), 'frames')
            pg.close()
        print('errors', errs[:5]); b.close()

def run36b():
    tod = ['dusk', 'night', 'dawn']
    with sync_playwright() as p:
        b = p.chromium.launch(); errs = []
        def page(src):
            pg = b.new_page(viewport=VP, device_scale_factor=1)
            pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.goto('file://' + src); pg.wait_for_timeout(300); pg.add_style_tag(content=CSS); return pg
        def firsts(pg, looks):
            fl = pg.evaluate('''()=>{const H=__HK,o={};for(let n=2;n<=180;n++){if(!H.crossDue(n))continue;const th=H.themeOf(n),k=th.look+':'+H.progOf(n).tod;if(!o[k])o[k]=n;}return o;}''')
            return sorted([(k, n) for k, n in fl.items() if k.split(':')[0] in looks], key=lambda q: q[1])
        if WHAT in ('dunes36b', 'r36b'):
            base = os.path.join(OUT, 'r36b_base36a.html')
            if not os.path.exists(base):
                open(base, 'wb').write(subprocess.run(['git', 'show', '250c213:dev/hourglass-keep.html'], cwd=HERE, capture_output=True, check=True).stdout)
            pa, pb = page(base), page(SRC); rows, labels = [], []
            for k, n in firsts(pb, ('blue', 'foggara', 'napata')):
                for mode in ('torch', 'classic'):
                    row = []
                    for x, t, g in [(70, 1.2, -1), (340, 4.0, 1.2)]:
                        for pg in (pa, pb):
                            r = pg.evaluate(BEGIN, [n, mode]); pg.evaluate(AT, [x, t, g, 0]); row.append(shot(pg)); pg.evaluate('()=>__HK.crossEnd()')
                    rows.append(row); labels.append('floor %d  %s  (%s, %s)  %s:   36a | 36b at the start,   36a | 36b in the gust' % (n, r['name'], r['set'], tod[r['tod']], mode))
            sheet(rows, labels, os.path.join(OUT, 'r36b_dunes.png'), 0.42); pa.close(); pb.close()
        if WHAT in ('oasis', 'r36b'):
            pg = page(SRC); rows, labels = [], []
            for k, n in firsts(pg, ('meroe', 'deffufa', 'shali')):
                for mode in ('torch', 'classic'):
                    r = pg.evaluate(BEGIN, [n, mode]); row = []
                    for x, t, g in [(80, 1.2, -1), (360, 4.4, 0.9), (657, 9.0, -1)]:
                        pg.evaluate(AT, [x, t, g, 0]); row.append(shot(pg))
                    pg.evaluate('()=>__HK.crossEnd()'); rows.append(row); labels.append('floor %d  %s  (%s %s, %s)  %s' % (n, r['name'], r['set'], r['ov'], tod[r['tod']], mode))
            sheet(rows, labels, os.path.join(OUT, 'r36b_oasis.png'), 0.5); pg.close()
        if WHAT in ('oasisgif', 'r36b'):
            pg = page(SRC); frames = []
            pg.evaluate(BEGIN, [13, 'torch'])
            for i in range(900):
                held = i >= 30
                st = pg.evaluate('''(held)=>{const H=__HK;H.setKey('kb','r',held);if(H.CR){H.crossStep(1/60);H.crossStep(1/60);}else{H.tick(2);}
                  return {cr:!!H.CR,mode:H.mode,state:H.P.state};}''', held)
                if i % 3 == 0:
                    pg.evaluate('()=>__HK.render()'); frames.append(shot(pg).resize((426, 196), Image.LANCZOS))
                if not st['cr'] and st['state'] != 'enter': break
            out = os.path.join(OUT, 'r36b_oasis.gif')
            frames[0].save(out, save_all=True, append_images=frames[1:], duration=100, loop=0); print('wrote', out, len(frames), 'frames')
            pg.close()
        print('errors', errs[:5]); b.close()

def run36c():
    tod = ['dusk', 'night', 'dawn']
    with sync_playwright() as p:
        b = p.chromium.launch(); errs = []
        def page(src, dpr=1):
            pg = b.new_page(viewport=VP, device_scale_factor=dpr)
            pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.goto('file://' + src); pg.wait_for_timeout(300); pg.add_style_tag(content=CSS); return pg
        if WHAT in ('garden', 'r36c'):
            pg = page(SRC); rows, labels = [], []
            fl = pg.evaluate('''()=>{const H=__HK,o={};for(let n=2;n<=180;n++){if(!H.crossDue(n))continue;const th=H.themeOf(n),k=th.look+':'+H.progOf(n).tod;if(!o[k])o[k]=n;}return o;}''')
            for k, n in sorted([(k, n) for k, n in fl.items() if k.split(':')[0] in ('west', 'osiris', 'hawara', 'nun')], key=lambda q: q[1]):
                for mode in ('torch', 'classic'):
                    r = pg.evaluate(BEGIN, [n, mode]); row = []
                    for x, t, g in [(80, 1.2, -1), (360, 5.0, 1.5), (657, 9.0, -1)]:
                        pg.evaluate(AT, [x, t, g, 0]); row.append(shot(pg))
                    pg.evaluate('()=>__HK.crossEnd()'); rows.append(row); labels.append('floor %d  %s  (garden, %s)  %s:  the start | the beat (1.5 s on) | the doorway' % (n, r['name'], tod[r['tod']], mode))
            sheet(rows, labels, os.path.join(OUT, 'r36c_garden.png'), 0.5); pg.close()
        if WHAT in ('gardengif', 'r36c'):
            pg = page(SRC); frames = []
            pg.evaluate(BEGIN, [5, 'torch'])
            for i in range(900):
                held = i >= 30
                st = pg.evaluate('''(held)=>{const H=__HK;H.setKey('kb','r',held);if(H.CR){H.crossStep(1/60);H.crossStep(1/60);}else{H.tick(2);}
                  return {cr:!!H.CR,mode:H.mode,state:H.P.state};}''', held)
                if i % 3 == 0:
                    pg.evaluate('()=>__HK.render()'); frames.append(shot(pg).resize((426, 196), Image.LANCZOS))
                if not st['cr'] and st['state'] != 'enter': break
            out = os.path.join(OUT, 'r36c_garden.gif')
            frames[0].save(out, save_all=True, append_images=frames[1:], duration=100, loop=0); print('wrote', out, len(frames), 'frames')
            pg.close()
        if WHAT in ('fixes36c', 'r36c'):
            base = os.path.join(OUT, 'r36c_base36b.html')
            if not os.path.exists(base):
                open(base, 'wb').write(subprocess.run(['git', 'show', '87ab266:dev/hourglass-keep.html'], cwd=HERE, capture_output=True, check=True).stdout)
            pa, pb = page(base, 2), page(SRC, 2); rows, labels = [], []
            for n, x, clip, what in [(13, 360, (300, 150, 552, 150), "Meroe's hafir"), (25, 360, (250, 130, 602, 170), 'the Nile at Kerma')]:
                for mode in ('classic', 'torch'):
                    row = []
                    for t, g in [(4.0, -1), (5.6, 1.6)]:
                        for pg in (pa, pb):
                            r = pg.evaluate(BEGIN, [n, mode]); pg.evaluate(AT, [x, t, g, 0])
                            row.append(Image.open(io.BytesIO(pg.screenshot(clip={'x': clip[0], 'y': clip[1], 'width': clip[2], 'height': clip[3]}))).convert('RGB')); pg.evaluate('()=>__HK.crossEnd()')
                    rows.append(row); labels.append('floor %d  %s, the geese (%s):  36b | 36c resting,   36b | 36c lifting off (1.6 s on)' % (n, what, mode))
            for mode in ('classic', 'torch'):
                row = []
                for x in (200, 430):
                    for pg in (pa, pb):
                        pg.evaluate(BEGIN, [45, mode]); pg.evaluate(AT, [x, 3.0, -1, 0])
                        row.append(Image.open(io.BytesIO(pg.screenshot(clip={'x': 0, 'y': 120, 'width': 852, 'height': 150}))).convert('RGB')); pg.evaluate('()=>__HK.crossEnd()')
                rows.append(row); labels.append("floor 45  Siwa's mudbrick garden walls (%s):  36b | 36c, and further on 36b | 36c" % mode)
            rows = [[im.resize((int(im.size[0] * 0.5), int(im.size[1] * 0.5)), Image.LANCZOS) for im in r] for r in rows]
            S = Image.new('RGB', (max(sum(im.size[0] + 4 for im in r) for r in rows) + 4, sum(max(im.size[1] for im in r) + 18 for r in rows) + 4), INK); d = ImageDraw.Draw(S); y = 4
            for r, lab in zip(rows, labels):
                d.text((6, y), lab, fill=(230, 220, 200)); x = 4
                for im in r: S.paste(im, (x, y + 14)); x += im.size[0] + 4
                y += max(im.size[1] for im in r) + 18
            out = os.path.join(OUT, 'r36c_fixes.png'); S.save(out); print('wrote', out); pa.close(); pb.close()
        print('errors', errs[:5]); b.close()

if WHAT in ('garden', 'gardengif', 'fixes36c', 'r36c'): run36c()
elif WHAT in ('dunes36b', 'oasis', 'oasisgif', 'r36b'): run36b()
else: run()
