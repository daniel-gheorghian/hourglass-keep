# r23grips.py [v69.html]: round 23's gameplay contacts, read from the v69 release (the last build whose drawing gameplay was tuned to).
# Round 23 rebuilds the prince's body and poses from motion capture, but where a hand holds something (a ledge's lip, the floor while
# climbing or crawling, a hilt, the sword's place in a fight, the flask at the mouth) the hand must stay where v69 put it: these are
# places in the world (HANG, the climb's offsets, the bar's grip, the sword's reach were tuned to them), not a look. For every pose that
# holds something this writes the hands (front gF, back gB) and v69's mouth (gM, for the drink) in the hip's frame (x forward, y down),
# to r23grips.json, which r23poses.py reads. Run from dev/tools.
import json, os, sys, tempfile, shutil
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
_old = os.path.join(HERE, 'hk_v69_release.html')
if not os.path.exists(_old):
    _old = os.path.join(HERE, '..', '..', '..', '..', '..', 'dev', 'tools', 'hk_v69_release.html')
SRC = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else _old)
EXPORT = 'window.__G={skel,LEN,PS,mk,crawlPose,DK,climbFrame};'
JS = r'''()=>{const F=__G,L=F.LEN,o={};
 const one=p=>{const s=F.skel(p),ha=p.lean+p.head,hx=Math.sin(ha),hy=-Math.cos(ha),nx=-hy,ny=hx,r=L.hd,
   m=[s.hd[0]+nx*r*0.8-hx*r*0.62,s.hd[1]+ny*r*0.8-hy*r*0.62],R=a=>[+a[0].toFixed(3),+a[1].toFixed(3)];
   return {gF:R(s.hF),gB:R(s.hB),gM:R(m),sh:R(s.sh),hd:R(s.hd),hipH:+s.hipH.toFixed(3),p:Object.fromEntries(Object.entries(p).map(([k,v])=>[k,+(+v).toFixed(4)]))};};
 for(const k of Object.keys(F.PS))o['PS.'+k]=one(F.PS[k]);
 for(let i=0;i<16;i++)o['crawl '+i]=one(F.crawlPose(i/16));
 F.DK.forEach((k,i)=>{o['DK '+i]=Object.assign(one(k[1]),{t:k[0],tilt:k[2],fill:k[3]});});
 return {LEN:L,o};}'''

if __name__ == '__main__':
    tmp = tempfile.mkdtemp(prefix='r23g', dir=HERE)
    try:
        s = open(SRC, encoding='utf-8').read()
        i = s.find('window.__HK={')
        fn = os.path.join(tmp, 'v69.html')
        open(fn, 'w', encoding='utf-8').write(s[:i] + EXPORT + s[i:])
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page()
            pg.goto('file://' + fn)
            pg.wait_for_timeout(500)
            R = pg.evaluate(JS)
            b.close()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    R['src'] = os.path.basename(SRC)
    json.dump(R, open(os.path.join(HERE, 'r23grips.json'), 'w'), indent=0)
    print('r23grips:', len(R['o']), 'poses from', SRC)
