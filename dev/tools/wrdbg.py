from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(300)
    print(pg.evaluate('''()=>{const H=__HK;const L=H.load(6,500,true);const ins=L.path.find(a=>a.a==='wallrun');const c=ins.from,P=H.P;
      // find the row: the floor tile at c
      let r=0;for(let rr=0;rr<L.rows;rr++)if(L.base[rr*L.cols+c]===1)r=rr;
      const cell=(cc,rr)=>L.base[rr*L.cols+cc];
      const map=[];for(let rr=r-3;rr<=r;rr++){let row='';for(let cc=c-3;cc<=c+3;cc++)row+=['.','=','#'][cell(cc,rr)];map.push(row);}
      P.x=(c-2)*32+16;P.y=(r+1)*64-4;P.fallY=P.y;P.state='stand';P.face=1;
      const log=[];H.setKey('kb','r',true);let pressed=false;
      for(let f=0;f<150;f++){if(!pressed&&P.state==='run'&&P.x>=c*32+16-34){H.setKey('kb','j',true);pressed=true;}else H.setKey('kb','j',false);
        H.tick(1);if(f%3===0)log.push(P.state+' x'+Math.round(P.x-c*32)+' y'+Math.round(P.y-((r+1)*64-4))+' vx'+Math.round(P.vx)+' pj'+(P.pendingJump?1:0));}
      H.setKey('kb','r',false);return map.join('\\n')+'\\n'+log.slice(0,40).join(' | ');}'''))
    b.close()
