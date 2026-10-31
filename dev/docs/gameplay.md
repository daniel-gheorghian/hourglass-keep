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

Pause shows the floor's number and name, this floor's time, the run's time and the falls (since round 50g the only place the
floor's number and time are shown), then:

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
- The HUD (`drawHUD`; round 50g, A2, owner: "Agree with the changes"): the hearts and three sky clocks for the sands only, in muted
  ochre (red-ochre hearts `HUD_HEART`, the clocks' quiet palette `NUTQ`, no glow), with no dark band behind them; the floor's number and
  its time are in the pause menu. It fades to `HUD_LO` 0.36 when nothing has changed for `HUD_HOLD` 3.5 s (over `HUD_FADE` 1.4 s) and
  is back at `HUD_HI` 0.9 within `HUD_RISE` 0.22 s on any change (a heart lost or gained, a sky clock spent or regained, a new floor),
  and held there at the last heart, in a fight, a rewind, while dead or paused (`hudFadeTick` once a frame on gameTime, `hudAlpha`
  quantised to `HUD_Q` 24 steps, so Torchlight's HUD canvas, `hudKey`, is redrawn only at each step). Unchanged and always at full
  strength: the nearest running gate timer in the middle (it flashes under a quarter), a foe's hearts and rank on the right (a skull for
  a skeleton), Show FPS.

| Flask (`it.type`) | Effect |
|---|---|
| small red (`heal`) | +1 heart |
| large red (`big`) | all hearts; rare, at the far ends of gated side passages |
| gold (`life`) | +1 to `S.maxHp`; in side passages without a gate; once taken on a floor it stays taken (`S.lifeTaken`) |
| dark blue (`poison`) | -1 heart |

A drink's flash (round 50g, A7) is a soft tint at the screen's edges, the middle (the prince) left clear: shorter and less saturated than
v90's (`FLASK_FL`: heal and big `#b0705a` at 0.2 / 0.26 over 0.2 / 0.28 s, life `#bfa477` 0.26 over 0.28 s, poison `#5f8a68` 0.22 over
0.22 s; v90 `#ff6a3d`, `#ffd76b`, `#3fae66` at 0.38-0.5 over 0.3-0.45 s, capped at 0.3 at the edges). Softer flashes still takes 0.3 of it.

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
- Falls are counted per floor (`S.floorDeaths`) and per run (`S.deaths`, the pause menu's); a rewind counts as a fall. (The card no
  longer shows them, round 50g.)
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
  (now a rattle, `sealed`), the gate lines (`gateMsg`) and "A heavy door grinds open somewhere on this floor." (the gate cue, below), "The
  slab lands on the plate and holds it down.", "The cracked floor behind you is starting to give way. Run!", "The dark wakes behind you.
  Run!", "Dawn breaks at the arch...", "Ambush! A guard drops in...", and the death card's "Spikes spare a careful step...".
