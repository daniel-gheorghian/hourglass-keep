# Every trap, obstacle and puzzle part: per theme where it occurs in several, plus time / state strips.
import json
TF = [('dungeon', 4), ('palace', 8), ('tile', 12), ('forge', 16), ('crypt', 20)]
T1 = ('torch',)


def D(t, extra=None, walk=3):
    return "return V.dynSpot(L,%s,%s,%d)" % (json.dumps(t), json.dumps(extra) if extra else 'null', walk)


def SEG(k, extra=None, off=2):
    return "return V.segSpot(L,%s,%s,%d)" % (json.dumps(k), json.dumps(extra) if extra else 'null', off)


CH = {'collapse': 'a', 'jumpup': 'a', 'jumpdown': 'a', 'hgap': 'b', 'shaft2': 'b', 'up': 'b', 'down': 'c', 'drop2': 'c', 'lift2d': 'c', 'chn': 'd'}
FOCUS = "V.box(s.x-70,(s.r+1)*64-125,s.x+170,(s.r+1)*64+12)"


def run(rig):
    S = rig.scene
    # ---------- per theme
    for i, (th, n) in enumerate(TF):
        sd = 9000 + 31 * i
        S('T-spikes-' + th, n, sd, D('spikes', 'o.f.fixed===false'), 'Spike trap, raised, three tiles ahead (%s).' % th, 'traps', 'trap-spikes', js2='V.dynAt(s).f.ext=1')
        S('T-loose-' + th, n, sd, D('loose', '!o.f.plank&&!o.f.drop&&!o.f.sturdy'), 'A loose (cracked) floor tile ahead, intact (%s).' % th, 'traps', 'trap-loose')
        S('T-loosefall-' + th, n, sd, D('loose', '!o.f.plank&&!o.f.drop&&!o.f.sturdy'), 'The loose floor tile shaking, about to give way (%s).' % th, 'traps', 'trap-loose', modes=T1,
          js2='V.dynAt(s).f.s=1;V.dynAt(s).f.tm=0.2')
        if n >= 4:
            S('T-chomp-' + th, n, sd, D('chomp'), 'Chomper (blade jaws) ahead (%s).' % th, 'traps', 'trap-chomp')
    for i, (th, n) in enumerate(TF[1:] + [('dungeon-II', 22)]):
        S('T-saw-' + th, n, 9500 + i * 7, D('saw', None, 4), 'Floor saw ahead (%s).' % th, 'traps', 'trap-saw', tries=80)
    # ---------- strips and states
    for th, n in (('dungeon', 4), ('forge', 16)):
        rig.statestrip('TS-spikes-' + th, n, 9100, D('spikes', 'o.f.fixed===false'), 'Spikes retracted / half / raised (%s).' % th, 'traps', 'trap-spikes',
                       [('ext 0', 'V.dynAt(s).f.ext=0'), ('ext 0.5', 'V.dynAt(s).f.ext=0.5'), ('ext 1', 'V.dynAt(s).f.ext=1')])
        rig.statestrip('TS-loose-' + th, n, 9100, D('loose', '!o.f.plank&&!o.f.drop&&!o.f.sturdy'), 'Loose floor: intact / shaking / gone (%s).' % th, 'traps', 'trap-loose',
                       [('s=0 intact', 'V.dynAt(s).f.s=0'), ('s=1 shaking', 'V.dynAt(s).f.s=1;V.dynAt(s).f.tm=0.2'), ('s=2 fallen', 'V.dynAt(s).f.s=2')])
    for th, n in (('dungeon', 5), ('palace', 8), ('forge', 16), ('crypt', 20)):
        rig.timestrip('TS-chomp-' + th, n, 9200, D('chomp'), 'Chomper through one cycle (%s).' % th, 'traps', 'trap-chomp', pre=None)
    for th, n in (('palace', 7), ('crypt', 19)):
        rig.timestrip('TS-saw-' + th, n, 9200, D('saw', None, 4), 'Saw through one pass (%s).' % th, 'traps', 'trap-saw', tries=80,
                      clipf="V.box(s.x-60,(s.r+1)*64-110,s.x+220,(s.r+1)*64+12)")
    # ---------- theme-specific
    for k, sd in enumerate((9300, 9330)):
        S('T-pend-%d' % (k + 1), 11 if k else 10, sd, D('pend', None, 4), 'Pendulum blade (Lapis Gallery).', 'traps', 'trap-fire', tries=60)
    rig.timestrip('TS-pend', 11, 9300, D('pend', None, 4), 'Pendulum through one swing (tile).', 'traps', 'trap-fire', tries=60, clipf="V.box(s.x-40,(s.r+1)*64-190,s.x+260,(s.r+1)*64+12)")
    for k, sd in enumerate((9400, 9433)):
        S('T-vent-%d' % (k + 1), 14 if k else 13, sd, D('vent', None, 4), 'Fire vent (Ember Forge).', 'traps', 'trap-fire', tries=60)
    rig.timestrip('TS-vent', 14, 9400, D('vent', None, 4), 'Fire vent through one cycle: idle, warning, flare (forge).', 'traps', 'trap-fire', tries=60, clipf="V.box(s.x-40,(s.r+1)*64-170,s.x+240,(s.r+1)*64+12)")
    for k, (n, sd) in enumerate(((3, 9500), (22, 9540))):
        S('T-stone-%d' % (k + 1), n, sd, D('stone', None, 3), 'Cracked ceiling stone (falling stone) above the walkway (%s).' % ('Cistern' if n < 8 else 'Cistern II'), 'traps', 'trap-ceil', tries=80)
    rig.timestrip('TS-stone', 3, 9500, D('stone', None, 1), 'Falling stone: the prince walks under the cracked ceiling and the stone drops.', 'traps', 'trap-ceil', span=2.2, tries=80,
                  clipf="V.box(s.x-70,(s.r+1)*64-190,s.x+170,(s.r+1)*64+12)", inv=True)
    for k, (n, sd) in enumerate(((7, 9600), (14, 9633))):
        S('T-darts-%d' % (k + 1), n, sd, D('darter', None, 4), 'Dart trap (wall darter at chest height).', 'traps', 'trap-ceil', tries=80)
    rig.timestrip('TS-darts', 7, 9600, D('darter', None, 4), 'Dart trap firing: darts cross the corridor.', 'traps', 'trap-ceil', tries=80,
                  clipf="V.box(s.x-60,(s.r+1)*64-120,s.x+260,(s.r+1)*64+12)")
    for k, (n, sd) in enumerate(((5, 9700), (8, 9733), ([14, 15, 16, 13, 18, 19, 20], 9766))):
        S('T-bridge-%d' % (k + 1), n, sd, D('loose', 'o.f.plank', 3), 'Plank bridge (old planks that give way).', 'traps', 'trap-ceil', tries=250)
    S('T-bridgefall', 5, 9700, D('loose', 'o.f.plank', 3), 'Plank bridge, planks shaking after a step.', 'traps', 'trap-ceil', tries=80, modes=T1, js2='V.dynAt(s).f.s=1;V.dynAt(s).f.tm=0.2')
    # ---------- gates and plates
    GATES = [('latch', 4, 'o.f.far&&o.f.latch&&o.f.pair===undefined&&!o.f.blockGate&&!o.f.puz', 'A plain gate (stays open once its plate is pressed), shut.'),
             ('hourglass', 6, 'o.f.race&&!o.f.latch', 'A gate with an hourglass (shuts again; its plate lies back the way you came), shut.'),
             ('timed', 8, 'o.f.dur>0&&!o.f.latch&&o.f.pair===undefined&&!o.f.race&&o.f.far', 'A timed hourglass gate, shut.'),
             ('violet', 9, 'o.f.loop', 'The violet gate behind a fork grating (opens from the violet plate on the long way).'),
             ('pairA', 8, 'o.f.pair===0', 'Coloured double gate, amber.'),
             ('pairB', 8, 'o.f.pair===1', 'Coloured double gate, teal.'),
             ('pairC', 10, 'o.f.pair===2', 'Coloured double gate, violet.'),
             ('block', 8, 'o.f.blockGate', 'Gate held by a push block on its plate (block gate).'),
             ('slab', 8, 'o.f.slab', 'A gate that needs a falling slab to hold its plate (slab gate).')]
    for gk, (gid, n, ex, what) in enumerate(GATES):
        S('T-gate-' + gid, n, 9800 + gk * 40, D('gate', ex, 3), what, 'traps', 'trap-gates', tries=120, modes=T1)
        rig.statestrip('TS-gate-' + gid, n, 9800 + gk * 40, D('gate', ex, 3), what.replace(', shut', '') + ' Shut / half / open.', 'traps', 'trap-gates', tries=120,
                       states=[('shut', 'const f=V.dynAt(s).f;f.open=0'), ('half', 'const f=V.dynAt(s).f;f.open=0.5'), ('open', 'const f=V.dynAt(s).f;f.open=1')]) if gid in ('latch', 'hourglass', 'pairA') else None
    PLATES = [('plate', 4, "o.f.t==='plate'&&!o.f.slabF&&o.f.pair===undefined&&!o.f.fwd", 'A plate (raises its gate), not pressed.', 'plate'),
              ('closer', 6, "true", 'A red closing plate (slams its gate shut).', 'closer'),
              ('remote', 8, "o.f.fwd", 'A remote plate: a timed gate far ahead opens when it is pressed; race for it.', 'plate'),
              ('pair', 8, "o.f.pair!==undefined", 'A coloured plate (pair of double gates).', 'plate'),
              ('slabplate', 8, "o.f.slabF", 'A plate with a loose slab hanging in the gallery above (slab will fall and jam it).', 'plate'),
              ('slabcloser', 8, "o.f.slabF", 'A closing plate with a loose slab above.', 'closer'),
              ('lplate', 8, "true", 'A lift-call plate.', 'lplate'),
              ('xplate', 6, "true", 'The exit-door plate (opens the floor exit).', 'xplate')]
    for pk, (pid, n, ex, what, t) in enumerate(PLATES):
        S('T-plate-' + pid, n, 9850 + pk * 40, D(t, ex, 3), what, 'traps', 'trap-plates', tries=120, modes=T1)
    rig.statestrip('TS-plate', 4, 9850, D('plate', "!o.f.slabF&&o.f.pair===undefined&&!o.f.fwd", 0), 'Plate: not pressed / pressed (prince standing on it).', 'traps', 'trap-gates', tries=100,
                   states=[('unpressed', 'const f=V.dynAt(s).f;f.press=-9'), ('pressed', 'const f=V.dynAt(s).f;f.press=H.gameTime')])
    # pressed plate and its gate open: prince stands on the plate
    S('T-plate-pressed', 4, 9850, D('plate', "!o.f.slabF&&o.f.pair===undefined&&!o.f.fwd", 0), 'Prince on a plate, gate raised by it (gate off-screen unless close).', 'traps', 'trap-plates', tries=100, modes=T1, ticks=40)
    # slab and push blocks
    S('T-slab-1', 8, 9900, D('loose', "o.f.sturdy===undefined&&false"), 'x', 'traps', 'x') if False else None
    for k, (n, sd) in enumerate(((7, 9900), (11, 9930))):
        S('T-block-%d' % (k + 1), n, sd, "const b=L.ext.blocks.find(b=>V.near(b.c,b.r,3));return b&&V.near(b.c,b.r,3)", 'A loose block to push or pull (and climb over).', 'traps', 'trap-snake', tries=120, modes=T1)
    for k, (n, sd) in enumerate(((7, 9950), (10, 9970))):
        S('T-snake-%d' % (k + 1), n, sd, "const s=L.snakeSpecs.find(s=>V.near(Math.floor(s.x/32),s.r,3));return s&&V.near(Math.floor(s.x/32),s.r,3)", 'A snake in a low tunnel / on the floor.', 'traps', 'trap-snake',
          tries=120, guards=True, modes=T1)
    # chambers, drops, moves
    for kind, n, what in (('collapse', 9, 'A collapse ledge (a loose ledge that drops him a storey).'), ('jumpup', 9, 'A jump-up ledge (jump with Grab held to catch the edge).'),
                          ('jumpdown', 9, 'A jump-down from a chamber.'), ('hgap', 9, 'The damaging drop (hurtdrop): ragged lip, dark shaft, rubble below.'),
                          ('shaft2', 9, 'A kick shaft (wall-jump shaft) between two walls.'), ('up', 9, 'A plain climb-up step in a chamber.'), ('down', 9, 'A plain hang-and-drop step in a chamber.'),
                          ('drop2', 9, 'A two-storey drop step.'), ('lift2d', 9, 'A counterweight lift chamber.'), ('chn', 9, 'A chain-loop lift chamber.')):
        for th, tn in (('dungeon', 22), ('tile', 12), ('crypt', 20)):
            S('T-turn-%s-%s' % (kind, th), tn if kind not in ('lift2d', 'chn') else max(tn, 8), 10000 + 13 * len(kind), SEG('^turn-' + kind), what + ' (%s).' % th, 'traps', 'chamber-' + CH[kind], tries=150, modes=T1)
    for k, (n, sd) in enumerate(((6, 10200), (10, 10230), (18, 10260))):
        S('T-hurtdrop-%d' % (k + 1), n, sd, D('hurtdrop', None, 3), 'The damaging drop: its own look (ragged lip, darker shaft, rubble pile).', 'traps', 'trap-grate', tries=150)
    for k, (n, sd) in enumerate(((7, 10300), (12, 10330), (21, 10360))):
        S('T-bar-%d' % (k + 1), n, sd, "const o=L.dyn.find(o=>o.f.t==='bar'&&V.near(o.c,o.r,4));return o&&V.near(o.c,o.r,4)", 'A swing bar over a gap.', 'traps', 'trap-moves', tries=120, modes=T1)
    for k, (n, sd) in enumerate(((5, 10400), (9, 10430), (16, 10460), (22, 10490))):
        S('T-banner-%d' % (k + 1), n, sd, D('banner', None, 3), 'A banner hanging down a shaft (slide with Grab).', 'traps', 'trap-moves', tries=120, modes=T1)
    for k, (n, sd) in enumerate(((6, 10500), (13, 10530), (20, 10560))):
        S('T-shaftfoot-%d' % (k + 1), n, sd, D('shaftfoot', None, 2), 'Foot of a kick shaft.', 'traps', 'trap-moves', tries=120, modes=T1)
    for k, (n, sd) in enumerate(((7, 10600), (11, 10630), (16, 10660))):
        S('T-jgrab-%d' % (k + 1), n, sd, D('jgrab', None, 3), 'A ledge a floor up across a pit (jump-grab).', 'traps', 'trap-moves', tries=120, modes=T1)
    for k, (n, sd) in enumerate(((7, 10700), (12, 10730), (18, 10760))):
        S('T-lift-%d' % (k + 1), n, sd, "const f=L.lifts.find(f=>f.t==='lift'&&V.near(f.sc,f.rT,3));return f&&V.near(f.sc,f.rT,3)", 'A counterweight lift (platform in its shaft).', 'traps', 'trap-lift', tries=120, modes=T1)
    for k, (n, sd) in enumerate(((9, 10800), (14, 10830), (19, 10860))):
        S('T-chainlift-%d' % (k + 1), n, sd, "const f=L.lifts.find(f=>f.t==='chain'&&V.near(f.sc,f.rT,3));return f&&V.near(f.sc,f.rT,3)", 'A chain-loop lift (slabs on a chain).', 'traps', 'trap-lift', tries=120, modes=T1)
    for k, (n, sd) in enumerate(((7, 10900), (11, 10930), (15, 10960), (21, 10990))):
        S('T-grate-%d' % (k + 1), n, sd, "const q=L.forks.find(q=>q.grate&&V.near(q.H,q.rUp,3));return q&&V.near(q.H,q.rUp,3)", 'A fork grating over a shaft (kind 4 with a flask below).', 'traps', 'trap-grate', tries=200, modes=T1)
    rig.scene('T-grate-peek', 8, 10900, "const q=L.forks.find(q=>q.grate&&V.near(q.H,q.rUp,0));return q&&V.near(q.H,q.rUp,0)", 'Crouching on the grating and holding Down: the view drops to the flask behind its violet gate.',
              'traps', 'trap-grate', tries=250, modes=T1, js='H.setKey("kb","d",true)', js2='V.hold(90,{state:"crouch"})') # (settle() forces "stand" every tick, so the crouch needs its own hold)
