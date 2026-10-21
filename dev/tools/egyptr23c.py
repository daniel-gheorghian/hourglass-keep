# egyptr23c.py [new.html] [old.html]: round 23c's picture (owner: "1.28 is fine. Now make the neck 2px shorter and keep everything else as
# is"), into egypt_themes/r23c_neck.png: before (round 23b at MUS 1.28, made with git show e4ca9e1:dev/hourglass-keep.html unless old.html is
# given) | after (the source, which now draws 1.28 with no override): standing at 10x with the chin and shoulder-joint lines; stand, hang,
# reach, run, crouch, crawl, drink, en garde and a robber at 4x; standing at 1x and 3x beside a robber; and in the game at the phone's
# resolution (852x393 at 2 device pixels a CSS pixel, crops 1:1), Torchlight and Classic, standing and running. Run from dev/tools. The data used in this project was obtained from mocap.cs.cmu.edu (NSF EIA-0196217); ANSUR II.
import base64, io, os, subprocess, sys, tempfile, shutil
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
import egyptr22b as B22

HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(a[0] if len(a) > 0 and a[0] else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = os.path.abspath(a[1]) if len(a) > 1 and a[1] else None
OUT = os.path.join(HERE, 'egypt_themes')
INK = (20, 16, 24)
BG = (250, 246, 238)
WHITE = (240, 230, 210)
MUS = 1.28
EXPORT = 'window.__R23={skel,PS,mk,RP,crawlPose,drinkFrame,figDraw,PAL_HERO,GFX,LEN,guardPal};'

# one figure on a plain ground at S times; guides: the chin's and the shoulder joint's heights (standing only)
FIG = r'''([spec,S,W,Hh,x,y,who])=>{const H=window.__HK,F=window.__R23;H.setMus(%s);let p;const [k,v]=spec.split(' ');
 if(spec.startsWith('PS.'))p=F.PS[spec.slice(3)];else if(k==='run')p=F.RP(+v);else if(k==='crawl')p=F.crawlPose(+v);else if(k==='drink')p=F.drinkFrame(+v).p;
 p=Object.assign(F.mk({}),p);F.GFX().hd=true;
 const cv=document.createElement('canvas');cv.width=W*S;cv.height=Hh*S;const c=cv.getContext('2d');c.fillStyle='#e8dcc8';c.fillRect(0,0,cv.width,cv.height);c.scale(S,S);
 c.strokeStyle='rgba(0,0,0,.25)';c.lineWidth=0.25/Math.max(1,S/4);c.beginPath();c.moveTo(0,y);c.lineTo(W,y);c.stroke();
 const sw=spec==='PS.garde';
 F.figDraw(c,x,y,1,p,who==='rob'?F.guardPal({tier:1}):F.PAL_HERO,{sword:sw,hasSword:true,time:0,lt:{dir:1,col:'255,220,170',k:0.6}});
 const s=F.skel(p),r=F.LEN.hd,ha=p.lean+p.head,hip=y-s.hipH,chin=hip+s.hd[1]+1.15*r*Math.cos(ha),sh=hip+s.sh[1];
 return {u:cv.toDataURL('image/png'),chin,sh,neck:F.LEN.nk};}''' % MUS


def b64img(u):
    return Image.open(io.BytesIO(base64.b64decode(u.split(',')[1]))).convert('RGB')


def fig_page(b, src, tmp, tag):
    s = open(src, encoding='utf-8').read()
    i = s.find('window.__HK={')
    fn = os.path.join(tmp, '_r23c_%s.html' % tag)
    open(fn, 'w', encoding='utf-8').write(s[:i] + EXPORT + s[i:])
    pg = b.new_page()
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.goto('file://' + fn)
    pg.wait_for_timeout(700)
    return pg


def game_page(b, src, mode, dsf=2):
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=dsf)
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.goto('file://' + src)
    pg.wait_for_timeout(700)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true)")
    pg.evaluate("([m,k])=>{__HK.S.set.lightMode=m;if(__HK.GLP)__HK.GLP.pipe=false;__HK.setMus(k);}", [mode, MUS])
    import egyptr12 as R12
    pg.evaluate(R12.PC['JS'])
    pg.add_script_tag(path=os.path.join(HERE, 'bot.js'))
    return pg


def crop(im, xy, dsf, cw, ch):
    x0 = int(min(max(0, xy[0] * dsf - cw / 2), im.width - cw))
    y0 = int(min(max(0, xy[1] * dsf - ch / 2), im.height - ch))
    return im.crop((x0, y0, x0 + cw, y0 + ch))


def label(im, txt, col=WHITE):
    ImageDraw.Draw(im).text((4, 3), txt, fill=col)
    return im


