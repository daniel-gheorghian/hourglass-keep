from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont
import os,json
# the same floor and seed, old vs new, as a strip map of the first ~11 rooms the prince runs through
JS=r'''([n,sd,cols])=>{const H=__HK;const L=H.load(n,sd,true);const F=[];for(const o of L.dyn)if(o.c<cols)F.push([o.c,o.r,o.f.t,o.f.dur||0]);
 return {rows:L.rows,cols:L.cols,base:Array.from(L.base.slice()),W:L.cols,F,guards:L.guards.filter(g=>g.x<cols*32).map(g=>[Math.floor(g.x/32),g.r,g.skel?1:0])};}'''
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',15); small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12)
COL={'spikes':(220,60,50),'loose':(240,150,40),'chomp':(170,90,220),'gate':(250,215,90),'plate':(80,200,220),'closer':(80,200,220),'low':(120,170,90),'stone':(240,150,40),'pend':(170,90,220),'vent':(255,110,40),'saw':(170,90,220),'darter':(170,90,220),'bar':(150,150,160),'banner':(150,150,160)}
NC=100; S=11
def draw(data,label,y0,im,d):
    rows=data['rows'];W=data['W'];b=data['base']
    used=[r for r in range(rows) if any(b[r*W+c]==1 for c in range(NC))]; r0=max(0,min(used)-1); r1=min(rows-1,max(used)+1)
    d.text((8,y0),label,fill=(240,220,170),font=font); y0+=22; y0-=r0*S
    for r in range(r0,r1+1):
        for c in range(NC):
            v=b[r*W+c]; x=8+c*S; y=y0+r*S
            if v==0: col=(52,46,58)          # wall
            elif v==1: col=(205,190,160)     # floor
            else: col=(10,9,12)              # open air
            d.rectangle([x,y,x+S-1,y+S-1],fill=col)
    for c,r,t,dur in data['F']:
        if c>=NC or t not in COL: continue
        x=8+c*S;y=y0+r*S; col=COL[t]
        if t=='gate' and dur>0: col=(255,90,60)
        d.rectangle([x+1,y+1,x+S-2,y+S-2],fill=col)
    for c,r,sk in data['guards']:
        if c>=NC: continue
        x=8+c*S;y=y0+r*S; d.ellipse([x,y-S,x+S-1,y-1],fill=(235,235,235) if sk else (90,140,255))
    return y0+(r1+1)*S
with sync_playwright() as p:
    b=p.chromium.launch(); out=[]
    for label,f in (('Before (v30)','v30_hooks.html'),('After (v31)','/Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html')):
        pg=b.new_page(); pg.goto('file://'+os.path.abspath(f)); pg.wait_for_timeout(300)
        out.append((label,pg.evaluate(JS,[12,2468,NC]))); pg.close()
    b.close()
H=sum(o[1]['rows']*S+30 for o in out)+70
im=Image.new('RGB',(16+NC*S,H),(18,16,22)); d=ImageDraw.Draw(im); y=8
for label,data in out: y=draw(data,f'Floor 12, first {NC} columns — {label}',y,im,d)+14
legend=[('spikes',(220,60,50)),('crumbling / falling',(240,150,40)),('blades / saws',(170,90,220)),('gate',(250,215,90)),('timed gate',(255,90,60)),('plate',(80,200,220)),('low tunnel',(120,170,90)),('guard',(90,140,255))]
x=8
for t,col in legend: d.rectangle([x,y+3,x+10,y+13],fill=col); d.text((x+14,y),t,fill=(220,210,200),font=small); x+=14+d.textlength(t,font=small)+18
im=im.crop((0,0,im.width,y+22)); im.save('pacing_strip.png'); print(im.size)
