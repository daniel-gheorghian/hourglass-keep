from playwright.sync_api import sync_playwright
import json,sys,statistics
def run(src,newapi):
  with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.add_init_script("""(()=>{window.__q=[];window.requestAnimationFrame=cb=>{window.__q.push(cb);return 1;};})();""")
    pg.goto('file://'+src); pg.wait_for_timeout(500)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    r=pg.evaluate('''(newapi)=>{const H=__HK;let L,seg=null;
      for(let s=0;s<60&&!seg;s++){L=H.load(9,3000+s,true);for(let r=0;r<L.rows&&!seg;r++){let run=0;for(let c=2;c<L.cols-2;c++){const ok=L.base[r*L.cols+c]!==2&&(L.base[r*L.cols+c]===1||L.base[(r+1)*L.cols+c]===2)&&!L.feat[r*L.cols+c]&&L.base[(r-1)*L.cols+c]!==2;run=ok?run+1:0;if(run>=26){seg={c:c-25,r};break;}}}}
      if(!seg)return null;H.P.x=seg.c*32+16;H.P.y=(seg.r+1)*64-4;H.P.fallY=H.P.y;H.P.state='stand';H.P.face=1;H.cam.snap=true;H.tick(2);H.mode='play';
      H.setKey('kb','r',true);
      // seeded jitter so both builds see the same frame timing
      let seed=7;const rnd=()=>{seed=(seed*16807)%2147483647;return seed/2147483647;};
      let ts=1000;const xs=[],ts_=[],wall=[];
      for(let i=0;i<260;i++){ts+=16.667+(rnd()-0.5)*2.6;const q=window.__q;window.__q=[];const t0=performance.now();for(const cb of q)cb(ts);wall.push(performance.now()-t0);
        xs.push(newapi?H.drawnCamX:H.cam.x);ts_.push(ts);}
      const v=[];for(let i=120;i<xs.length;i++)v.push((xs[i]-xs[i-1])/((ts_[i]-ts_[i-1])/1000));
      wall.sort((a,b)=>a-b);
      return {seg,vel:v,wallMed:+wall[130].toFixed(2),wallP95:+wall[Math.floor(0.95*wall.length)].toFixed(2),wallMax:+wall[wall.length-1].toFixed(2),state:H.P.state};}''',newapi)
    b.close()
    if not r: return None
    v=r.pop('vel'); m=statistics.mean(v); sd=statistics.pstdev(v)
    r.update({'meanSpeed':round(m,1),'speedJitterSD':round(sd,1),'jitterPct':round(100*sd/abs(m),1) if m else None,'minV':round(min(v),1),'maxV':round(max(v),1)})
    print(src.split('/')[-1],json.dumps(r),errs[:3])
run(__import__('os').getcwd()+'/hk_v20_release.html',False)
run('/Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html',True)
