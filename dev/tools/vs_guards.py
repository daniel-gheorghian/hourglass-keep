# Guards (every rank's dress, skeletons, reinforcements, a guard falling), fights, and the prince hurt or dying.
import json
from vreplay import Planner
FIGHT = [(6, 4106), (7, 4107), (9, 4109), (10, 4110), (12, 4112), (13, 4113), (15, 4115), (18, 4118), (21, 4121), (24, 4124)]
GUARD = "const g=L.guards.find(g=>%s&&V.near(Math.floor(g.x/32),g.r,4));return g&&V.near(Math.floor(g.x/32),g.r,4)"
RANKS = [('recruit', "g.tier===0&&!g.cap&&!g.skel"), ('soldier', "g.tier===1&&!g.cap&&!g.skel"), ('veteran', "g.tier===2&&!g.cap&&!g.skel"),
         ('captain', "g.cap"), ('skeleton', "g.skel")]
D = lambda t, ex=None, w=3: "return V.dynSpot(L,%s,%s,%d)" % (json.dumps(t), json.dumps(ex) if ex else 'null', w)
KEY = "H.setKey('kb',s.dir>0?'r':'l',true)"


def run(rig):
    for k, (nm, ex) in enumerate(RANKS):
        if nm in ('captain', 'skeleton'):
            fl = [5, 9, 13, 21] if nm == 'captain' else [17, 18, 19, 20]
            rig.scene('G-%s' % nm, fl, 11000 + k * 50, GUARD % ex, 'Guard rank "%s", prince approaching.' % nm, 'guards', 'guard-dress', guards=True, tries=200, ticks=20)
            continue
        for th, n in (('palace', 7), ('crypt', 19), ('forge', 15)):
            rig.scene('G-%s-%s' % (nm, th), n, 11000 + k * 50, GUARD % ex, 'Guard rank "%s" (%s theme), prince approaching.' % (nm, th),
                      'guards', 'guard-dress', guards=True, tries=150, ticks=20, modes=('torch', 'classic') if th == 'palace' else ('torch',))
    P = Planner(rig, [], FIGHT)
    for tag, lab, what in (('g:drop', 'reinforcement-drop', 'A reinforcement guard dropping in from the gallery'), ('g:fall', 'guard-falls', 'A guard falling into a pit'),
                           ('g:dying', 'guard-dying', 'A guard dying'), ('g:hurt', 'guard-hurt', 'A guard hit'), ('g:parry', 'guard-parry', 'A guard parrying'),
                           ('g:strike', 'guard-strike', 'A guard striking'), ('gr:skel', 'skeleton-fight', 'Fighting a skeleton'), ('gr:cap', 'captain-fight', 'Fighting a captain'),
                           ('s:hurt', 'prince-hurt', 'The prince struck by a guard'), ('s:blocked', 'prince-blocked', 'The prince blocked')):
        P.shot('G-' + lab, tag, what, 'guards', 'guard-events', 'guard-events-closeups', minlen=1, prefer_fight=True)
    for i in range(4):
        P.strip('GS-exchange-%d' % (i + 1), 'sword', 'Fight exchange: the sword drawn, blows and parries', 'fights', 'fight-strips', 8, 80, 8, 90, minlen=60, prefer_fight=True, nth=i, crop=(80, 85, 20))
    for tag, nm in (('s:strike', 'strike'), ('s:parry', 'parry'), ('g:dying', 'kill')):
        P.strip('GS-%s' % nm, tag, 'Sword move "%s" (strip)' % nm, 'fights', 'fight-strips', 10, 14, 7, 0, minlen=1, prefer_fight=True, crop=(80, 85, 20))
    P.execute()
    # forced scenarios: the prince hurt and dying
    E = rig.eventstrip
    E('GS-die-spikes', 'Death on spikes', 'prince deaths', 'prince-deaths', 5, 11500, D('spikes', 'o.f.fixed===false'), KEY, "H.P.state==='dead'", 25, 70, 8, inv=False, full_after=90)
    E('GS-die-chomp', 'Death in the chomper', 'prince deaths', 'prince-deaths', 7, 11500, D('chomp'), "window.__s=s", "(function(){const o=V.dynAt(window.__s);if(!window.__d&&H.danger(o.f,H.gameTime+0.04)){H.P.x=o.c*32+16;window.__d=1;}return H.P.state==='dead'})()", 25, 70, 8, inv=False, tries=100)
    E('GS-die-saw', 'Death on the saw', 'prince deaths', 'prince-deaths', 8, 11500, D('saw', None, 4), "window.__s=s", "(function(){const o=V.dynAt(window.__s);if(!window.__d){H.P.x=H.sawX(o.f,H.gameTime+0.06);window.__d=1;}return H.P.state==='dead'})()", 25, 70, 8, inv=False, tries=100)
    E('GS-die-pend', 'Death by the pendulum', 'prince deaths', 'prince-deaths', 11, 11500, D('pend', None, 4), "window.__s=s", "(function(){const o=V.dynAt(window.__s);if(!window.__d){H.P.x=o.c*32+16;window.__d=1;}return H.P.state==='dead'})()", 25, 70, 8, inv=False, tries=100)
    E('GS-die-vent', 'Death in a fire vent', 'prince deaths', 'prince-deaths', 14, 11500, D('vent', None, 4), KEY, "H.P.state==='dead'", 25, 70, 8, inv=False, tries=100)
    E('GS-die-guard', 'Death by a guard sword (prince with one life stands in front of a guard)', 'prince deaths', 'prince-deaths', 9, 11500, GUARD % "g.tier>=1&&!g.cap&&!g.skel", KEY, "H.P.state==='dead'", 30, 80, 8,
      guards=True, inv=False, tries=150, hp=1, maxt=2400, crop=(80, 85, 20))
    E('GS-hurt-guard', 'The prince hit by a guard (sword hurt)', 'prince deaths', 'prince-deaths', 9, 11500, GUARD % "g.tier>=1&&!g.cap&&!g.skel", KEY, "H.P.state==='hurt'", 20, 25, 7,
      guards=True, inv=False, tries=150, maxt=2400, crop=(80, 85, 20))
    E('GS-landhurt', 'A long drop: landing hurt (damaging drop, hurtdrop tile)', 'prince deaths', 'prince-deaths', 10, 11500, D('hurtdrop', None, 3), KEY, "H.P.state==='landHurt'", 40, 25, 8, inv=False, tries=200,
      crop=(60, 110, 25))
