# egyptr36.py [png|gif|all] [html]: round 36a's pictures, the Crossing (owner: an interlude at each change of theme; research in
# dev/INTERLUDE_RESEARCH.md). Run from dev/tools; writes into egypt_themes/ (untracked):
#   r36a_dunes.png  the dune crossings (The Blue Chambers, The Foggaras of Garama, The Pyramids of Napata) at every hour they come in
#                   floors 1-180, three moments each (the start, the gust, at the doorway), Torchlight over Classic
#   r36a_all.png    every theme's crossing (the nine not yet built play the plain stub), one frame each, Torchlight | Classic
#   r36a_cross.gif  one crossing played through the game's own input (Right held: the walk, then the run; the gust; into the doorway;
#                   the entry), Torchlight
# The scene is stepped by hand (crossStep at 60 Hz, frozen clock) so the pictures are the same every run.
import io, os, sys
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
WHAT = a[0] if a and a[0] in ('png', 'gif', 'all') else 'all'
a = [x for x in a if x not in ('png', 'gif', 'all')]
SRC = os.path.abspath(a[0] if a else os.path.join(HERE, '..', 'hourglass-keep.html'))
OUT = os.path.join(HERE, 'egypt_themes'); os.makedirs(OUT, exist_ok=True)
VP = {'width': 852, 'height': 393}
INK = (20, 16, 24)

BEGIN = r'''([n,mode])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;H.S.set.lightMode=mode;H.S.set.cross=true;H.S.started=true;
  H.startLevel(n-1,-1,true);H.levelComplete();document.getElementById('bNext').click();const c=H.CR;if(!c)return {err:'no crossing on '+n};
  if(H.GLP)H.GLP.pipe=false;return {name:H.themeName(n),set:c.set,look:c.look,tod:c.tod};}'''
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

run()
