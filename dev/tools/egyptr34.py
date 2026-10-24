# egyptr34.py [new.html] [--measure] [--quick] [--bot]: round 34's pictures and numbers (owner after v79: "The standing jump is fine, the
# running jump is not: him tilting his head and rotating like that is not natural. The previous movement was fine, except the apex."),
# into egypt_themes/:
#   r34_runjump.png  for the running jumps the bot makes (floors 3, 4 and 6, seed 1: level, caught at the far lip, to a ledge a storey up, the
#                    low leap): v77 | v79 | round 34 as onion skins (every 3rd game frame, later darker; the crown's path and apex green, the
#                    standing crown dashed), then each build's frame strip of the level jump (every 2nd frame, the standing crown dashed, the
#                    drawn crown's apex green)
#   r34_runjump.gif  the level running jump in play, v77 | v79 | round 34, at half speed, the standing crown dashed
#   r34.json         the numbers: per build, the drawn crown (and head, hip) over standing for each kind (egyptr33a's measure), every running
#                    and standing jump on floors 1-27 seed 1 grouped (the median and highest crown over standing), the largest turn of the
#                    figure (rot) and head pitch (lean + rot + head, from upright, + forward) in a running jump's flight, scissoring (egyptr32's
#                    40 take-offs over the run's phases)
# --bot: the bot's frames (state, x, y, vx, vy, face, hp every game frame) and every standing jump's drawn pose (jumpPrep, air, the landing
# 'sl', P.pose, P.yo) on floors 1-27 (seeds 1 and 2; --quick seed 1), v79 against round 34: must be identical.
# Sources: hk_v77_release.html and hk_v79_release.html here (else git's 9ba4241 and b1e893e). Run from dev/tools. CMU mocap
# (mocap.cs.cmu.edu, NSF EIA-0196217): 09_01, 49_04 (the restored flight), 127_21, 13_11.
import os, sys, json, subprocess, tempfile, shutil, math, statistics as st
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
import egyptr26c as E
import egyptr32 as R32
import egyptr33a as R33

HERE = os.path.dirname(os.path.abspath(__file__))
args = [x for x in sys.argv[1:] if not x.startswith('--')]
MEASURE = '--measure' in sys.argv
QUICK = '--quick' in sys.argv
BOT = '--bot' in sys.argv
NEW = os.path.abspath(args[0] if args else os.path.join(HERE, '..', 'hourglass-keep.html'))
OUTD = os.path.join(HERE, 'egypt_themes')
INK, TXT, DIM = E.INK, E.TXT, E.DIM
S = 3
TAGS = ('v77', 'v79', 'r34')
NAME = {'v77': 'v77', 'v79': 'v79', 'r34': 'round 34'}
KINDS = [('run level', 'running jump, level (floor 3)'),
         ('run caught lip', 'long running jump, caught at the far lip (floor 4)'),
         ('run ledge-up', 'running jump to a ledge a storey up (floor 4)'),
         ('run low level', 'running low leap under a ceiling (floor 4)')]


def src_of(tag, tmp):
    if tag == 'r34':
        return NEW
    rel, rev = {'v77': ('hk_v77_release.html', '9ba4241'), 'v79': ('hk_v79_release.html', 'b1e893e')}[tag]
    for d in (HERE, '/home/user/hourglass-keep/dev/tools'):
        f = os.path.join(d, rel)
        if os.path.exists(f):
            return f
    fn = os.path.join(tmp, '_' + rel)
    open(fn, 'w', encoding='utf-8').write(subprocess.run(['git', 'show', rev + ':dev/hourglass-keep.html'], cwd=HERE, capture_output=True, text=True, check=True).stdout)
    return fn


def prep(src, tmp, tag):
    s = open(src, encoding='utf-8').read()
    i = s.find('window.__HK={')
    fn = os.path.join(tmp, '_r34_%s.html' % tag)
    open(fn, 'w', encoding='utf-8').write(s[:i] + 'window.__J32={livePose};' + s[i:])
    return fn


