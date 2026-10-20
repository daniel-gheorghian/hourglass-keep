# figscan.py [new.html] [old.html] [json]: round 22b's check that the prince's new proportions are look only. Before (old.html, default the
# v69 release: hk_v69_release.html here or in the main checkout's dev/tools) and after (new.html, default ../hourglass-keep.html), for every
# pose the game draws (the pose table PS, the run cycle, the crawl, the drink, the climb onto a ledge, the swing, the wall run, the kick-shaft
# plant), it reads the joints that gameplay or other drawing depends on, in the entity's own frame (x right as he faces, y down, the entity's
# x,y at 0,0): both hands, both feet, the hip, the sword's base and tip (swordTip), figReach (wallPress, lowceil), the head's centre and the
# mouth (the drink), and from a silhouette drawn at 8x: the crown (the highest pixel), the sole (the lowest) and the reach to the front and
# back. It reports every difference over 0.25 px and checks the rules:
#   contact  hands in poses where they hold something (a ledge, the floor, a hilt, the bar, a sword, the flask) within 0.35 px of before
#            (both hands on a ledge, the floor or the hilt; the sword hand in a fight, 0.75 px for the lunges' straight arms; the climb until
#            he stands up from his knees)
#   crown    the drawn head no higher than before (0.25 px): round 23, no higher than v69's standing crown in any pose (a storey he can
#            stand in holds all of them), and no higher than v69's own in the poses used under a low ceiling: the crawl, the low leaps,
#            the slide (lowceil.py checks the jumps in rooms one storey tall)
#   feet     on the ground (air 0): the sole's lowest pixel on the floor as before (round 23: the legs are the clips', so the feet and the
#            hip are no longer where v69's were; only the sole on the floor is gameplay's)
#   crawl    (round 23) the hands at the floor while crawling (the palm's centre 0 to 3 px over it), not v69's places
#   swing    hands on the bar: no further from it than before (0.25 px; v69's straight arms fell 0.7 px short, inside the hand)
#   drink    the hand at the mouth while he drinks (within 0.6 px of before's hand-to-mouth offset)
# It also lists every place in the source that reads the skeleton (skel(), LEN), so a reader can see none of them is a hit box.
# Prints one line per pose with a difference, then 'figscan: ok' or 'figscan: FAIL (n)'. Writes figscan.json. Run from dev/tools.
import json, os, re, sys, tempfile, shutil
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
a = [x for x in sys.argv[1:]]
NEW = os.path.abspath(a[0] if len(a) > 0 and a[0] else os.path.join(HERE, '..', 'hourglass-keep.html'))
_old = os.path.join(HERE, 'hk_v69_release.html')
if not os.path.exists(_old):
    _old = os.path.join(HERE, '..', '..', '..', '..', '..', 'dev', 'tools', 'hk_v69_release.html')  # (from a worktree: the main checkout's)
