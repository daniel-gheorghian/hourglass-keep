# egyptr28b.py [new.html] [old.html]: round 28b's picture (owner, a phone shot of the Blue Chambers, Torchlight: the open arches with their gold
# posts, the dusk beam through them and the prince standing in it, the shadow he casts down the beam's haze circled: "jaggies in the light beams"),
# into egypt_themes/r28b_beams.png:
#   1. the owner's scene: floor 11 (the Blue Chambers), seed 1101, the prince standing in the beam of a run of open arches, at 844x390 CSS px and
#      DPR 3 (the game draws at DPR 2), Torchlight before | after, 1:1 crops of the screen at GLP.rs 1, .75 and .5;
#   2. 3x crops: the shadow's edge down the haze, and the haze's cut round his head (standing further into the beam), before | after; and the
#      same at Battery saver (DPR 1);
#   3. the evidence: the shafts' own target (quarter size, read back; dust motes and drifting haze off) at 10x, before | after; and the figures' mask (an eighth before, a quarter after) at 6x;
#   4. Classic before | after (it draws no figure shadow in the beams: unchanged);
#   5. the cost: GPU time by stage (EXT_disjoint_timer_query_webgl2, this Mac, medians of 120 frames, three rounds).
# old.html defaults to round 28a (git 1588880), else the v74 release. Run from dev/tools.
import io, os, sys, base64, subprocess, tempfile
from PIL import Image, ImageDraw, ImageOps
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(a[0] if a else os.path.join(HERE, '..', 'hourglass-keep.html'))
OUT = os.path.join(HERE, 'egypt_themes', 'r28b_beams.png')
INK = (20, 16, 24)
TXT = (250, 240, 215)
HDR = (255, 210, 140)
TMP = tempfile.mkdtemp(prefix='r28b_')


def old_src():
    if len(a) > 1:
        return os.path.abspath(a[1])
    try:
        s = subprocess.run(['git', 'show', '1588880:dev/hourglass-keep.html'], cwd=HERE, capture_output=True, check=True).stdout
        p = os.path.join(TMP, 'old_src.html'); open(p, 'wb').write(s); return p
    except Exception:
        p = os.path.join(HERE, 'hk_v74_release.html')
        return p if os.path.exists(p) else os.path.join(HERE, '..', '..', '..', '..', '..', 'dev', 'tools', 'hk_v74_release.html')


OLD = old_src()


def prep(fn, tag, clean=False):
    """a copy that hands the shafts' state to the page (GLC, GLA); clean: dust motes, drifting haze and dither off (to measure the edge)"""
    s = open(fn, encoding='utf-8').read()
    if clean:
        for x, y in (('(.7+.6*nz+u_sk.z*mo)', '(1.)'), ('float lt=dot(t,vec3(.3,.5,.2)),dz=', 'float lt=dot(t,vec3(.3,.5,.2)),dz=0.*')):
            assert x in s
            s = s.replace(x, y)
    s = s.replace('window.__HK={', 'window.__GLC=GLC;window.__GLA=GLA;window.__HK={', 1)
    p = os.path.join(TMP, '%s%s.html' % (tag, '_c' if clean else ''))
    open(p, 'w', encoding='utf-8').write(s)
    return p


FIND = r'''([n,skip,pdx])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;let k=0;
  for(let sd=1;sd<20;sd++){const L=H.load(n,1100+sd);H.banner=null;
    for(const o of H.ryOps()){if(o.kind!=='arch'||o.sh.own||o.x0<12*32||o.x1>(L.cols-12)*32)continue;if(k++<skip)continue;
      window.__O={x:(o.x0+o.x1)/2,y:(o.y0+o.y1)/2,fl:o.fl,pdx};return [n,1100+sd,H.themeName(n),o.x0,o.y0,o.x1,o.y1];}}return null;}'''