POSES = [('stand', 'PS.stand', 64), ('hang', 'PS.hang', 62), ('reach', 'PS.reach', 62), ('run', 'run 0.25', 64), ('crouch', 'PS.crouch', 64),
         ('crawl', 'crawl 0.25', 64), ('drink (sip)', 'drink 0.72', 64), ('en garde', 'PS.garde', 64), ('robber', 'PS.stand', 64)]

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix='r23c', dir=HERE)
    try:
        if not OLD:
            OLD = os.path.join(tmp, '_r23b_src.html')
            open(OLD, 'wb').write(subprocess.check_output(['git', 'show', 'e4ca9e1:dev/hourglass-keep.html'], cwd=HERE))
        with sync_playwright() as p:
            b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
            V = (('before: round 23b at MUS 1.28', OLD), ('after: round 23c, the neck 2 px shorter', NEW))
            big, prow, info, small = [], [], [], []
            for tag, (nm, src) in zip(('old', 'new'), V):
                pg = fig_page(b, src, tmp, tag)
                q = pg.evaluate(FIG, ['PS.stand', 10, 40, 62, 20, 58, 'hero'])
                im = b64img(q['u'])
                d = ImageDraw.Draw(im)
                for yy, col in ((q['chin'], (190, 40, 40)), (q['sh'], (40, 90, 190))):
                    d.line((0, round(yy * 10), 70, round(yy * 10)), fill=col, width=1)
                info.append(q)
                big.append(im)
                prow.append([b64img(pg.evaluate(FIG, [sp, 4, 56, 74, 28 if k != 'crawl' else 24, y, 'rob' if k == 'robber' else 'hero'])['u']) for k, sp, y in POSES])
                sm = Image.new('RGB', (300, 200), (232, 220, 200))
                x = 4
                for S in (1, 3):
                    for who in ('hero', 'rob'):
                        t = b64img(pg.evaluate(FIG, ['PS.stand', S, 22, 62, 11, 58, who])['u'])
                        sm.paste(t, (x, 196 - t.height))
                        x += t.width
                    x += 6
                small.append(sm)
                pg.close()
            # the 10x rows share the before's chin line too, so the drop reads at a glance
            d = ImageDraw.Draw(big[1])
            for x in range(70, 400, 8):
                d.line((x, round(info[0]['chin'] * 10), x + 3, round(info[0]['chin'] * 10)), fill=(190, 40, 40))
            tiles = []
            for mode in ('torch', 'classic'):
                for tag, (nm, src) in zip(('old', 'new'), V):
                    pg = game_page(b, src, mode)
                    cw, ch = 200, 250
                    xy = pg.evaluate(B22.STAND, [7, 1, 1, 1])
                    t1 = crop(Image.open(io.BytesIO(pg.screenshot())).convert('RGB'), (xy[0], xy[1] + 4), 2, cw, ch)
                    qm = pg.evaluate(B22.MOMENT, [6, 1, "H.P.state==='run'", 14, 1])
                    t2 = crop(Image.open(io.BytesIO(pg.screenshot())).convert('RGB'), (qm['xy'][0], qm['xy'][1] + 6), 2, cw, ch)
                    if pg.errs:
                        print('page errors', tag, mode, pg.errs[:2])
                    tiles.append((mode, tag, t1, t2))
                    pg.close()
            b.close()
        pw, ph = prow[0][0].size
        W = max(big[0].width * 2 + 60, 140 + len(POSES) * (pw + 6))
        H = 60 + big[0].height + 20 + 2 * (ph + 22) + 30 + 230 + 30 + 260 + 60
        im = Image.new('RGB', (W, H), BG)
        d = ImageDraw.Draw(im)
        d.text((8, 8), 'Round 23c (owner: "1.28 is fine. Now make the neck 2px shorter and keep everything else as is"). The game now draws MUS 1.28.', fill=INK)
        d.text((8, 22), 'Shoulder joint to chin %.2f px -> %.2f px (LEN.nk %.3f -> %.3f): the head 2 px lower on the same body. Red: the chin; blue: the shoulder joint;'
               % (info[0]['sh'] - info[0]['chin'], info[1]['sh'] - info[1]['chin'], info[0]['neck'], info[1]['neck']), fill=INK)
        d.text((8, 36), 'dashed red on the right: the chin before. Light from his left.', fill=INK)
        y = 56
        for i, (nm, _) in enumerate(V):
            x = i * (big[0].width + 60) + 8
            d.text((x, y), nm + ' (10x)', fill=INK)
            im.paste(big[i], (x, y + 16))
        y += big[0].height + 26
        for i, (nm, _) in enumerate(V):
            d.text((8, y + 4), nm.split(':')[0] + ' (4x)', fill=INK)
            for j, (k, _, _) in enumerate(POSES):
                if i == 0:
                    d.text((140 + j * (pw + 6), y - 12), k, fill=INK)
                im.paste(prow[i][j], (140 + j * (pw + 6), y))
            y += ph + 22
        y += 8
        d.text((8, y), 'Standing at 1x and 3x, each beside a robber (robbers share the skeleton: their necks are 2 px shorter too)', fill=INK)
        y += 18
        for i, (nm, _) in enumerate(V):
            d.text((8 + i * 320, y), nm.split(':')[0], fill=INK)
            im.paste(small[i], (8 + i * 320, y + 14))
        y += 230
        d.text((8, y), 'In the game at the phone\'s resolution (852x393 CSS px at 2 device px, crops 1:1): Torchlight and Classic; standing (floor 7), running (floor 6)', fill=INK)
        y += 18
        x = 8
        for t in tiles:
            for tt in (t[2], t[3]):
                tt = label(tt.copy(), '%s %s' % ('before' if t[1] == 'old' else 'after', 'Torchlight' if t[0] == 'torch' else 'Classic'))
                im.paste(tt, (x, y))
                x += tt.width + 2
            x += 8
        y += 250 + 6
        im = im.crop((0, 0, W, y + 6))
        im.save(os.path.join(OUT, 'r23c_neck.png'), optimize=True)
        print('r23c_neck.png', im.size, 'neck (joint to chin) before %.2f after %.2f px' % (info[0]['sh'] - info[0]['chin'], info[1]['sh'] - info[1]['chin']))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
