# lowceil.py [file.html] [shots] [classic]: jumps under stone at the prince's height (a corridor one storey tall).
# Builds small test rooms in a generated floor and jumps in them (standing and running): in a low room the jump must be the
# low ducked leap, and nothing of his drawn figure (figReach's top, as drawn) may go into a WALL cell at any frame; in an
# open room the jumps must carry exactly as far as before (fixed numbers, from v59). 'shots': also saves a frame strip
# per room (lowceil_<room>.png, Torchlight unless 'classic'). Run from dev/tools.
import os, sys, json
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html'))
SHOTS = 'shots' in a
MODE = 'classic' if 'classic' in a else 'torch'
ONLY = next((x[5:].split(',') for x in a if x.startswith('only=')), None)
TAG = next((x[4:] for x in a if x.startswith('tag=')), '')
# a room: rows R-3..R+2 over columns C0-2..C0+21 are rebuilt. 'o' open (floor), '_' floor with stone overhead, '.' a gap
# (a floor a storey down under it), 'L' open floor a storey down (no gap). The prince starts at column C0+START, facing right.
ROOMS = {
  # name: (row R plan, row R-1 overhead: '#' stone or ' ' open; the start column; 'stand' or 'run')
  'low_stand':     ('_' * 22, '#' * 22, 6, 'stand'),
  'low_run':       ('_' * 22, '#' * 22, 3, 'run'),
  'low_gap_stand': ('_' * 8 + '.' + '_' * 13, '#' * 22, 7, 'stand'),
  'low_gap_run':   ('_' * 9 + '..' + '_' * 11, '#' * 22, 3, 'run'),
  'low_gap2_stand':('_' * 8 + '..' + '_' * 12, '#' * 22, 7, 'stand'),
  'low_gap3_run':  ('_' * 9 + '...' + '_' * 10, '#' * 22, 3, 'run'),
  'low_spike_run': ('_' * 9 + 'ss' + '_' * 11, '#' * 22, 3, 'run'),
  'into_low_stand':('_' * 22, ' ' * 8 + '#' * 14, 7, 'stand'),   # jumps from under open air in under the stone
  'into_low_run':  ('_' * 22, ' ' * 9 + '#' * 13, 4, 'run'),
  'stepdown_stand':('_' * 8 + 'LLLLLLLLLLLLLL', ' ' * 9 + '#' * 13, 7, 'stand'),  # the bot's case: a jump down a storey
  'stepdown_run':  ('_' * 8 + 'LLLLLLLLLLLLLL', ' ' * 10 + '#' * 12, 4, 'run'),
  'slab_stand':    ('_' * 22, 'f' * 22, 6, 'stand'),   # an upper floor overhead: its slab is the ceiling
  'slab_run':      ('_' * 22, 'f' * 22, 3, 'run'),
  'slab_gap_run':  ('_' * 9 + '..' + '_' * 11, 'f' * 22, 3, 'run'),
  'slab_gap2_stand':('_' * 8 + '..' + '_' * 12, 'f' * 22, 7, 'stand'),
  'into_slab_run': ('_' * 22, ' ' * 9 + 'f' * 13, 4, 'run'),
  'open_stand':    ('_' * 22, ' ' * 22, 6, 'stand'),
  'open_run':      ('_' * 22, ' ' * 22, 3, 'run'),
  'open_gap_run':  ('_' * 9 + '..' + '_' * 11, ' ' * 22, 3, 'run'),
}
JS = r'''([name,plan,over,start,kind,shots])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;
  const L=H.load(2,4321,true);H.banner=null;const R=4,C0=30,W=2,E=0,FL=1,set=(c,r,v)=>{L.base[r*L.cols+c]=v;L.feat[r*L.cols+c]=null;};
  for(let c=C0-2;c<=C0+22;c++)for(let r=R-3;r<=R+2;r++)set(c,r,W);
  for(let i=0;i<22;i++){const c=C0+i,p=plan[i],o=over[i]!=='#';
    if(p==='_'||p==='s'){set(c,R,FL);if(p==='s')L.feat[R*L.cols+c]={t:'spikes',s:0,tm:0};}
    else if(p==='.'){set(c,R,E);set(c,R+1,FL);}else if(p==='L'){set(c,R,E);set(c,R+1,FL);}
    if(over[i]==='f'){set(c,R-1,FL);set(c,R-2,E);}else if(o){set(c,R-1,E);set(c,R-2,E);}}
  L.dyn=L.dyn.filter(d=>d.r<R-3||d.r>R+2||d.c<C0-2||d.c>C0+22);
  for(const f of ['spikes'])for(let i=0;i<22;i++){const ft=L.feat[R*L.cols+C0+i];if(ft&&ft.t==='spikes')L.dyn.push({c:C0+i,r:R,f:ft});}
  H.clearRooms();const P=H.P;P.inv=1e9;P.x=(C0+start)*32+16;P.y=(R+1)*64-4;P.fallY=P.y;P.state='stand';P.face=1;P.hp=P.hp||3;
  H.cam.snap=true;H.tick(3);const fr=[];let jumped=false,air=false,peak=1e9,low=null,pen=0,penAt=null,headPen=0;
  const B=(c,r)=>c<0||c>=L.cols||r<0?2:r>=L.rows?0:L.base[r*L.cols+c];
  if(kind==='run'){H.setKey('kb','r',true);}
  for(let i=0;i<240;i++){
    if(!jumped&&(kind==='stand'||(P.state==='run'&&P.x>=(C0+start+3)*32+16))){H.setKey('kb','j',true);H.tick(1);H.setKey('kb','j',false);jumped=true;}
    else H.tick(1);
    if(jumped&&kind==='run'&&P.state==='air')H.setKey('kb','r',false);
    if(jumped&&(P.state==='air'||P.state==='jumpPrep'))air=true;
    if(P.state==='air'&&low===null)low=!!P.lowJump;
    if(jumped){const R0=H.figReach(P.face,P.pose),yt=P.y+(P.yo||0)+(P.rdy||0)+R0.top,hy=P.y-(P.lowJump?44:52),xs=[P.x-8,P.x,P.x+8];
      for(const x of xs){const c=Math.floor(x/32),b=B(c,R-1),cy=R*64+(b===1?5:0);if((b===2||b===1)&&B(c,R)!==2&&yt<cy){const d=cy-yt;if(d>pen){pen=d;penAt=[i,Math.round(x),Math.round(yt)];}}
        if((b===2||b===1)&&B(c,R)!==2&&hy<cy)headPen=Math.max(headPen,cy-hy);}
      peak=Math.min(peak,yt);
      if(shots&&fr.length<12&&(air||P.state==='jumpPrep')&&i%3===0){H.GLP&&(H.GLP.pipe=false);H.render();H.render();const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),Rc=cv.getBoundingClientRect();
        fr.push([Rc.left+(P.x*X.VZ-X.camD)/cv.width*Rc.width,Rc.top+((P.y-30)*X.VZ-X.camDY)/cv.height*Rc.height,i,P.state,!!P.lowJump]);
        window.__shot=fr[fr.length-1];return {more:true,name};}
    }
    if(air&&(P.state==='stand'||P.state==='dead'||P.state==='land'&&false))break;
  }
  H.setKey('kb','r',false);
  return {name,state:P.state,dist:Math.round(P.x-((C0+start)*32+16)),col:Math.floor(P.x/32)-C0,row:Math.floor((P.y-1)/64)-R,low,pen:Math.round(pen*10)/10,headPen:Math.round(headPen*10)/10,penAt,peak:Math.round(peak-R*64),hp:P.hp,cause:P.cause};}'''
