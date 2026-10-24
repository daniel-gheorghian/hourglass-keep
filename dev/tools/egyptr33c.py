# egyptr33c.py [new.html] [old.html] [--measure | --nogif | --gifonly]: round 33c's pictures and numbers (owner, floor 16: "the prince is hanging and we need a short
# animation that plays when the prince is transitioning from hanging to the slide down position"), into egypt_themes/:
#   r33c_bannerdrop.png  three ways onto a hanging (floor 16 seed 1, the hanging in column 250 from row 17, its lip in column 251), v78 | round 33c,
#                        every game frame from the hang (or the step off) to the steady slide: the figure as drawn (livePose), the hands
#                        marked (front red, back blue), the lip and the hanging's middle as lines:
#                          A  hanging, Down (let go), Grab 8 frames later: the bot's way (bot.js 'slide': g off, press d, g on after 8 frames)
#                          B  hanging, Grab held and Down: v78 caught the same lip again; 33c takes the cloth straight away
#                          C  walking off the lip, Grab 8 frames later: the plain fall into the slide
#   r33c_bannerdrop.gif  A and B in game (the page's own render, Torchlight), v78 | round 33c, at half speed
#   r33c.json            (local) the numbers --measure prints: per case the largest move of each hand and the head in one frame (px),
#                        the drawn x's jump at the slide's first frame, the knees' largest change in a frame
# old.html defaults to hk_v78_release.html (or git show 3f7fe77:dev/hourglass-keep.html). Run from dev/tools.
# CMU mocap (mocap.cs.cmu.edu, NSF EIA-0196217): 01_09, 01_10 were read for the release timing (see the source's round 33c note).
import io, os, sys, tempfile, shutil, base64, json, math, subprocess
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
import egyptr26c as E

