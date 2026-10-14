// Prototype "modern" passes layered over a frame of the real game. Not shipped code: a look test.
window.mockFrame=function(stage,opt){
  const H=__HK,cv=document.getElementById('game'),W=cv.width,Hh=cv.height,VS=H.VS,cam=H.cam,L=H.L,P=H.P;
  const camD=Math.round(cam.x*VS),camDY=Math.round(cam.y*VS);
  const S=(x,y)=>[x*VS-camD,y*VS-camDY];
  const mk=()=>{const c=document.createElement('canvas');c.width=W;c.height=Hh;return c;};
  const world=g=>g.setTransform(VS,0,0,VS,-camD,-camDY);
  // 1. the base frame (without the prince from stage 3 on, so he can be lit separately)
  window.__noHUD=true;window.__noP=stage>=3;H.render();
  const out=mk(),o=out.getContext('2d');o.drawImage(cv,0,0);
  if(stage===0){window.__noP=false;window.__noHUD=false;return out;}
  const T=Math.PI*2,R=x=>x*VS,warm=opt.warm||'255,178,110',cool=opt.cool||'150,175,255';
  const torches=L.torches.map(t=>({x:t.c*32+16+3,y:H.SURF(t.r)-44})).filter(t=>{const [sx,sy]=S(t.x,t.y);return sx>-R(200)&&sx<W+R(200)&&sy>-R(200)&&sy<Hh+R(200);});
  const wins=L.windows.map(w=>({x:w.c*32+16+8,y:w.r*64+38})).filter(t=>{const [sx,sy]=S(t.x,t.y);return sx>-R(120)&&sx<W+R(120)&&sy>-R(150)&&sy<Hh+R(80);});
  // 2. lighting: ambient darkness times a light map of torch pools, window spill and a soft fill around the hero
  const lm=mk(),l=lm.getContext('2d');l.fillStyle=opt.ambient||'rgb(62,56,88)';l.fillRect(0,0,W,Hh);l.globalCompositeOperation='lighter';
  const blob=(x,y,r,col,a)=>{const [sx,sy]=S(x,y);const g=l.createRadialGradient(sx,sy,0,sx,sy,R(r));g.addColorStop(0,'rgba('+col+','+a+')');g.addColorStop(0.35,'rgba('+col+','+(a*0.55)+')');g.addColorStop(1,'rgba('+col+',0)');l.fillStyle=g;l.fillRect(sx-R(r),sy-R(r),R(2*r),R(2*r));};
  for(const t of torches){blob(t.x,t.y,150,warm,1);blob(t.x,t.y+30,80,warm,0.5);}
  for(const w of wins){blob(w.x,w.y+30,90,cool,0.55);}
  blob(P.x,P.y-24,70,'190,180,210',0.35);
  o.globalCompositeOperation='multiply';o.drawImage(lm,0,0);o.globalCompositeOperation='source-over';
  // bloom on the flames and windows, and moonlight shafts falling through the windows
  o.globalCompositeOperation='lighter';
  const glow=(x,y,r,col,a)=>{const [sx,sy]=S(x,y);const g=o.createRadialGradient(sx,sy,0,sx,sy,R(r));g.addColorStop(0,'rgba('+col+','+a+')');g.addColorStop(1,'rgba('+col+',0)');o.fillStyle=g;o.fillRect(sx-R(r),sy-R(r),R(2*r),R(2*r));};
  for(const t of torches){glow(t.x,t.y-4,22,'255,214,150',0.55);glow(t.x,t.y,55,warm,0.18);}
  for(const w of wins){glow(w.x,w.y,20,cool,0.35);
    const [ax,ay]=S(w.x-6,w.y-10),[bx,by]=S(w.x+6,w.y+12),dx=R(-70),dy=R(120);
    const g=o.createLinearGradient(ax,ay,ax+dx,ay+dy);g.addColorStop(0,'rgba('+cool+',0.22)');g.addColorStop(1,'rgba('+cool+',0)');o.fillStyle=g;
    o.beginPath();o.moveTo(ax,ay);o.lineTo(bx,ay);o.lineTo(bx+dx*1.25,by+dy);o.lineTo(ax+dx*0.8,by+dy);o.closePath();o.fill();}
  o.globalCompositeOperation='source-over';
  if(stage>=2){
    // 3. depth: haze that thickens with distance up the screen, a fog bank along the floor, dust in the light
    let g=o.createLinearGradient(0,0,0,Hh);g.addColorStop(0,'rgba('+(opt.haze||'90,90,140')+',0.22)');g.addColorStop(0.6,'rgba(0,0,0,0)');o.fillStyle=g;o.fillRect(0,0,W,Hh);
    const fy=S(0,H.SURF(Math.floor(P.y/64)))[1];o.globalCompositeOperation='screen';
    for(let i=0;i<14;i++){const x=((i*173+opt.t*30)%(W/VS+200))*VS-R(100),r=R(60+((i*37)%40));const gg=o.createRadialGradient(x,fy+R(4),0,x,fy+R(4),r);gg.addColorStop(0,'rgba('+(opt.fog||'150,140,175')+',0.16)');gg.addColorStop(1,'rgba(0,0,0,0)');o.fillStyle=gg;o.fillRect(x-r,fy-r,2*r,2*r);}
    o.globalCompositeOperation='lighter';
    let seed=7;const rnd=()=>{seed=(seed*16807)%2147483647;return seed/2147483647;};
    for(const t of [...torches,...wins]){for(let i=0;i<26;i++){const a=rnd()*T,d=rnd()*90,[sx,sy]=S(t.x+Math.cos(a)*d,t.y+20+Math.sin(a)*d*0.8),r=R(0.4+rnd()*0.8);o.fillStyle='rgba(255,235,200,'+(0.25+rnd()*0.4)+')';o.beginPath();o.arc(sx,sy,r,0,T);o.fill();}}
    // embers drifting up from each torch
    for(const t of torches)for(let i=0;i<10;i++){const [sx,sy]=S(t.x+(rnd()-0.5)*10,t.y-8-rnd()*40);o.fillStyle='rgba(255,'+(140+rnd()*80|0)+',60,'+(0.5+rnd()*0.5)+')';o.fillRect(sx,sy,R(0.9),R(0.9));}
    o.globalCompositeOperation='source-over';
    // foreground: dark silhouettes much nearer the camera, scrolling faster than the level and out of focus
    o.save();o.filter='blur('+(R(1.6))+'px)';o.fillStyle='rgba(8,6,14,0.94)';
    const par=1.45,base=cam.x*par;
    for(let k=-1;k<4;k++){const x=k*360-(base%360)+60;const px=x*VS;
      o.fillRect(px,0,R(30),Hh);o.fillRect(px-R(6),Hh-R(22),R(42),R(22));o.fillRect(px-R(5),R(18),R(40),R(9));
      // chains hanging between pillars
      o.fillRect(px+R(150),0,R(2.2),R(52+((k*31)%30)));o.beginPath();o.arc(px+R(151),R(56+((k*31)%30)),R(4),0,T);o.fill();}
    o.restore();
    // grade: cool shadows, warm floor, stronger vignette
    o.globalCompositeOperation='soft-light';g=o.createLinearGradient(0,0,0,Hh);g.addColorStop(0,'rgba(60,80,160,0.55)');g.addColorStop(1,'rgba(170,100,40,0.5)');o.fillStyle=g;o.fillRect(0,0,W,Hh);
    o.globalCompositeOperation='source-over';
    const vg=o.createRadialGradient(W/2,Hh*0.55,Hh*0.35,W/2,Hh*0.55,W*0.62);vg.addColorStop(0,'rgba(0,0,0,0)');vg.addColorStop(1,'rgba(0,0,0,0.55)');o.fillStyle=vg;o.fillRect(0,0,W,Hh);
  }
  if(stage>=3){
    // 4. materials: a little grit over the stone, then the hero lit on his own: contact shadow, rim light from the nearest flame, shading away from it
    const nc=document.createElement('canvas');nc.width=nc.height=96;const n=nc.getContext('2d'),id=n.createImageData(96,96);for(let i=0;i<id.data.length;i+=4){const v=200+Math.random()*55;id.data[i]=id.data[i+1]=id.data[i+2]=v;id.data[i+3]=255;}n.putImageData(id,0,0);
    o.globalCompositeOperation='multiply';o.fillStyle=o.createPattern(nc,'repeat');o.globalAlpha=0.55;o.fillRect(0,0,W,Hh);o.globalAlpha=1;o.globalCompositeOperation='source-over';
    const lt=torches.slice().sort((a,b)=>Math.hypot(a.x-P.x,a.y-P.y)-Math.hypot(b.x-P.x,b.y-P.y))[0]||{x:P.x+100,y:P.y-60},dir=Math.sign(lt.x-P.x)||1;
    const [px,py]=S(P.x,P.y);let sg=o.createRadialGradient(px,py,0,px,py,R(16));sg.addColorStop(0,'rgba(0,0,0,0.6)');sg.addColorStop(1,'rgba(0,0,0,0)');o.save();o.translate(px,py);o.scale(1,0.28);o.translate(-px,-py);o.fillStyle=sg;o.fillRect(px-R(16),py-R(16),R(32),R(32));o.restore();
    const fig=mk(),f=fig.getContext('2d');world(f);
    const rimPal={};for(const k in H.PAL_HERO)rimPal[k]='#ffd49a';
    const opts={yo:P.yo,sword:false,hasSword:true,flash:0,flutter:0.8,time:opt.t};
    H.drawFigure(f,P.x+dir*1.1,P.y-0.4,P.face,P.pose,rimPal,opts);H.drawFigure(f,P.x,P.y,P.face,P.pose,H.PAL_HERO,opts);
    // shade: lit toward the flame, falling off into the ambient colour on the far side
    f.setTransform(1,0,0,1,0,0);f.globalCompositeOperation='source-atop';
    const g2=f.createLinearGradient(px-dir*R(16),0,px+dir*R(16),0);g2.addColorStop(0,'rgba(40,30,80,0.55)');g2.addColorStop(0.55,'rgba(40,30,80,0.1)');g2.addColorStop(1,'rgba(255,170,90,0.12)');f.fillStyle=g2;f.fillRect(0,0,W,Hh);
    o.drawImage(fig,0,0);
  }
  window.__noP=false;window.__noHUD=false;return out;
};
