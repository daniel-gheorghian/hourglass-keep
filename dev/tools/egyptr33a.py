# egyptr33a.py [new.html] [old.html] [--inv] [--measure]: round 33a's pictures and numbers (owner after v78, floor 16: "again the jump
# animation: I still think the prince is raised too high, the arc of the jump has a too high apex. Compare to the original PoP animation"),
# into egypt_themes/:
#   r33a_jump.png  for each kind of jump the bot makes (one each, floors 3, 4 and 6, seed 1: a level running jump, a long one caught at the far
#                  lip, a running jump to a ledge a storey up, a standing jump, the standing low leap): PoP 1989 (its own sprites, SDLPoP's
#                  seqtbl.c runjump/standjump, scaled to his height) | v78 | round 33a as onion skins (every 3rd game frame, later darker),
#                  the drawn crown's path (green) and its apex (a green line, the px over the standing crown), the standing crown (dashed)
#   r33a.json      the numbers: per kind, the drawn crown, head centre, hip and lowest sole's apex over the take-off floor and over the standing
#                  (and running) figure; with --inv also every running and standing jump the bot makes on floors 1-27, seed 1, grouped
# --measure prints the numbers only. old.html defaults to hk_v78_release.html (here or in the main checkout's dev/tools), else git's v78.
# The PoP sprites are read from ref/pop1/ (or HK_POP1): SDLPoP's KID images (fNNN_resMMM.png, bottom-anchored at Char.y), local only.
# Run from dev/tools. CMU mocap (mocap.cs.cmu.edu, NSF EIA-0196217): 127_21, 13_11, 09_01.
import os, sys, json, glob, subprocess, tempfile, shutil, collections, statistics as st
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
import egyptr26c as E
import egyptr32 as R32

HERE = os.path.dirname(os.path.abspath(__file__))
args = [x for x in sys.argv[1:] if not x.startswith('--')]
INV = '--inv' in sys.argv
MEASURE = '--measure' in sys.argv
NEW = os.path.abspath(args[0] if args else os.path.join(HERE, '..', 'hourglass-keep.html'))
OUTD = os.path.join(HERE, 'egypt_themes')
POP = R32.POP
_d = HERE
while not glob.glob(os.path.join(POP, 'f*_res*.png')) and os.path.dirname(_d) != _d:   # (in a git worktree: the main checkout's local copy)
    _d = os.path.dirname(_d)
    POP = os.path.join(_d, 'dev', 'tools', 'ref', 'pop1')
R32.POP = POP
INK, TXT, DIM = E.INK, E.TXT, E.DIM
S = 3
KINDS = [('run level', 'running jump, level (floor 3)', 'runjump'),
         ('run caught lip', 'long running jump, caught at the far lip (floor 4)', 'runjump'),
         ('run ledge-up', 'running jump to a ledge a storey up (floor 4)', 'runjump'),
         ('stand level', 'standing jump (floor 3)', 'standjump'),
         ('stand low down', 'standing low leap under a ceiling, down a storey (floor 6)', 'standjump')]
FLOORS = (3, 4, 6)


def old_src(tmp):
    if len(args) > 1:
        return os.path.abspath(args[1])
    for d in (HERE, '/home/user/hourglass-keep/dev/tools'):
        f = os.path.join(d, 'hk_v78_release.html')
        if os.path.exists(f):
            return f
    fn = os.path.join(tmp, '_v78.html')
    open(fn, 'w', encoding='utf-8').write(subprocess.run(['git', 'show', '3f7fe77:dev/hourglass-keep.html'], cwd=HERE, capture_output=True, text=True, check=True).stdout)
    return fn


def prep(src, tmp, tag):
    s = open(src, encoding='utf-8').read()
    i = s.find('window.__HK={')
    fn = os.path.join(tmp, '_r33a_%s.html' % tag)
    open(fn, 'w', encoding='utf-8').write(s[:i] + 'window.__J32={livePose};' + s[i:])
    return fn


