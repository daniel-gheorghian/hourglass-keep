# egyptr16b.py [new.html] [old.html] [outdir]: round 16b's pictures for egypt_themes.html (the swing bar). r16_swing.gif: from a still
# hang, a person's presses (switching to the way he swings 0.2 s after each turn, give or take 0.15 s, the touch source), the chime
# and glow when it will carry him, the throw on the next forward swing and the landing; Torchlight at half size (the swing needs the whole pit in view; 96 colours),
# the keys held printed under each frame. r16_swingchart.png: the time from a still hang to SW_CLEAR for each input style of
# swingfeel.py, before (old.html, default: git show e2f776f:dev/hourglass-keep.html saved as ../_r16a.html) and after. Also writes
# egypt_themes/r16b.json (the two summaries) for egyptround16b.py. Run from dev/tools.
import json, os, sys
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
import egyptr12 as R12
import swingfeel as SF
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(a[0] if len(a) > 0 else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = os.path.abspath(a[1] if len(a) > 1 else os.path.join(HERE, '..', '_r16a.html'))
OUT = a[2] if len(a) > 2 else os.path.join(HERE, 'egypt_themes')
R12.OUT = OUT
SETUP = r'''([n,sd])=>{const H=__HK;window.__HKnoauto=true;const L=__P.load(n,sd),o=L.dyn.find(q=>q.f.t==='bar'),f=o.f,D=L.base[o.r*L.cols+o.c+2]===L.base[o.r*L.cols+o.c]?1:-1;
  __P.stand(o.c-2*D,o.r,D);const p=H.P;p.x=f.x;p.y=f.y+57;p.vx=0;p.vy=0;p.state='air';p.autoGrab=true;p.face=D;p.fallY=p.y;f.ps=0;f.pw=0;H.tick(1);p.swTh=0;p.swOm=0;
  let s=4242;const rnd=()=>{s=(s+0x6D2B79F5)|0;let t=Math.imul(s^(s>>>15),1|s);t=(t+Math.imul(t^(t>>>7),61|t))^t;return((t^(t>>>14))>>>0)/4294967296;};
  window.__sw={t:0,want:0,last:0,turnT:-9,sched:[[0.3,1]],tc:null,tRel:null,rel:false,done:0,kicks:0,kt:-9,D,c:o.c,r:o.r,bx:f.x,by:f.y,rnd};return {D,c:o.c,r:o.r,x:f.x,y:f.y};}'''
STEP = r'''()=>{const H=__HK,P=H.P,w=window.__sw,FW=w.D>0?'r':'l',BK=w.D>0?'l':'r';let jump=false;
  for(let i=0;i<2;i++){const om=P.swOm||0;
    if(P.state==='swing'){const sg=Math.abs(om)>0.05?Math.sign(om):0;if(sg&&sg!==w.last){w.last=sg;w.turnT=w.t;w.sched.push([w.t+Math.max(0,0.2+(w.rnd()*2-1)*0.15),sg]);}
      while(w.sched.length&&w.sched[0][0]<=w.t)w.want=w.sched.shift()[1];
      if(w.tc!==null&&w.tRel===null&&w.last>0&&w.turnT>w.tc)w.tRel=w.turnT+0.29+(w.rnd()*0.32-0.12);
      if(w.tRel!==null&&w.t>=w.tRel&&!w.rel){w.rel=true;w.want=0;jump=true;}}
    else w.want=0;
    H.setKey('touch',FW,w.want>0);H.setKey('touch',BK,w.want<0);H.setKey('touch','j',jump);
    const k0=P.swKT;H.tick(1);if(P.swKT!==undefined&&P.swKT!==k0&&P.state==='swing'){w.kicks++;w.kt=w.t;}
    if(jump){H.setKey('touch','j',false);jump=false;w.jt=w.t;}
    w.t+=1/60;if(w.tc===null&&P.state==='swing'&&P.swRdy)w.tc=w.t;if(w.rel&&['stand','land','run','hang','climb','landHurt'].includes(P.state))w.done++;}
  P.inv=1e9;H.banner=null;if(H.GLP)H.GLP.pipe=false;H.render();H.render();
  const key=w.jt!==undefined&&w.t-w.jt<0.25?'JUMP':w.want===0?'':(w.want>0?'forward >':'< back');
  return {xy:__P.scr(w.bx+w.D*56,w.by+30),amp:+H.swAmp(P.swTh||0,P.swOm||0).toFixed(2),key,kicks:w.kicks,kick:w.t-w.kt<0.2,rdy:!!(P.state==='swing'&&P.swRdy),t:+w.t.toFixed(2),done:w.done,st:P.state};}'''
CW, CH = 1040, 600
NAMES = {'alt 0.2+-0.08': 'switch 0.2 s after each turn, +-0.08', 'alt 0.2+-0.15': 'switch 0.2 s after each turn, +-0.15', 'alt 0+-0.15': 'switch on the turn, +-0.15',
         'alt 0.35+-0.15': 'switch 0.35 s after each turn, +-0.15', 'tap': 'tap 0.12-0.25 s, 0.15 s after turns', 'rhythm 0.45': 'own beat 0.45 s, +-0.1 (swing: 0.58)',
         'rhythm 0.58': 'own beat 0.58 s, +-0.1', 'rhythm 0.75': 'own beat 0.75 s, +-0.1', 'hold fwd': 'hold forward', 'mash': 'mash (a press every 0.08-0.2 s)'}


def note(im, q):
    d = ImageDraw.Draw(im); y = im.height - 14
    d.rectangle((0, y - 2, im.width, im.height), fill=(14, 11, 18))
    d.text((4, y), 't %.1f s   key: %s   pumps: %d%s' % (q['t'], q['key'] or '-', q['kicks'], '   CHIME: will carry him' if q['rdy'] else ''), fill=(255, 214, 140) if q['rdy'] else (240, 230, 210))
    return im


def chart(B, A, fn):
    st = list(A.keys()); W, rowh, x0, cap = 900, 34, 250, 8.0; H = 60 + rowh * len(st)
    im = Image.new('RGB', (W, H), (250, 246, 238)); d = ImageDraw.Draw(im); sc = (W - x0 - 70) / cap
    d.text((8, 8), 'Time from a still hang to SW_CLEAR (median of 40 runs, whisker to the 90th percentile), touch input', fill=(31, 26, 20))
    d.rectangle((x0, 26, x0 + 12, 36), fill=(170, 160, 150)); d.text((x0 + 16, 26), 'before (round 16a)', fill=(31, 26, 20))
    d.rectangle((x0 + 150, 26, x0 + 162, 36), fill=(138, 58, 28)); d.text((x0 + 166, 26), 'after (round 16b)', fill=(31, 26, 20))
    for s in range(0, int(cap) + 1, 2):
        x = x0 + s * sc; d.line((x, 44, x, H - 8), fill=(226, 217, 200)); d.text((x - 3, H - 10 + 0), '', fill=(0, 0, 0))
        d.text((x + 2, 44), '%d s' % s, fill=(107, 97, 86))
    for i, nm in enumerate(st):
        y = 58 + i * rowh; d.text((8, y + 6), NAMES.get(nm, nm), fill=(31, 26, 20))
        for k, (S, col) in enumerate(((B, (170, 160, 150)), (A, (138, 58, 28)))):
            q = S.get(nm); yy = y + k * 13
            if not q or not q['cleared']:
                d.text((x0 + 4, yy), 'never (0 of %d)' % (q['n'] if q else 0), fill=col); continue
            m, p9 = q['med'], q['p90']; d.rectangle((x0, yy, x0 + min(cap, m) * sc, yy + 10), fill=col)
            d.line((x0 + min(cap, m) * sc, yy + 5, x0 + min(cap, p9) * sc, yy + 5), fill=col)
            t = '%.1f s, %d/%d%s' % (m, q['cleared'], q['n'], '' if p9 <= cap else ' (p90 %.0f s)' % p9)
            if p9 > cap * 0.7: d.text((x0 + 4, yy - 1), t, fill=(255, 255, 255))
            else: d.text((x0 + min(cap, p9) * sc + 4, yy - 1), t, fill=col)
    im.save(fn)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        S = {}
        for k, src in (('before', OLD), ('after', NEW)):
            pg = b.new_page(); pg.goto('file://' + src); pg.wait_for_timeout(300); S[k] = SF.summary(pg.evaluate(SF.JS, [6, SF.STY, 40])); pg.close()
        json.dump(S, open(os.path.join(OUT, 'r16b.json'), 'w'), indent=1)
        chart(S['before'], S['after'], os.path.join(OUT, 'r16_swingchart.png'))
        P = {m: R12.page(b, NEW, m) for m in ('torch',)}
        pg = P['torch']; q0 = pg.evaluate(SETUP, [6, 7104]); fr = []
        for k in range(400):
            q = pg.evaluate(STEP); im = R12.crop(R12.shot(pg), q['xy'], CW, CH)
            fr.append(note(R12.label(im.resize((CW // 2, CH // 2), Image.LANCZOS), 'Torchlight, half size'), q))
            if k % 3 == 0: print(q['t'], q['st'], q['key'], q['kicks'], q['amp'], q['rdy'])
            if q['done'] > 40: break
        R12.gif([f.quantize(colors=96, method=Image.MEDIANCUT, dither=Image.NONE) for f in fr], 'r16_swing.gif', 33)
        print('errors', P['torch'].errs[:3]); b.close()