HERE = os.path.dirname(os.path.abspath(__file__))
args = [x for x in sys.argv[1:] if not x.startswith('--')]
MEASURE = '--measure' in sys.argv
NOGIF = '--nogif' in sys.argv
GIFONLY = '--gifonly' in sys.argv
NEW = os.path.abspath(args[0] if args else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = args[1] if len(args) > 1 else os.path.join(HERE, 'hk_v78_release.html')
OUTD = os.path.join(HERE, 'egypt_themes')
INK, TXT, DIM = E.INK, E.TXT, E.DIM
S = 3
N, SD, LIPC, ROW, DIR = 16, 1, 251, 17, -1   # floor 16 seed 1: the lip in column 251 (row 17), the hanging in column 250
CEN = (LIPC + DIR) * 32 + 16
LIPX = (LIPC + (1 if DIR > 0 else 0)) * 32
CASES = [('A', 'A  hanging, Down, Grab 8 frames later (the bot)'), ('B', 'B  hanging, Grab held and Down'),
         ('C', 'C  walking off the lip, Grab 8 frames later')]


def old_src(tmp):
    if os.path.exists(OLD):
        return os.path.abspath(OLD)
    fn = os.path.join(tmp, '_v78.html')
    open(fn, 'w', encoding='utf-8').write(subprocess.run(['git', 'show', '3f7fe77:dev/hourglass-keep.html'], capture_output=True, text=True, cwd=HERE).stdout)
    return fn


def prep(src, tmp, tag):
    s = open(src, encoding='utf-8').read()
    i = s.find('window.__HK={')
    fn = os.path.join(tmp, '_r33c_%s.html' % tag)
    open(fn, 'w', encoding='utf-8').write(s[:i] + "window.__J33={livePose,slBlade:typeof slBlade==='function'?slBlade:null};" + s[i:])
    return fn


SETUP = r"""([n,sd,c,r,dir])=>{const H=__HK;__P.load(n,sd);H.GFX().hd=true;__P.stand(c,r,-dir);const P=H.P;P.inv=1e9;window.__k={};return [P.x,P.y,P.state];}"""
# one game frame with the keys given, then the figure as drawn
STEP = r"""([keys])=>{const H=__HK,P=H.P;for(const k in keys)H.setKey('kb',k,keys[k]);H.tick(1);H.banner=null;
  const q=__J33.livePose(P,P.pose),s=H.skel(q),f=P.face,c=Math.cos(q.rot||0),sn=Math.sin(q.rot||0),bx=P.x,by=P.y-s.hipH+(P.yo||0);
  const W=h=>[bx+f*((q.ox||0)+h[0]*c-h[1]*sn),by+(q.oy||0)+h[0]*sn+h[1]*c],sl=P.state==='slide',bl=sl?(__J33.slBlade?__J33.slBlade():9):0,lk=P.lk||{};
  return {gt:H.gameTime,st:P.state,t:P.t,x:P.x,y:P.y,vy:P.vy,face:f,dx:f*(q.ox||0),hF:W(s.hF),hB:W(s.hB),hd:W(s.hd),fF:W(s.fF),fB:W(s.fB),yo:P.yo||0,
    sw:sl&&bl>0,swl:bl,sq:lk.sq||1,cw:lk.cw||0,cwy:(lk.cwy||0)*(sl?0.3:1),p:Object.assign({},q)};}"""
# a cell: a plain diagram of the tiles (stone, floor tops, the lip), the hanging as a band, the figure as drawn, its hands marked
DRAW = r"""([fr,S,x0,y0,W,Hh,cen,lipx,mode])=>{const H=__HK,L=H.L;H.GFX().hd=true;const cv=document.createElement('canvas');cv.width=W*S;cv.height=Hh*S;const c=cv.getContext('2d');c.scale(S,S);c.translate(-x0,-y0);
  c.fillStyle='#e9dfcc';c.fillRect(x0,y0,W,Hh);
  for(let cc=Math.floor(x0/32);cc<=Math.floor((x0+W)/32);cc++)for(let rr=Math.floor(y0/64);rr<=Math.floor((y0+Hh)/64);rr++){const b=L.base[rr*L.cols+cc],X=cc*32,Y=rr*64;
    if(b===2){c.fillStyle='#8a7a62';c.fillRect(X,Y,32,64);}else if(b===1){c.fillStyle='#b9a888';c.fillRect(X,Y+60,32,4);c.fillStyle='#8a7a62';c.fillRect(X,Y+64,32,4);}}
  c.fillStyle='rgba(150,60,50,.28)';c.fillRect(cen-7,y0,14,Hh);c.strokeStyle='rgba(150,60,50,.6)';c.lineWidth=0.4;c.beginPath();c.moveTo(cen,y0);c.lineTo(cen,y0+Hh);c.stroke();
  const n=fr.length;fr.forEach((f,i)=>{const p=Object.assign(H.mk({}),f.p),o={hasSword:true,sword:f.sw,swLen:f.swl,time:f.gt,yo:f.yo,sq:Math.abs(f.sq-1)>0.004?f.sq:undefined,vx:f.cw,vy:f.cwy};
    if(mode==='onion')c.globalAlpha=0.22+0.78*(i+1)/n;H.figDraw(c,f.x,f.y,f.face,p,H.PAL_HERO,o);});c.globalAlpha=1;
  for(const f of fr){for(const [h,col] of [[f.hF,'#d0302a'],[f.hB,'#2e6bd8']]){c.fillStyle=col;c.beginPath();c.arc(h[0],h[1],0.9,0,7);c.fill();}}
  return cv.toDataURL('image/png');}"""


def keys_for(case, i, st):
    """the keys for frame i of a case (st: the state before the frame); None ends the run"""
    if case in 'AB':
        if i < 60:
            return {'d': i == 0}            # Down at the lip's middle: he lowers himself to the hang; let him settle
        j = i - 60
        if case == 'A':
            return {'d': j == 0, 'g': j >= 8}
        return {'g': True, 'd': j >= 1}
    k = 'l' if DIR < 0 else 'r'
    return None


def record(pg, case):
    pg.evaluate(SETUP, [N, SD, LIPC, ROW, DIR])
    fr = []
    if case == 'C':
        pg.evaluate("()=>{__HK.P.face=-__HK.P.face;}")
        k = 'l' if DIR < 0 else 'r'
        for i in range(120):
            q = pg.evaluate(STEP, [{k: True}])
            fr.append(q)
            if q['st'] == 'air':
                break
        i0 = len(fr) - 1
        for j in range(40):
            fr.append(pg.evaluate(STEP, [{k: False, 'g': j >= 7}]))
        return fr, i0
    for i in range(60 + 40):
        fr.append(pg.evaluate(STEP, [keys_for(case, i, None)]))
    pg.evaluate("()=>{__HK.setKey('kb','g',false);__HK.setKey('kb','d',false);}")
    return fr, 60


def numbers(fr, i0):
    w = fr[i0 - 1:]
    o = {'hand_max': 0, 'head_max': 0, 'x_jump': 0, 'knee_max_deg': 0, 'states': []}
    for a, b in zip(w, w[1:]):
        dF = math.hypot(b['hF'][0] - a['hF'][0], b['hF'][1] - a['hF'][1])
        dB = math.hypot(b['hB'][0] - a['hB'][0], b['hB'][1] - a['hB'][1])
        dH = math.hypot(b['hd'][0] - a['hd'][0], b['hd'][1] - a['hd'][1])
        o['hand_max'] = round(max(o['hand_max'], dF, dB), 2)
        o['head_max'] = round(max(o['head_max'], dH), 2)
        dk = max(abs(b['p']['kF'] - a['p']['kF']), abs(b['p']['kB'] - a['p']['kB']))
        o['knee_max_deg'] = round(max(o['knee_max_deg'], math.degrees(dk)), 1)
        if b['st'] == 'slide' and a['st'] != 'slide':
            o['x_jump'] = round((b['x'] + b['dx']) - (a['x'] + a['dx']), 2)
            o['slide_at'] = round(b['gt'] - w[1]['gt'], 3)
    sts = []
    for q in w:
        if not sts or sts[-1] != q['st']:
            sts.append(q['st'])
    o['states'] = sts
    return o


def strip(pg, fr, i0, every=1, per=30, n=30):
    sel = fr[i0 - 2:i0 - 2 + n:every]
    cells = []
    for k, q in enumerate(sel):
        im = E.img(pg.evaluate(DRAW, [[q], S, CEN - 26, int(q['y']) - 84, 56, 96, CEN, LIPX, 'cell']))   # (the view follows him down)
        d = ImageDraw.Draw(im)
        d.text((2, 1), '%d %s' % (k - 1, q['st'][:5]), fill=(40, 30, 20))
        cells.append(im)
    cw, ch = cells[0].size
    rows = (len(cells) + per - 1) // per
    out = Image.new('RGB', (per * (cw + 1), rows * (ch + 1)), INK)
    for k, c in enumerate(cells):
        out.paste(c, ((k % per) * (cw + 1), (k // per) * (ch + 1)))
    return out


GIFSTEP = r"""([keys,draw])=>{const H=__HK,P=H.P;for(const k in keys)H.setKey('kb',k,keys[k]);H.tick(1);H.banner=null;if(draw){H.cam.snap=true;__P.draw();}return P.state;}"""


def main():
    os.makedirs(OUTD, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix='r33c', dir=HERE)
    J, rec = {}, {}
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            pgs = {}
            for tag, src in (('v78', old_src(tmp)), ('r33c', NEW)):
                pg = E.page(b, prep(src, tmp, tag))
                pgs[tag] = pg
                J[tag], rec[tag] = {}, {}
                for case, lab in CASES:
                    fr, i0 = record(pg, case)
                    rec[tag][case] = (fr, i0)
                    J[tag][case] = numbers(fr, i0 if case != 'C' else [q['st'] for q in fr].index('slide'))   # (C: from the catch; the step off is v78's own)
                if pg.errs:
                    print(tag, 'errors', pg.errs[:3])
            json.dump(J, open(os.path.join(OUTD, 'r33c.json'), 'w'), indent=1)
            for case, lab in CASES:
                for tag in ('v78', 'r33c'):
                    print('%-5s %-4s %s' % (case, tag, json.dumps(J[tag][case])))
            if MEASURE:
                return
            rows = []
            if GIFONLY:
                CASES_ = []
            else:
                CASES_ = CASES
            for case, lab in CASES_:
                for tag in ('v78', 'r33c'):
                    pgs[tag].evaluate("([n,sd])=>{__P.load(n,sd);__HK.GFX().hd=true;}", [N, SD])
                    fr, i0 = rec[tag][case]
                    rows.append(('%s: %s, every game frame, numbered from the first after the hang (C: the step off); the view follows him; hands: front red, back blue; the hanging shaded, its middle a line' % (lab, 'v78' if tag == 'v78' else 'round 33c'),
                                 strip(pgs[tag], fr, i0)))
            W = max([r.width for _, r in rows] or [1])
            Ht = sum(r.height + 20 for _, r in rows) + 30
            out = Image.new('RGB', (W, Ht), INK)
            d = ImageDraw.Draw(out)
            d.text((6, 6), 'Round 33c: from the hang onto the hanging (floor 16 seed 1). v78: the hands leave the lip in a frame, the figure jumps 9 px to the hanging\'s middle, the arms snap to the cloth; 33c: each hand lets go in turn, the body swings in under them, one hand takes the cloth and then the other, the blade sinks in', fill=TXT)
            y = 30
            for lab, r in rows:
                d.text((6, y + 2), lab, fill=DIM)
                out.paste(r, (0, y + 18))
                y += r.height + 20
            if rows:
                out.save(os.path.join(OUTD, 'r33c_bannerdrop.png'), optimize=True)
            if NOGIF:
                print('wrote', os.path.join(OUTD, 'r33c_bannerdrop.png'))
                return
            # ---- the gif: A and B in game (the page's render, Torchlight), v78 | 33c side by side, half speed ----
            frames = {}
            for tag in ('v78', 'r33c'):
                pg = pgs[tag]
                pg.evaluate("()=>{__HK.S.set.lightMode='torch';if(__HK.GLP)__HK.GLP.pipe=false;}")
                frames[tag] = []
                for case in 'AB':
                    pg.evaluate(SETUP, [N, SD, LIPC, ROW, DIR])
                    for i in range(96):
                        pg.evaluate(GIFSTEP, [keys_for(case, i, None), i >= 57])   # (drawn only from just before the let-go: the software WebGL is slow)
                        if i >= 57:
                            x, yv = pg.evaluate("()=>__P.scr(%d,__HK.P.y-30)" % CEN)
                            im = Image.open(io.BytesIO(pg.screenshot(clip={'x': min(852 - 200, max(0, x - 100)), 'y': min(393 - 200, max(0, yv - 100)), 'width': 200, 'height': 200}))).convert('RGB')
                            E.label(im, '%s %s' % ('v78' if tag == 'v78' else '33c', case))
                            frames[tag].append(im)
                    pg.evaluate("()=>{__HK.setKey('kb','g',false);__HK.setKey('kb','d',false);}")
            n = min(len(frames['v78']), len(frames['r33c']))
            gif = []
            for i in range(n):
                a, c = frames['v78'][i], frames['r33c'][i]
                g = Image.new('RGB', (a.width + c.width + 6, max(a.height, c.height)), INK)
                g.paste(a, (0, 0))
                g.paste(c, (a.width + 6, 0))
                gif.append(g.convert('P', palette=Image.ADAPTIVE, colors=128))
            gif[0].save(os.path.join(OUTD, 'r33c_bannerdrop.gif'), save_all=True, append_images=gif[1:], duration=33, loop=0)
            print('wrote', os.path.join(OUTD, 'r33c_bannerdrop.png'), os.path.join(OUTD, 'r33c_bannerdrop.gif'))
            b.close()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    main()