# the drawn figure's heights: the hip, the head's centre, the crown (1.25 head radii over it) and the lowest sole, as drawFigureHD places them
# (P.yo, the pose's turn rot about the hip, its oy, the squash about the feet)
GEOJS = r"""()=>{window.__geo=function(H,P){const lp=__J32.livePose(P,P.pose),s=H.skel(lp),ro=lp.rot||0,c=Math.cos(ro),sn=Math.sin(ro);
  const sq=P.lk&&Math.abs(P.lk.sq-1)>0.004?P.lk.sq:1,b=P.y-s.hipH+(P.yo||0);const Y=v=>{const y=v[0]*sn+v[1]*c+(lp.oy||0);return b+s.hipH+(y-s.hipH)*sq;};
  const hd=Y(s.hd);return {lp,hip:Y([0,0]),hd,crown:hd-1.25*H.LEN.hd,sole:Math.max(Y(s.fF),Y(s.fB))};};}"""

# the bot plays floor n; the first jump of each kind is kept with 30 frames before and 24 after, and the standing and running baselines
TRACE = r"""([n,sd])=>{const out={},base={stand:[],run:[]};let ring=[],cur=null,post=0;
 const r=runBot(n,sd,{fight:false,stop:H=>{const p=H.P;if(!p||!p.pose)return false;const g=__geo(H,p);
  if((p.state==='stand'&&p.t>0.6)||(p.state==='run'&&p.t>0.8))base[p.state].push([p.y-g.crown,p.y-g.hd,p.y-g.hip]);
  const lk=p.lk||{};const f={st:p.state,t:p.t,x:p.x,y:p.y,yo:p.yo||0,face:p.face,gt:H.gameTime,crown:g.crown,hd:g.hd,hip:g.hip,sole:g.sole,
    sq:lk.sq||1,cw:lk.cw||0,cwy:lk.cwy||0,p:Object.assign({},g.lp)};
  if(cur){cur.fr.push(f);if(p.state!=='air'&&!cur.end){cur.end=p.state;cur.dy=p.y-cur.jy;post=0;}
    if(cur.end&&++post>=24){const c=cur;cur=null;const k=c.kind+(c.low?' low':'')+' '+(c.end==='hang'?(Math.abs(c.dy)<8?'ledge-up':'caught lip'):c.end==='swing'?'swing bar':Math.abs(c.dy)<8?'level':c.dy>0?'down':'up');
      if(!c.kick&&!out[k])out[k]=c;}
    else if(p.jumpKind==='kick'||p.jumpKind==='wall'||p.plant)cur.kick=true;}
  else if(p.state==='air'&&(p.jumpKind==='run'||p.jumpKind==='stand')){cur={n,sd,kind:p.jumpKind,low:!!p.lowJump,jx:p.jx,jy:p.jy,jK:p.jK,jS:p.jS,face:p.face,fr:ring.slice(),i0:ring.length};cur.fr.push(f);}
  ring.push(f);if(ring.length>30)ring.shift();
  return false;}});return {out,base};}"""

# every running and standing jump the bot makes on a floor: its kind and the drawn apexes over the take-off floor
INVJS = r"""([n,sd])=>{const J=[];let cur=null;
 runBot(n,sd,{fight:false,stop:H=>{const p=H.P;if(!p||!p.pose)return false;const g=__geo(H,p);
  if(!cur&&p.state==='air'&&(p.jumpKind==='run'||p.jumpKind==='stand'))cur={kind:p.jumpKind,low:!!p.lowJump,jy:p.jy,jK:p.jK,box:0,crown:-1e9,hd:-1e9,hip:-1e9,sole:-1e9,kick:false};
  if(cur){if(p.jumpKind==='kick'||p.jumpKind==='wall'||p.plant)cur.kick=true;
   if(p.state==='air'){cur.box=Math.max(cur.box,cur.jy-p.y);for(const k of ['crown','hd','hip','sole'])cur[k]=Math.max(cur[k],cur.jy-g[k]);}
   else{cur.end=p.state;cur.dy=p.y-cur.jy;J.push(cur);cur=null;}}
  return false;}});return J;}"""

