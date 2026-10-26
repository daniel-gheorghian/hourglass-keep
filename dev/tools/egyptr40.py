# egyptr40.py v84.html new.html out.png (round 40, run from dev/tools) r40_clockshadow.png: for floors 10, 22, 29 seed 1, the clock with his shadow: v84 shadow on | off | round 40 shadow on | off, 4x, and the
# differing pixels inside the thing's outline (eroded, as shadowscan) in red
import sys,os
sys.path.insert(0,os.getcwd())
import shadowscan as S
from playwright.sync_api import sync_playwright
from PIL import Image, ImageChops, ImageDraw
old,new,out=sys.argv[1],sys.argv[2],sys.argv[3]
CASES=[(10,223),(22,45),(29,367)]
GPU=['--use-angle=metal','--enable-gpu','--ignore-gpu-blocklist','--force_high_performance_gpu']
def grab(pg,n,c):
    for i in range(pg.evaluate("([n])=>SHS.list(n,1,'clock')",[n])):
        r=pg.evaluate("([n,i])=>SHS.show(n,1,'clock',i,true,false)",[n,i])
        if r['c']==c:
            A=S.shot(pg);pg.evaluate("([n,i])=>SHS.show(n,1,'clock',i,false,false)",[n,i]);B=S.shot(pg);return r,A,B
with sync_playwright() as p:
    b=p.chromium.launch(args=GPU);po=S.page(b,old);pn=S.page(b,new)
    rows=[]
    for n,c in CASES:
        tiles=[]
        for pg in (po,pn):
            r,A,B=grab(pg,n,c);mk=S.mask(r['shc'],A.width,A.height);nb,_=S.changed(A,B,mk)
            d=ImageChops.difference(A,B).convert('L').point(lambda v:255 if v>8 else 0);bad=ImageChops.multiply(d,mk)
            cx,cy=int(r['mid'][0]*2),int(r['mid'][1]*2);box=(cx-70,cy-75,cx+70,cy+60)
            Ar=A.copy();Ar.paste((255,0,0),mask=bad)
            for im in (Ar,B):tiles.append(im.crop(box).resize((420,405),Image.NEAREST))
            tiles[-2].info['nb']=nb
            tiles.append(nb)
        row=Image.new('RGB',(4*424,430),(20,16,24));dr=ImageDraw.Draw(row)
        k=0
        for t in tiles:
            if isinstance(t,int):continue
            row.paste(t,(k*424,24));k+=1
        dr.text((4,4),'floor %d seed 1 c%d: v84 shadow on (bad px red: %d) | v84 off | round 40 on (bad px: %d) | round 40 off'%(n,c,tiles[2],tiles[5]),fill=(255,240,160))
        rows.append(row)
    sh=Image.new('RGB',(rows[0].width,sum(r.height for r in rows)))
    y=0
    for r in rows: sh.paste(r,(0,y));y+=r.height
    sh.save(out);b.close()