OLD = os.path.abspath(a[1] if len(a) > 1 and a[1] else _old)
OUTJ = a[2] if len(a) > 2 else os.path.join(HERE, 'figscan.json')
EXPORT = 'window.__FS={walkPose:typeof walkPose==="function"?walkPose:null,skel,LEN,PS,mk,lerpPose,crawlPose,swingPose,wallRunIK,wallRunPose,climbFrame,drinkFrame,RP,plantPose,figReach,swordTip,figDraw,PAL_HERO,guardPal,GFX};'
CONTACT = {'hang', 'reach', 'pull', 'press', 'kneelUp', 'kneel', 'slide', 'garde', 'windup', 'lunge', 'parry', 'lowStrike'}
SCAN = r'''()=>{const F=__FS,out=[];F.GFX().hd=true;
 const add=(name,p,ox,oy,kind,extra)=>{const s=F.skel(p),O=[ox||0,(oy||0)-s.hipH],P=q=>[+(q[0]+O[0]).toFixed(3),+(q[1]+O[1]).toFixed(3)];
   const r=F.LEN.hd,ha=p.lean+p.head,hx=Math.sin(ha),hy=-Math.cos(ha),hnx=-hy,hny=hx,m=[s.hd[0]+hnx*r*0.8-hx*r*0.62,s.hd[1]+hny*r*0.8-hy*r*0.62];
   const st=F.swordTip({x:O[0],y:(oy||0),face:1,pose:p,yo:0}),R=F.figReach(1,p);
   // the silhouette at 8x: crown, sole, front and back
   const S=8,W=120,H=120,cv=document.createElement('canvas');cv.width=W*S;cv.height=H*S;const c=cv.getContext('2d');c.scale(S,S);
   const X=60,Y=80;F.figDraw(c,X+(ox||0),Y+(oy||0),1,p,F.PAL_HERO,{sword:!!(kind&&kind.sw),hasSword:true,time:0,mono:'#000'});
   const d=c.getImageData(0,0,W*S,H*S).data;let t=1e9,b=-1,l=1e9,rr=-1;
   for(let yy=0;yy<H*S;yy++)for(let xx=0;xx<W*S;xx++)if(d[(yy*W*S+xx)*4+3]>127){if(yy<t)t=yy;if(yy>b)b=yy;if(xx<l)l=xx;if(xx>rr)rr=xx;}
   out.push(Object.assign({name,kind:kind?kind.k:'',hF:P(s.hF),hB:P(s.hB),fF:P(s.fF),fB:P(s.fB),hip:P([0,0]),sh:P(s.sh),hd:P(s.hd),mouth:P(m),
     swB:[+(st.bx).toFixed(3),+(st.by).toFixed(3)],swT:[+(st.tx).toFixed(3),+(st.ty).toFixed(3)],reachR:+R.right.toFixed(3),reachT:+(R.top+(oy||0)).toFixed(3),
     crown:+(t/S-Y).toFixed(3),sole:+((b+1)/S-Y).toFixed(3),front:+((rr+1)/S-X).toFixed(3),back:+(l/S-X).toFixed(3),hy:p.hy,air:p.air,head:p.head},extra||{}));};
 for(const k of Object.keys(F.PS))add('PS.'+k,F.mk(F.PS[k]),0,0,{k:k,sw:['garde','windup','lunge','parry','lowStrike','slide'].includes(k)});
 for(let i=0;i<8;i++)add('run '+i/8,F.mk(F.RP(i/8)),0,0,{k:'run'});
 for(let i=0;i<8;i++)add('walk '+i/8,F.mk(F.walkPose?F.walkPose(i/8):F.RP(i/8,0.6)),0,0,{k:'walk'});
 for(let i=0;i<4;i++)add('crawl '+i/4,F.crawlPose(i/4),0,0,{k:'crawl'});
 for(const t of [0.27,0.36,0.5,0.63,0.72,0.8,0.855,0.9,0.95,0.99,1.15])add('drink '+t,F.mk(F.drinkFrame(t).p),0,0,{k:t>=0.7&&t<=0.99?'sip':'drink'});
 // climbing onto a ledge: the ledge's surface at y 0, its lip at x 0; he hangs at y 57 (HANG) a little out from it, and stands at 10 in
 const cs={x0:-6,y0:57,x1:10,y1:0};for(let i=0;i<=12;i++){const k=i/12,f=F.climbFrame(cs,k);add('climb '+k.toFixed(2),F.mk(f.p),f.x,f.y,{k:'climb'},{k});}
 for(const [th,om] of [[0,0],[0.5,0],[-0.5,0],[0.8,0],[0,3],[0.3,-2],[-0.6,1.5]]){const p=F.mk(F.swingPose(th,om,0));
   const c=Math.cos(th),sn=Math.sin(th),lift=p.hy-24.5,wx=-34*sn,wy=-34*c+lift,bx=wx*c-wy*sn,by=wx*sn+wy*c,s=F.skel(p);
   add('swing '+th+','+om,p,0,0,{k:'swing'},{bar:Math.max(Math.hypot(s.hF[0]-bx,s.hF[1]-by),Math.hypot(s.hB[0]-bx,s.hB[1]-by))});}
 for(const r of [0,20,40,55,69])add('wallrun '+r,F.mk(F.wallRunIK(r,null)),0,0,{k:'wallrun'});
 for(const ph of [0,0.25,0.5])add('wallrunPose '+ph,F.mk(F.wallRunPose(ph,ph)),0,0,{k:'wallrun'});
 add('plant',F.mk(F.plantPose()),0,0,{k:'plant'});
 return {LEN:F.LEN,poses:out};}'''


def prep(src, tmp, tag):
    s = open(src, encoding='utf-8').read()
    i = s.find('window.__HK={')
    assert i > 0, 'no __HK in ' + src
    fn = os.path.join(tmp, '_figscan_%s.html' % tag)
    open(fn, 'w', encoding='utf-8').write(s[:i] + EXPORT + s[i:])
    return fn, s


def readers(s):
    # every function that reads the skeleton or its lengths
    out = []
    cur = None
    for ln, line in enumerate(s.split('\n'), 1):
        m = re.match(r'\s*function ([A-Za-z0-9_]+)\(', line)
        if m:
            cur = m.group(1)
        if 'skel(' in line or 'LEN.' in line:
            if not out or out[-1][0] != cur:
                out.append([cur, ln])
    return out


D = lambda a, b: ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

