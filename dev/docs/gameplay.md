# Gameplay

How Dawnward plays as of v84 (round 39 changed only how things are drawn): the controls, every move of the prince with its numbers, falls, lives, death and the sands, timed
gates, fighting and the chase. Numbers are the code's (`dev/hourglass-keep.html`); the elements' own rules live in `elements/`, the
generator's in [level-design.md](level-design.md), the figure's poses in `dev/FIGURE_SPEC.md`.

A worked case first. On a floor with a three-tile pit, he runs (`RUN` 100 px/s) and Jump is pressed 60 px short of the lip: the press
is kept (`P.pendingJump`) and he runs on until the lip is 9 px ahead (`hazardEdge(80)`), then takes off. The running jump reaches
97.6 px, about 7 px short of the far lip (96 px of pit), so he drops past it and, because a jump arms `P.autoGrab`, his hands catch
it and he hangs (`tryGrab`). Up climbs (`climb`, 0.72 s). The bot's action for this is `rjumpg`. On a one-tile pit the same press from a standstill walks him to the lip
(`edgeWalk`) and makes a standing jump.

## Controls

| Control | Touch | Keys | Notes |
|---|---|---|---|
| Direction | the pad (`#pad`): four sectors, no diagonals; a dead zone of 10% of its width (`padDir`) | arrows, WASD | `I.l/r/u/d` |
| Jump | `#bJump` | Space, X | `I.j` |
| Grab | `#bGrab` | Shift, Z, C | `I.g`; the button names what Grab would do now (below) |
| Pause | `#bPause` (top right, kept clear of iOS's top edge) | P, Esc | also on leaving the app (`visibilitychange`) and on turning the phone upright |

- A press is buffered 0.15 s (`took(k, win)` reads `I.buf`): Jump pressed just before a lip or a wall still counts.
- Landscape only: upright, the game pauses behind "Turn your phone sideways to play" (`layout`, `body.portrait`).
- "Pad on right" (`S.set.lefty`) swaps the pad and the buttons.
- The controls fade to a ghost (`ctlThin`, checked every 0.2 s) while a trap, lip, door, flask or the hanging prince is under them
  (`CTL_WATCH`).
- During the Crossing Grab and pause are hidden and Jump is the skip ([the Crossing](elements/the-crossing.md)).

### The Grab button's word

`grabLabel()` follows the game's own checks in their order and changes nothing; a new word shows after 0.15 s of agreeing guesses,
plain "Grab" after 0.3 s, and Rewind, Rise and Strike at once (`updateGrabLabel`).

| State | Word | When |
|---|---|---|
| dead | Rewind / Rise | sands left (after 0.7 s) / none (after 0.9 s) |
| stand | Strike | a snake within 44 px |
| stand | Drink | on a flask, no direction held (poison too) |
| stand | Push / Pull | a movable block in reach and free to move that way |
| stand | Step | spikes under him or an edge within 64 px: Grab + a tap is the careful step |
| crouch | Thrust / Draw | blade drawn low / not yet (in a tunnel: "Grab", there is no room to draw) |
| fighting | Strike | a living foe and no stumble |
| air | Swing / Slide / Hang | a bar in reach / falling past a hanging / a ledge the hands will pass in the next 0.45 s |

## The pause menu and settings

Pause shows the floor's name, this floor's time, the run's time and the falls, then:

| Button | Setting | Effect |
|---|---|---|
| Sound | `S.set.sound` | |
| Battery saver | `S.set.saver` | canvas at 1x device pixels and every other frame drawn (`loop`: `frame&1`) |
| Pad on right | `S.set.lefty` | mirrors the controls |
| Softer flashes | `S.set.calm` | screen flashes at 0.3 of their strength (`flashScreen`) |
| Crossings | `S.set.cross` | the interlude at theme changes; on unless set false |
| Graphics… | `S.set.gfx` and `S.set.lightMode` | toggles Lighting, Atmosphere, Colour grade, Lit characters, Effects & camera, New characters, Background (`GFX()`, all on by default); and the lighting mode button "Lighting: Torchlight / Classic" (`gShader`) |
| Tools… | `S.set.fps` and reloads | Show FPS (off by default); Benchmark, Benchmark (classic), Benchmark (auto scale), Profiler reload with `?bench`, `?bench=classic`, `?bench=auto`, `?prof` |
| Restart floor | | the floor from its start door, checkpoints and pressed plates cleared; the floor clock runs on |
| How to play, Title screen | | |

Torchlight draws only when the mode is `torch` and Graphics' Lighting toggle is on (`shaderOn()`); see
[concept.md](concept.md#lighting-modes) and [rendering.md](rendering.md).

## Physics and the grid

| Constant | Value | Meaning |
|---|---|---|
| `TW`, `TH` | 32, 64 px | a tile; a room is `RW` 10 by `RH` 3 tiles (320 by 192 px) |
| `SURF(r)` | `(r+1)*64-4` | the walking surface of row r |
| `GRAV` | 700 px/s² | gravity; the fall speed is capped at 480 px/s (`stAir`) |
| `STEP` | 1/60 s | fixed simulation step; up to 6 steps a frame, drawn interpolated between the last two (`renderAt`) |
| `BW` | 6 px | half-width of a body against walls (`clampMove`) |
| `HANG` | 57 px | from the lip he holds down to his feet, when hanging |
| `HEAD_UP`, `HEAD_LOW` | 52, 44 px | head height for the ceiling clamp, full and low leap |

Tiles are `EMPTY`, `FLOOR`, `WALL` in `L.base`; features (traps, plates, gates, banners...) sit in `L.feat`. `solidBelow(L,c,r)` is
the test for "he can stand here". The world is drawn in oblique depth (`DX` 16, `DY` 8): actors walk at mid-depth.

## Moves

States are `P.state`; each is a case in `updatePlayer`. Times are in seconds.

### On the floor

| Move | Input | Numbers | Notes |
|---|---|---|---|
| Run | hold left or right | starts at 35 px/s, reaches `RUN` 100 at 650 px/s²; a stride every 44 px (`P.ph`) | reversing brakes at 1000 px/s², then turns |
| Stop | let go | slows at 700 px/s² (`stop`) | |
| Turn | the other way from standing | 0.14 (`turn`) | |
| Careful step (tiptoe) | hold Grab, tap a direction | 13 px over `STEP_T` 0.3, eased (`startStep`) | never steps off an edge: it stops 2 px short of it; safe on spikes; PoP's test foot at a lip (round 33b, look only) |
| Walk | none in play | | a walk is drawn only to the lip before a standing jump (`edgeWalk`, 120 px/s), at the exit door (40 px/s), the entry and the Crossing (`CROSS_WALK` 40) |
| Crouch | Down where there is no edge to hang from | | Up or Jump stands, except under a low ceiling (`underLow`) |
| Crawl | left or right while crouched | `CRAWL` 42 px/s | the only way through a tunnel (`low` feature); keeps 14 px from a facing wall (`CROUCH_ROOM`) |
| Look down | hold Down crouched, no direction | after 0.4 the camera drops 56 px; on a grating it frames the flask below (`gratePeek`) | |
| Push / pull a block | hold Grab, press toward / away | one tile in 0.55 | [movable blocks](elements/movable-blocks.md) |
| Drink | Grab standing on a flask, no direction | `DR_T` 1.3 in all; the effect at `DR_FX` 0.9 | knocked out of it, the flask takes effect at once and falls |
| Exit | Up at the open door (within 16 px) | he walks to the doorway's middle and climbs its stairs; the card about 1.7 after Up (`EX_N`) | the door opens from the floor's exit plate (`xplate`); [doors](elements/doors.md) |

### Jumps

| Move | Input | Numbers | Notes |
|---|---|---|---|
| Standing jump | Jump from a standstill | wind-up `JP_T` 0.28; launch 132 px/s across, 159 up; 0.45 in the air; reach ~60 px (one tile cleared), rise 18 px | a hazard edge within 30 px: he walks to 4 px short of it first (`tryJump`) |
| Running jump | Jump while running (> 45 px/s) | the arc of 183 across, 190 up, flown in `RJ_K` 0.75 of its time (`rjK()`, `RJ_DV`): 244 px/s across, 0.40 in the air, reach 97.6 px (two tiles cleared), rise 25.8 px | taken at the lip (`hazardEdge(80)`, within 9 px); with no pit in 80 px it goes at once; lands on its own level with the way held and Grab up: runs straight on |
| Low leap | either jump where the full arc would meet a ceiling (`beamOverhead`) | running 212 / 128 (reach ~75 px, rise 11.7, 0.27); standing 150 / 112 (reach ~48 px) | `LOWJ`; it may fall short, by design; the head clamp holds every frame |
| Running jump onto a ledge a storey up (`jgrab`) | Jump while running, hold Grab in the air | | without Grab held a jump catches only ledges at or below its take-off (`findLedge`) |
| Jump up | Up under an open cell | a hop (0.46) | under a ledge within 28 px of its edge he jumps to hang from it (0.1 + 0.22); under a ceiling he bonks (0.3) and knocks a cracked slab above loose |
| Wall run | Jump while running at a wall within 30 px, two storeys of wall ahead, open above him | 234 px/s up at half gravity (`WR_V`, `WR_G`): rises 78 px; catches a ledge two rows up | `startWallRun`; learned as `wallrun` |
| Kick (wall to wall) | Jump touching a wall in the air (or within 0.12 of leaving it) | `KICK_VX` 62, `KICK_VY` 275 up (54 px a kick); the soles plant `PLANT_MIN` 0.11 at least | no Jump: they hold to `PLANT_STICK` 0.16, slip from `PLANT_MAX` 0.45; no kicks in a lift's shaft (`inLiftShaft`); [kick shafts](elements/kick-shafts-and-jet-streams.md) |

The drawn jump differs from the physics (lower apex, stride for the distance, take-off foot): look only, see CLAUDE.md rounds 26c-35a
and [prince](elements/prince.md).

### Ledges, cloth, bars and lifts

| Move | Input | Numbers | Notes |
|---|---|---|---|
| Hang from an edge | Down within 26 px of an edge with open space beyond | `climbDown` 0.6 | never from a broken lip (`hurtdrop`) |
| Climb up | Up (or held) while hanging | `climb` 0.72 | |
| Let go | Down or Jump while hanging | the fall starts from the hang, his feet already 57 px under the lip | the way to take the sting out of a two-storey drop |
| Catch a ledge | Grab held while falling; any jump, kick, wall run or swing release catches on its own (`P.autoGrab`) | the hands pass the lip's height within 12 px of the hang point (`findLedge`) | a fall without Grab catches nothing; a cracked slab grabbed starts to give way |
| Slide down a hanging | hold Grab while falling past one, or Grab + Down while hanging over one | bites for 0.07, then `SL_V` 170 px/s (braking `SL_A` 1100) | no fall damage at the foot; letting go of Grab drops him; [banners and slides](elements/banners-and-slides.md) |
| Swing | catch a bar in reach of the hands (15 px across, 20 up or down) | period 1.15 (`SW_W`); dies down in ~4 (`SW_TAU`); a press of the way he swings arms one pump (`SW_KICK`, `SW_PRE` 0.8) | Jump throws him, more the faster he swings; it carries over from `SW_CLEAR` 0.55 (a chime); Down held 0.15 lets go; [swing bar](elements/swing-bar.md) |
| Ride a counterweight lift | stand on the platform, hold Up or Down | `LIFT_V` 64 px/s | a plate on each landing calls it (`lplate`); he arrives standing (`P.liftHold`); [lifts](elements/lifts.md) |
| Ride a paternoster | hold toward the shaft as a slab passes the landing | `CHAIN_V` 44 px/s; boards within `CHAIN_TOL` 14 px | step off by holding away as a slab passes a landing |
| Ride a sand lift | stop on its slab | sinks at `SAND_LV` 140 px/s after `SAND_LW` 0.25, once, and does not stop at the foot (round 41): it goes on into a spike pit a storey under it | get off at the foot: the arrow toward its open door, Up or Jump (kept 0.3 s) from the door 45% open (the slab 22 px over the floor) until the slab is 60 px under it (0.59 s): within 20 px of the floor a step out, deeper a jump to the lip; missed, he is impaled on the spikes; [lifts](elements/lifts.md) |

## Falls

The drop is measured from where the fall began (`P.fallY`: the take-off floor of a jump, the hang, the last kick) to the floor he
lands on (`land`).

| Drop | Result | Example |
|---|---|---|
| under 100 px | safe | one storey (64 px), or two storeys from a hang (128 - 57 = 71) |
| 100 to 169 px | one life, `landHurt` 0.6 s, then unsteady (`P.stumble`: 0.6 to 2.2 s, longer for a longer drop and fewer lives) | two storeys from standing (128) |
| 170 px or more | death (`die('fall')`) | three storeys from standing (192) |
| below the map | death | |
| onto spikes | death, whatever the height | |

While unsteady he cannot jump, runs at about 34 px/s and wobbles. A [hurtdrop](elements/hurtdrop.md) is a drop the generator places to
cost exactly one life; a cracked slab gives way under him ([cracked slabs and sand wells](elements/cracked-slabs-and-sand-wells.md)).

## Health, lives and flasks

- Lives are hearts: `P.hp` of `S.maxHp`. A run starts with 3 (`newSave`); a gold flask adds one, up to 10, for the rest of the run.
- Every respawn starts with full hearts (`makePlayer`).
- The HUD (`drawHUD`): hearts, FLOOR n, the floor's time, three sky clocks for the sands, the nearest running gate timer in the
  middle (it flashes under a quarter), and a foe's hearts and rank on the right (a skull for a skeleton).

| Flask (`it.type`) | Effect |
|---|---|
| small red (`heal`) | +1 heart |
| large red (`big`) | all hearts; rare, at the far ends of gated side passages |
| gold (`life`) | +1 to `S.maxHp`; in side passages without a gate; once taken on a floor it stays taken (`S.lifeTaken`) |
| dark blue (`poison`) | -1 heart |

Details: [flasks and secrets](elements/flasks-and-secrets.md).

### What hurts

| Cause (`P.cause`) | Damage | Invulnerable after |
|---|---|---|
| [spikes](elements/spikes.md) landed on or run into at over 35 px/s | death | |
| [slicer jaws](elements/slicer-jaws.md) (`blade`) | death | |
| [the dark](elements/the-dark.md) (`sand`, the old name) | death | |
| fall 170 px or more | death | |
| fall 100-169 px | 1 | |
| sword | 1, knocked back 7 px | 0.3 s |
| snake | 1 | 0.6 s |
| [pendulum](elements/pendulum.md), [saw](elements/saws.md), [fire vent](elements/fire-vent.md), [dart](elements/darts.md) (`trapHit`) | 1; on his feet, pushed back 12 px into `landHurt` (0.6 s) | 0.9 s |
| [roof block](elements/roof-blocks.md) (`crush`) | 1 | |
| poison | 1 | |

## Death, the sands and checkpoints

On death (`die`) the mode is `dead` and the save's resume point is dropped. Then:

| Sands left | Grab | Jump | Otherwise |
|---|---|---|---|
| some (`canRewind()`) | after 0.7 s: rewind | after 0.7 s: rise at the checkpoint | waits |
| none | after 0.9 s: rise | after 0.9 s: rise | a tap on the view after 0.9 s, or 3.2 s: rise |

- **The rewind** (`startRewind`): every 0.1 s of play the moving world is copied into a ring of 100 snapshots (10 s; `snapAll`,
  `REW`). The rewind plays them backward at 1.6 snapshots a step to the last calm moment (`REW_STATES`) at least 4.5 s before the
  death, and play resumes there with 1.2 s of invulnerability. It costs one hour of `S.sands` (`SANDS` 3). A gold or large flask
  drunk in that time stays drunk. Example: he misjudges a slicer and dies; Grab plays the last five seconds back to where he stood
  before it, with two hours left.
- **Rise** (`respawn`): the floor is rebuilt from its seed at the last lit checkpoint (`L.cpIndex`, or the start door), with full
  hearts and the sands back to 3. Latching plates pressed before the checkpoint are pressed again and their gates open
  (`S.cpPlates`); guards and snakes before it are gone; everything else is as generated.
- **Checkpoints**: the sky clock (Nut's, `nutClock`). Passing within 14 px lights it (`standOn`): it becomes the
  respawn point and refills the sands. [checkpoint](elements/checkpoint.md).
- Falls are counted per floor (`S.floorDeaths`, the card's "Falls") and per run (`S.deaths`); a rewind counts as a fall.

## Timed gates

A plate raises a gate (`pressPlate`). A latching plate keeps it open for good; a timed one starts its timer (`f.g.tm = f.g.dur`) and
the gate drops when it runs out; a closing plate (`closer`) slams it. The HUD shows the nearest running timer.

| Gate | Timer (`g.dur`) |
|---|---|
| plate a few tiles before the gate | the time to run there at `RUN`, times a slack of 1.03 to 1.15 (tighter as `L.d` grows): run over the plate without stopping |
| plate out of sight (up a climb, down a hole, back the way he came) | `estPath` of the way from plate to gate at its plain pace, times `timerK()` (0.84 + 0.14 rng + 0.1 (1 - `L.d`)), + 0.3 s |
| timed remote plate (P4: press, then run for a gate ahead) | `estPath` at its careful pace, times `timerK()`, + 0.3 s |

`estPath` is measured against the bot, so the tightest factor stays beatable. Details: [gates](elements/gates.md),
[plates](elements/plates.md), [level-design.md](level-design.md).

## Fighting

He draws his sword (`enterGarde`) when a guard on his level (within 8 px of height) is within 64 px, unless he sheathed in the last
second (`P.peace`).

| Input in `garde` | Action | Numbers |
|---|---|---|
| Grab | strike | lands at 0.17 s, over at 0.4 s; reaches 6 to 40 px (`resolveStrike`) |
| Up | parry | lasts 0.36 s, blocks a blow arriving in its first 0.32 s; a parried guard reels |
| left / right | advance / retreat | 13 px over 0.2 s |
| Down | sheathe | 1 s before he engages again |

- A blow that lands costs one heart (guard or prince). Guards may parry his blows (`g.parry`, more after several quick blows,
  `g.cu`) and strike straight back (`g.ripo`).
- Ranks by tier: RECRUIT, SOLDIER, VETERAN (`TIERS`), and the CAPTAIN (`CAPT`) before the exit on every fifth floor from 5; their
  dress shows the rank.
- A guard who carries a reinforcement (`reinf`) calls it as he dies: it drops in 0.9 s later a few tiles ahead of the prince
  (`pendingGuards`, `dropSpot`). A side passage's flask can wake an ambush that drops in on the way back out.
- A skeleton cannot be killed: each blow drives it back 12 px (`SKEL_KNOCK`); it falls only into a pit.
- Snakes live in tunnels. Strike one with Grab standing (within 44 px, `lowStrike`), or crouch, Grab to draw the blade low, then Grab
  to thrust in a tunnel (`poke`). A snake coils for 0.42 s before it strikes; a bite costs a heart, but crouched or poking it does not
  stagger him (no `hurt` state), and hanging, climbing or in the air he is out of its reach.

Guards' moves, budgets and looks: [guards and snakes](elements/guards-and-snakes.md).

## The chase

From floor 6 about two floors in three hold one chase (a 0.65 roll; the route plan then keeps a run heading right of 70 columns or
more for it; `chaseSeg`, `L.ext.chase`): a checkpoint before it, a long corridor of obstacles that never ask him to wait, and the dark behind him. It wakes as he passes the
corridor's second column heading right, four tiles behind him, moves after 0.7 s at 55 to 92 px/s (`chs.v`, fitted to the corridor;
he runs at 100) and surges when he gets more than 190 - 30 `L.d` px ahead, so any stop lets it catch up. It kills when he is less than
4 px ahead of its line (`die('sand')`), and ends at the arch at the far end (`chs.done`). Details: [the dark](elements/the-dark.md).

## Hints and learned moves

- A hint is a banner (`msg`, 3.8 s) chosen by `checkHints` from what is ahead of him (traps two tiles on, ledges, lifts, flasks,
  checkpoints, gates, guards, the door). One at a time; one waiting over 2.5 s is dropped.
- Move hints (`HINT_MOVE`: gap, wide, climb, drop, spikes, crawl, fight, parried, poke, snake, potion, plate, block, wallrun,
  walljump, swing, banner, shaft, collapse, jgrab, lift, chain) come back once a floor until the move is done (`learn(id)`, stored in
  `S.learned`). Every other hint shows once ever (`S.hints`).
- Both survive a new run (`newSave(prev)` keeps `hints`, `learned` and `set`).
- Learning changes some looks: the kick shaft's jet stream fades to 0.65 once `shaft` is learned, the jgrab jump's goes once
  `jgrab` is learned ([kick shafts and jet streams](elements/kick-shafts-and-jet-streams.md)).

## The bot: the reference player

`dev/tools/bot.js` plays a floor through the game's own input (`H.setKey('kb', ...)`), one action of `L.path` at a time:
`runBot(n, seed, opts)` returns `{ok, n, seed, frames, hurt, fights}`. Every trap the generator lays pushes its action onto
`L.path`, so a new trap needs its action in `bot.js`.

- Actions: walk, climb, drop, hangdrop, sjump, rjump, rjumpg, jgrab, tiptoe, runover, crawl, timed, saw, darts, dash, dashjump,
  wallrun, walljump, swing, slide, lift, sandlift, collapse, push, pull, drink, look, door.
- `opts.fight` keeps the guards and fights them (`H.load(n, seed, test)` drops them otherwise); `opts.entry` plays the floor's entry;
  `opts.at`, `opts.done`, `opts.path` start, end or steer a test. Math.random is seeded from the floor and seed, so a run replays
  exactly.
- The bot always takes the safe way; `forktest.py` and `hdtest.py` take the damaging one.
- `estPath`'s times are measured against it, so the gate timers are sized by its pace.
- `?bench` drives it from the real frame loop (`botGen`).
- `run2.py 1 27 4` (bot, four seeds, no fighting, 0 runs with damage) is the main regression; the full suite is in CLAUDE.md.
