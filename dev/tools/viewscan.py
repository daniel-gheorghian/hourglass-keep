# viewscan.py [file.html] [lo hi] [seeds]: round 47b's same-storey check (owner: "the courts - the background they show isn't in sync with what
# the windows show"; chose C, one horizon per storey). For every court (not a light well) on floors lo..hi (default 3-48) and seeds (default 1,2):
# the openings of its storey (its own bays, the windows in the headroom row over its floor, the open arches and open breaches whose foot is on that
# floor) within 16 cells of it. With the camera at its rest on that floor and 40 px and 100 px above and 40 px below it, each layer of the theme's
# view (BGART, the stars and every land layer) must stand at the same screen y in every one of them (bgLayerY on each opening's bgAnchor): spread
# at most 0.5 px. (Its x is the same in every opening by construction: paintBackdrop's x is -(camera x f) mod 640 less the shake, no term of the
# opening.) And the court's own art must stand on the same horizon: each court layer's eye line (ctLayersOf) at the windows' eye line for its depth
# (bgEyeY on the window's anchor), within 0.5 px. An opening that touches one of another storey (an arch over a breach below) is one hole with
# it and takes the largest one's anchor (bgAnchors, round 25e): it is left out. A build without ctLayersOf (v88 and before) is measured by its own formula: the court's strips'
# eye 44 px over the floor's back edge moved by BG_VK, against the windows' horizon (the farthest land's foot, bgLayerY(0)+BG_BASE).
# Prints the worst spreads by floor band and 'viewscan: ok', or the failing cases and 'viewscan: FAIL'. v88: the windows stand a storey's 0.8-0.85
# (51-54 px) above the arches and courts, and the court's eye 60-150 px above the windows' horizon. Run from dev/tools.
import os, sys
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = os.path.abspath(next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html')))
NUM = [int(x) for x in a if x.isdigit()]
LO, HI = (NUM[0], NUM[1]) if len(NUM) >= 2 else (3, 48)
SEEDS = [int(s) for s in next((x for x in a if ',' in x), '1,2').split(',')]
JS = r'''([n,sd])=>{const H=__HK,L=H.load(n,sd,true),TW=32,TH=64,SURF=r=>(r+1)*64-4,out=[];const art=H.BGART[L.theme.look]||H.BGART.nun,BASE=176;
  const lys=[{f:0,sky:1}].concat(art.layers.filter(q=>q.kind!=='stars').map(q=>({f:q.f,sky:q.kind==='clouds'?1:0})));
  for(const k of L.courts){if(k.k==='well')continue;const yF=SURF(k.r),x0=(k.c0-16)*TW,x1=(k.c1+17)*TW;
    const ops=H.openingsIn(x0,x1,(k.r-1)*TH,k.r*TH+TH-1).filter(o=>{const yb=o[1]+o[3],row=Math.floor((yb-1)/TH);return o[4]===1?row===k.r-1:row===k.r;})
      .filter(o=>{const fy=H.bgFoot?H.bgFoot(o):o[1]+o[3],own=Math.max(0,Math.min(L.rows*TH-192,SURF(Math.floor((fy-1)/TH))-115.2));return Math.abs(H.bgAnchor(o)-own)<0.01;}); // (an opening that touches one of another storey is one hole with it and takes the largest's anchor: left out)
    const kind=o=>o[4]===1?'window':o[0]>=k.c0*TW&&o[0]<(k.c1+1)*TW&&o[1]===(k.r-1)*TH?'court':'arch';
    const win=ops.filter(o=>kind(o)==='window');const rest=Math.max(0,Math.min(L.rows*TH-192,yF-115.2));
    for(const dy of [0,-40,-100,40]){const cy=Math.max(0,Math.min(L.rows*TH-192,rest+dy));H.BGV.y=cy;H.BGV.x=k.c0*TW;H.BGV.sx=0;
      let worst=0,wk='';for(const ly of lys){let lo=1e9,hi=-1e9,lw='',hw='';for(const o of ops){const y=H.bgLayerY(ly.f,H.bgAnchor(o),art.inner,0,ly.sky);if(y<lo){lo=y;lw=kind(o);}if(y>hi){hi=y;hw=kind(o);}}
        if(ops.length>1&&hi-lo>worst){worst=hi-lo;wk='f '+ly.f+' '+lw+' vs '+hw;}}
      let cw=null;if(win.length){const anW=H.bgAnchor(win[0]);cw=0;
        if(H.ctLayersOf){for(const q of H.ctLayersOf(k,k.c0*TW,416,H.VS,cy*H.VS)){const e=(q.eye-cy)-H.bgEyeY(q.f,anW);if(Math.abs(e)>Math.abs(cw))cw=e;}}
        else{const fl=yF-4,hz=H.bgLayerY(0,anW)+BASE;for(const f of [0.7,0.18,0.5]){const e=(fl-44+H.BG_VK*(1-f)*(cy-Math.max(0,Math.min(L.rows*TH-192,yF-115.2)))-cy)-hz;if(Math.abs(e)>Math.abs(cw))cw=e;}}}
      out.push({c:k.c0,r:k.r,k:k.k,dy,ops:ops.length,win:win.length,worst:+worst.toFixed(2),wk,cw:cw===null?null:+cw.toFixed(2)});}}
  return {theme:H.themeName(n),out};}'''
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 852, 'height': 393}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.goto('file://' + SRC); pg.wait_for_timeout(700)
    bad, rows, nopen, ncw = [], {}, 0, 0
    for n in range(LO, HI + 1):
        for s in SEEDS:
            r = pg.evaluate(JS, [n, s]); band = (n - 1) // 12
            for q in r['out']:
                rw = rows.setdefault(band, [0, 0.0, 0.0, 0]); rw[0] += 1; rw[1] = max(rw[1], q['worst'])
                if q['cw'] is not None: rw[2] = max(rw[2], abs(q['cw'])); ncw += 1
                if q['ops'] > 1: nopen += 1
                if q['worst'] > 0.5 or (q['cw'] is not None and abs(q['cw']) > 0.5):
                    bad.append('floor %d seed %d court %d,%d %s dy %d: layers %.2f px (%s), court eye %s px' % (n, s, q['c'], q['r'], q['k'], q['dy'], q['worst'], q['wk'], q['cw']))
    print('band     courts x views  worst layer spread  worst court eye off the windows\' horizon')
    for band in sorted(rows): rw = rows[band]; print('%2d-%-3d   %5d            %8.2f            %8.2f' % (band * 12 + 1, band * 12 + 12, rw[0], rw[1], rw[2]))
    print('views with two or more openings: %d, with a window to hold the court to: %d' % (nopen, ncw))
    for x in bad[:20]: print('  ' + x)
    if errs: print('page errors', errs[:3])
    print('viewscan: ' + ('ok' if not bad and not errs and nopen and ncw else 'FAIL (%d)' % len(bad)))
    b.close()
