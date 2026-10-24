# egyptr35a.py [new.html] [old.html] [--measure] [--quick]: round 35a's pictures and numbers (owner after v80: "again the jump, just the running
# jump: the prince hangs too much in air while jumping. Tweak the timings so it is shorter. The prince running speed doesn't match the running
# jump, the fact that the prince hangs too much in air breaks the tempo"), into egypt_themes/:
#   r35a_jump.png   the same running jumps (two tiles of pit, floor 2 seed 2; three tiles, floor 10 seed 1; the low leap, floor 4 seed 1) in
#                   v80 | round 35a, the way held throughout (he runs up, jumps and runs on): every 3rd game frame on one clock, aligned at
#                   the take-off (column 0), from 0.4 s before it to 0.75 s after, with the frames in the air marked; the hit box's path
#                   (feet) over the whole stretch, a tick every 0.1 s
#   r35a_jump.gif   the two-tile jump in play, v80 over round 35a, in real time (every 2nd game frame at 33 ms), a clock in each
#   r35a.json       the numbers: per build, every running and standing jump the bot makes on floors 1-27 (seed 1; --quick floors 1-9) by
#                   kind (level, down, caught at the far lip, a ledge a storey up, the swing bar, the low leap, the chase's dash): air time,
#                   distance flown, horizontal speed, rise of the hit box; the run's speed and step; the arcs' formulas; PoP 1989's runjump
# --pics: the pictures only, the bot's numbers kept from r35a.json if it is there.
# old.html defaults to hk_v80_release.html here (else git's cd72a27). Run from dev/tools.
# PoP 1989: SDLPoP src/seqtbl.c, runjump (frames 34-44) and runcyc1 (frames 7-14), at 12 ticks a second; 14 x-units to a 32 px tile.
import os, sys, json, subprocess, tempfile, shutil, statistics as st
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
import egyptr26c as E
import egyptr32 as R32

