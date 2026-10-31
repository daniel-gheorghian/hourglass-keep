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
- How to play (title and pause menus; round 49a, owner: "keep the how to play screen that describes what the buttons do") says what each
  button does and the few rules no look shows: Run, Jump (from a standstill or from a run), Up and Down (climb, hang and let go, crouch and
  crawl, the chimney's kicks, Down to let go, Up at the top to leap out), Grab (its word; catching a ledge or a tapestry while falling; the
  careful step; push, pull, drink, strike; in a fight Up blocks and Down sheathes), after a fall (Grab turns back the hours, Jump rises at
  the last sky clock or the floor's start), the three hours and the sky clocks, the flasks' colours, the keys. No jump distances, no trap,
  gate or fight tactics: those are found in play.

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
| Sound | `S.set.sound`, `S.set.sndQ` | round 50c: Full, Quiet, Off in turn (the button reads "Sound: Full"); an old save's on is Full, off is Off; a stone click at the new level (`plate`), no longer the clock's chime ([Sound](#sound-round-50c)) |
| Battery saver | `S.set.saver` | canvas at 1x device pixels and every other frame drawn (`loop`: `frame&1`) |
| Pad on right | `S.set.lefty` | mirrors the controls |
| Softer flashes | `S.set.calm` | screen flashes at 0.3 of their strength (`flashScreen`) |
| Crossings | `S.set.cross` | the interlude at theme changes; on unless set false |
| Graphics… | `S.set.gfx` and `S.set.lightMode` | toggles Lighting, Atmosphere, Colour grade, Lit characters, Effects & camera, New characters, Background (`GFX()`, all on by default); and the lighting mode button "Lighting: Torchlight / Classic" (`gShader`) |
| Tools… | `S.set.fps` and reloads | Show FPS (off by default); Benchmark, Benchmark (classic), Benchmark (auto scale), Profiler reload with `?bench`, `?bench=classic`, `?bench=auto`, `?prof` |
| Restart floor | | the floor from its start door, checkpoints and pressed plates cleared; the floor clock runs on |
| How to play, Title screen | | How to play (round 49a): the buttons and the short rules only (below) |

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
| Wade / clamber | hold left or right in a sand drift / on a rubble heap | `HILL_WADE` 42 / `HILL_CLIMB` 35 px/s | drawn walking (the clip's walk cycle) knee deep in the sand or on the heap's surface; no jump of any kind on either, and none carries him onto one: a jump that would is checked to land short of its foot, then he tests it with his foot (round 47a); no crawl into one. Look only: he stays on the floor's level ([heaps and drifts](elements/heaps-and-drifts.md), round 43) |
| Into the wind | hold left or right against a wind (round 44; round 45c) | `RUN` (1 - 0.35 e): 65 px/s in a steady draught; at a gust's peak 55 (floors 7-12, peak 1.15), 48 (13-24, 1.25), 40 (25 on, 1.375); 70 on a drift's approach, the wade 33 | never a help going with it; a jump into it loses its drag (a running jump 14%, more at a gust's peak); a gust's lull (1.8-2.8 s, then a 0.6 s warning) always lets a jump through; standing in a gust he is pushed back at up to 16 px/s, never over an edge, crouched he holds; after a death in a zone it eases to 60%, after two to 30% (kept through rewinds and respawns, cleared at the next floor). [wind](elements/wind.md) |
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
| Wall run | Jump while running at a wall within 30 px, two storeys of wall ahead, open above him (not a kick shaft's wall: round 48b) | 234 px/s up at half gravity (`WR_V`, `WR_G`): rises 78 px; catches a ledge two rows up | `startWallRun`; learned as `wallrun` |
| The chimney (kick shaft, round 48b) | in: a running Jump at its wall, a standing Jump at its foot facing the ledge's wall, or Up at its foot (walking or falling in does not lock him); then one press of Up a kick; Up at the top stance is the Y; Down lets go at once; Jump and Grab do nothing (dimmed) | the jump in 0.3 to the first stance; stances at feet 50 + 46 n px over the foot's floor (`CHM_G0`, `CHM_GS`), resting as long as he likes; a kick 62 px/s across, 0.32; the Y: 0.18 gathering, up 12 px past the lip, landing 12 px onto the ledge; press to standing on the ledge 1.65-1.93 (two storeys), 2.15-2.43 (three) | no kick off a single wall anywhere; nothing locks in a lift's shaft; [kick shafts](elements/kick-shafts-and-jet-streams.md) |

The drawn jump differs from the physics (lower apex, stride for the distance, take-off foot): look only, see CLAUDE.md rounds 26c-35a
and [prince](elements/prince.md).

### Ledges, cloth, bars and lifts

| Move | Input | Numbers | Notes |
|---|---|---|---|
| Hang from an edge | Down within 26 px of an edge with open space beyond | `climbDown` 0.6 | never from a broken lip (`hurtdrop`) |
| Climb up | Up (or held) while hanging | `climb` 0.72 | |
| Let go | Down or Jump while hanging | the fall starts from the hang, his feet already 57 px under the lip | the way to take the sting out of a two-storey drop |
| Catch a ledge | Grab held while falling; any jump, wall run or swing release catches on its own (`P.autoGrab`; not the chimney's flights) | the hands pass the lip's height within 12 px of the hang point (`findLedge`) | a fall without Grab catches nothing; a cracked slab grabbed starts to give way |
| Slide down a hanging | hold Grab while falling past one, or Grab + Down while hanging over one | bites for 0.07, then `SL_V` 170 px/s (braking `SL_A` 1100) | no fall damage at the foot; letting go of Grab drops him; [banners and slides](elements/banners-and-slides.md) |
| Swing | catch a bar in reach of the hands (15 px across, 20 up or down) | period 1.15 (`SW_W`); dies down in ~4 (`SW_TAU`); a press of the way he swings arms one pump (`SW_KICK`, `SW_PRE` 0.8) | Jump throws him, more the faster he swings; it carries over from `SW_CLEAR` 0.55 (a chime); Down held 0.15 lets go; [swing bar](elements/swing-bar.md) |
| Ride a counterweight lift | stand on the platform, hold Up or Down | `LIFT_V` 64 px/s | a plate on each landing calls it (`lplate`); he arrives standing (`P.liftHold`); [lifts](elements/lifts.md) |
| Ride a paternoster | hold toward the shaft as a slab passes the landing | `CHAIN_V` 44 px/s; boards within `CHAIN_TOL` 14 px | step off by holding away as a slab passes a landing |
| Ride a sand lift | stop on its slab | sinks at `SAND_LV` 140 px/s after `SAND_LW` 0.25, once, and does not stop at the foot (round 41): it goes on into a spike pit a storey under it | get off at the foot: the arrow toward its open door, Up or Jump (kept 0.3 s) from the door 45% open (the slab 22 px over the floor) until the slab is 60 px under it (0.59 s): within 20 px of the floor a step out, deeper a jump to the lip; missed, he is impaled on the spikes; [lifts](elements/lifts.md) |

## Falls

The drop is measured from where the fall began (`P.fallY`: the take-off floor of a jump, the hang, the chimney's stance he let go from) to the floor he
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
| a court's pool (`drown`, round 45): falling through its surface, 11 px under the walking floor | death (a storey sooner than the stakes under it) | |
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
- **The death card** (round 50c, owner: "D2 death screen", ash): over `DTH_F` 1.2 s the picture drains of colour (Torchlight: the
  composite's `u_dr`; Classic: a `saturation` blend with grey) and darkens to near black (`DTH_DK` 0.64, the HUD with it); the cause is one
  quiet italic line in bone (`DTH_BONE`, lower case, e.g. "the fall was too far.") at 0.6 of the view; from `DTH_CT` 2.2 s a faint line at
  `DTH_CA` 0.35: "grab · turn back the hours      jump · rise" (no sands left: "jump · rise"). The timings above are unchanged; the sound
  is a drum and a breath (`die`).

## Timed gates

A plate raises a gate (`pressPlate`). A latching plate keeps it open for good; a timed one starts its timer (`f.g.tm = f.g.dur`) and
the gate drops when it runs out; a closing plate (`closer`, since round 48a drawn exactly as an opening plate, with no warning) slams it. The HUD shows the nearest running timer.

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

## No hints; learned moves (round 49a)

- No hint banners (round 49a, owner: "the Dark Souls thing ... the part where you discover how and what works. I would drop all hint
  messages, rely only on subtle graphic hints ... I would keep the how to play screen that describes what the buttons do"). Until v89 a
  banner (`msg`, 3.8 s, chosen by `checkHints`) named what lay ahead: 53 texts in `HINTS` (traps, ledges, lifts, flasks, checkpoints,
  gates, guards, the door), move hints coming back each floor until learned. They are gone with `checkHints`, `hint()`, its queue and the
  'hint' banner kind. So are the messages that told what to do or what happened: the flask names ("Red flask. One life restored.", the
  large red, gold and poison lines), the rewind's "The hours turn back. N hours left", the sky clock's "...your hours are restored. If you
  fall, you rise here.", "No room to draw a sword in here..." (now the `bump` alone), "Sealed. A floor plate somewhere opens this door."
  (now a rattle, `sealed`), the gate lines (`gateMsg`) and "A heavy door grinds open somewhere on this floor." (the glance, below), "The
  slab lands on the plate and holds it down.", "The cracked floor behind you is starting to give way. Run!", "The dark wakes behind you.
  Run!", "Dawn breaks at the arch...", "Ambush! A guard drops in...", and the death card's "Spikes spare a careful step...".
- Kept: the Grab button's word (`grabLabel`), the floor's banner and the card's rare flag (`FLAG_TEXT`), the Crossing's pad cue, the death
  card's cause and its two lines (Rewind, rise), How to play (the buttons and the short rules, below), the tools' messages (`?bench`).
- What tells instead: the looks (the jet streams, the gold flask's stars, a gate's sky clock and the HUD's countdown, the cracks, the sand
  running from a roof block), the sounds, and for a gate or door opening out of sight the glance (below).
- `learn(id)` still sets `S.learned` where a move succeeds (`LRN_ST`, `learnGrab`, `land`, ...; the ids in `LEARN_IDS`), and the looks read
  it: the jgrab jump's jet stream is drawn until `jgrab` is learned, the swing's throw at 0.75 once `swing` is, the kick shaft's at 0.65
  once `shaft` is (learned at the Y out of the top since round 49a). `S.hints` stays in the save, unused; `newSave(prev)` keeps `learned`
  and `set`. `__HK.HINTS` is an object of `LEARN_IDS` (and `__HK.HINT_MOVE` their Set), so the tools' `for(const id in H.HINTS)` loops still
  set every learned flag.

### Out of sight: heard where it is, and a glance (round 49a)

A gate whose plate is far from it (a remote plate, `f.where`: P1 detours, P4 races, the loop's violet plate; a latched gate's first press;
a slab that lands on a plate) and the exit door (`xplate`) used to name themselves in a banner (`gateMsg`: "A gate grinds open far below,
but its hours are running out..."; "A heavy door grinds open somewhere on this floor."). Now (`gateCue`):

- **Its sound from where it stands** (`Snd.playAt(n, x, y)`): the gate's grind (`grind`, a timed gate) or the long rumble (`door`, a gate
  that stays open, the exit) routed through a lowpass, a gain and a `StereoPanner`: panned by its side of him (dx / 280 px, at most 0.9),
  quieter with distance (1.15 - d/900, at least 0.35, d with storeys weighted 1.6) and muffled the farther it is and the more storeys of
  stone lie between (9000 / (1 + d/220) / (1 + 0.7 storeys) Hz, 380 to 12000).
- **A glance** (`glanceAt`, `GLN`, `updateCamera`) when the gate is out of view: the view's target eases toward it over `GL_IN` 0.35 s,
  holds, and eases back over `GL_OUT` 0.5 s (`GL_T` 1.6 s in all; the camera follows at 4.5/s while it looks). Play goes on: input stays
  live and the prince is kept inside the view (`GL_M` 44 px from its sides, wholly inside it up and down), so the glance costs no time and
  hides nothing; no timer is held (a held timer would have needed play paused, which breaks a P4 race's run over its plate). If the gate
  is farther than the view allows he stays at its edge and the view shows the way to it. Once a plate (`f.told`; a latched gate once).
  None while the dark chases, in a fight, dead, on a test load (`__HK.load` sets `GLN.off`) or under `?bench`; a rewind or a new floor ends
  one.
- Why: PoP 1989 has neither (SDLPoP: a plate's event opens its door wherever it is, silently off screen; the player learns the level).
  Zelda (Ocarina of Time onward) and Metroid Prime cut or pan to a door a switch opened, with a chime; Dark Souls plays the far door's
  sound and, for the great ones, a short camera cut. Here the owner chose the sound plus a short glance (round 49 research); the glance
  keeps the prince in view because play never stops in this game but for death and the menus.
- `hinttest.py` checks it at every remote plate (the suite's floors 1-35; floors 1-16: 26 remote plates, 26 glances): one glance when the gate is out of view, none when in
  view or for the same plate again, the prince inside the view every frame, the view 100-240 px nearer the gate and back at rest, the
  timer at the game's rate.


## Sound (round 50c)

Owner (the "Dark Souls mood"): "no music in the floors", only the sky clock's motif; "Yes on all" to round 50b's prototypes; the silent
switch: "Let the user play his own music". Everything is synthesised WebAudio in the page (`Snd`), no samples, no square or bare sawtooth
voices.

- **The graph** (`Snd.build`, once at unlock): each cue -> `master` (the dry bus) -> `comp` (DynamicsCompressor, threshold -12 dB,
  ratio 3) -> `out` (the setting's level, `SND_LV` Full 0.3, Quiet 0.1) -> the speakers. The room: `master` -> `rvS` (the place's send) ->
  one ConvolverNode (`conv`, a stereo impulse made once: noise decaying 60 dB over `RV_T` 3 s, a lowpass closing as it decays) -> `rvLP`
  -> `comp`; and for low ceilings a slap (`slS`: delays of 17 and 29 ms, one fed back through a 2.2 kHz lowpass). The sends stand before
  the room, so a hall's tail rings on as he steps into a tunnel. A cue may add its own send into the room (`o.rv`: the motif, the
  death, the flasks).
- **The places** (`sndZone`, every frame; `Snd.env` eases the room over `SND_TC` 0.35 s, only when the place changes):

| Place | Test | Hall send | Slap | Room lowpass | Air bed |
|---|---|---|---|---|---|
| low ceiling | `lowAt(P.x, r)` | 0.06 | 0.32 | 2.6 kHz | 0.55 |
| room (a corridor a storey high) | the cell above him not empty | 0.2 | 0.09 | 3 kHz | 0.8 |
| hall | headroom above | 0.36 | 0.04 | 3.6 kHz | 1 |
| shaft | headroom, walls both sides above, open two storeys | 0.55 | 0.06 | 4.4 kHz | 0.9 |
| court | in `L.courts` on his row | 0.07 | 0.02 | 5.2 kHz | 0 |
| the Crossing | `mode` 'cross' | 0.03 | 0 | 4.2 kHz | 0 |
| menus, pause | otherwise | 0.2 | 0.05 | 3.2 kHz | 0 |

- **The air bed** (`Snd.bed`): a looped low noise (lowpass 180 Hz) breathing on a 0.07 Hz swell at `SND_BED` 0.03 times the place's
  share, and a far drip now and then (`drip`, every 3-10 s, played where it falls by `playAt`), only in play.
- **The cues** (names and call sites as before): `cp` the motif (a lyre's plucked D, A, F, Karplus-Strong strings made once, `Snd.pluck`,
  with a low D under the last, over a low open fifth breathing in and a breath of fire); `die` a low frame drum and a breath falling away;
  `clear` silent; `life` a deep bowl over a low string; `drink` gulps with a faint ring; `poison` choked gasps; `clang` bronze
  (inharmonic partials 1 : 2.76 : 5.4 : 8.93 : 13.3 over noise); `hit`, `hurt`, `guardDie` body sounds; `rewind` sand drawn back (a swell
  like a sound played backward, grains ticking faster); `swready` the ropes drawing taut and a breath (still the swing's cue); `chomp` a
  bronze bang; `bones` dry knocks; `tick` a stone click; `draw` a bronze scrape; `exitlight` air; `step` two layers and the weight,
  each step a little different, carried by the room; the birds of the Crossing through a formant. The rest were already physical.
- **The setting**: Full, Quiet (about -10 dB), Off (`S.set.sound`, `S.set.sndQ`; `Snd.setLevel`).
- **iOS**: `navigator.audioSession.type` is 'ambient' where it exists (it mixes with the player's own music; the silent switch silences
  it); the context is suspended while the page is hidden (`Snd.sleep`, `visibilitychange`) and resumed when shown, on `pageshow` or by the
  next touch or key (`unlock` resumes any state but running, iOS's 'interrupted' too).
- `sndtest.py` (suite.py play): every cue rendered offline through the whole graph (`Snd.render`): no NaN, under 0 dBFS after the
  compressor alone and piled up, audible, the setting's levels; the live context unlocked by a key, every cue, the places, sleep and wake.

## The bot: the reference player
### Tells: his body, the grit, the swing's beat (round 49b)

Round 49b (owner after the round 49 research: "rely only on subtle graphic hints"; his choices: the animation tells, grit over a slab's plate, the swing's beat as sound). Look and sound only: play, layouts, the bot and every timer unchanged.

- **The tells** (`tellTgt`, `tellKind`, `TELL`; Limbo's lesson, the boy turns toward what can be used). Standing still `TL_D` 0.5 s (not
  in a fight, the chase, a wind, a stumble; nothing held) he turns to what is there, eased in over `TL_IN` 0.55 s and dropped at once by
  any input: under a ledge he can climb, facing it, he looks up and lifts his hand toward the lip where his hands would hang (`reach`);
  at an edge he can hang from he glances down (`edge`); stakes within a step ahead, on his floor or in the pit before him, he eyes them
  (`stakes`); a flask on his floor up to 44 px ahead, he looks at it (`flask`); at the mouth of a low tunnel he stoops with a hand on the
  lintel's end (`low`); locked in the chimney, planted between kicks for `TL_CD` 0.5 s, he looks up the shaft (`chim`). Order when more
  than one holds: flask, stakes, edge, reach, low. `tellscan.py` checks them (none before 0.5 s, full by 1.2 s, gone the frame Grab is
  held, the pose back 0.35 s later, play identical with `TELL.off`; it takes no spot in or within 16 px of a wind zone, where `tellIdle` gives
  none: the wind's lean and a gust's arm come first, and a lull can end at any moment; round 49d).
- **Grit over a slab's plate** (`drawGrit`, `gritList`): where a cracked slab in a gallery can jam the plate or closer under it (the
  slab-holds-plate puzzles P2G1 and P3G1), single grains sift from its underside onto that plate, a few at a time with pauses, and a few
  lie on the plate; gone the moment the slab lets go. Faint and steady, unlike the roof block's thickening threads of sand.
- **The swing's beat** (`swbeat`, `SWB`): each turn of the swing creaks on the log, louder and a little higher as the swing grows; while a
  pump is armed (a press waiting for the bottom) the turn is brighter, with a breath of air over it. Under the ready chime.

### Wear and bones (round 49c)

Round 49c (owner after the round 49 research: "rely only on subtle graphic hints"; "All five you suggested": the last two). What has been
used is worn, and where a thief died before him his bones lie. Look only, placed from the layout alone (no generator stream: layouts,
play, the bot and the timers unchanged). `wearscan.py` checks the rules.

- **Sandal scuffs** on the face of every wall the route runs up (the wall run), at the heights his feet strike it (6, 27, 48 and 69 px over
  the floor), near the face's edge on the side he runs at: dark translucent smudges of soles with fainter older ones and a pale scratch.
  Kick shafts take none (their grips and jet stream already mark them).
- **Drag grooves** on every cell a movable block can travel: two shallow grooves where its bottom edges scrape, a small ridge of grit at
  each end of the track. In the floor's own picture, so the block stands over them and they never cross its face.
- **Bones of earlier thieves** at the first trap of each lethal kind on the floor by the route's order: a walled spike pit (remains among
  the stakes), a banner shaft's foot (bones and a torn strip of the runner), a slicer (a skull and bones by its jaws), a sand lift's
  spike pit (half in the sand on the pit's floor, seen while he rides down). Once a kind a floor: the lesson where it is first met, not a
  signpost at each one (about 3.5 sets a floor). Lying, partial, bleached and dusty, never upright, no sword, no blood, so never a
  skeleton guard; on a route tile they lie behind his walking line, low, never in his way.

### Stronger grit, grooves and scuffs (round 50a)

Round 50a (owner after v90: "Yes, strengthen the grit, grooves and scuffs"; from pictured levels A, B, C he chose grit B, grooves C,
scuffs B; `CUE`, level 0 is v90's look). At phone size the three had barely read. Still hints, not signposts; look only.

- **Grit**: more grains (26), each streaked along its fall, a few larger with a lit top; now and then a thin trickle that breaks into grains
  as it falls (never the roof block's continuous threads); a small cone of grit on the plate, growing over the floor's first two minutes.
- **Grooves**: the track polished lighter, scrape marks along it, the grooves a dark trough with a lit near lip that wander a little in
  depth (never along a tile's seam), ridges of grit pushed up at the ends.
- **Scuffs**: a lighter worn patch up the face where his soles rub, each strike a sole print with a skid smear down from it, pale scratches
  and dust specks.


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