DRAW = r"""([fr,S,x0,y0,W,Hh,jy,lines])=>{const H=__HK,L=H.L;H.GFX().hd=true;const cv=document.createElement('canvas');cv.width=W*S;cv.height=Hh*S;const c=cv.getContext('2d');c.scale(S,S);c.translate(-x0,-y0);
  c.fillStyle='#e9dfcc';c.fillRect(x0,y0,W,Hh);
  const r=Math.floor((jy-1)/64);for(let cc=Math.floor(x0/32);cc<=Math.floor((x0+W)/32);cc++)for(let rr=r-2;rr<=r+1;rr++){const b=L.base[rr*L.cols+cc],X=cc*32,Y=rr*64;
    if(b===2){c.fillStyle='#8a7a62';c.fillRect(X,Y,32,64);}else if(b===1){c.fillStyle='#b9a888';c.fillRect(X,Y+60,32,4);c.fillStyle='#8a7a62';c.fillRect(X,Y+64,32,6);}
    else if(rr===r&&!H.solidBelow(cc,rr)){c.fillStyle='#3a3028';c.fillRect(X,Y+60,32,44);}}
  for(let g=1;g<=10;g++){c.strokeStyle='rgba(60,50,40,.16)';c.lineWidth=0.3;c.beginPath();c.moveTo(x0,jy-g*8);c.lineTo(x0+W,jy-g*8);c.stroke();}
  const n=fr.length;fr.forEach((f,i)=>{const o={hasSword:true,time:f.gt,yo:f.yo,sq:Math.abs(f.sq-1)>0.004?f.sq:undefined,vx:f.cw,vy:f.cwy};
    c.globalAlpha=0.22+0.78*(i+1)/n;H.figDraw(c,f.x,f.y,f.face,Object.assign(H.mk({}),f.p),H.PAL_HERO,o);});c.globalAlpha=1;
  c.lineWidth=0.6;c.strokeStyle='#1f9a55';c.beginPath();fr.forEach((f,i)=>{if(i)c.lineTo(f.x,f.crown);else c.moveTo(f.x,f.crown);});c.stroke();
  for(const [y,col,dash] of lines){c.strokeStyle=col;c.lineWidth=0.5;c.setLineDash(dash?[2,1.5]:[]);c.beginPath();c.moveTo(x0,y);c.lineTo(x0+W,y);c.stroke();}c.setLineDash([]);
  return cv.toDataURL('image/png');}"""

# PoP 1989, measured from the sprites (bottom-anchored at Char.y; the crown is the topmost hair pixel), Char.y's rise from seqtbl.c's dy;
# the hip is read by eye on each sprite (where the thighs leave the trunk), +-1 px. The kid stands 41 px (frame 15), runs 38-40 (7-14).
POPN = {'runjump': {'frames': [(38, 0, 41, 21), (39, 0, 43, 22), (40, 3, 39, 19), (41, 12, 27, 15), (42, 14, 26, 14), (43, 3, 34, 17), (44, 0, 32, 15)],
                    'air': (40, 41, 42, 43), 'base': 'run', 'crown0': 38.9, 'hip0': 20},
        'standjump': {'frames': [(22, 0, 33, 14), (23, 0, 34, 14), (24, 0, 33, 16), (25, 6, 26, 14), (26, 0, 26, 11)],
                      'air': (23, 24, 25), 'base': 'stand', 'crown0': 41, 'hip0': 21}}
POP_H = 41.0


