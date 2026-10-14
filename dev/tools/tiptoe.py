from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(300)
    r=pg.evaluate('''()=>{const H=__HK;const out={};
      // tiptoe across live spikes, and onto a flask without drinking it
      for(let n=2;n<30;n++){const L=H.load(n,600+n,true);const sp=L.dyn.find(o=>o.f.t==='spikes'&&!o.f.fixed);if(!sp)continue;
        const P=H.P;P.x=(sp.c-1)*32+16;P.y=(sp.r+1)*64-4;P.state='stand';P.face=1;
        for(let k=0;k<10;k++){H.setKey('kb','g',true);H.setKey('kb','r',true);H.tick(2);H.setKey('kb','r',false);H.tick(20);}
        H.setKey('kb','g',false);out.spikes={floor:n,alive:P.state!=='dead',crossed:Math.floor(P.x/32)>sp.c,spikesUp:sp.f.ext>0.5};break;}
      const L=H.load(8,77,true);const it={c:0,r:0};const P=H.P;
      L.items.push({c:Math.floor(P.x/32)+1,r:Math.floor((P.y-1)/64),x:(Math.floor(P.x/32)+1)*32+16,type:'poison',taken:false});
      for(let k=0;k<4;k++){H.setKey('kb','g',true);H.setKey('kb','r',true);H.tick(2);H.setKey('kb','r',false);H.tick(20);}H.setKey('kb','g',false);H.tick(5);
      out.tiptoeOntoPoison={drank:L.items[L.items.length-1].taken,hp:P.hp};
      H.setKey('kb','g',true);H.tick(1);H.setKey('kb','g',false);H.tick(60);out.tapGrabOnFlask={drank:L.items[L.items.length-1].taken};
      return out;}''')
    print(json.dumps(r)); b.close()
