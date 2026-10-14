from playwright.sync_api import sync_playwright
import sys
JS=r'''([n,s,kind])=>{const H=__HK;const L=H.load(n,s,true);const idx=L.path.findIndex(a=>a.a===kind);const ins=L.path[idx];
  // teleport to the action's start: find the floor row under ins.from
  const c=ins.from;let r=-1;for(let rr=0;rr<L.rows;rr++){if(L.base[rr*L.cols+c]===1&&(rr===0||L.base[(rr-1)*L.cols+c]!==1))r=rr;}
  const cell=(cc,rr)=>(cc<0||rr<0||rr>=L.rows)?'#':['.','=','#'][L.base[rr*L.cols+cc]];
  const map=[];for(let rr=Math.max(0,r-4);rr<=Math.min(L.rows-1,r+3);rr++){let row='';for(let cc=c-4;cc<=c+8;cc++)row+=cell(cc,rr);map.push((rr===r?'>':' ')+row);}
  const P=H.P;P.x=(c-2)*32+16;P.y=(r+1)*64-4;P.fallY=P.y;P.state='stand';P.face=1;
  // run the bot from this instruction only
  L.path.splice(0,idx);L.path.splice(1);L.path.push({a:'walk',c:ins.to??(c+3)},{a:'door'});
  const log=[];const r0=runBot.__single?0:0;
  return {map:map.join('\n'),ins:JSON.stringify(ins),row:r};}'''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    n,s,kind=int(sys.argv[1]),int(sys.argv[2]),sys.argv[3]
    out=pg.evaluate(JS,[n,s,kind]); print(out['ins'],'row',out['row']); print(out['map'])
    # now drive the same action manually with the bot's logic, logging states
    log=pg.evaluate(r'''([n,s,kind])=>{const H=__HK;const L=H.load(n,s,true);const ins=L.path.find(a=>a.a===kind);const c=ins.from;let r=-1;for(let rr=0;rr<L.rows;rr++){if(L.base[rr*L.cols+c]===1&&(rr===0||L.base[(rr-1)*L.cols+c]!==1))r=rr;}
      const P=H.P;P.x=(c-2)*32+16;P.y=(r+1)*64-4;P.fallY=P.y;P.state='stand';P.face=1;
      const out=[];let pulse=null;const set=(k,v)=>H.setKey('kb',k,v);const press=k=>{set(k,true);pulse=k;};
      let ph=1,t0=0;set('r',true);
      for(let f=0;f<400;f++){
        if(kind==='wallrun'){if(ph===1&&P.state==='run'&&P.x>=c*32+16-34){press('j');ph=2;}if(ph===2&&P.state!=='run')set('r',false);if(P.state==='hang')set('u',true);}
        if(kind==='swing'){if(ph===1&&P.state==='run'&&P.x>=c*32+16-44){press('j');ph=2;}if(ph===2&&P.state==='air')set('r',false);if(ph===2&&P.state==='swing'){ph=3;t0=H.gameTime;}
          if(ph===3){const t=H.gameTime-P.sw0;if(P.state==='swing'&&Math.cos(H.SW_W*t)>0.8&&t>0.05)press('j');if(P.state!=='swing')ph=4;}if(ph===4&&P.state==='hang')set('u',true);}
        H.tick(1);if(pulse){set(pulse,false);pulse=null;}
        if(f%4===0)out.push(P.state+' x'+Math.round(P.x-c*32)+' y'+Math.round(P.y-((r+1)*64-4))+' vy'+Math.round(P.vy));
        if(P.state==='dead')break;}
      ['l','r','u','d','j','g'].forEach(k=>set(k,false));return out.join(' | ');}''',[n,s,kind])
    print(log[:2500])
    b.close()