SHOW = r'''([rs])=>{const H=__HK,o=window.__O,P=H.P;P.inv=1e9;P.x=o.x+o.pdx;P.y=o.fl;P.state='stand';P.face=1;H.cam.x=o.x+40-H.viewW/2;H.cam.y=o.y-50;H.cam.gy=H.cam.y;
  H.mode='play';H.GLP.pipe=false;H.GLP.rs=rs;H.GLP.inSession=true;window.__HKnoauto=true;for(let i=0;i<4;i++)H.render();return H.GLP.rs;}'''
RD = r'''()=>{const gl=__HK.GLP.gl,C=window.__GLC,A=window.__GLA.G,AT=__HK.GLS.atlT;
 const rd=(f,w,h)=>{const px=new Uint8Array(w*h*4);gl.bindFramebuffer(gl.FRAMEBUFFER,f);gl.readPixels(0,0,w,h,gl.RGBA,gl.UNSIGNED_BYTE,px);gl.bindFramebuffer(gl.FRAMEBUFFER,null);return px;};
 const enc=(px,w,h,x0,y0,cw,ch,k)=>{const c=document.createElement('canvas');c.width=cw;c.height=ch;const g=c.getContext('2d'),im=g.createImageData(cw,ch);
   for(let y=0;y<ch;y++)for(let x=0;x<cw;x++){const s=((h-1-(y0+y))*w+x0+x)*4,d=(y*cw+x)*4;for(let i=0;i<3;i++)im.data[d+i]=Math.min(255,px[s+i]*k);im.data[d+3]=255;}g.putImageData(im,0,0);return c.toDataURL();};
 const s=rd(C.fs.f,C.fw,C.fh),at=rd(AT.rf,AT.w,AT.h);
 return [enc(s,C.fw,C.fh,0,0,C.fw,C.fh,2),enc(at,AT.w,AT.h,A.lw+2,0,A.ow,A.oh,1),C.fw,C.fh,A.ow,A.oh];}'''
COST = r'''async([N])=>{const H=__HK,gl=H.GLP.gl,X=gl.getExtension('EXT_disjoint_timer_query_webgl2');if(!X)return null;
  const res={},pend=[],raf=()=>new Promise(r=>requestAnimationFrame(r)),PF=H.PF,op=PF.p;let q=null;
  const begin=()=>{q=gl.createQuery();gl.beginQuery(X.TIME_ELAPSED_EXT,q);};
  PF.p=function(name){if(q){gl.endQuery(X.TIME_ELAPSED_EXT);pend.push([name,q]);q=null;}begin();};
  const coll=()=>{for(let i=pend.length-1;i>=0;i--){const [nm,qq]=pend[i];if(gl.getQueryParameter(qq,gl.QUERY_RESULT_AVAILABLE)){(res[nm]=res[nm]||[]).push(gl.getQueryParameter(qq,gl.QUERY_RESULT)/1e6);gl.deleteQuery(qq);pend.splice(i,1);}}};
  for(let f=0;f<N;f++){begin();H.render();if(q){gl.endQuery(X.TIME_ELAPSED_EXT);pend.push(['rest',q]);q=null;}await raf();coll();}
  for(let w=0;w<30&&pend.length;w++){await raf();coll();}
  PF.p=op;const o={};const med=v=>{v=v.slice().sort((x,y)=>x-y);return v[v.length>>1];};let tot=0;for(const k in res){o[k]=med(res[k]);tot+=o[k];}o.total=tot;return o;}'''


def page(b, src, mode='torch', dpr=3, saver=False):
    pg = b.new_page(viewport={'width': 844, 'height': 390}, device_scale_factor=dpr)
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.goto('file://' + src)
    pg.wait_for_timeout(700)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen')")
    pg.evaluate("m=>{__HK.S.set.lightMode=m;}", mode)
    if saver:
        pg.evaluate("()=>{__HK.S.set.saver=true;window.dispatchEvent(new Event('resize'));}")
        pg.wait_for_timeout(300)
    return pg


def shot(pg, pdx=5, rs=1):
    q = pg.evaluate(FIND, [11, 3, pdx])
    pg.evaluate(SHOW, [rs])
    return Image.open(io.BytesIO(pg.screenshot())).convert('RGB'), q