# every running jump's flight on a floor: the largest turn of the figure and pitch of the head and trunk (degrees from upright, + forward)
ROTJS = r"""([n,sd])=>{const J=[];let cur=null;
 runBot(n,sd,{fight:false,stop:H=>{const p=H.P;if(!p||!p.pose)return false;
  if(!cur&&p.state==='air'&&p.jumpKind==='run')cur={low:!!p.lowJump,rot:0,head:-9,headMin:9,trunk:-9};
  if(cur){if(p.state!=='air'){J.push(cur);cur=null;}
   else{const lp=__J32.livePose(p,p.pose),r=lp.rot||0;cur.rot=Math.max(cur.rot,Math.abs(r));cur.head=Math.max(cur.head,lp.lean+r+lp.head);
    cur.headMin=Math.min(cur.headMin,lp.lean+r+lp.head);cur.trunk=Math.max(cur.trunk,lp.lean+r);}}
  return false;}});return J;}"""

# the bot's frames and the standing jumps' drawn poses, hashed per floor (FNV-1a over the rounded numbers); the standing frames also listed
BOTJS = r"""([n,sd])=>{const H=__HK,K=['lean','head','aF','eF','aB','eB','hF','kF','hB','kB','hy','rot','ox','oy','sb','soF','soB','fpF','fpB','khF','khB'];
 let hb=2166136261>>>0,hs=2166136261>>>0,nb=0,ns=0;const fs=[];
 const mix=(h,s)=>{for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return h;};
 const r=runBot(n,sd,{fight:false,stop:H=>{const p=H.P;if(!p)return false;
  hb=mix(hb,[p.state,p.x.toFixed(4),p.y.toFixed(4),(p.vx||0).toFixed(4),(p.vy||0).toFixed(4),p.face,p.hp].join(','));nb++;
  const sj=(p.state==='jumpPrep')||(p.state==='air'&&p.jumpKind==='stand')||((p.state==='land'||p.state==='stand')&&p.stK==='sl'&&H.gameTime-p.stT<0.8);
  if(sj&&p.pose){const q=p.pose,s=[p.state,(p.yo||0).toFixed(5)].concat(K.map(k=>(q[k]||0).toFixed(5))).join(',');hs=mix(hs,s);ns++;if(fs.length<4000)fs.push(nb+':'+s);}
  return false;}});return {n,sd,ok:r.ok,nb,hb,ns,hs,fs};}"""


def trace_all(b, src):
    """egyptr33a's trace (the first jump of each kind on floors 3, 4, 6, seed 1) and the standing and running baselines"""
    got, base = R33.trace(b, src)
    return got, base


def rot_numbers(b, src):
    J = []
    for n in range(1, 28):
        pg = E.page(b, src)
        J += pg.evaluate(ROTJS, [n, 1])
        pg.close()
    o = {}
    for low in (False, True):
        q = [j for j in J if j['low'] == low]
        if q:
            o['low' if low else 'full'] = {'n': len(q), 'rot_max': round(math.degrees(max(j['rot'] for j in q)), 1),
                                           'head_max': round(math.degrees(max(j['head'] for j in q)), 1), 'head_min': round(math.degrees(min(j['headMin'] for j in q)), 1),
                                           'trunk_max': round(math.degrees(max(j['trunk'] for j in q)), 1)}
    return o


def bot_check(b, srcs):
    seeds = (1,) if QUICK else (1, 2)
    res = {}
    for tag in ('v79', 'r34'):
        res[tag] = {}
        for n in range(1, 28):
            for sd in seeds:
                pg = E.page(b, srcs[tag])
                res[tag][(n, sd)] = pg.evaluate(BOTJS, [n, sd])
                pg.close()
    bad_bot, bad_st, tot, tots = [], [], 0, 0
    for k in res['v79']:
        a, c = res['v79'][k], res['r34'][k]
        tot += a['nb']
        tots += a['ns']
        if (a['nb'], a['hb'], a['ok']) != (c['nb'], c['hb'], c['ok']):
            bad_bot.append(k)
        if (a['ns'], a['hs']) != (c['ns'], c['hs']):
            i = next((i for i, (x, y) in enumerate(zip(a['fs'], c['fs'])) if x != y), None)
            bad_st.append((k, a['ns'], c['ns'], a['fs'][i] if i is not None else '', c['fs'][i] if i is not None else ''))
    return {'runs': len(res['v79']), 'frames': tot, 'stand_frames': tots, 'bot_differ': [list(k) for k in bad_bot], 'stand_differ': [list(x) for x in bad_st],
            'bot_identical': not bad_bot, 'stand_identical': not bad_st}


