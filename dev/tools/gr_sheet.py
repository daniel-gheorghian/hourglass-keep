# gr_sheet.py out_dir tag: ranks (prince, recruit, soldier, veteran, captain) on each theme, standing and in garde,
# Classic/Torchlight, HD/normal figures. Writes one PNG per (theme, mode, hd, pose) and a contact sheet per tag.
import sys, os
from vlib import Rig
from PIL import Image
out, tag = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
FLOORS = [(4, 'cistern'), (8, 'sandstone'), (12, 'lapis'), (16, 'forge'), (20, 'crypt')]
rig = Rig('gr_' + tag)
SETUP = """([n,pose,hd,mode])=>{
 const L=V.load(n,5000+n,{guards:true}); const H_=H;
 let sp=null; for(let r=0;r<L.rows&&!sp;r++)for(let c=8;c<L.cols-8&&!sp;c++){let ok=true;for(let k=0;k<9;k++){if(!V.sb(c+k,r)||V.B(c+k,r)===2||V.F(c+k,r)||L.dyn.find(o=>o.c===c+k&&o.r===r)){ok=false;break;}} if(ok)sp={c,r};}
 if(!sp)return 'nospot';
 H.S.set.gfx.hd=hd; const t0=H.G.find(g=>!g.skel); if(!t0)return 'noguard'; H.G.length=0;
 const x0=sp.c*32+16, r=sp.r;
 const mkg=(tier,cap,x)=>{const g=Object.assign({},t0,{x,y:(r+1)*64-4,r,lo:x-300,hi:x+300,cap,tier,skel:false,alive:true,gone:false,state:'idle',face:-1,lk:undefined});H.G.push(g);return g;};
 const gs=[mkg(0,false,x0+36),mkg(1,false,x0+72),mkg(2,false,x0+108),mkg(3,true,x0+144)];
 V.place(x0,r,1,{});
 const P=H.P;
 for(let k=0;k<70;k++){P.x=x0;P.y=(r+1)*64-4;P.face=1;P.vx=0;P.inv=1e9;P.state=pose==='garde'?'garde':'stand';P.sword=pose==='garde';P.foe=null;
   gs.forEach((g,i)=>{g.x=x0+36*(i+1);g.face=-1;g.vx=0;g.think=9;g.state=pose==='garde'?'garde':'idle';g.aggr=0;}); H.tick(1);}
 V.clean(); V.light(mode); V.R(); return [x0,r];}"""
imgs = []
for pose in ('stand', 'garde'):
  for hd in (True, False):
    for mode in ('torch', 'classic'):
      row = []
      for n, nm in FLOORS:
        rig.fresh()
        res = rig.ev(SETUP, [n, pose, hd, mode])
        if isinstance(res, str): print(n, res); continue
        x0, r = res
        P = rig.ev('({x:H.P.x,y:H.P.y})')
        clip = rig.ev('([x,y])=>V.box(x-30,y-80,x+185,y+14)', [P['x'], P['y']])
        p = os.path.join(out, '%s_%s_%s_%s_%s.png' % (tag, nm, 'hd' if hd else 'flat', mode, pose))
        open(p, 'wb').write(rig.png(clip)); row.append(p)
      imgs.append((pose, hd, mode, row))
# contact sheet: rows = pose/hd/mode, columns = themes
ims = [[Image.open(p) for p in row] for *_, row in imgs]
w = max(i.width for r in ims for i in r); h = max(i.height for r in ims for i in r)
for part, sel in (('hd', lambda a: a[1]), ('flat', lambda a: not a[1])):
    rows = [(a, r) for a, r in zip(imgs, ims) if sel(a)]
    S = Image.new('RGB', (w * len(FLOORS), h * len(rows)))
    for y, (a, r) in enumerate(rows):
        for x, im in enumerate(r): S.paste(im, (x * w, y * h))
    S.save(os.path.join(out, 'sheet_%s_%s.png' % (tag, part)))
    S.convert('L').save(os.path.join(out, 'sheet_%s_%s_grey.png' % (tag, part)))
rig.close()
print('done', w, h)