def b64(u):
    return Image.open(io.BytesIO(base64.b64decode(u.split(',')[1]))).convert('RGB')


def label(im, t, xy=(4, 2)):
    d = ImageDraw.Draw(im)
    d.rectangle((xy[0] - 2, xy[1] - 1, xy[0] + 6 * len(t) + 4, xy[1] + 12), fill=(0, 0, 0))
    d.text(xy, t, fill=TXT)
    return im


def z(im, box, k):
    c = im.crop(box)
    return c.resize((c.width * k, c.height * k), Image.NEAREST)


def row(cells, gap=8):
    w = sum(c.width for c in cells) + gap * (len(cells) - 1)
    h = max(c.height for c in cells)
    r = Image.new('RGB', (w, h), INK)
    x = 0
    for c in cells:
        r.paste(c, (x, 0)); x += c.width + gap
    return r


def text_block(w, lines, head=None):
    lh = 14
    im = Image.new('RGB', (w, lh * (len(lines) + (1 if head else 0)) + 10), INK)
    d = ImageDraw.Draw(im)
    y = 4
    if head:
        d.text((6, y), head, fill=HDR); y += lh
    for t in lines:
        d.text((6, y), t, fill=TXT); y += lh
    return im


if __name__ == '__main__':
    src = {'before': prep(OLD, 'before'), 'after': prep(NEW, 'after')}
    cln = {'before': prep(OLD, 'before', True), 'after': prep(NEW, 'after', True)}
    errs = []
    parts = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        P = {t: page(b, s) for t, s in src.items()}
        # 1. the owner's scene at each scale (1:1 device pixels of the DPR 3 screen)
        info = None
        S1 = {}
        for rs in (1, 0.75, 0.5):
            cells = []
            for t in ('before', 'after'):
                im, info = shot(P[t], 5, rs)
                S1[(t, rs)] = im
                cells.append(label(im.crop((900, 40, 1660, 700)), 'Torchlight %s, GLP.rs %s, 844x390 at DPR 3, 1:1' % (t, rs)))
            parts.append(row(cells))
        head = ('The owner\'s scene: floor %d (%s), seed %d, the prince standing in the dusk beam of a run of open arches. The game draws at DPR 2 '
                '(1688x780) and the phone shows it at 3; the shafts are drawn at a quarter of that (422x195) at every GLP.rs.' % (info[0], info[2], info[1]))
        parts.insert(0, text_block(parts[0].width, [], head))
        # 2. 3x crops: the shadow's edge (rs 1), the haze's cut round the head, and Battery saver (DPR 1)
        cells = [label(z(S1[(t, 1)], (1040, 380, 1240, 580), 3), 'shadow edge, %s, 3x' % t) for t in ('before', 'after')]
        parts.append(row(cells))
        cells = []
        for t in ('before', 'after'):
            im, _ = shot(P[t], 22, 1)
            cells.append(label(z(im, (1100, 360, 1300, 560), 3), 'standing further in: the haze cut round his head, %s, 3x' % t))
        parts.append(row(cells))
        for pg in P.values():
            errs += pg.errs; pg.close()
        cells = []
        for t in ('before', 'after'):
            pg = page(b, src[t], saver=True)
            im, _ = shot(pg, 5, 1)
            cells.append(label(z(im, (1040, 380, 1240, 580), 3), 'Battery saver (DPR 1), %s, 3x' % t))
            errs += pg.errs; pg.close()
        parts.append(row(cells))
        # 3. the shafts' target and the figures' mask, read back (DPR 2)
        cells, mk = [], []
        for t in ('before', 'after'):
            pg = page(b, cln[t], dpr=2)
            shot(pg, 5, 1)
            r = pg.evaluate(RD)
            Sx = b64(r[0]); Mx = b64(r[1])
            cells.append(label(ImageOps.autocontrast(Sx.crop((170, 58, 234, 122)).convert('L'), cutoff=0.5).convert('RGB').resize((640, 640), Image.NEAREST),
                               'the shafts\' target (%dx%d), %s, 10x, contrast' % (r[2], r[3], t)))
            sx, sy = r[4] / r[2], r[5] / r[3]
            mk.append(label(Mx.crop((int(170 * sx), int(58 * sy), int(234 * sx), int(122 * sy))).resize((640, 640), Image.NEAREST),
                            'the figures\' mask (%dx%d), %s, same area' % (r[4], r[5], t)))
            errs += pg.errs; pg.close()
        parts.append(row(cells))
        parts.append(row(mk))
        # 4. Classic
        cells = []
        for t in ('before', 'after'):
            pg = page(b, src[t], mode='classic')
            im, _ = shot(pg, 5, 1)
            cells.append(label(im.crop((900, 40, 1660, 700)), 'Classic %s, 1:1 (no figure shadow in its beams)' % t))
            errs += pg.errs; pg.close()
        parts.append(row(cells))
        # 5. cost
        cost = {'before': [], 'after': []}
        for rnd in range(3):
            for t in ('before', 'after'):
                pg = page(b, src[t], dpr=2)
                shot(pg, 5, 1)
                c = pg.evaluate(COST, [120])
                if c:
                    cost[t].append(c)
                errs += pg.errs; pg.close()
        b.close()

    def mean(t, k):
        v = [c.get(k, 0) for c in cost[t]]
        return sum(v) / max(1, len(v))
    W = max(pp.width for pp in parts)
    lines = ['Cause: his shadow down the haze had a hard edge, narrower than one texel of the shafts\' quarter-size target, so the composite\'s bilinear',
             'upsample drew it as a staircase (one step per 4 screen px; 6 px on the phone, 12 at Battery saver). Two things made it hard: the figures\' mask',
             'was an eighth of the screen (8 px texels), and every one of the march\'s 12 steps multiplied its reading into the light, so a dozen readings',
             'of the bilinear ramp at 0.1-0.3 hardened it into an edge that traced the mask\'s texels. And the haze over a figure was cut where the',
             'mask read over 0.15, a dark fringe up to a texel past his outline on the lit side (stepped the same way).',
             'Fix (Torchlight; look only): the mask a quarter of the screen (as the shafts\' pass; the atlas keeps its size); each step reads it at three',
             'points across the light (1-2-1, at least 1.25 texels apart and wider with distance: a penumbra, as the walls have) at two places a quarter',
             'step either side along it; the figure shades by the most any step saw of it (one occluder: its cover, not a product); the haze is cut',
             'over him from 0.35 to 0.75 of the mask (inside his outline). Walls, slabs, blades, the floor slab and the wall faces: unchanged.',
             'GPU time per frame on this scene (this Mac, 1688x780, means of three medians of 120 frames): atmosphere + bloom %.3f > %.3f ms, the scene and'
             % (mean('before', 'atmo') + mean('before', 'bloom'), mean('after', 'atmo') + mean('after', 'bloom')),
             'masks %.3f > %.3f ms, total %.3f > %.3f ms.' % (mean('before', 'scene'), mean('after', 'scene'), mean('before', 'total'), mean('after', 'total')),
             'Research: GPU Gems 3 ch. 13 (Mitchell: march toward the light, occluders cut it); Toth and Umenhoffer 2009 (interleaved sampling, then a',
             'filter); Wronski 2014 (volumetric fog: low-resolution march, filtered); Kopf et al. 2007 (joint bilateral upsampling); Reeves et al. 1987',
             'and Fernando 2005 (PCF and PCSS: filter the occluder test, a penumbra that widens with distance). Per-pixel jitter stays out (v61b, WEBGL_LESSONS).']
    parts.append(text_block(W, lines, 'Round 28b: no jaggies in the light beams'))
    H = sum(pp.height + 8 for pp in parts)
    sheet = Image.new('RGB', (W, H), INK)
    y = 0
    for pp in parts:
        sheet.paste(pp, (0, y)); y += pp.height + 8
    sheet.save(OUT)
    print('cost', {t: {k: round(mean(t, k), 3) for k in ('atmo', 'bloom', 'scene', 'total')} for t in cost})
    print('errors', errs[:4])
    print('wrote', OUT, sheet.size)
