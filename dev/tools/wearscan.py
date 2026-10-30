# wearscan.py [file.html] [lo hi] [seeds]: round 49c's wear marks and bones of earlier thieves keep their rules (no picture of the game;
# the marks themselves are drawn on a scratch canvas to measure them). For each floor lo..hi (default 1-48) and seeds 1..K (default 3;
# floor seeds 700000+97n+13s, run2's), against the build's own wearList():
#   scuffs  on every wall the route runs up (each 'wallrun' seg) and nowhere else: the wall cell and the one over it are wall, the run-up
#           cell before it floor with two storeys of headroom, the ledge on top (r-2) floor; drawn only inside the wall's front face
#   grooves on every movable block's track and nowhere else: the cells lo..hi of its row it can stand on (not wall), every one of them;
#           drawn only inside each cell's floor top face (so never on a lip or a face: the block, drawn live, stands over them)
#   bones   at most one set a kind a floor, each at the first trap of its kind by the route's order (this scan's own list of the traps and
#           of the segs' order): a walled spike pit's stake cell (met by a fall), a banner shaft's foot, a slicer's cell, a sand lift with
#           its spike pit; a kind with a trap on the floor has its set. On a route tile (banner foot, slicer) every drawn pixel lies behind
#           his walking line (d >= WB_DR, 0.55: he walks in front of them) and under WB_HR px over the floor; a pit's set inside its cell
# Prints the counts and 'wearscan: ok' or 'wearscan: FAIL' with the first faults. Run from dev/tools.
import os, sys
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = os.path.abspath(next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html')))
NUM = [int(x) for x in a if x.isdigit()]
LO, HI = (NUM[0], NUM[1]) if len(NUM) >= 2 else (1, 48)
NS = NUM[2] if len(NUM) >= 3 else 3

SCAN = r'''([n,sd])=>{const H=__HK,L=H.load(n,sd,false),W=H.wearList(),C=L.cols,TW=32,TH=64,DX=16,DY=8,HX=8,SURF=r=>(r+1)*TH-4,bad=[],B=(c,r)=>c<0||c>=C||r<0?2:r>=L.rows?0:L.base0[r*C+c],F=(c,r)=>L.feat[r*C+c];
 const tag=(s)=>bad.push('fl'+n+' s'+sd+': '+s);
 // the route's order, this scan's own: the first seg whose box (a cell either side, a row over, three under) holds the cell
 const ord=(c,r)=>{for(let i=0;i<L.segs.length;i++){const s=L.segs[i],a=Math.min(s.c0,s.c1),b=Math.max(s.c0,s.c1),r0=Math.min(s.r0,s.r1),r1=Math.max(s.r0,s.r1);if(c>=a-1&&c<=b+1&&r>=r0-1&&r<=r1+3)return i;}return 1e9;};
 const dirOf=i=>{const s=L.segs[i];return s?(s.dir||Math.sign(s.c1-s.c0)||1):1;};
 // scuffs
 const wr=L.segs.filter(s=>/wallrun$/.test(s.k));if(W.scuff.length!==wr.length)tag('scuffs '+W.scuff.length+' for '+wr.length+' wall runs');
 for(const q of W.scuff){const c=q.c,r=q.r,d=q.s;if(!wr.some(s=>s.r0===r&&(s.dir||1)===d))tag('scuff at '+c+','+r+' on no wall run');
   if(B(c,r)!==2||B(c,r-1)!==2||B(c-d,r)!==1||B(c-d,r-1)===2||B(c-d,r-2)===2||B(c,r-2)===2)tag('scuff wall '+c+','+r+' not a wall run up two storeys');}
 // grooves
 const blk=L.ext.blocks;if(W.groove.length!==blk.length)tag('groove tracks '+W.groove.length+' for '+blk.length+' blocks');
 for(const b of blk){const q=W.groove.find(g=>g.r===b.r&&g.lo===b.lo&&g.hi===b.hi);if(!q){tag('no grooves for the block at '+b.c+','+b.r);continue;}
   const want=[];for(let c=b.lo;c<=b.hi;c++)if(B(c,b.r)!==2)want.push(c);if(want.join()!==q.cells.join())tag('groove cells '+q.cells+' for the track '+want);}
 for(const [k,arr] of W.floor)for(const g of arr)if(g.k==='groove'&&!blk.some(b=>b.r===((k/C)|0)&&g.c>=b.lo&&g.c<=b.hi))tag('a groove off a track at '+(k%C)+','+((k/C)|0));
 // the traps of each kind, this scan's own
 const T={pit:[],banner:[],slicer:[],sand:[]};
 for(let r=1;r<L.rows;r++)for(let c=1;c<C-1;c++){const f=F(c,r);if(!f)continue;
   if(f.t==='spikes'&&!f.sl&&B(c,r-1)===0&&!(L._ctP&&L._ctP.has(r*C+c))){let a=c,b=c;const sp=x=>{const g=F(x,r);return g&&g.t==='spikes'&&!g.sl&&B(x,r-1)===0;};while(sp(a-1))a--;while(sp(b+1))b++;
     if(B(a-1,r)===2&&B(b+1,r)===2&&a===c)T.pit.push({c0:a,c1:b,r,o:ord(a,r)});}
   if(f.t==='banner'&&!(F(c,r-1)&&F(c,r-1).t==='banner')){let rb=r;while(F(c,rb+1)&&F(c,rb+1).t==='banner')rb++;const rf=rb+1;if(rf<L.rows&&B(c,rf)!==2&&(B(c,rf)===1||B(c,rf+1)===2))T.banner.push({c,r:rf,o:ord(c,r)});}
   if(f.t==='chomp'){const o=ord(c,r);T.slicer.push({c,r,o:o+(dirOf(o)>0?c:-c)*1e-6});}}
 for(const lf of L.lifts)if(lf.sand&&lf.rD!==undefined)T.sand.push({lf,c:lf.sc,r:lf.rD,o:ord(lf.sc,lf.rT)});
 const cnt={};for(const k in T){const got=W.bones.filter(b=>b.k===k);cnt[k]=[T[k].length,got.length];
   if(got.length>1)tag(got.length+' sets of '+k);if(T[k].length&&!got.length)tag('no '+k+' set ('+T[k].length+' traps)');if(!T[k].length&&got.length)tag(k+' set with no trap');
   if(got.length&&T[k].length){let f=T[k][0];for(const q of T[k])if(q.o<f.o)f=q;const g=got[0];
     if(k==='pit'?!(g.r===f.r&&g.c>=f.c0&&g.c<=f.c1):k==='sand'?g.lf!==f.lf:!(g.c===f.c&&g.r===f.r))tag(k+' set at '+g.c+','+g.r+' not at the first ('+(f.c0!==undefined?f.c0:f.c)+','+f.r+')');}}
 // the drawn marks, on a scratch canvas at 4x: where their pixels lie
 const cv=window.__WSC||(window.__WSC=document.createElement('canvas'));cv.width=480;cv.height=480;const g=cv.getContext('2d',{willReadFrequently:true});
 const draw=(fn)=>{g.setTransform(1,0,0,1,0,0);g.clearRect(0,0,480,480);g.setTransform(4,0,0,4,0,0);fn();g.setTransform(1,0,0,1,0,0);return g.getImageData(0,0,480,480).data;};
 const X0=40,YS=80; // the cell's left and floor line on the scratch canvas (canvas px / 4)
 const each=(D,fn)=>{for(let y=0;y<480;y++)for(let x=0;x<480;x++)if(D[(y*480+x)*4+3]>40)fn(x/4,y/4);};
 for(const [k,arr] of W.floor){const c=k%C,r=(k/C)|0;
   for(const q of arr){if(q.k==='groove'){const D=draw(()=>H.wearFloor(g,X0,YS,c,r));let out=0;
       each(D,(x,y)=>{const d=(YS+4-y)/DY,xl=X0-HX+d*DX,xr=X0+TW-HX+d*DX;if(d<-0.15||d>1.15||x<xl-2||x>xr+2)out++;});if(out>8)tag('grooves at '+c+','+r+' off the floor top ('+out+' px)');break;}}
   const bs=arr.filter(q=>q.k!=='groove');if(!bs.length)continue;const q=bs[0];
   const D=draw(()=>H.wearFloor(g,X0,YS,c,r));let front=0,high=0,side=0;
   const route=q.k!=='pit',lim=YS+(0.5-H.WB_DR)*DY;
   each(D,(x,y)=>{if(route&&y>lim+1)front++;const d=(YS+4-y)/DY;if(y<YS+(0.5-Math.min(1,Math.max(0,d)))*DY-H.WB_HR-4.5)high++;if(x<X0-HX-0.5||x>X0+TW+HX+0.5)side++;});
   if(front>4)tag(q.k+' set at '+c+','+r+': '+front+' px in front of his walking line');if(high>4)tag(q.k+' set at '+c+','+r+': '+high+' px too high');if(side>4)tag(q.k+' set at '+c+','+r+': '+side+' px outside its cell');}
 // the scuffs drawn on a face: inside it
 for(const q of W.scuff)for(const rr of [q.r,q.r-1]){const D=draw(()=>H.wearFace(g,X0-HX,YS-60,q.c,rr));let out=0,any=0;each(D,(x,y)=>{any++;if(x<X0-HX-0.5||x>X0-HX+TW+0.5)out++;});
   if(out>4)tag('scuffs at '+q.c+','+rr+' off the face');if(rr===q.r&&!any)tag('no scuffs drawn on '+q.c+','+rr);}
 return {bad,cnt,sc:W.scuff.length,gr:W.groove.length,gc:W.groove.reduce((s,q)=>s+q.cells.length,0)};}'''

if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('file://' + SRC); pg.wait_for_timeout(600)
        pg.evaluate("()=>{window.__HKfreeze=true;}")
        bad, tot, floors = [], {'scuff': 0, 'track': 0, 'cells': 0}, 0
        kinds = {k: [0, 0, 0] for k in ('pit', 'banner', 'slicer', 'sand')}  # traps, sets, floors with the kind
        for n in range(LO, HI + 1):
            for s in range(1, NS + 1):
                r = pg.evaluate(SCAN, [n, 700000 + 97 * n + 13 * s]); floors += 1
                bad += r['bad']; tot['scuff'] += r['sc']; tot['track'] += r['gr']; tot['cells'] += r['gc']
                for k, (nt, ng) in r['cnt'].items(): kinds[k][0] += nt; kinds[k][1] += ng; kinds[k][2] += 1 if nt else 0
        b.close()
    print('floors %d (%d-%d x %d seeds)' % (floors, LO, HI, NS))
    print('scuffed walls %d, block tracks %d (%d cells grooved)' % (tot['scuff'], tot['track'], tot['cells']))
    for k, (nt, ng, nf) in kinds.items(): print('bones %-7s %4d sets (floors with the trap %d, traps %d)' % (k, ng, nf, nt))
    if errs: bad += ['page error: ' + e for e in errs[:5]]
    for x in bad[:20]: print('  ' + x)
    print('wearscan: ok' if not bad else 'wearscan: FAIL (%d)' % len(bad))
    sys.exit(1 if bad else 0)