def pop_numbers():
    o = {}
    for name, d in POPN.items():
        air = [f for f in d['frames'] if f[0] in d['air']]
        crown = max(f[1] + f[2] for f in air)
        hip = max(f[1] + f[3] for f in air)
        feet = max(f[1] for f in air)
        o[name] = {'crown': crown, 'crown_over_base': crown - d['crown0'], 'crown_over_stand': crown - POP_H, 'hip_over_base': hip - d['hip0'], 'feet': feet,
                   'scaled_51.5': {k: round(v * 51.5 / POP_H, 1) for k, v in (('crown_over_base', crown - d['crown0']), ('crown_over_stand', crown - POP_H), ('hip_over_base', hip - d['hip0']), ('feet', feet))}}
    return o


def numbers(c, base):
    jy = c['jy']
    air = [f for f in c['fr'] if f['st'] == 'air']
    ap = {k: max(jy - f[k] for f in air) for k in ('crown', 'hd', 'hip', 'sole')}
    ap['box'] = max(jy - f['y'] for f in air)
    o = {'jK': c['jK'], 'jS': c['jS'], 'apex': {k: round(v, 1) for k, v in ap.items()},
         'over_stand': {k: round(ap[k] - base['stand'][i], 1) for i, k in enumerate(('crown', 'hd', 'hip'))},
         'over_run': {k: round(ap[k] - base['run'][i], 1) for i, k in enumerate(('crown', 'hd', 'hip'))}}
    return o


def trace(b, src):
    got, B = {}, {'stand': [], 'run': []}
    for n in FLOORS:
        pg = E.page(b, src)
        pg.evaluate(GEOJS)
        r = pg.evaluate(TRACE, [n, 1])
        for k, v in r['out'].items():
            got.setdefault(k, v)
        for k in B:
            B[k] += r['base'][k]
        if pg.errs:
            print('errors', n, pg.errs[:2])
        pg.close()
    base = {k: [st.median(q[i] for q in v) for i in range(3)] for k, v in B.items()}
    return got, base


def inventory(b, src):
    J = []
    for n in range(1, 28):
        pg = E.page(b, src)
        pg.evaluate(GEOJS)
        J += pg.evaluate(INVJS, [n, 1])
        pg.close()
    G = collections.defaultdict(list)
    for j in J:
        if j['kick']:
            continue
        dy = j['dy']
        e = ('ledge-up' if abs(dy) < 8 else 'caught lip') if j['end'] == 'hang' else 'swing bar' if j['end'] == 'swing' else 'level' if abs(dy) < 8 else 'down' if dy > 0 else 'up'
        G['%s%s %s' % (j['kind'], ' low' if j['low'] else '', e)].append(j)
    return {k: {'n': len(v), **{q: round(st.median(x[q] for x in v), 1) for q in ('box', 'crown', 'hd', 'hip', 'sole')}, 'crown_max': round(max(x['crown'] for x in v), 1)} for k, v in sorted(G.items())}


def pop_onion(name, h, every=1):
    """R32.pop_onion with the crown's apex (green) and the standing crown (dashed) marked"""
    im = R32.pop_onion(name, h)
    k = h / POP_H
    base = h + 14
    d = ImageDraw.Draw(im)
    n = pop_numbers()[name]
    for y, col in ((base - POP_H * k, (120, 90, 60)), (base - n['crown'] * k, (31, 154, 85))):
        for x in range(0, im.width, 6):
            d.line([(x, y), (x + (6 if col[1] == 154 else 3), y)], fill=col)
    return im


def panel(pg, c, base, n):
    jy = c['jy']
    fr = c['fr'][max(0, c['i0'] - 8):]
    air = [i for i, f in enumerate(fr) if f['st'] == 'air']
    fr = fr[:air[-1] + 10]
    sel = [f for i, f in enumerate(fr) if i % 3 == 0 or (i and f['st'] != fr[i - 1]['st'])]
    x0 = min(f['x'] for f in fr) - 30
    x1 = max(f['x'] for f in fr) + 34
    top = min(f['crown'] for f in fr if f['st'] == 'air')
    lines = [[jy - base['stand'][0], '#7a5a3c', True], [top, '#1f9a55', False]]
    pg.evaluate("([n,sd])=>{__P.load(n,sd);__HK.GFX().hd=true;}", [n, 1])
    im = E.img(pg.evaluate(DRAW, [sel, S, x0, jy - 92, x1 - x0, 104, jy, lines]))
    return im, jy - top - base['stand'][0]


