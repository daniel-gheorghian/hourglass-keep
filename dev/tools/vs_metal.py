# vs_metal.py: the Torchlight metal shader (unit MS) side by side: before (GLFX.metal off), each strength preset, and Classic.
#   python3 vs_metal.py [scene ...]          one sheet per scene in $VREVIEW_OUT/options/ (default: the scratchpad's ms folder)
#   python3 vs_metal.py strips               time strips: the saw spinning, a gate rising past a lamp (all variants stacked)
#   MSDBG=1 also saves the half-resolution metal mask of each scene (mask-<scene>.png)
# The frame is not advanced between variants, so every column shows the same instant.
import os, sys, io, base64
from vlib import Rig, font, OUT
from PIL import Image, ImageDraw

VARS = [('before', 'torch', None), ('subtle', 'torch', 'subtle'), ('satin (default)', 'torch', 'satin'), ('glossy', 'torch', 'glossy'), ('Classic', 'classic', None)]
NEAR = "L.torches.some(t=>!t.broken&&t.r===o.r&&Math.abs(t.c-o.c)<=%d)"
BOX = "V.box(s.c*32-%d,(s.r+1)*64-%d,s.c*32+%d,(s.r+1)*64+%d)"
SAWB = "(()=>{const o=V.dynAt(s);const x=H.sawX(o.f,H.gameTime);return V.box(x-60,(s.r+1)*64-80,x+60,(s.r+1)*64+8)})()"
SCENES = {
    # id: (floors, seed0, finder (JS body), clip (JS, s = spot), setup after settling (JS), what)
    'gate-lamp': ([4, 5, 6], 9801, "return V.dynSpot(L,'gate','o.f.latch&&' + %r,2)" % (NEAR % 3), BOX % (34, 135, 100, 8), '', 'A gate near a lamp'),
    'gate-lamp-forge': ([16, 15, 17], 9801, "return V.dynSpot(L,'gate',%r,2)" % (NEAR % 3), BOX % (34, 135, 100, 8), '', 'A gate near a lamp (Forge, iron)'),
    'jaws': ([4, 5, 22], 9000, "return V.dynSpot(L,'chomp',%r,2)" % (NEAR % 4), BOX % (34, 135, 100, 8), "const o=V.dynAt(s);o.f.off=-H.gameTime+o.f.per*0.5", 'Guillotine jaws, open'),
    'jaws-palace': ([8, 9], 9031, "return V.dynSpot(L,'chomp',%r,2)" % (NEAR % 4), BOX % (34, 135, 100, 8), "const o=V.dynAt(s);o.f.off=-H.gameTime+o.f.per*0.5", 'Guillotine jaws, open (Sandstone)'),
    'saw': ([8, 7], 9501, "return V.dynSpot(L,'saw',null,4)", SAWB, '', 'Floor saw'),
    'saw-crypt': ([20, 19], 9522, "return V.dynSpot(L,'saw',null,4)", SAWB, '', 'Floor saw (Jade Crypt)'),
    'pendulum': ([10, 11], 9300, "return V.dynSpot(L,'pend',null,4)", BOX % (60, 175, 110, 6), '', 'Pendulum blade'),
    'lift-chains': ([7, 12, 18], 10700, "const f=L.lifts.find(f=>f.t==='lift'&&L.torches.some(t=>!t.broken&&Math.abs(t.c-f.sc)<=4&&t.r>=f.rT&&t.r<=f.rB)&&V.near(f.sc,f.rT,3));return f&&Object.assign(V.near(f.sc,f.rT,3),{c:f.sc})", BOX % (100, 170, 110, 70), '', 'Counterweight lift: chains, pulley, mouth gates'),
    'chain-lift': ([9, 14, 19], 10800, "const f=L.lifts.find(f=>f.t==='chain'&&L.torches.some(t=>!t.broken&&Math.abs(t.c-f.sc)<=4&&t.r>=f.rT&&t.r<=f.rB)&&V.near(f.sc,f.rT,3));return f&&Object.assign(V.near(f.sc,f.rT,3),{c:f.sc})", BOX % (100, 170, 130, 70), '', 'Chain-loop lift'),
    'sword': ([6, 9, 13, 5, 8], 11000, "const g=H.G.find(g=>{const r=Math.floor((g.y-1)/64);return g.alive&&!g.skel&&V.sb(Math.floor(g.x/32)-2,r)&&L.torches.some(t=>!t.broken&&t.r===r&&Math.abs(t.c*32+16-g.x)<100)});if(!g)return null;const r=Math.floor((g.y-1)/64);return {x:g.x-58,r,face:1,c:Math.floor(g.x/32),gi:H.G.indexOf(g)}",
              BOX % (100, 120, 80, 14), "const P=H.P,g=H.G[s.gi];P.sword=true;P.foe=g;P.state='garde';g.state='garde';g.face=-1;for(let k=0;k<20;k++){P.inv=1e9;H.tick(1);}", 'Swords and a helmet in a fight'),
}


def variant(rig, light, preset):
    rig.ev("([l,p])=>{H.GLFX.metal=!!p;if(p)H.msPreset(p);V.light(l);V.clean();V.R();return 1}", [light, preset])


def warm(rig):  # a dozen frames first: the relief pass copies the rooms in view one a frame
    rig.ev("()=>{V.light('torch');for(let k=0;k<12;k++)V.R();return 1}")


