# UI: title, menus, pause, between-floors cards, death, portrait, gate countdown. (round 49a: no hint banners or game messages any more)
import json
def run(rig):
    px = lambda: rig.pg.wait_for_timeout
    repro = lambda sid: 'cd dev/tools && python3 vshots.py ui ' + sid

    def snap(sid, what, sheet, state='ui screen', light='torch', fname=None):
        if not rig.want(sid):
            return
        fn = 'shots/%s.png' % sid
        open('%s/%s' % (OUT(), fn), 'wb').write(rig.png())
        meta = rig.ev("()=>{const H=__HK;return {floor:H.L?H.L.n:null,seed:H.L?H.L.seed:null,theme:H.L?H.L.theme.name:'',style:H.L?H.L.theme.style:'',light:'ui ('+H.S.set.lightMode+')',state:'%s'}}" % state)
        rig.add(id=sid, file=fn, topic='ui', sheet=sheet, what=what, repro=repro(sid), closeup=False, label=sid, kind='shot', face=None, hp=None, x=None, row=None, jk=None, feature=None, **meta)
        print('ok', sid)

    # real (running) page, clean storage
    rig.fresh(init=False, clean=True)
    rig.pg.wait_for_timeout(1200)
    snap('U-title-new', 'Title screen, new player ("Enter the keep"), the first floor previewed behind it.', 'ui-menus', 'title')
    rig.pg.click('#bHowT'); rig.pg.wait_for_timeout(300)
    snap('U-how', 'How to play.', 'ui-menus', 'how')
    rig.pg.click('#bHowClose'); rig.pg.wait_for_timeout(200)
    rig.pg.click('#bGfxT'); rig.pg.wait_for_timeout(400)
    snap('U-gfx-torch', 'Graphics menu with Torchlight on.', 'ui-menus', 'gfx')
    rig.pg.click('#gShader'); rig.pg.wait_for_timeout(300)
    snap('U-gfx-classic', 'Graphics menu with lighting set to Classic.', 'ui-menus', 'gfx')
    rig.pg.click('#gShader'); rig.pg.click('#bGfxClose'); rig.pg.wait_for_timeout(200)
    rig.pg.click('#bNew'); rig.pg.wait_for_timeout(900)
    snap('U-floor-intro', 'The floor title shown as a floor begins ("Floor 1", theme name).', 'ui-play', 'play')
    rig.pg.wait_for_timeout(3200)
    snap('U-play-start', 'Floor 1 in play after its title: controls and HUD (round 49a: no hint banner).', 'ui-play', 'play')
    rig.pg.click('#bPause'); rig.pg.wait_for_timeout(400)
    snap('U-pause', 'Pause screen with this floor, times, falls and the settings toggles.', 'ui-menus', 'paused')
    rig.pg.click('#bGfxP'); rig.pg.wait_for_timeout(300)
    snap('U-gfx-from-pause', 'Graphics menu opened from the pause screen.', 'ui-menus', 'gfx')
    rig.pg.click('#bGfxClose'); rig.pg.wait_for_timeout(200)
    rig.pg.click('#bQuit'); rig.pg.wait_for_timeout(500)
    snap('U-title-continue', 'Title screen with a run in progress ("Continue on Floor N", "New run").', 'ui-menus', 'title')
    rig.pg.click('#bNew'); rig.pg.wait_for_timeout(300)
    snap('U-confirm', 'Confirmation before replacing the current run.', 'ui-menus', 'confirm')
    rig.pg.click('#bConfirmNo')
    # lefty pad
    rig.pg.click('#bContinue'); rig.pg.wait_for_timeout(500)
    rig.pg.evaluate("document.getElementById('bPause').click()"); rig.pg.wait_for_timeout(300)
    rig.pg.click('#tLefty'); rig.pg.click('#bResume'); rig.pg.wait_for_timeout(1500)
    snap('U-play-lefty', 'Play with the pad on the right ("Pad on right" setting): controls mirrored.', 'ui-play', 'play')
    rig.scene('U-gate-timer', 6, 13320, "return V.dynSpot(L,'gate','o.f.race&&!o.f.latch',2)", 'HUD gate countdown (hourglass and seconds at the top centre) while a timed gate is open.', 'ui', 'ui-play',
              tries=150, modes=('torch',), ticks=10, js2='const f=V.dynAt(s).f;f.tm=6.5;f.dur=11;f.open=1')
    # cards
    card(rig, snap, 'U-card', 4, False)
    card(rig, snap, 'U-card-flag', 5, True)
    portrait(rig, snap)


def OUT():
    from vlib import OUT as o
    return o


def card(rig, snap, sid, n, flag):
    if not rig.want(sid):
        return
    rig.fresh()
    seed = rig.ev('''([n,flag])=>{const H=__HK;for(let s=1;s<4000;s++){H.setGameSeed(s);const f=H.featFor(n+1,H.levelSeed(n+1)).flag;if(!!f===flag)return s;}return -1;}''', [n, flag])
    rig.ev('([n])=>{const r=runBot(n,5000+n,{});return r.ok}', [n])
    rig.pg.wait_for_timeout(200)
    snap(sid, 'Between-floors card after floor %d%s.' % (n, ' with a rare-flag line for the next floor' if flag else ''), 'ui-menus', 'card')


def portrait(rig, snap):
    if not rig.want('U-portrait'):
        return
    rig.fresh(init=False, clean=True, viewport={'width': 390, 'height': 844})
    rig.pg.wait_for_timeout(1200)
    snap('U-portrait-title', 'Portrait orientation: the title screen.', 'ui-portrait', 'title')
    rig.pg.evaluate("document.getElementById('bNew').click()"); rig.pg.wait_for_timeout(1500)
    snap('U-portrait-play', 'Portrait orientation, in play: the "turn your phone" prompt pauses the game.', 'ui-portrait', 'play')