def main():
    os.makedirs(OUTD, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix='r33a', dir=HERE)
    J = {'pop': pop_numbers()}
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            srcs = {'v78': prep(old_src(tmp), tmp, 'v78'), 'r33a': prep(NEW, tmp, 'r33a')}
            T = {}
            for tag, src in srcs.items():
                got, base = trace(b, src)
                T[tag] = (got, base)
                J[tag] = {'base_stand': [round(v, 1) for v in base['stand']], 'base_run': [round(v, 1) for v in base['run']],
                          'kinds': {k: numbers(got[k], base) for k, _, _ in KINDS if k in got}}
                if INV:
                    J[tag]['inventory'] = inventory(b, src)
            json.dump(J, open(os.path.join(OUTD, 'r33a.json'), 'w'), indent=1)
            print('PoP 1989 (px of a 41 px kid; and scaled to 51.5 px):', json.dumps(J['pop']))
            for tag in ('v78', 'r33a'):
                print('%s baselines (crown, head centre, hip over the floor): standing %s running %s' % (tag, J[tag]['base_stand'], J[tag]['base_run']))
                for k, v in J[tag]['kinds'].items():
                    print('  %-16s k %.2f apex %s over standing %s over running %s' % (k, v['jK'] or 1, json.dumps(v['apex']), json.dumps(v['over_stand']), json.dumps(v['over_run'])))
                for k, v in J[tag].get('inventory', {}).items():
                    print('  inv %-18s %s' % (k, json.dumps(v)))
            if MEASURE:
                return
            rows = []
            for key, lab, popseq in KINDS:
                imgs = [pop_onion(popseq, int(51.5 * S))]
                tit = ['PoP 1989 (seqtbl.c %s, every tick; crown apex %+.1f px of 41 over standing)' % (popseq, J['pop'][popseq]['crown_over_stand'])]
                for tag in ('v78', 'r33a'):
                    got, base = T[tag]
                    if key not in got:
                        continue
                    pg = E.page(b, srcs[tag])
                    im, ov = panel(pg, got[key], base, got[key]['n'])
                    pg.close()
                    imgs.append(im)
                    tit.append('%s: crown apex %+.1f px over standing' % ('v78' if tag == 'v78' else 'round 33a', ov))
                Hh = max(i.height for i in imgs)
                row = Image.new('RGB', (sum(i.width for i in imgs) + 20, Hh + 22), INK)
                x = 0
                for t, im in zip(tit, imgs):
                    row.paste(im, (x, 20))
                    ImageDraw.Draw(row).text((x + 4, 4), t, fill=TXT)
                    x += im.width + 10
                rows.append((lab, row))
            W = max(r.width for _, r in rows)
            out = Image.new('RGB', (W, sum(r.height + 20 for _, r in rows) + 46), INK)
            d = ImageDraw.Draw(out)
            d.text((6, 6), 'Round 33a: the jump\'s apex (owner: "the prince is raised too high, the arc of the jump has a too high apex. Compare to the original PoP"). '
                   'Onion skins every 3rd frame; green: the crown\'s path and apex; dashed: the standing crown.', fill=TXT)
            d.text((6, 22), 'The hit box flies the same arc in both builds (24.2 px running, 16.8 standing); only the drawn figure is lowered: D = k ap sin^2(pi t/T), '
                   'on the arc for a catch.', fill=DIM)
            y = 46
            for lab, r in rows:
                d.text((6, y + 2), lab, fill=DIM)
                out.paste(r, (0, y + 18))
                y += r.height + 20
            out.save(os.path.join(OUTD, 'r33a_jump.png'), optimize=True)
            print('wrote', os.path.join(OUTD, 'r33a_jump.png'), out.size)
            b.close()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    main()
