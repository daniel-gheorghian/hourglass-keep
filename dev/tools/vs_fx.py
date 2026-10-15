# Effects: Torchlight vs Classic pairs (lamps, darkness, wall shadows, heat shimmer, sandstorm), colour grade, bloom, HUD, rewind.
import json
TF = [('dungeon', 4), ('palace', 8), ('tile', 12), ('forge', 16), ('crypt', 20)]
TORCH1 = "const t=L.torches.filter(t=>t.c>8&&V.sb(t.c-2,t.r)&&V.sb(t.c-1,t.r)&&V.B(t.c-2,t.r)!==2&&V.walkway(t.c,t.r,1,2))[%d];return t&&{x:t.c*32-48,r:t.r,face:1}"
TWO = ("for(const a of L.torches){if(a.c<9)continue;const b=L.torches.find(b=>b.r===a.r&&b.c-a.c>=4&&b.c-a.c<=7);if(b){const c=(a.c+b.c)>>1;"
       "if(V.sb(c,a.r)&&V.walkway(c+1,a.r,1,3))return {x:c*32+16,r:a.r,face:1}}}return null")
DARK = ("let best=null,bd=-1;for(const s of L.segs){if(Math.abs(s.c1-s.c0)<3)continue;for(let c=Math.min(s.c0,s.c1);c<=Math.max(s.c0,s.c1);c++){let d=1e9;for(const t of L.torches)d=Math.min(d,Math.abs(t.c-c)+Math.abs(t.r-s.r0)*6);"
        "if(d>bd&&V.sb(c,s.r0)){bd=d;best={x:c*32+16,r:s.r0,face:1}}}}return bd>=5?best:null")
D = lambda t, ex=None, w=3: "return V.dynSpot(L,%s,%s,%d)" % (json.dumps(t), json.dumps(ex) if ex else 'null', w)
ITEM = "const it=L.items.find(i=>!i.taken&&i.type===%s&&V.near(i.c,i.r,2)&&V.near(i.c,i.r,2));return it&&V.near(it.c,it.r,2)"


def run(rig):
    S = rig.scene
    for i, (th, n) in enumerate(TF):
        sd = 12000 + 23 * i
        S('FX-shadow-' + th, n, sd, TORCH1 % 1, 'Prince 1.5 tiles from one wall torch: his soft shadow on the wall and the lamp pool (%s).' % th, 'effects', 'fx-shadow', tries=80)
        S('FX-twotorch-' + th, n, sd + 5, TWO, 'Prince between two wall torches: two shadows (%s).' % th, 'effects', 'fx-shadow', tries=120, modes=('torch',))
        S('FX-dark-' + th, n, sd + 9, DARK, 'The darkest stretch of a floor, far from any lamp (%s).' % th, 'effects', 'fx-dark', tries=60)
    for k, (nm, tp, fl) in enumerate((('flask', 'heal', [3, 5, 8]), ('largeflask', 'big', [6, 9, 12, 15]), ('goldflask', 'life', [[4, 5, 6, 7, 8, 9], [10, 11, 12, 13, 14], [15, 16, 17, 18, 19, 20]]))):
        for j, n in enumerate(fl[:3]):
            tr = 30 if isinstance(n, list) else 200
            S('FX-bloom-%s-%d' % (nm, j + 1), n, 12100 + k * 40, ITEM % json.dumps(tp), 'Bloom on a %s (item type %s).' % (nm, tp), 'effects', 'fx-bloom', tries=tr)
    # grade on/off at the arch hall spots
    for i, (th, n) in enumerate(TF):
        S('FX-gradeoff-' + th, n, 8000 + 17 * i, "const t=L.torches.filter(t=>t.c>8&&V.walkway(t.c,t.r,1,4))[2];if(!t)return null;return V.near(t.c,t.r,2)",
          'Same spot as A-hall-%s with the Colour grade graphics option switched OFF (compare).' % th, 'effects', 'fx-gradeoff', modes=('torch',), js='H.S.set.gfx=H.S.set.gfx||{};H.S.set.gfx.grade=false')
    rig.ev('()=>{H.S.set.gfx.grade=true;return 1}')
    for k, n in enumerate((13, 15)):
        S('FX-forgetorch-%d' % (k + 1), n, 12200 + k * 40, TORCH1 % 0, 'Heat shimmer over a forge torch / hot air (Ember Forge).', 'effects', 'fx-heat', tries=80)
        S('FX-vent-%d' % (k + 1), n, 12250 + k * 40, D('vent', None, 4), 'A fire vent at the top of its flare: flame plume and heat shimmer.', 'effects', 'fx-heat', tries=80,
          js2="const o=V.dynAt(s);for(let k=0;k<600;k++){const f=o.f,ph=(((H.gameTime+f.off)%f.per)+f.per)%f.per/f.per;if(ph>0.8)break;V.hold(1)}")
    rig.timestrip('FXS-heat-forge', 14, 12250, TORCH1 % 0, 'Heat shimmer over a forge torch over one second (Torchlight).', 'effects', 'fx-heat', span=1.2, tries=80,
                  clipf="V.box(s.x-30,(s.r+1)*64-150,s.x+190,(s.r+1)*64+10)")
    rig.timestrip('FXS-heat-vent', 14, 12250, D('vent', None, 4), 'Fire vent flare and the shimmer above it (Torchlight), through one cycle.', 'effects', 'fx-heat', tries=80,
                  clipf="V.box(s.x-30,(s.r+1)*64-170,s.x+240,(s.r+1)*64+10)")
    # sandstorm
    STORM = "const c=L.ext.chase;if(!c)return null;return {x:(c.c0+8)*32,r:c.rBot-1,face:1}"
    for k, n in enumerate((6, 9, 12, 15)):
        S('FX-storm-%d' % (k + 1), list(range(n, n + 6)), 12300 + k * 40, STORM, 'Sandstorm chase: the wall of sand behind the prince and the haze.', 'effects', 'fx-storm', tries=60,
          js='const c=H.L.ext.chase;c.on=true;c.t=0;c.wx=s.x-150', js2='const c=H.L.ext.chase;for(let k=0;k<120;k++){c.wx=s.x-150;V.hold(1)}')
    storm_strip(rig)
    hud(rig)
    rewind(rig)


