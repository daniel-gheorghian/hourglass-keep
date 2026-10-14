from playwright.sync_api import sync_playwright
import sys
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(300)
    print(pg.evaluate(r'''([n,s])=>{const H=__HK;const L=H.load(n,s,true);const i=L.path.findIndex(a=>a.a==='pull'||a.a==='push');const ins=L.path[i];
      const bl=L.ext.blocks[0];const r=bl.r;const c0=ins.a==='pull'?ins.from-4:ins.from-1;
      const cell=(cc,rr)=>{const k=rr*L.cols+cc;if(L.blockAt.get(k))return 'B';const f=L.feat[k];if(f&&f.t==='plate')return 'p';if(f&&f.t==='gate')return 'g';return ['.','=','#'][L.base[k]];};
      const m=[];for(let rr=r-2;rr<=r+1;rr++){let row='';for(let cc=c0-1;cc<=c0+10;cc++)row+=cell(cc,rr);m.push(row);}
      const P=H.P;P.x=ins.from*32+16;P.y=SURF=(r+1)*64-4;P.fallY=P.y;P.state='stand';P.face=1;H.cam.snap=true;
      const set=(k,v)=>H.setKey('kb',k,v);set('g',true);set(ins.a==='pull'?'l':'r',true);const log=[];let last='';
      for(let f=0;f<120;f++){H.tick(1);const st=P.state+' x'+Math.round(P.x-ins.from*32)+' blk'+bl.c+(bl.mv?'m':'')+' hp'+P.hp;if(st!==last){log.push(st);last=st;}}
      ['g','l','r'].forEach(k=>set(k,false));
      return JSON.stringify(ins)+' block '+JSON.stringify({c:bl.c,lo:bl.lo,hi:bl.hi})+'\n'+m.join('\n')+'\n'+log.join(' | ');}''',[int(sys.argv[1]),int(sys.argv[2])]))
    b.close()
