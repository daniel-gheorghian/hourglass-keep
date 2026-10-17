import json,sys,os
from playwright.sync_api import sync_playwright
# every floor jump the bot makes: does his head (P.y-52, or -44 in the low leap) ever go into a WALL cell? prints the cases with a map
WT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
lo,hi,seeds=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3])
src=sys.argv[4] if len(sys.argv)>4 and sys.argv[4]!='-' else WT+'/hourglass-keep.html'
FEAT=sys.argv[5] if len(sys.argv)>5 and sys.argv[5]!='-' else None  # e.g. obstacle:saw
SEEDS=[int(x) for x in sys.argv[6].split(',')] if len(sys.argv)>6 else None
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390})
    pg.goto('file://'+os.path.abspath(src)); pg.wait_for_timeout(300); pg.add_script_tag(path=WT+'/tools/bot.js')
    out=[];tot=0;bad=0;lows=0
    for n in range(lo,hi+1):
      for s in range(seeds):
        seed=SEEDS[s] if SEEDS else 700000+n*97+s*13
        pg.evaluate('f=>{window.__FEAT=f?{[f.split(":")[0]]:f.split(":")[1]}:undefined}',FEAT)
        r=pg.evaluate('''([n,seed])=>{const H=__HK;let cur=null;const J=[];
          const B=(L,c,r)=>c<0||c>=L.cols||r<0?2:r>=L.rows?0:L.base[r*L.cols+c];
          const stop=H=>{const P=H.P,L=H.L;
            if(P.state==='air'&&(P.jumpKind==='run'||P.jumpKind==='stand')){
              if(!cur){const row=Math.floor((P.y-1)/64);cur={x0:Math.round(P.x),row,kind:P.jumpKind,low:!!P.lowJump,pen:0,face:P.face,map:[]};
                const c0=Math.floor(P.x/32);for(let r=row-1;r<=row+1;r++){let s='';for(let c=c0-4;c<=c0+6;c++){const cc=P.face>0?c:2*c0-c,b=B(L,cc,r),f=L.feat[r*L.cols+cc];s+=b===2?'#':b===1?(f?f.t[0]:'_'):'.';}cur.map.push(s);}}
              const hy=P.y-(P.lowJump?44:52),fr=Math.floor((P.y-1)/64);
              const cY=(c,r)=>{for(let k=1;k<=2;k++){const b=B(L,c,r-k);if(b===2)return (r-k+1)*64;if(b===1)return (r-k+1)*64+5;}return -1e9;};
              for(const dx of [-6,0,6]){const c=Math.floor((P.x+dx)/32);if(B(L,c,fr)===2)continue;const cy=cY(c,fr);if(hy<cy){cur.pen=Math.max(cur.pen,Math.round(cy-hy));cur.slab=cur.slab||B(L,c,Math.round(cy/64)-1)===1;}}
            } else if(cur){cur.x1=Math.round(P.x);cur.end=P.state;J.push(cur);cur=null;}
            return false;};
          window.__hurts=[];const res=runBot(n,seed,{stop});return {ok:res.ok,why:res.why,J:J,frames:res.frames,hurt:res.hurt,h:window.__hurts};}''',[n,seed])
        B=[j for j in r['J'] if j['pen']>0]
        tot+=len(r['J']);bad+=len(B);lows+=sum(1 for j in r['J'] if j['low'])
        for j in B: j['n']=n;j['seed']=seed;out.append(j)
        print(n,seed,r['ok'],r.get('why'),'frames',r.get('frames'),'jumps',len(r['J']),'low',sum(1 for j in r['J'] if j['low']),'head in stone',len(B),'hurt',r.get('hurt'),r.get('h'),flush=True)
    b.close()
print('total jumps',tot,'low',lows,'head in stone',bad)
for j in out:
    m=j.pop('map');print(json.dumps(j));print('   '+'\n   '.join(m))
