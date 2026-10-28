# egyptr46b.py old.html new.html [outdir] [torch|classic]: round 46b's pictures (owner on a B3 heap before an opening, the Waters of Nun at night:
# "it looks transparent, the background wall art seems drawn over it, the shadow renders just over the far left of the heap, and that center
# circle/oval doesn't look right"). Before | after, Torchlight on the GPU and Classic, a lamp beyond him so his shadow falls toward the heap:
#   r46b_<case>_3x.png     the heap's crop at 3x (rows: Torchlight, Classic; columns: old | new)
#   r46b_<case>_phone.png  the whole view at phone size (852 x 393), old over new, both modes
#   r46b_ends_3x.png       the B3 column's three end looks (fracture, socket, buried) on the same column, new only, both modes, beside old's end
# Cases: the owner's (B3 at night before an opening, floor 3 seed 46291), B1 (floor 6 seed 46595, an opening), B2 (floor 25 seed 48425),
# a drift before an opening (floor 8 seed 46789), a drift with blocks (C4, floor 8 seed 46776), B1 in the Blue Chambers (floor 9 seed 46873).
# Run from dev/tools (HK_GPU=0: WebGL in SwiftShader).
import io, os, sys
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
a = [x for x in sys.argv[1:]]
OLD, NEW = os.path.abspath(a[0]), os.path.abspath(a[1])
OUT = os.path.abspath(a[2]) if len(a) > 2 and not a[2] in ('torch', 'classic') else os.path.dirname(os.path.abspath(__file__))
MODES = [m for m in ('torch', 'classic') if m in a] or ['torch', 'classic']
GPU = [] if os.environ.get('HK_GPU') == '0' else ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist', '--force_high_performance_gpu']
CASES = [('owner_B3_nun_night', 3, 46291, 92, 30), ('B1_west', 6, 46595, 115, 9), ('B2_kerma', 25, 48425, 307, 12),
         ('drift_opening', 8, 46789, 253, 41), ('C4_blocks', 8, 46776, 246, 20), ('B1_blue', 9, 46873, 190, 47)]
SETUP = r'''([n,seed,c,r,end])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS){H.S.hints[id]=1;if(H.S.learned)H.S.learned[id]=1;}const L=H.load(n,seed,true);H.banner=null;
  const h=(L.hills||[]).find(q=>q.c===c&&q.r===r);if(!h)return null;if(H.HILL_DBG){H.HILL_DBG.end=end||null;for(const k of ['_bl','_sil','_sd','_c0','_c1','_tg'])delete h[k];}
  const P=H.P;P.inv=1e9;for(const e of H.G||[])e.x=-9999;P.x=(c+h.n)*32+12;P.y=(r+1)*64-4;P.fallY=P.y;P.vx=0;P.face=-1;P.state='stand';H.mode='play';
  L.torches.push({c:c+h.n+3,r}); /* (a lamp beyond him: his shadow falls toward the heap) */
  for(const kk of ['l','r','u','j','g'])H.setKey('kb',kk,false);H.tick(20);return [H.themeName(n),h.v,h.n,H.hillEnd?H.hillEnd(h):''];}'''
SHOW = r'''([fx,fy])=>{const H=__HK;H.banner=null;H.setClock(()=>1e6);H.setGT(10);H.clearRooms();
  H.cam.x=fx-H.viewW/2;H.cam.y=fy-192*0.62;H.cam.gy=H.cam.y;if(H.GLP){H.GLP.pipe=false;H.GLP.rs=1;window.__HKnoauto=true;}for(let i=0;i<4;i++)H.render();
  const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect(),k=X.VZ/cv.width*R.width;
  return [R.left-X.camD/cv.width*R.width,R.top-X.camDY/cv.height*R.height,k];}'''
DSF = 3


def label(im, t):
    d = ImageDraw.Draw(im); d.rectangle((0, 0, 8 + 6 * len(t), 13), fill=(0, 0, 0)); d.text((4, 1), t, fill=(250, 240, 215))