def sheet(rig, sid, box, title, path, z=3):
    warm(rig)
    tiles = []
    for lab, light, pre in VARS:
        variant(rig, light, pre)
        tiles.append((rig.png(box), lab))
    ims = [Image.open(io.BytesIO(b)).convert('RGB') for b, _ in tiles]
    ims = [im.resize((im.width * z // 3, im.height * z // 3), Image.LANCZOS) for im in ims]
    w, h, bar = ims[0].width, ims[0].height, 40
    sh = Image.new('RGB', (w * len(ims) + 6 * (len(ims) - 1), h + bar * 2), (18, 14, 24))
    d = ImageDraw.Draw(sh)
    d.text((8, 8), title, fill=(232, 196, 127), font=font(24))
    for i, (im, (_, lab)) in enumerate(zip(ims, tiles)):
        sh.paste(im, (i * (w + 6), bar))
        d.text((i * (w + 6) + 8, bar + h + 8), lab, fill=(240, 240, 240), font=font(22))
    sh.save(path)
    rig.ev("()=>{H.GLFX.metal=true;H.msPreset('satin');return 1}")


def mask(rig, path):
    url = rig.ev("()=>{H.GLFX.metal=true;V.light('torch');V.R();return H.MS.c?H.MS.c.toDataURL():''}")
    if url:
        open(path, 'wb').write(base64.b64decode(url.split(',')[1]))


def scene(rig, sid):
    floors, seed0, pred, clip, setup, what = SCENES[sid]
    r = None
    for n in floors:
        r = rig.find(n, seed0, pred, 120, guards=(sid == 'sword'))
        if r:
            break
    if not r:
        print('NOT FOUND', sid)
        return
    sp = r['spot']
    rig.place(sp, inv=True)
    rig.settle(60)
    if setup:
        rig.ev('(s)=>{' + setup + ';return 1}', sp)
    rig.render('torch')
    box = rig.ev('(s)=>' + clip, sp)
    sheet(rig, sid, box, '%s  (floor %d, seed %d)' % (what, n, r['seed']), os.path.join(OUT, 'options', sid + '.png'))
    if os.environ.get('MSDBG'):
        mask(rig, os.path.join(OUT, 'options', 'mask-' + sid + '.png'))
    print('ok', sid, n, r['seed'])


def strip(rig, sid, n, seed0, pred, clip, title, nfr, ticks, setup=None, step=None):
    r = rig.find(n, seed0, pred, 120)
    if not r:
        print('NOT FOUND', sid); return
    sp = r['spot']
    rig.place(sp, inv=True)
    rig.settle(60)
    if setup:
        rig.ev('(s)=>{' + setup + ';return 1}', sp)
    rig.render('torch')
    box = rig.ev('(s)=>' + clip, sp)
    warm(rig)
    rows = []
    for lab, light, pre in VARS[:4]:
        rows.append([])
    for i in range(nfr):
        for k, (lab, light, pre) in enumerate(VARS[:4]):
            variant(rig, light, pre)
            rows[k].append(Image.open(io.BytesIO(rig.png(box))).convert('RGB'))
        if step:
            rig.ev('(s)=>{' + step + ';return 1}', sp)
        else:
            rig.settle(ticks)
    w, h, lw = rows[0][0].width, rows[0][0].height, 190
    sh = Image.new('RGB', (lw + nfr * (w + 4), 44 + len(rows) * (h + 4)), (18, 14, 24))
    d = ImageDraw.Draw(sh)
    d.text((8, 8), title + '  (floor %d, seed %d)' % (n, r['seed']), fill=(232, 196, 127), font=font(24))
    for k, row in enumerate(rows):
        d.text((8, 44 + k * (h + 4) + h // 2 - 12), VARS[k][0], fill=(240, 240, 240), font=font(20))
        for i, im in enumerate(row):
            sh.paste(im, (lw + i * (w + 4), 44 + k * (h + 4)))
    sh.save(os.path.join(OUT, 'options', sid + '.png'))
    rig.ev("()=>{H.GLFX.metal=true;H.msPreset('satin');return 1}")
    print('ok strip', sid, n, r['seed'])


def strips(rig):
    strip(rig, 'strip-saw', 8, 9501, "return V.dynSpot(L,'saw',null,4)", "(()=>{const o=V.dynAt(s);const x=H.sawX(o.f,H.gameTime);return V.box(x-40,(s.r+1)*64-60,x+40,(s.r+1)*64+4)})()",
          'The saw spinning (frames 1/60 s apart; the sheen should hold still while teeth and holes turn)', 6, 1,
          setup="const o=V.dynAt(s);o.f.x0=o.f.x1=H.sawX(o.f,H.gameTime)")  # (held in place so only the spin shows)
    strip(rig, 'strip-gate', 4, 9801, "return V.dynSpot(L,'gate','o.f.latch&&' + %r,2)" % (NEAR % 3), BOX % (34, 135, 100, 8),
          'A gate rising past a lamp (open 0, .2, .4, .6, .8)', 5, 0, setup="V.dynAt(s).f.open=0", step="const f=V.dynAt(s).f;f.open=Math.min(1,f.open+0.2)")


if __name__ == '__main__':
    os.makedirs(os.path.join(OUT, 'options'), exist_ok=True)
    args = sys.argv[1:]
    rig = Rig('metal')
    try:
        if args == ['strips']:
            strips(rig)
        else:
            for sid in (args or list(SCENES)):
                scene(rig, sid)
    finally:
        if rig.errs:
            print('PAGE ERRORS', rig.errs[:3])
        rig.br.close()