HERE = os.path.dirname(os.path.abspath(__file__))
args = [x for x in sys.argv[1:] if not x.startswith('--')]
MEASURE = '--measure' in sys.argv
QUICK = '--quick' in sys.argv
PICS = '--pics' in sys.argv
NEW = os.path.abspath(args[0] if args else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLDA = args[1] if len(args) > 1 else None
OUTD = os.path.join(HERE, 'egypt_themes')
INK, TXT, DIM = E.INK, E.TXT, E.DIM
TAGS = ('v80', 'r35a')
NAME = {'v80': 'v80', 'r35a': 'round 35a'}
S = 2
# (label, floor, seed, start x, feet y, facing, Jump pressed at x): the prince set back on a real floor and run at the lip, the way held
SC = [('two tiles of pit (floor 2 seed 2)', 2, 2, 418.6, 444, 1, 528.6),
      ('three tiles of pit, caught at the far lip (floor 10 seed 1)', 10, 1, 4960.4, 1212, 1, 5060.4),
      ('the low leap under a ceiling (floor 4 seed 1)', 4, 1, 4330.6, 1404, 1, 4420.6)]

# PoP 1989 (SDLPoP seqtbl.c): runcyc1 frames 7-14, dx a tick; runjump frames 34-44 (dx, dy into each frame); 12 ticks a second
POP_RUN = [5, 1, 2, 4, 5, 2, 3, 4]                       # two steps (SND_FOOTSTEP at frames 9 and 13)
POP_RJ = [(34, 0, 0), (35, 5, 0), (36, 6, 0), (37, 3, 0), (38, 5, 0), (39, 7, 0), (40, 12, -3), (41, 8, -9), (42, 8, -2), (43, 4, 11), (44, 4, 3)]
POP_UNIT = 32 / 14.0                                     # px (ours) per PoP x-unit: a tile is 14 units, 32 px here
POP_HZ = 12.0


def pop_numbers():
    run_u = sum(POP_RUN) / len(POP_RUN)                  # units a tick
    air = [q for q in POP_RJ if q[0] >= 40]               # 40-43 in the air, 44 on the floor
    air_dx = sum(q[1] for q in air)                       # from frame 39 (last on the floor) to 44 (landed): 5 ticks
    air_ticks = len(air)
    rise = -min(sum(q[2] for q in POP_RJ[:i + 1]) for i in range(len(POP_RJ)))
    gather = [q for q in POP_RJ if 35 <= q[0] <= 39]
    return {'run_units_per_tick': run_u, 'run_px_s': round(run_u * POP_UNIT * POP_HZ, 1), 'step_s': round(4 / POP_HZ, 3),
            'air_ticks_drawn': air_ticks - 1, 'air_ticks_floor_to_floor': air_ticks, 'air_s': round(air_ticks / POP_HZ, 3),
            'air_steps': round(air_ticks / 4.0, 2), 'air_units': air_dx, 'air_px': round(air_dx * POP_UNIT, 1),
            'air_px_s': round(air_dx / air_ticks * POP_UNIT * POP_HZ, 1), 'air_over_run': round(air_dx / air_ticks / run_u, 2),
            'gather_ticks': len(gather), 'gather_over_run': round(sum(q[1] for q in gather) / len(gather) / run_u, 2),
            'rise_px_of_63': rise, 'whole_jump_ticks': len(POP_RJ) - 1, 'whole_jump_s': round((len(POP_RJ) - 1) / POP_HZ, 3)}


def arcs(k):
    """the arcs in closed form (GRAV 700; the clock k): time in the air on a level floor, reach, rise, horizontal speed"""
    o = {}
    for name, vx, vy in (('running', 183, 190), ('low leap', 212, 128), ('standing', 132, 159), ('standing low', 150, 112)):
        kk = k if name in ('running', 'low leap') else 1
        T = 2 * vy / 700.0
        o[name] = {'T_s': round(T * kk, 3), 'reach_px': round(vx * T, 1), 'rise_px': round(vy * vy / 1400.0, 1), 'vx_px_s': round(vx / kk, 1),
                   'vy_px_s': round(vy / kk, 1), 'g_px_s2': round(700 / kk / kk, 1), 'vx_over_RUN': round(vx / kk / 100.0, 2),
                   'steps_in_air': round(T * kk / 0.22, 2)}
    return o


def src_of(tag, tmp):
    if tag == 'r35a':
        return NEW
    if OLDA:
        return os.path.abspath(OLDA)
    for d in (HERE, '/home/user/hourglass-keep/dev/tools'):
        f = os.path.join(d, 'hk_v80_release.html')
        if os.path.exists(f):
            return f
    fn = os.path.join(tmp, '_hk_v80.html')
    open(fn, 'w', encoding='utf-8').write(subprocess.run(['git', 'show', 'cd72a27:dev/hourglass-keep.html'], cwd=HERE, capture_output=True, text=True, check=True).stdout)
    return fn


# every jump the bot makes on a floor: kind, outcome, air time, distance, the hit box's rise; the run's speed and phase rate
MEAS = r"""([n,sd])=>{const H=__HK,J=[],R=[];let cur=null,dashOn=false,dn=0;
 const r=runBot(n,sd,{fight:false,stop:H=>{const p=H.P;if(!p)return false;
  if(window.__dashStart!==undefined&&!dashOn&&(window.__dash||[]).length===dn){dashOn=true;}
  if(dashOn&&(window.__dash||[]).length>dn){dashOn=false;dn=(window.__dash||[]).length;window.__dashStart=undefined;}
  if(p.state==='run'&&p.t>0.8&&R.length<400)R.push([Math.abs(p.vx),p.ph]);
  if(!cur&&p.state==='air'&&(p.jumpKind==='run'||p.jumpKind==='stand'))cur={kind:p.jumpKind,low:!!p.lowJump,dash:dashOn,x0:p.jx,y0:p.jy,vx:Math.abs(p.vx),vy:-p.vy,f:0,top:p.y,kick:false,jT:p.jT};
  if(cur){if(p.jumpKind==='kick'||p.jumpKind==='wall'||p.plant)cur.kick=true;
   if(p.state==='air'){cur.f++;cur.top=Math.min(cur.top,p.y);}
   else{cur.end=p.state;cur.dy=p.y-cur.y0;cur.dx=Math.abs(p.x-cur.x0);J.push(cur);cur=null;}}
  return false;}});return {ok:r.ok,hurt:r.hurt,J,R};}"""


def kind_of(j):
    if j['kick']:
        return None
    dy = j['dy']
    e = ('ledge-up' if abs(dy) < 8 else 'caught lip') if j['end'] == 'hang' else 'swing bar' if j['end'] == 'swing' else 'level' if abs(dy) < 8 else 'down' if dy > 0 else 'up'
    k = j['kind'] + (' low' if j['low'] else '') + ' ' + e
    return ('dash ' if j['dash'] else '') + k


def measure(b, src):
    J, R, bad = [], [], []
    for n in (range(1, 10) if QUICK else range(1, 28)):
        pg = E.page(b, src)
        r = pg.evaluate(MEAS, [n, 1])
        pg.close()
        J += r['J']
        R += r['R']
        if r['ok'] is not True or r['hurt']:
            bad.append((n, r['ok'], r['hurt']))
    G = {}
    for j in J:
        k = kind_of(j)
        if k:
            G.setdefault(k, []).append(j)
    out = {}
    for k, v in sorted(G.items()):
        air = [x['f'] / 60.0 for x in v]
        out[k] = {'n': len(v), 'air_s_median': round(st.median(air), 3), 'air_s_min': round(min(air), 3), 'air_s_max': round(max(air), 3),
                  'dx_px_median': round(st.median(x['dx'] for x in v), 1), 'vx_launch': round(st.median(x['vx'] for x in v), 1),
                  'vx_mean_px_s': round(st.median(x['dx'] / max(1, x['f']) * 60 for x in v), 1),
                  'rise_px_max': round(max(x['y0'] - x['top'] for x in v), 1), 'air_total_s': round(sum(air), 2)}
    run = {'vx_median': round(st.median(x[0] for x in R), 1) if R else None}
    return out, run, bad


SETUP = R32.SETUP
STEP = R32.STEP


def record(pg, sc, nframes):
    lab, n, sd, x0, jy, face, px = sc
    pg.evaluate(SETUP, [n, sd, x0, jy, face])
    fr = []
    for i in range(nframes):
        fr.append(pg.evaluate(STEP, [i, True, face, px, True]))
    return fr


def take_off(fr):
    return next(i for i, q in enumerate(fr) if q['st'] == 'air')


def strip(pgs, recs, sc, every=3, pre=24, post=45):
    """both builds' frames on one clock, aligned at the take-off"""
    lab, n, sd, x0, jy, face, px = sc
    rows = []
    xs = []
    for t in TAGS:
        fr = recs[t]
        ia = take_off(fr)
        xs += [q['x'] for q in fr[ia - pre:ia + post + 1]]
    X0, X1 = int(min(xs)) - 26, int(max(xs)) + 26
    for t in TAGS:
        fr = recs[t]
        ia = take_off(fr)
        cells = []
        for rel in range(-pre, post + 1, every):
            q = fr[ia + rel]
            im = E.img(pgs[t].evaluate(R32.DRAW, [[dict(q, ox=0)], S, q['x'] - 26, jy - 70, 52, 80, 'cell', jy]))
            d = ImageDraw.Draw(im)
            if q['st'] == 'air':
                d.rectangle((0, 0, im.width - 1, im.height - 1), outline=(200, 60, 40), width=2)
            d.text((3, 2), '%+d ms' % round(rel * 1000 / 60), fill=(40, 30, 20))
            d.text((3, im.height - 12), q['st'][:5], fill=(90, 60, 40))
            cells.append(im)
        cw, ch = cells[0].size
        row = Image.new('RGB', (len(cells) * (cw + 1), ch), INK)
        for k, im in enumerate(cells):
            row.paste(im, (k * (cw + 1), 0))
        # the feet's path over the stretch on one clock: a tick every 0.1 s
        Wp = X1 - X0
        im = E.img(pgs[t].evaluate(R32.DRAW, [[], S, X0, jy - 70, Wp, 80, 'cell', jy]))
        d = ImageDraw.Draw(im)
        pts = [((q['x'] - X0) * S, (q['y'] - (jy - 70)) * S) for q in fr[ia - pre:ia + post + 1]]
        d.line(pts, fill=(46, 107, 216), width=2)
        for k in range(0, len(pts), 6):
            rel = k - pre
            c = (200, 60, 40) if fr[ia - pre + k]['st'] == 'air' else (40, 30, 20)
            d.ellipse((pts[k][0] - 3, pts[k][1] - 3, pts[k][0] + 3, pts[k][1] + 3), fill=c)
            if rel % 12 == 0:
                d.text((pts[k][0] - 8, pts[k][1] + 6), '%+.1f' % (rel / 60), fill=(40, 30, 20))
        nair = sum(1 for q in fr if q['st'] == 'air')
        rows.append(('%s: %s, in the air %d frames (%.3f s), take-off at %+.0f ms; every 3rd frame on one clock (red: in the air)'
                     % (NAME[t], lab, nair, nair / 60, 0), row))
        rows.append(('%s: the hit box\'s feet, a dot every 0.1 s (red in the air), seconds from take-off' % NAME[t], im))
    return rows


def gif(b, srcs, recs, sc):
    lab, n, sd, x0, jy, face, px = sc
    xs = [q['x'] for t in TAGS for q in recs[t]]
    X0, X1 = int(min(xs)) - 30, int(max(xs)) + 30
    pgs = {t: E.page(b, srcs[t]) for t in TAGS}
    for t in TAGS:
        pgs[t].evaluate("([n,sd])=>{__P.load(n,sd);__HK.GFX().hd=true;}", [n, sd])
    frames = []
    nn = min(len(recs[t]) for t in TAGS)
    for i in range(0, nn, 2):
        tiles = []
        for t in TAGS:
            q = recs[t][i]
            im = E.img(pgs[t].evaluate(R32.DRAW, [[dict(q, ox=0)], 2, X0, jy - 80, X1 - X0, 96, 'cell', jy]))
            d = ImageDraw.Draw(im)
            d.text((4, 2), '%s   %.2f s   %s' % (NAME[t], i / 60, q['st']), fill=(40, 30, 20))
            tiles.append(im)
        g = Image.new('RGB', (tiles[0].width, sum(im.height for im in tiles) + 4), INK)
        y = 0
        for im in tiles:
            g.paste(im, (0, y))
            y += im.height + 4
        frames.append(g.convert('P', palette=Image.ADAPTIVE, colors=96))
    for p in pgs.values():
        p.close()
    fn = os.path.join(OUTD, 'r35a_jump.gif')
    frames[0].save(fn, save_all=True, append_images=frames[1:], duration=33, loop=0)
    return fn


def main():
    os.makedirs(OUTD, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix='r35a', dir=HERE)
    J = {'pop': pop_numbers(), 'arcs': {'v80': arcs(1.0)}}
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            srcs = {t: R32.prep(src_of(t, tmp), tmp, t) for t in TAGS}
            k = E.page(b, srcs['r35a'])
            K = k.evaluate('__HK.RJ_K||1')
            k.close()
            J['RJ_K'] = K
            J['arcs']['r35a'] = arcs(K)
            jf = os.path.join(OUTD, 'r35a.json')
            if PICS and os.path.exists(jf):
                J0 = json.load(open(jf))
                for t in TAGS:
                    J[t] = J0[t]
            else:
                for t in TAGS:
                    out, run, bad = measure(b, srcs[t])
                    J[t] = {'jumps': out, 'run': run, 'bot_bad': bad}
            json.dump(J, open(jf, 'w'), indent=1)
            print('PoP 1989:', json.dumps(J['pop']))
            for t in TAGS:
                print('%s arcs: %s' % (t, json.dumps(J['arcs'][t])))
                print('%s run %s, bot not clean: %s' % (t, J[t]['run'], J[t]['bot_bad']))
                for kk, v in J[t]['jumps'].items():
                    print('  %-26s n %3d air %.3f s (%.3f-%.3f) dx %5.1f px  vx launch %5.1f mean %5.1f  rise %4.1f' % (kk, v['n'], v['air_s_median'], v['air_s_min'], v['air_s_max'],
                          v['dx_px_median'], v['vx_launch'], v['vx_mean_px_s'], v['rise_px_max']))
            if MEASURE:
                return
            rows = []
            pgs = {t: E.page(b, srcs[t]) for t in TAGS}
            first = None
            for sc in SC:
                recs = {t: record(pgs[t], sc, 150) for t in TAGS}
                if first is None:
                    first = recs
                for t in TAGS:
                    pgs[t].evaluate("([n,sd])=>{__P.load(n,sd);__HK.GFX().hd=true;}", [sc[1], sc[2]])
                rows += strip(pgs, recs, sc)
            for pg in pgs.values():
                pg.close()
            W = max(r.width for _, r in rows)
            out = Image.new('RGB', (W, sum(r.height + 18 for _, r in rows) + 44), INK)
            d = ImageDraw.Draw(out)
            a0, a1 = J['arcs']['v80']['running'], J['arcs']['r35a']['running']
            d.text((6, 6), 'Round 35a: the running jump\'s tempo (owner after v80: "the prince hangs too much in air ... breaks the tempo"). The same arc on a shorter '
                   'clock: in the air %.3f s -> %.3f s (PoP 1989: %.3f s), %.0f -> %.0f px/s (the run 100).' % (a0['T_s'], a1['T_s'], J['pop']['air_s'], a0['vx_px_s'], a1['vx_px_s']), fill=TXT)
            d.text((6, 22), 'Both builds from the same start, the way held throughout (he runs up, jumps and runs on); columns on one clock (ms from take-off).', fill=DIM)
            y = 44
            for lab, r in rows:
                d.text((6, y + 2), lab, fill=DIM)
                out.paste(r, (0, y + 16))
                y += r.height + 18
            fn = os.path.join(OUTD, 'r35a_jump.png')
            out.save(fn, optimize=True)
            print('wrote', fn, out.size, gif(b, srcs, first, SC[0]))
            b.close()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    main()
