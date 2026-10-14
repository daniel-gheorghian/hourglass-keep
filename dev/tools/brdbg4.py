from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(400)
    print(pg.evaluate('''()=>{const H=__HK;const L=H.load(3,5555,true);const b=H.breaches().filter(Boolean)[5];
      const ox=-7*320,oy=0;const mk=(dx,dy)=>{const p=new Path2D();for(const pc of b.pieces){pc.forEach(([x,y],i)=>i?p.lineTo(x+ox+dx,y+oy+dy):p.moveTo(x+ox+dx,y+oy+dy));p.closePath();}return p;};
      const c=document.createElement('canvas');c.width=320;c.height=192;const g=c.getContext('2d');const P=mk(0,0),S=mk(5,-2.5);
      const pc=b.pieces[0];const x=(pc[0][0]+pc[1][0])/2+ox,y=(pc[0][1]+pc[2][1])/2;
      const types=b.pieces.map(p=>p.length);
      // winding check
      let inP=g.isPointInPath(P,x,y),inS=g.isPointInPath(S,x,y),inPev=g.isPointInPath(P,x,y,'evenodd');
      const areas=b.pieces.slice(0,8).map(pc=>{let a=0;for(let i=0,j=pc.length-1;i<pc.length;j=i++)a+=(pc[j][0]*pc[i][1]-pc[i][0]*pc[j][1]);return Math.round(a/2);});
      return {x,y,inP,inS,inPev,types:types.slice(0,40).join(''),areas};}'''))
    print(errs)
    b.close()