def storm_strip(rig):
    sid = 'FXS-storm'
    if not rig.want(sid):
        return
    r = None
    for n in range(7, 20):
        r = rig.find(n, 12300, "const c=L.ext.chase;if(!c)return null;return {x:(c.c0+3)*32,r:c.rBot-1,face:1}", 40)
        if r:
            break
    if not r:
        print('NOT FOUND', sid); rig.missing.append(sid); return
    rig.place(r['spot'])
    rig.ev("()=>{const c=H.L.ext.chase;c.on=true;c.t=0;c.wx=H.P.x-200;H.setKey('kb','r',true);return 1}")
    fr = []
    for i in range(6):
        rig.ev('()=>{for(let k=0;k<30;k++){H.P.inv=1e9;H.tick(1)}return 1}')
        rig.render('torch')
        fr.append((rig.png(None), '+%.1fs' % ((i + 1) * 0.5)))
    rig.ev("()=>{H.setKey('kb','r',false);return 1}")
    meta = rig.meta()
    rig._strip_wrap(sid, 'The sandstorm chase over three seconds: the wave edge closing on the running prince (full view; strip cells are scaled down).', 'effects', 'fx-storm', fr, meta)
    print('ok', sid, meta['floor'])


def hud(rig):
    for th, n in (('palace', 24), ('crypt', 28)):
        sid = 'FX-hud-hearts-' + th
        if not rig.want(sid):
            continue
        r = rig.find(n, 12400, "const t=L.torches.filter(t=>t.c>8&&V.walkway(t.c,t.r,1,4))[2];return t&&V.near(t.c,t.r,2)", 40)
        if not r:
            print('NOT FOUND', sid); rig.missing.append(sid); continue
        rig.ev("()=>{H.S.maxHp=9;return 1}")
        rig.place(r['spot'], hp=9)
        rig.ev("()=>{H.P.hp=6;return 1}")
        rig.settle(40)
        rig.shot(sid, 'HUD with nine life triangles (six full), late floor %d.' % n, 'effects', 'fx-misc', 'cd dev/tools && python3 vshots.py fx ' + sid, modes=('torch',))
        rig.ev("()=>{H.S.maxHp=3;return 1}")


def rewind(rig):
    sid = 'FX-rewind'
    if not rig.want(sid):
        return
    r = rig.find(5, 12500, "return V.dynSpot(L,'spikes','o.f.fixed===false',3)", 40)
    if not r:
        print('NOT FOUND', sid); return
    rig.place(r['spot'], inv=False)
    rig.ev("(s)=>{H.setKey('kb',s.dir>0?'r':'l',true);for(let t=0;t<400&&H.P.state!=='dead';t++)H.tick(1);for(let t=0;t<90;t++)H.tick(1);H.startRewind();for(let t=0;t<14;t++)H.tick(1);return 1}", r['spot'])
    rig.shot(sid, 'Rewinding the sands after a death: tint, grains and the text "The sands turn back".', 'effects', 'fx-misc', 'cd dev/tools && python3 vshots.py fx ' + sid, modes=('torch',))