def shoot(pg, n, seed, c, r, end=None):
    info = pg.evaluate(SETUP, [n, seed, c, r, end])
    if not info: return None
    nn = info[2]; fx, fy = c * 32 + nn * 16, (r + 1) * 64 - 4
    q = pg.evaluate(SHOW, [fx, fy]); im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
    k = q[2] * DSF; bw, bh = nn * 32 + 64, 70
    x0, y0 = q[0] * DSF + (fx - bw / 2) * k, q[1] * DSF + (fy - 52) * k
    crop = im.crop((int(x0), int(y0), int(x0 + bw * k), int(y0 + bh * k))).resize((bw * 3, bh * 3), Image.LANCZOS)
    return crop, im.resize((852, 393), Image.LANCZOS), info


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(args=GPU); pages = {}; errs = []
        for src in (OLD, NEW):
            for mode in MODES:
                pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=DSF); pg.on('pageerror', lambda e: errs.append(str(e)))
                pg.goto('file://' + src); pg.wait_for_timeout(800)
                pg.evaluate("()=>{document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen');const st=document.createElement('style');st.textContent='.ctl,#pause,#pauseBtn,#pad{display:none!important}';document.head.appendChild(st);}")
                pg.evaluate("m=>{__HK.S.set.lightMode=m;}", mode); pages[(src, mode)] = pg
        for tag, n, seed, c, r in CASES:
            cells = {}
            for src in (OLD, NEW):
                for mode in MODES:
                    s = shoot(pages[(src, mode)], n, seed, c, r)
                    if s: label(s[0], '%s %s %s fl%d s%d %s %s' % ('old' if src == OLD else 'new', tag, s[2][1], n, seed, s[2][0][:22], mode)); cells[(src, mode)] = s
            if not cells: print('no hill', tag); continue
            cw, ch = next(iter(cells.values()))[0].size
            sh = Image.new('RGB', (2 * cw + 6, len(MODES) * (ch + 6)), (20, 16, 24)); ph = Image.new('RGB', (852 * len(MODES) + 6, 2 * 393 + 6), (20, 16, 24))
            for i, mode in enumerate(MODES):
                for j, src in enumerate((OLD, NEW)):
                    if (src, mode) not in cells: continue
                    cr, im, _ = cells[(src, mode)]; sh.paste(cr, (j * (cw + 6), i * (ch + 6))); label(im, '%s %s %s' % ('old' if src == OLD else 'new', tag, mode)); ph.paste(im, (i * 858, j * 399))
            sh.save(os.path.join(OUT, 'r46b_%s_3x.png' % tag)); ph.save(os.path.join(OUT, 'r46b_%s_phone.png' % tag)); print('wrote', tag, flush=True)
        # the column's three ends on the owner's column and on a lit one (Halls of the West, floor 6 seed 46582)
        rows = []
        for n, seed, c, r in ((3, 46291, 92, 30), (6, 46582, 186, 33)):
            for mode in MODES:
                row = [shoot(pages[(OLD, mode)], n, seed, c, r)] + [shoot(pages[(NEW, mode)], n, seed, c, r, e) for e in ('frac', 'sock', 'bury')]
                for s, t in zip(row, ('old', 'A fracture', 'B socket', 'C buried')): label(s[0], '%s fl%d %s %s' % (t, n, s[2][0][:20], mode))
                rows.append(row)
        cw, ch = rows[0][0][0].size; sh = Image.new('RGB', (4 * (cw + 6), len(rows) * (ch + 6)), (20, 16, 24))
        for i, row in enumerate(rows):
            for j, s in enumerate(row): sh.paste(s[0], (j * (cw + 6), i * (ch + 6)))
        sh.save(os.path.join(OUT, 'r46b_ends_3x.png')); print('wrote ends')
        if errs: print('errors', errs[:3])
        b.close()