if __name__ == '__main__':
    tmp = tempfile.mkdtemp(prefix='figscan', dir=HERE)
    try:
        R = {}
        src = {}
        with sync_playwright() as p:
            b = p.chromium.launch()
            for tag, f in (('old', OLD), ('new', NEW)):
                fn, src[tag] = prep(f, tmp, tag)
                pg = b.new_page()
                errs = []
                pg.on('pageerror', lambda e: errs.append(str(e)))
                pg.goto('file://' + fn)
                pg.wait_for_timeout(600)
                R[tag] = pg.evaluate(SCAN)
                R[tag]['errors'] = errs
                pg.close()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    O = {q['name']: q for q in R['old']['poses']}
    N = {q['name']: q for q in R['new']['poses']}
    print('LEN before', R['old']['LEN'])
    print('LEN after ', R['new']['LEN'])
    fails = []
    rows = []
    for k, n in N.items():
        o = O.get(k)
        if not o:
            continue
        kd = n['kind']
        contact = kd in CONTACT or kd in ('swing', 'sip')
        both = kd in ('hang', 'reach', 'pull', 'press', 'kneelUp', 'kneel', 'slide', 'climb')
        d = {j: D(n[j], o[j]) for j in ('hF', 'hB', 'fF', 'fB', 'hip', 'sh', 'hd', 'mouth', 'swT')}
        line = []
        for j, v in d.items():
            if v > 0.25:
                line.append('%s %.2f' % (j, v))
        for j in ('crown', 'sole', 'front', 'back', 'reachR', 'reachT'):
            v = n[j] - o[j]
            if abs(v) > 0.25:
                line.append('%s %+.2f' % (j, v))
        bad = []
        tol = 0.75 if kd in ('lunge', 'lowStrike') else 0.35  # (the lunge's straight arm cannot reach quite as far from the lower shoulder)
        if contact and kd not in ('swing', 'sip') and (d['hF'] if not both else max(d['hF'], d['hB'])) > tol:
            bad.append('hands moved (contact)')
        lim = o['crown'] if kd in ('crawl', 'jumpLow', 'jumpLowS', 'slide') else min(o['crown'], O['PS.stand']['crown'])
        if n['crown'] < lim - 0.25 and kd != 'swing':  # (swinging he is turned on the rope, in open air under the bar)
            bad.append('crown higher by %.2f' % (lim - n['crown']))
        if o['air'] == 0 and n['air'] == 0 and (abs(n['sole'] - o['sole']) > 0.5 if kd != 'crawl' else not -0.25 <= n['sole'] <= max(o['sole'], 2.5)):
            bad.append('sole off the floor %+.2f' % (n['sole'] - o['sole']))
        if kd == 'climb' and n['k'] < 0.7:  # (round 23: on the lip while pulling up (v69's hanging hand), then on the floor inside it until he kneels up)
            lip = O['climb 0.00']['hF']
            ok = all(D(n[h], lip) < 2.2 for h in ('hF', 'hB')) if n['k'] <= 0.36 else all(-3.2 <= n[h][1] <= 0.5 and n[h][0] >= lip[0] - 0.5 for h in ('hF', 'hB'))
            if not ok:
                bad.append('hands off the ledge %s %s' % (n['hF'], n['hB']))
        if kd == 'crawl' and not all(-3.2 <= n[h][1] <= 0.3 for h in ('hF', 'hB')):
            bad.append('hands off the floor %.2f %.2f' % (n['hF'][1], n['hB'][1]))
        if kd == 'swing':
            line.append('bar %.2f (before %.2f)' % (n['bar'], o['bar']))
            if n['bar'] > o['bar'] + 0.25:
                bad.append('hands off the bar %.2f' % n['bar'])
        if kd == 'sip':
            om = [o['hF'][0] - o['mouth'][0], o['hF'][1] - o['mouth'][1]]
            nm = [n['hF'][0] - n['mouth'][0], n['hF'][1] - n['mouth'][1]]
            if D(om, nm) > 0.6:
                bad.append('hand to mouth off by %.2f' % D(om, nm))
        rows.append({'pose': k, 'kind': kd, 'contact': contact, 'diff': line, 'bad': bad,
                     'old': {j: o[j] for j in ('hF', 'hB', 'crown', 'sole', 'reachT', 'hy')}, 'new': {j: n[j] for j in ('hF', 'hB', 'crown', 'sole', 'reachT', 'hy')}})
        if line or bad:
            print('%-18s %s%s' % (k, ', '.join(line) or '-', ('   <<< ' + '; '.join(bad)) if bad else ''))
        if bad:
            fails.append(k)
    st = N['PS.stand']
    so = O['PS.stand']
    print('standing height (sole to crown): before %.2f, after %.2f' % (so['sole'] - so['crown'], st['sole'] - st['crown']))
    print('skeleton readers, before:', ', '.join('%s:%d' % (f, l) for f, l in readers(src['old'])))
    print('skeleton readers, after: ', ', '.join('%s:%d' % (f, l) for f, l in readers(src['new'])))
    errs = R['old']['errors'] + R['new']['errors']
    if errs:
        print('page errors', errs[:4])
        fails.append('errors')
    json.dump({'LEN': {'old': R['old']['LEN'], 'new': R['new']['LEN']}, 'rows': rows, 'fails': fails,
               'readers': {'old': readers(src['old']), 'new': readers(src['new'])}}, open(OUTJ, 'w'), indent=1)
    print('figscan: ok' if not fails else 'figscan: FAIL (%d) %s' % (len(fails), ', '.join(fails)))
