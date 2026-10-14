from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
  b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300)
  r=pg.evaluate('''()=>{const H=__HK;const kit={},vert={step:0,special:0},inrun={up:0,down:0,drop2:0},det={n:0,dbl:0,lens:[],floors:0,flatRun:[]},band={};
    let floors=0,turnsN=0;
    for(let n=1;n<=27;n++)for(let s=0;s<20;s++){const L=H.genLevel(n,50000+s*131+n*7,true);floors++;
      const tk={};for(const q of L.segs){if(q.k.startsWith('turn-')){const m=q.k.slice(5);kit[m]=(kit[m]||0)+1;const dr=Math.abs(q.r1-q.r0);
          if(['up','down','drop2'].includes(m))vert.step+=dr;else vert.special+=dr;}
        else if(['up','down','drop2'].includes(q.k)){inrun[q.k]++;}}
      if(L.plan)turnsN+=L.plan.turns.length;
      const ds=L.detours||[];let any=false;for(const d of ds){if(d.secret)continue;any=true;det.n++;if(d.double)det.dbl++;det.lens.push(d.len);}
      if(any)det.floors++;
      const b=n<=5?'1-5':n<=12?'6-12':n<=20?'13-20':'21-27';band[b]=band[b]||{step:0,special:0};
      for(const q of L.segs)if(q.k.startsWith('turn-')){const m=q.k.slice(5),dr=Math.abs(q.r1-q.r0);if(['up','down','drop2'].includes(m))band[b].step+=dr;else band[b].special+=dr;}
    }
    det.lens.sort((a,b)=>a-b);
    return {floors,turnsN,kit,vert,inrun,det:{n:det.n,dbl:det.dbl,floors:det.floors,lenMin:det.lens[0],lenMed:det.lens[det.lens.length>>1],lenMax:det.lens[det.lens.length-1]},band};}''')
  print(json.dumps(r,indent=1))
  b.close()
