# egyptr46a.py old.html new.html [outdir]: pictures for round 46a (the sky beams without staircases; rules S1-S7 in dev/docs/rendering.md).
# For the owner's case (floor 26 at night, a run of open arches: the dark stepped wedge from each pier's top), a floor's shadow across a beam
# (floor 50, dawn), a low ceiling's shadow in the haze (floor 7, dusk) and round 28b's prince in a beam (floor 11), both modes, the normal
# look (motes and drifting haze on, the clock frozen): r46a_f<N>.png, before | after, 3x crops of the beam at Torchlight's GLP.rs 1, .75,
# .5, Battery saver (canvas at 1x) and Classic; r46a_f<N>_<mode>_phone.png, before | after at phone size (852 x 393 CSS px, device scale 2).
import sys, os, io
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
OLD, NEW = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
OUTD = os.path.abspath(sys.argv[3] if len(sys.argv) > 3 else os.path.dirname(os.path.abspath(__file__))); os.makedirs(OUTD, exist_ok=True)
FIND = r'''([n,skip,ao])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;let k=0;
  for(let sd=1;sd<20;sd++){const L=H.load(n,2600+sd);H.banner=null;
    for(const o of H.ryOps()){if(o.sh.own||o.x0<12*32||o.x1>(L.cols-12)*32)continue;if(o.kind==='arch'&&o.sh.key<'a2')continue;if(ao&&(o.kind!=='arch'||o.sh.key<'a3'))continue;if(k++<skip)continue;
      window.__O={x:(o.x0+o.x1)/2,y:(o.y0+o.y1)/2,fl:o.fl,o};return [n,2600+sd,H.themeName(n),o.kind,o.sh.key];}}return null;}'''
SHOW = r'''([mode,rs,px])=>{const H=__HK,O=window.__O,P=H.P,sb=H.skyBeam();P.inv=1e9;P.x=O.x+(px===null?sb.dx/sb.dy*(O.fl-O.y)+4:px);P.y=O.fl;P.state='stand';P.face=-1;
  H.cam.x=O.x-H.viewW/2;H.cam.y=O.y-40;H.cam.gy=H.cam.y;H.S.set.lightMode=mode;H.mode='play';H.GLP.pipe=false;H.GLP.rs=rs;H.GLP.inSession=true;window.__HKnoauto=true;
  for(let i=0;i<4;i++)H.render();const X=H.renderXf||H.XF,cv=document.getElementById('game'),k=cv.getBoundingClientRect().width/cv.width,o=O.o,r=o.fl+6-o.y0;
  const xs=[o.x0,o.x1,o.x0+sb.dx/sb.dy*r,o.x1+sb.dx/sb.dy*r];return [(Math.min(...xs)-14)*X.VZ*k-X.camD*k,(o.y0-10)*X.VZ*k-X.camDY*k,(Math.max(...xs)+14)*X.VZ*k-X.camD*k,(o.fl+10)*X.VZ*k-X.camDY*k];}'''
CASES = [(26, 0, 1, 400, "owner's case: a run of open arches at night (the Deffufa of Kerma)"), (50, 4, 0, 400, "a floor's shadow across the beam, dawn"),
         (7, 2, 0, 400, "a low ceiling's shadow in the haze, dusk"), (11, 3, 0, None, "round 28b's case: the prince in the beam (the Blue Chambers)")]
SETS = [('torch', 1, False), ('torch', .75, False), ('torch', .5, False), ('torch', 1, True), ('classic', 1, False), ('classic', 1, True)]
def lab(im, t):
    d = ImageDraw.Draw(im); d.rectangle((0, 0, 8 + 6 * len(t), 14), fill=(0, 0, 0)); d.text((4, 2), t, fill=(250, 240, 215)); return im
with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist', '--force_high_performance_gpu'])
    def page(src, saver):
        pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2); pg.goto('file://' + src); pg.wait_for_timeout(700)
        pg.evaluate("()=>{document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen');const st=document.createElement('style');st.textContent='.ctl,#pause,#pauseBtn,#pad{display:none!important}';document.head.appendChild(st);}")
        if saver: pg.evaluate("()=>{__HK.S.set.saver=true;window.dispatchEvent(new Event('resize'));}"); pg.wait_for_timeout(300)
        return pg
    pgs = {(t, sv): page(src, sv) for t, src in (('before', OLD), ('after', NEW)) for sv in (False, True)}
    for (n, sk, ao, px, title) in CASES:
        rows = []
        for (mode, rs, sv) in SETS:
            cells = []; box = None
            for tag in ('before', 'after'):
                pg = pgs[(tag, sv)]; q = pg.evaluate(FIND, [n, sk, ao]); bx = pg.evaluate(SHOW, [mode, rs, px]); box = box or [int(v * 2) for v in bx]
                im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
                if rs == 1 and not sv:
                    im.save(os.path.join(OUTD, 'r46a_f%d_%s_%s_phone.png' % (n, mode, tag)))
                W, H = im.size; c = im.crop((max(0, box[0]), max(0, box[1]), min(W, box[2]), min(H, box[3])))
                f = 3 if c.width < 420 else 2; c = c.resize((c.width * f, c.height * f), Image.NEAREST)
                cells.append(lab(c, '%s, %s, %s (x%d)' % (tag, mode, 'Battery saver' if sv else 'GLP.rs %g' % rs if mode == 'torch' else 'full size', f)))
            w = sum(c.width for c in cells) + 8; h = max(c.height for c in cells); r = Image.new('RGB', (w, h), (20, 16, 24)); x = 0
            for c in cells: r.paste(c, (x, 0)); x += c.width + 8
            rows.append(r)
        Wd = max(r.width for r in rows); Hd = sum(r.height + 8 for r in rows) + 20; sh = Image.new('RGB', (Wd, Hd), (20, 16, 24)); d = ImageDraw.Draw(sh)
        d.text((6, 4), 'Floor %d seed %d, %s: %s. Left before (v87), right after (round 46a). Crops of the 852x393 screen at device scale 2.' % (n, q[1], q[4], title), fill=(255, 210, 140)); y = 20
        for r in rows: sh.paste(r, (0, y)); y += r.height + 8
        sh.save(os.path.join(OUTD, 'r46a_f%d.png' % n)); print('wrote r46a_f%d.png' % n, flush=True)
        for mode in ('torch', 'classic'):
            a, c = [Image.open(os.path.join(OUTD, 'r46a_f%d_%s_%s_phone.png' % (n, mode, t))) for t in ('before', 'after')]
            s2 = Image.new('RGB', (a.width * 2 + 8, a.height), (20, 16, 24)); s2.paste(lab(a, 'before (v87), ' + mode), (0, 0)); s2.paste(lab(c, 'after (round 46a), ' + mode), (a.width + 8, 0))
            s2.save(os.path.join(OUTD, 'r46a_f%d_%s_phone.png' % (n, mode)))
            for t in ('before', 'after'): os.remove(os.path.join(OUTD, 'r46a_f%d_%s_%s_phone.png' % (n, mode, t)))
    b.close()
