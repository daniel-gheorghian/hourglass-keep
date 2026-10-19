# egyptr18b.py [new.html] [old.html] [outdir]: round 18b's pictures for egypt_themes.html: the swing rigged in rope and timber (was a
# metal pole on link chains), and every other chain in the game turned to rope, before (old.html, default ../_r18a.html, made with
# git show 0934781:dev/hourglass-keep.html) and after, in the game at the phone's resolution (crops of the 1704 px canvas):
#  r18b_swing.png   the swing before and after, two themes, Torchlight and Classic, 1:1, and a smaller crop at 2x (smoothed)
#  r18b_swing.gif   pumping and the throw, before and after, Torchlight, 0.1 s a frame
#  r18b_rigs.png    the rig in the twelve themes' fibres and timbers (Torchlight), 1:1
#  r18b_chains.png  the other chains, before and after: the pendulum's pivot, Siwa's hanging lamp, a fallen lamp's cord (free and
#                   tile style), the fallen lantern, the Cistern's and the Forge's backdrops
# Writes r18b.json (floors and seeds used, errors). Run from dev/tools.
import base64, io, json, os, sys
from playwright.sync_api import sync_playwright
from PIL import Image
import egyptr12 as R12
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(a[0] if len(a) > 0 else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = os.path.abspath(a[1] if len(a) > 1 else os.path.join(HERE, '..', '_r18a.html'))
OUT = a[2] if len(a) > 2 else os.path.join(HERE, 'egypt_themes')
R12.OUT = OUT
SWINGS = [6, 17]   # the Halls of the West, the Green Hall of Osiris
SWING = r"""([n,A,th0])=>{const H=__HK;let L,o,SD;const roofed=q=>{for(let r=q.r-1;r>=0;r--)if(L.base[r*L.cols+q.c]===2)return r>=1;return false;}; // (a ceiling under the level's top edge, so the anchor is in view)
 for(let sd=1;sd<=40&&!o;sd++){SD=7100+sd;L=__P.load(n,SD);o=L.dyn.find(q=>q.f.t==='bar'&&roofed(q));}
 if(!o)return null;const f=o.f,D=L.base[o.r*L.cols+o.c+2]===L.base[o.r*L.cols+o.c]?1:-1,p=H.P;H.S.learned.swing=1;
 p.x=f.x;p.y=f.y+57;p.vx=0;p.vy=0;p.state='air';p.autoGrab=true;p.face=D;p.fallY=p.y;p.inv=1e9;f.ps=0;f.pw=0;H.tick(1);
 p.swTh=th0;p.swOm=Math.sqrt(Math.max(0,2*(Math.cos(th0)-Math.cos(A))))*H.SW_W;H.cam.snap=true;H.tick(1);p.swGl=-9;H.banner=null;__P.up(30);
 return {n,seed:SD,D,fx:f.x,fy:f.y,pv:f.pv,look:L.theme.look,name:H.themeName(n)};}"""
AT = r"""([x,y])=>__P.scr(x,y)"""
STEP = r"""(k)=>{const H=__HK;H.tick(k);H.banner=null;__P.up(30);}"""
# (the camera raised 50 px for the picture, so the rope's anchor under the lintel is in view; put back after)
UP = r"""()=>{__P.up=k=>{const H=__HK;H.cam.y-=k;H.cam.gy-=k;__P.draw();H.cam.y+=k;H.cam.gy+=k;};
 __P.look=(x,y)=>{const H=__HK,cx=H.cam.x,cy=H.cam.y;H.cam.x=x-208;H.cam.y=y-96;__P.draw();const r=__P.scr(x,y);H.cam.x=cx;H.cam.y=cy;return r;};}"""
# (__P.look: the view centred on a world point for one picture, without moving the game's camera; viewW is about 416 at this size)
PEND = r"""()=>{const H=__HK;for(let n=10;n<60;n++)for(const sd of [801,802]){const L=__P.load(n,sd);const o=L.dyn.find(q=>q.f.t==='pend');if(!o)continue;
 let r=o.r-1;while(r>=0&&L.base[r*L.cols+o.c]!==2)r--;if(r<1)continue;
 __P.stand(o.c-3,o.r,1);return {n,seed:sd,name:H.themeName(n),xy:__P.look(o.c*32+16,(r+1)*64+4)};}return null;}"""
SCAR = r"""([look,free])=>{const H=__HK;const fl=H.floorsOf(look);for(const n0 of fl)for(let n=n0;n<n0+4;n++)for(let sd=1;sd<=8;sd++){const L=__P.load(n,700+sd);
   const t=L.torches.find(q=>!q.broken&&(!!H.lampFree(q))===free&&H.solidBelow(q.c,q.r)&&H.solidBelow(q.c+1,q.r)&&H.solidBelow(q.c-1,q.r));if(!t)continue;
   t.broken=true;H.clearRooms();__P.stand(t.c+3,t.r,-1);return {n,seed:700+sd,name:H.themeName(n),xy:__P.look(t.c*32+16,free?t.r*64-36:(t.r+1)*64-14)};}return null;}"""
BG = r"""([look])=>{const H=__HK,ls=H.bgLayers(look,0),c0=ls[0].c||ls[0],c=document.createElement('canvas');c.width=c0.width;c.height=c0.height;const g=c.getContext('2d');
 const sk=H.BGART[look].sky,gr=g.createLinearGradient(0,0,0,c.height);sk.forEach((s,i)=>gr.addColorStop(i/(sk.length-1),s));g.fillStyle=gr;g.fillRect(0,0,c.width,c.height);
 for(const l of ls)g.drawImage(l.c||l,0,0);return c.toDataURL('image/png');}"""


def up(im, k=2):
    return im.resize((im.width * k, im.height * k), Image.LANCZOS)


def lab(im, t):
    return R12.label(im, t)


def b64(u):
    return Image.open(io.BytesIO(base64.b64decode(u.split(',')[1]))).convert('RGB')


if __name__ == '__main__':
    J = {'errors': []}
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        P = {(t, m): R12.page(b, s, m) for t, s in (('before', OLD), ('after', NEW)) for m in ('torch', 'classic')}
        for pg in P.values():
            pg.evaluate(UP)
        # ---- the swing, still: before and after, two themes, both modes
        t1, t2 = [], []
        for n in SWINGS:
            for m in ('torch', 'classic'):
                for t in ('before', 'after'):
                    pg = P[(t, m)]; q = pg.evaluate(SWING, [n, 0.5, 0.3]); im = R12.shot(pg)
                    xy = pg.evaluate(AT, [q['fx'] + 6, q['pv'] + 50])
                    t1.append(lab(R12.crop(im, xy, 300, 480), '%s, %s, %s, 1:1' % (q['name'], m, t)))
                    t2.append(lab(up(R12.crop(im, pg.evaluate(AT, [q['fx'], q['pv'] + 14]), 150, 140)), '%s, %s, 2x' % (m, t)))
                J.setdefault('swing', []).append([n, q['seed']])
        R12.stack([R12.grid(t1, 4), R12.grid(t2, 4)]).save(os.path.join(OUT, 'r18b_swing.png'))
        # ---- pumping and the throw, before and after (Torchlight)
        cols = []
        for t in ('before', 'after'):
            for n in SWINGS[:1]:
                pt = P[(t, 'torch')]; q = pt.evaluate(SWING, [n, 0.3, 0.0]); fr = []
                for k in range(34):
                    if k == 22:
                        pt.evaluate("()=>{const H=__HK,p=H.P;let i=0;while(i<120&&!(p.swOm>0&&p.swTh>=0&&p.swTh<0.15)){H.tick(1);i++;}H.setKey('kb','j',true);H.tick(1);H.setKey('kb','j',false);}")
                    elif k < 22:
                        pt.evaluate("()=>{const H=__HK,p=H.P,d=p.swOm>=0?(p.face>0?'r':'l'):(p.face>0?'l':'r');H.setKey('kb',d,true);H.tick(1);H.setKey('kb',d,false);}")
                    pt.evaluate(STEP, 5)
                    xy = pt.evaluate(AT, [q['fx'] + q['D'] * 18, q['pv'] + 48])
                    fr.append(lab(R12.crop(R12.shot(pt), xy, 560, 440), '%s, %s' % (q['name'], t)))
                cols.append(fr)
        R12.gif([R12.grid([c[k] for c in cols], 2).convert('P', palette=Image.ADAPTIVE, colors=128) for k in range(len(cols[0]))], 'r18b_swing.gif', 100)
        # ---- the rig in each theme's fibre and timber
        pn = P[('after', 'torch')]; tl = []; J['rigs'] = []
        looks = pn.evaluate("()=>__HK.THEMES.map(t=>t.look)")
        for lk in looks:
            got = None
            for n0 in pn.evaluate("l=>__HK.floorsOf(l)", lk):
                for n in range(max(n0, 6), n0 + 4):
                    q = pn.evaluate(SWING, [n, 0.5, 0.25])
                    if q and q['look'] == lk:
                        got = q; break
                if got:
                    break
            if not got:
                J['errors'].append('no bar for ' + lk); continue
            xy = pn.evaluate(AT, [got['fx'] + 6, got['pv'] + 32])
            tl.append(lab(R12.crop(R12.shot(pn), xy, 260, 300), '%s (%d)' % (got['name'], got['n'])))
            J['rigs'].append([lk, got['n'], got['seed']])
        R12.grid(tl, 6).save(os.path.join(OUT, 'r18b_rigs.png'))
        # ---- the other chains, before and after (Torchlight above, Classic below for the in-game ones)
        rows = []
        def pair(label, js, args, cw, ch, modes=('torch',)):
            out = []
            for m in modes:
                for t in ('before', 'after'):
                    pg = P[(t, m)]; q = pg.evaluate(js, args)
                    if not q:
                        J['errors'].append('none: ' + label); return None
                    out.append(lab(up(R12.crop(R12.shot(pg), q['xy'], cw, ch)), '%s: %s, %s, %s, 2x' % (label, q['name'], m, t)))
                J.setdefault('chains', []).append([label, q.get('n'), q.get('seed')])
            return out
        tiles = []
        for label, js, args, cw in (('pendulum pivot', PEND, None, 200), ('fallen lamp, in an opening', SCAR, ['nun', True], 200),
                                    ('fallen lamp, tile style', SCAR, ['blue', False], 200)):
            r = pair(label, js, args, cw, 130, ('torch', 'classic'))
            if r:
                tiles += r
        # Siwa's lamp hanging in an opening (egyptprop's finder)
        for m in ('torch', 'classic'):
            for t in ('before', 'after'):
                pg = P[(t, m)]; ti = pg.evaluate("()=>__HK.THEMES.findIndex(t=>t.look==='shali')")
                lq = pg.evaluate(R12.PC['LAMPF'], [ti])['free']
                pg.evaluate(R12.PC['SHOWLAMP'], [lq, True, True, False])
                xy = pg.evaluate("q=>__P.look(q.c*32+16,q.r*64-27)", lq)
                tiles.append(lab(up(R12.crop(R12.shot(pg), xy, 150, 240)), 'hanging lamp, Siwa, %s, %s, 2x' % (m, t)))
        R12.stack([R12.grid(tiles[:-4], 4), R12.grid(tiles[-4:], 4)]).save(os.path.join(OUT, 'r18b_chains.png'))
        bgs = []
        for lk, nm in (('nun', 'the Waters of Nun'), ('meroe', 'the Furnaces of Meroe')):
            for t in ('before', 'after'):
                im = b64(P[(t, 'torch')].evaluate(BG, [lk]))
                im = im.crop((0, 0, min(im.width, 640), im.height))
                bgs.append(lab(im, 'backdrop, %s, %s' % (nm, t)))
        R12.grid(bgs, 2).save(os.path.join(OUT, 'r18b_bgropes.png'))
        for pg in P.values():
            J['errors'] += pg.errs
        json.dump(J, open(os.path.join(OUT, 'r18b.json'), 'w'), indent=1)
        print(json.dumps(J))
        b.close()