def over_stand(c, base):
    return R33.numbers(c, base)


def strip(pg, c, base, every=2, per=22):
    jy = c['jy']
    fr = c['fr'][max(0, c['i0'] - 10):]
    air = [i for i, f in enumerate(fr) if f['st'] == 'air']
    fr = fr[:air[-1] + 12]
    ia = air[0]
    top = min(f['crown'] for f in fr if f['st'] == 'air')
    ys = jy - base['stand'][0]
    cells = []
    for i in range(0, len(fr), every):
        q = fr[i]
        im = E.img(pg.evaluate(R32.DRAW, [[dict(q, ox=0)], S, q['x'] - 26, jy - 70, 52, 80, 'cell', jy]))
        d = ImageDraw.Draw(im)
        for y, col, dash in ((ys, (122, 90, 60), True), (top, (31, 154, 85), False)):
            Y = (y - (jy - 70)) * S
            for x in range(0, im.width, 6):
                d.line([(x, Y), (x + (3 if dash else 6), Y)], fill=col)
        d.text((2, 1), '%+d %s' % (i - ia, q['st'][:5]), fill=(40, 30, 20))
        cells.append(im)
    cw, ch = cells[0].size
    rows = (len(cells) + per - 1) // per
    out = Image.new('RGB', (per * (cw + 1), rows * (ch + 1)), INK)
    for k, im in enumerate(cells):
        out.paste(im, ((k % per) * (cw + 1), (k // per) * (ch + 1)))
    return out


def gif(b, srcs, T):
    key = 'run level'
    fa, x0, x1 = {}, 1e9, -1e9
    for t in TAGS:
        c = T[t][0][key]
        fr = c['fr'][max(0, c['i0'] - 14):]
        air = [i for i, f in enumerate(fr) if f['st'] == 'air']
        fa[t] = (c, fr[:air[-1] + 30])
        x0 = min(x0, min(f['x'] for f in fa[t][1]) - 30)
        x1 = max(x1, max(f['x'] for f in fa[t][1]) + 30)
    x0, x1 = int(x0), int(x1)
    pgs = {t: E.page(b, srcs[t]) for t in TAGS}
    for t in TAGS:
        pgs[t].evaluate("([n,sd])=>{__P.load(n,sd);__HK.GFX().hd=true;}", [3, 1])
    n = max(len(fa[t][1]) for t in TAGS)
    frames = []
    for i in range(n):
        tiles = []
        for t in TAGS:
            c, fr = fa[t]
            jy = c['jy']
            q = fr[min(i, len(fr) - 1)]
            im = E.img(pgs[t].evaluate(R32.DRAW, [[dict(q, ox=0)], 2, x0, jy - 80, x1 - x0, 96, 'cell', jy]))
            d = ImageDraw.Draw(im)
            Y = (T[t][1]['stand'][0] * -1 + 80) * 2
            for x in range(0, im.width, 6):
                d.line([(x, Y), (x + 3, Y)], fill=(122, 90, 60))
            d.text((4, 2), NAME[t], fill=(40, 30, 20))
            tiles.append(im)
        W = sum(im.width for im in tiles) + 6 * (len(tiles) - 1)
        g = Image.new('RGB', (W, tiles[0].height), INK)
        x = 0
        for im in tiles:
            g.paste(im, (x, 0))
            x += im.width + 6
        frames.append(g.convert('P', palette=Image.ADAPTIVE, colors=128))
    for p in pgs.values():
        p.close()
    fn = os.path.join(OUTD, 'r34_runjump.gif')
    frames[0].save(fn, save_all=True, append_images=frames[1:], duration=33, loop=0)
    return fn


def main():
    os.makedirs(OUTD, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix='r34', dir=HERE)
    J = {}
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            srcs = {t: prep(src_of(t, tmp), tmp, t) for t in TAGS}
            if BOT:
                r = bot_check(b, srcs)
                J['bot'] = r
                print('bot: %d runs, %d frames: identical %s %s; standing jumps: %d frames: identical %s %s' % (r['runs'], r['frames'], r['bot_identical'], r['bot_differ'][:6],
                      r['stand_frames'], r['stand_identical'], r['stand_differ'][:3]))
                json.dump(J, open(os.path.join(OUTD, 'r34_bot.json'), 'w'), indent=1)
                return
            T = {}
            for tag in TAGS:
                got, base = trace_all(b, srcs[tag])
                T[tag] = (got, base)
                pg = E.page(b, srcs[tag])
                sc = R32.scissor(pg)
                pg.close()
                J[tag] = {'base_stand': [round(v, 1) for v in base['stand']], 'base_run': [round(v, 1) for v in base['run']],
                          'kinds': {k: over_stand(got[k], base) for k in sorted(got)},
                          'scissor': '%d/%d' % sc}
                if not QUICK:
                    inv = R33.inventory(b, srcs[tag])
                    s0 = base['stand'][0]
                    J[tag]['inventory'] = {k: dict(v, crown_over_stand=round(v['crown'] - s0, 1), crown_max_over_stand=round(v['crown_max'] - s0, 1)) for k, v in inv.items()}
                    J[tag]['flight'] = rot_numbers(b, srcs[tag])
            json.dump(J, open(os.path.join(OUTD, 'r34.json'), 'w'), indent=1)
            for tag in TAGS:
                print('%s: baselines (crown, head, hip) standing %s running %s; scissor %s; flight %s' % (tag, J[tag]['base_stand'], J[tag]['base_run'], J[tag]['scissor'],
                      json.dumps(J[tag].get('flight', {}))))
                for k, v in J[tag]['kinds'].items():
                    print('  %-18s k %.2f s %.2f over standing %s' % (k, v['jK'] or 1, v['jS'] if v['jS'] is not None else -1, json.dumps(v['over_stand'])))
                for k, v in J[tag].get('inventory', {}).items():
                    print('  inv %-20s n %3d crown over standing median %+.1f max %+.1f' % (k, v['n'], v['crown_over_stand'], v['crown_max_over_stand']))
            if MEASURE:
                return
            rows = []
            for key, lab in KINDS:
                imgs, tit = [], []
                for tag in TAGS:
                    got, base = T[tag]
                    if key not in got:
                        continue
                    pg = E.page(b, srcs[tag])
                    im, ov = R33.panel(pg, got[key], base, got[key]['n'])
                    pg.close()
                    imgs.append(im)
                    tit.append('%s: crown apex %+.1f px over standing' % (NAME[tag], ov))
                Hh = max(i.height for i in imgs)
                row = Image.new('RGB', (sum(i.width for i in imgs) + 20, Hh + 22), INK)
                x = 0
                for t, im in zip(tit, imgs):
                    row.paste(im, (x, 20))
                    ImageDraw.Draw(row).text((x + 4, 4), t, fill=TXT)
                    x += im.width + 10
                rows.append((lab, row))
            for tag in TAGS:
                got, base = T[tag]
                pg = E.page(b, srcs[tag])
                pg.evaluate("([n,sd])=>{__P.load(n,sd);__HK.GFX().hd=true;}", [3, 1])
                rows.append(('%s, the level running jump: every 2nd game frame (numbered from take-off; dashed the standing crown, green the drawn crown\'s apex)' % NAME[tag],
                             strip(pg, got['run level'], base)))
                pg.close()
            W = max(r.width for _, r in rows)
            out = Image.new('RGB', (W, sum(r.height + 20 for _, r in rows) + 46), INK)
            d = ImageDraw.Draw(out)
            d.text((6, 6), 'Round 34: the running jump\'s flight (owner after v79: "him tilting his head and rotating like that is not natural. The previous movement was fine, '
                   'except the apex"): v77\'s upright flight back, on round 33a\'s low apex.', fill=TXT)
            fl = {t: J[t].get('flight', {}).get('full', {}) for t in TAGS}
            d.text((6, 22), 'Onion skins every 3rd frame; green: the crown\'s path and apex; dashed: the standing crown. Largest turn / head pitch in a running flight: '
                   + ', '.join('%s %s / %s deg' % (NAME[t], fl[t].get('rot_max', '?'), fl[t].get('head_max', '?')) for t in TAGS), fill=DIM)
            y = 46
            for lab, r in rows:
                d.text((6, y + 2), lab, fill=DIM)
                out.paste(r, (0, y + 18))
                y += r.height + 20
            fn = os.path.join(OUTD, 'r34_runjump.png')
            out.save(fn, optimize=True)
            print('wrote', fn, out.size, gif(b, srcs, T))
            b.close()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    main()