- Kept: the Grab button's word (`grabLabel`), the floor's banner (the theme's name, round 50g) and the card's rare flag (`FLAG_TEXT`), the Crossing's pad cue, the death
  card's cause and its two lines (Rewind, rise), How to play (the buttons and the short rules, below), the tools' messages (`?bench`).
- What tells instead: the looks (the jet streams, the gold flask's stars, a gate's sky clock and the HUD's countdown, the cracks, the sand
  running from a roof block), the sounds, and for a gate or door opening the gate cue (round 50e, below; round 49a's glance is gone).
- `learn(id)` still sets `S.learned` where a move succeeds (`LRN_ST`, `learnGrab`, `land`, ...; the ids in `LEARN_IDS`), and the looks read
  it: the jgrab jump's jet stream is drawn until `jgrab` is learned, the swing's throw at 0.75 once `swing` is, the kick shaft's at 0.65
  once `shaft` is (learned at the Y out of the top since round 49a). `S.hints` stays in the save, unused; `newSave(prev)` keeps `learned`
  and `set`. `__HK.HINTS` is an object of `LEARN_IDS` (and `__HK.HINT_MOVE` their Set), so the tools' `for(const id in H.HINTS)` loops still
  set every learned flag.

### Out of sight: heard where it is, and a glance (round 49a; the glance gone in round 50e)

A gate whose plate is far from it (a remote plate, `f.where`: P1 detours, P4 races, the loop's violet plate; a latched gate's first press;
a slab that lands on a plate) and the exit door (`xplate`) used to name themselves in a banner (`gateMsg`: "A gate grinds open far below,
but its hours are running out..."; "A heavy door grinds open somewhere on this floor."). Now (`gateCue`):

- **Its sound from where it stands** (`Snd.playAt(n, x, y)`): round 49a's `grind` and `door` (since round 50e `gopen` for every gate and
  `gdoor` for the exit, the gate cue below) routed through a lowpass, a gain and a `StereoPanner`: panned by its side of him (dx / 280 px, at most 0.9),
  quieter with distance (1.15 - d/900, at least 0.35, d with storeys weighted 1.6) and muffled the farther it is and the more storeys of
  stone lie between (9000 / (1 + d/220) / (1 + 0.7 storeys) Hz, 380 to 12000).
- **A glance** (round 49a to round 50e; gone): the view's target eased toward a gate out of view over 0.35 s, held and eased back (1.6 s in
  all), the prince kept inside it. The owner after round 50's research: "the current animation is distracting pulling the screen like
  that". The gate cue below replaced it.
- Why: PoP 1989 has neither (SDLPoP: a plate's event opens its door wherever it is, silently off screen; the player learns the level).
  Zelda (Ocarina of Time onward) and Metroid Prime cut or pan to a door a switch opened, with a chime; Dark Souls plays the far door's
  sound and, for the great ones, a short camera cut.

### The gate cue (round 50e)

Owner, on the r50r research's alternatives: "Go with your recommendations ... 1. Both: and apply to onscreen gates 2. Keep and apply to
onscreen gates 3. Go with the same - no camera glance. Need another way to differentiate [the exit] 4. Yes [the head] 5. No [no sand
draft] 6. Keep [the closing grind] for all, especially since we are going with the dark souls theme 7. Harmonize these decisions with
the dark souls theme"; for the lifts: "The lift doors: same sound and shake treatment". No camera move, nothing said: the keep itself
answers a plate, as Dark Souls' far doors do.

Every gate that opens from shut (a plate's `pressPlate`, an in-line gate too, on screen or off; a latched gate's first press; a slab
landing on a plate, `jamAt`), the exit door (`xplate`) and every lift's mouth slab is one cue (`gateCue(g)` -> `gcue(k, x, r)`, k `gate`,
`door`, `lift`):

| Part | Gate | Exit door (the great door) | Lift mouth |
|---|---|---|---|
| Sound, from where it stands (`Snd.playAt`, the room's reverb, ducking the ambience; never cut by 50d's voice cap) | `gopen` 2.5 s: the counterweight's low rumble in the wall, the slab grinding up, a stop thud at 0.36 s (it opens in 0.33), the rumble dying, grit pattering for two seconds | `gdoor` 3.8 s: a deeper, longer rumble with judders while the leaf rises (2.2 s), a heavy boom at the top, the outside air rushing in (filtered noise swelling and settling) while the room's air bed lifts (`Snd.bedLift`), longer grit | `lopen` 1.5 s: a lighter grind, home at 0.3 s, a short patter |
| Shudder (`shake`: Calm halves it, Effects off none; none on a test load) | 1.3 px, 0.8 at the stop | 2.3 px, 2.5 at the boom | 1.0, 0.6 at the stop, only in view or within `GC_LN` 300 px |
| Grit from the ceilings (`drawCueGrit`) | `GC_G` 110 grains: over it on its row in view (58 px either side), else at the view's edge toward it on his storey and the two beside it | 190, wider (84 px; 0.55 of the view at the edge) | 24, at the mouth (16 px), only in view |
| His head (`tellTgt` 'listen') | standing, nothing held: lifted toward it at once for about 1.2 s (`GC_LT` 1.6 s with the eases) | the same | none |
| Light | | `doorFlare`: the doorway's light a little brighter while the leaf rises | |

The grit is single sand-coloured grains (`sandC`), each letting go once (early ones more), at a depth of the corridor, falling from the
first slab or stone above (an open hall's two storeys) to the floor's top, streaked, lying a moment and fading; none where there is no
ceiling or inside a wall, none on the front plane (`onFace`). Not the roof block's threads (`sandFlow`) nor round 49b's steady sift over a
slab's plate. The head: on the tells' target before `followPose` (its overlap eases it in and out), craning up and back when the gate is
behind him, higher for one above, lower for one below; look only (P.x, P.y, state and every timer unchanged). `GCUE` keeps the last six
cues and everything drawn is a pure function of gameTime - t and hashes (rewind-safe, nothing allocated a frame; a rewind drops cues later
than its clock, `gcuePrune`; a new floor clears them).

Closing (owner: "Keep [the closing grind] for all"): every gate's closing is heard where it stands, near or far, through `playAt`'s falloff:
`gshut` as the slab starts down (`slam` heavier and quicker for a closer's slam, which keeps its own shake) and `gthud`, a deep stop at the
sill; a lift's mouth closing `lshut` (grind and thud in one).

`hinttest.py` checks it at every remote plate: one cue, its sound at the gate, the grit's side, the view never pulled (within 6 px of its
rest), the head lifted with P.x/P.y/state unchanged, no second cue while the gate is open, the timer at its rate (floors 1-12: 37
remote plates, 37 cues, the view at most 1 px off its rest; 171 cues while the bot played). `sndtest.py` checks the cues' lengths, the door's boom, the falloff and the duck.

### The summoned lift (round 50e)

Owner: "the lift should not be waiting for the prince. It must be always on the other level and the prince must summon it"; then "Faster
empty" and "Sound and shudder, no glance". A counterweight lift now rests at the end the route leaves it by (`liftSeg`), its far mouth
open and his shut; the call plate on his landing (`lplate`) summons it. Empty it comes at `LIFT_VC` 128 px/s (two storeys a second),
eased in and out at `LIFT_VA` 480 px/s^2; ridden it keeps `LIFT_V` 64. While it comes he hears its counterweight rumble and its rope run
over the sheave from the shaft (`lsummon`, `Snd.playAt` at the platform), sees the rope's lay run, hears it dock (`larrive`) and its mouth
slab open (the lift's gate cue). Waiting: k storeys x 0.5 s + about 0.2 s of ease (lifttest: 1.18 s for two storeys, 1.68 s for three).
`estPath`'s careful pace (P4 races) adds k TH / `LIFT_VC` + 0.3 s (3 of 1,438 gate timers on floors 1-48 x 3 seeds, all P4 races, 1.3 s
longer); the plain pace is unchanged. The exit-side plate still sends it back; the paternoster and the sand lift are unchanged (the sand
lift's foot mouths take the lift's opening cue).


## Sound (round 50c)

(Round 50d adds footsteps by surface, traps and guards heard off screen and each theme's ambience: [below](#footsteps-traps-heard-off-screen-each-themes-ambience-round-50d).)

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

## Footsteps, traps heard off screen, each theme's ambience (round 50d)

Owner (the "Dark Souls mood"): "Yes on all" to round 50b's prototypes B3 (ambient beds) and B4 (footsteps by surface); "implement all of
them". Sound only: layouts, timings and play unchanged (`layoutcmp.py` against v90 same).

- **Footsteps by surface** (B4, `footSurf(x, y, me)`, `SND_SURF`, `Snd.foot`): each step, landing and crawl names what is under the
  foot and `Snd.play('step', surf)` (also `land`, `landh` for a landing of 60 px or more and a hurt one, under its `thud`) builds it from
  the surface's layers: a pat (lowpass noise), a click (bandpass), the body's thump (a sine falling) and one extra layer; each step a little
  different (the step count's sines), every one through the room's reverb.

| Surface | Where | Sound |
|---|---|---|
| `dungeon` | stone, the dungeon style (Nun, Garama, Hawara) | damp and dull, now and then a wet click |
| `palace` | stone, the palace style (West, Kerma, Shali) | polished limestone: a brighter click |
| `tile` | stone, the tile style (Blue Chambers, Well Corridors) | glazed faience: a short ringing tick |
| `forge` | stone, the forge style (Meroë, Napata) | a gritty floor: a high grit layer |
| `crypt` | stone, the crypt style (Osiris, Aksum) | hard granite: deeper, heavier |
| `sand` | a drift (round 43's wade) | a soft push and a hiss of grains |
| `rubble` | a heap | small stones knocking, three clicks |
| `plank` | a plank (a `loose` with `plank`) | a hollow wooden knock, now and then a creak |
| `grit` | a cracked slab (`loose`) | a crunch and a faint crack |
| `grate` | the fork's grating | bronze bars' partials and a rattle |
| `court` | a court's paving | dry, a little dust |
| `coping` | the cell beside a court's pool | stone with water lapping by |
| `hollow` | a counterweight lift's platform at its foot, under him or ridden, a paternoster slab | a box's boom |
| `sandslab` | the sand lift's slab | stone over running sand: a long hiss |

- **Guards** (`gstep`, `gland`, `gshift`): a guard's step as he advances or gives ground (`guardMove`), heavier, lower and quieter, a
  sandal's scuff after the heel; his landing when he drops in; and an idle guard at his post shifts his weight now and then (a scuff, a
  creak of leather, sometimes his hilt's tick; a 1.7 s clock of `gameTime`, 40% by a hash of his post), so he is heard before he is seen.
- **Heard off screen** (`Snd.tell(n, x, y, inView, surf)`): saws (`saw`), darts (`dart` and the warning `tick`), vents (`fire`), the
  slicer (`chomp`), the pendulum (`swoosh`), snakes (`hiss`, and `slither` now and then as they move) and guards are no longer silent
  out of view. In view they play as before (same step, full level), panned by side; out of view, within `TELL_R` 620 world px (storeys
  count 1.6 times), at 0.8 of the level and fading past `TELL_D0` 170 px and muffled by distance and by each storey of stone between (a lowpass). A step's
  requests are queued (the nearest `TELL_Q` 8, in order) and played at its end (`Snd.flush`, in `update`), so the timing is the
  step's own; at most `TELL_CAP` 4 out-of-view voices ring at once (`tvE`, their end times by `TELL_DUR`), the nearest first; in-view
  ones always play.
- **Each theme's ambience** (B3, `Snd.ambSlot`, `AMB_T`): over round 50c's air bed, on a clock of `AMB_SL` 0.25 s slots of the audio
  context, each slot's events picked by hashes of the slot, the floor (and the run's seed) and the room he is in: nothing kept in the
  game's state, so a rewind, a respawn or a checkpoint changes nothing. Chances a slot (about one in 1/p slots):

| Event | Where | Chance a slot |
|---|---|---|
| a far drip (`drip`) | every hall (the bed's places) | 0.03; Nun 0.11, Well Corridors and Garama 0.08, Aksum 0.02, Shali 0.015, Meroë 0.012 |
| a drop into standing water (`plunk`) | Nun 0.04, Well Corridors 0.02, Garama 0.01 | |
| the forge's far roar (`forge`) and bellows (`bellows`) | Meroë | 0.018, 0.02 |
| wind whistling in a slit (`whistle`: narrow bandpass noise gliding, no tone) | Aksum 0.022, Garama 0.02, Shali 0.018 | |
| stone settling (`settle`), grit trickling (`trickle`) | everywhere indoors | 0.005, 0.01 |
| the nearest lamp's crackle (`crackle`) | a burning lamp within 170 px | 0.22 |
| a rope creaking (`ropefar`) | a lift or swing bar within 380 px | 0.035 |
| a lit sky clock's embers (`ember`) | within 120 px | 0.3 |

  Each played where it is (`Snd.amb`: panned, quieter and muffled by distance and storeys) through the ambience bus `aB`, which carries
  the bed too and is ducked to 0.3 for about 0.5 s under the events (`SND_DUCK`: blows, clangs, hurts, deaths, gates, the clock, flasks,
  the slicer, the vent, the rewind). Not in the Crossing or the menus; drips, settling and trickles only where the bed breathes (not in
  courts). Quiet: 12 s of any theme's ambience over the bed peaks under 0.02 and its rms under 0.001 after the compressor, a phone speaker's
  murmur under the steps.
- `sndtest.py` (round 50d): every footfall cue on every surface (no NaN, under 0 dBFS, audible, no two surfaces alike within 6% in rms,
  brightness and ring), `footSurf` on a floor's tiles, the falloff of a trap heard off screen (with distance and through two storeys), the
  voice cap (11 requests, the nearest 4 played, none more while they ring, one in view still played, none past `TELL_R`), every theme's
  ambience (quiet, no NaN) and the duck. `wav=DIR` also writes the round's WAVs.

## The captain's drum, the title's piece, long noises whole (round 50h)

Owner on round 50h's prototypes: the duel "just a low drum", and after hearing both renders "For the captain duel: use just the drums, I
didn't like the other variant"; on the reinforcement "Carry to the last"; for the title "B: the Nubian lyre", played "Every time". Sound
only: play, layouts, timings and the bot unchanged (`layoutcmp.py` against v90 same).

- **The captain's drum** (`Snd.duel`, fed `duelState()` once a frame from `loop()`): a large frame drum (the Egyptian and Kushite tar)
  and nothing else: no drone, breath or swell over it, the fight's own clangs as they were. A stroke (`Snd.drum`) is a membrane's first
  three modes (1 : 1.59 : 2.14) as short sines gliding down, the skin's thud, the shell's boom in bands at 240 and 380 Hz (what a phone's
  speaker carries) and the hand's slap. The pattern is a heartbeat: `dum` on the beat, a softer `dub` 0.27 s after; every 8th beat two rim
  knocks (`tek`) for the dub; tense, a ghost knock off the beat every other beat and a doubled stroke every 16th. `DUEL_BPM` 64 calm, up
  to +`DUEL_UP` 10 tense (k 0.8 the prince at his last heart, 0.6 the foe at his, 1 both), up to 20% louder; the first four beats come in
  at 0.45, 0.65, 0.85, 1. It is laid `DUEL_LA` 0.15 s ahead on the audio clock (never the frame rate, the hit stop or the catch-up), on its
  own bus (`dB` dry, `dR` its sends), so one 50 ms fade stops what is laid ahead.

| When | The drum |
|---|---|
| the captain draws (garde within 100 px) or is the prince's foe | starts 0.25 s on, softly |
| he backs off (off his row, over 140 px) | beats on `DUEL_IDLE` 2.5 s, then stops (no last stroke); again softly if he comes back |
| the captain falls with his reinforcement still to drop in (floor 6 on: a veteran 0.9 s later) | beats on through it, on to the veteran (`capR`, marked by the drop) |
| another guard takes the prince on while it beats | he is one of the fight |
| the last of them falls (a blade or a fall) | one last stroke 0.42 s on (a grace stroke, the skin ringing 2.8 s to 33 Hz, the shell's rumble over 3.2 s), with `guardDie`'s thud |
| the prince dies | stops at once; the death's own frame-drum stroke closes it |
| the exit, the entry, a pause, the card, the Crossing, a rewind, Sound Off, the page hidden | stops; after a rewind (new guard objects) it starts afresh, softly, when the fight goes on |

  Captain floors are every fifth from 5 (`capFloor`); skeletons are never in the fight (they cannot fall). Nothing of it is in a
  snapshot. A beat is ~17 short-lived nodes for a `dum`, about 1.1-1.3 beats a second; the per-frame cost is a comparison.
- **The title's piece** (`Snd.title`, B "the Nubian lyre"): D minor pentatonic (D F G A C, as the Nubian tanbura and kissar lyres are
  tuned) on Karplus-Strong strings over a low open fifth (D2, A2) breathing and the air: a low D3-A2 ostinato every 1.5 s with a soft `dub`
  on the D, the sky clock's motif D4-A3-F3 at 4.5 s, the answer G3-A3-C4-A3, the motif closing G3-F3-D3 over D2, a last stroke at 19.5 s
  and two faint echoes; about 27 s (`TITLE_B`, rows laid `TITLE_LA` 0.5 s ahead), then its tail while the title stays: the air every 8 s
  and a far stroke every 11-16 s. Every time the title shows (the first load after the first touch, Quit to the title, the card's menu)
  the whole piece; How to play, Graphics and the confirm leave it playing. Leaving the title fades it over ~1 s (`tB` dry and `tR` its
  sends, both faded, freed 2 s on). Its strings are made at its start for it alone (`ksBuf(f, dur, true)`, 8 pitches, ~6 MB) and let go
  when its rows end. A fresh page's first touch on the title wakes the sound (a capture `pointerdown`: `Snd.unlock`; iOS and Chrome start
  audio only from a gesture), so it begins after the first tap. Quiet and Off as every cue (`out`); Off stops it and Sound back on plays
  the tail only; a hidden page's suspended clock holds it where it was. Not under `?bench`.
- **Long noises whole**: `Snd.noise` played its 0.8 s buffer once from up to 0.3 s in, so any noise longer than ~0.5-0.8 s went silent
  part way. The buffer is now `SND_NB` 2 s, looped, from a random point in it. Measured before and after (5 renders each, rms x1e4): the
  slit's `whistle` 0.27 to 1.74 (it was nearly silent), the Crossing's `breeze` 2.9 to 16.3 (its peak doubled: its volumes x0.55, peak as
  before), `exitlight` 4.3 to 6.3 (kept), the forge's roar +25% in peak (x0.8); `die`, `gopen`, `gdoor`, `lopen`, `storm`, `cliffwind`,
  `rockfall`, `cp`, `rewind` within the renders' spread (their long noises are low and already decayed by 0.8 s).
- **No click at a cue's start**: a GainNode's gain is 1 until its first automation event, so when a sound's start fell a sample before
  its `setValueAtTime(0.0001)` one sample went out at full level (spikes of 0.06-0.19 against ~0.005, found by the r50i research);
  `tone`, `noise` and the `howl` now make their gain at 0.0001.
- `sndtest.py` (round 50h): a 3 s noise still sounding at 2 s; the drum's tempo calm and tense, its entrance, one last stroke on the
  fight's end and nothing after it, a stop and a rewind's fresh start; `duelState` on floor 10's captain (held through his reinforcement,
  the last stroke on the last fall, stopped by a death and a pause); the title's piece, its tail, Quiet and Off, the fade when left; live:
  a fresh page's first key starts it, a floor stops it and frees its strings, Quit to the title starts it again.

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