# (with shots the run is replayed from the start for every frame taken: the jump is deterministic, so frame k is the same)
SHOTJS = JS.replace("fr.length<12", "fr.length<=window.__k&&fr.length<12").replace("window.__shot=fr[fr.length-1];return {more:true,name};", "if(fr.length>window.__k){window.__shot=fr[fr.length-1];return {more:true,name};}")
with sync_playwright() as p:
    # (a plain launch for the check, so suite.py's shared browser can run it; the pictures ask for this Mac's GPU)
    b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist']) if SHOTS and MODE == 'torch' else p.chromium.launch()
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2)
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    def fresh():
        pg.goto('file://' + os.path.abspath(SRC)); pg.wait_for_timeout(300)
        pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true)")
        pg.evaluate("m=>{__HK.S.set.lightMode=m}", MODE)
    fresh()
    res = {}
    for name, (plan, over, start, kind) in ROOMS.items():
        r = pg.evaluate(JS, [name, plan, over, start, kind, False])
        res[name] = r
        print(json.dumps(r))
    if SHOTS:
        from PIL import Image, ImageDraw
        for name, (plan, over, start, kind) in ROOMS.items():
            if name.startswith('open_gap') or (ONLY and name not in ONLY): continue
            tiles = []
            for k in range(12):
                pg.evaluate('k=>{window.__k=k}', k)
                r = pg.evaluate(SHOTJS, [name, plan, over, start, kind, True])
                if not r.get('more'): break
                x, y, i, st, low = pg.evaluate('window.__shot')
                pg.screenshot(path=os.path.join(HERE, '_lc_tmp.png'))
                im = Image.open(os.path.join(HERE, '_lc_tmp.png')).convert('RGB')
                cx, cy = int(x * 2), int(y * 2)
                t = im.crop((cx - 200, cy - 260, cx + 200, cy + 200)).resize((240, 276))
                ImageDraw.Draw(t).text((4, 4), '%d %s%s' % (i, st, ' low' if low else ''), fill=(255, 255, 0))
                tiles.append(t)
            if tiles:
                sh = Image.new('RGB', (len(tiles) * 242, 276))
                for j, t in enumerate(tiles): sh.paste(t, (j * 242, 0))
                sh.save(os.path.join(HERE, 'lowceil_%s%s.png' % (TAG, name)))
        os.remove(os.path.join(HERE, '_lc_tmp.png'))
    b.close()
print('errors', errs[:3])
OPEN = {'open_stand': (59, -7), 'open_run': (195, -16), 'open_gap_run': (265, -16)}  # (distance, peak of the drawn figure: v59)
bad = []
for name, r in res.items():
    if name in OPEN:
        if r['low'] or r['dist'] != OPEN[name][0] or r['peak'] < OPEN[name][1] or r['state'] != 'stand':  # (round 23: the drawn peak may be lower, never higher)
            bad.append('%s: open jump changed (dist %s peak %s low %s)' % (name, r['dist'], r['peak'], r['low']))
    else:
        if not r['low']: bad.append('%s: not the low leap' % name)
        if r['pen'] > 0 or r['headPen'] > 0: bad.append('%s: drawn %.1f px (head %.1f) into the ceiling at %s' % (name, r['pen'], r['headPen'], r['penAt']))
        if r['state'] == 'dead': bad.append('%s: died (%s)' % (name, r['cause']))
for x in bad: print(x)
print('ALL OK' if not bad and not errs else 'FAILURES')
sys.exit(1 if bad or errs else 0)
