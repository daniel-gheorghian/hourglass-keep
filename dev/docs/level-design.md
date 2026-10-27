# Level design: the generator

Every floor is generated from its seed by `genLevel(n, seed)`: no hand-made levels or rooms (owner). This file covers the pipeline
from seed to floor, the random streams, the rules that keep floors long, paced and fair, and where each element may be placed. The
elements themselves are in `elements/`; play is in [gameplay](gameplay.md).

## At a glance

| | |
|---|---|
| Code | `genLevel`, `buildLevel`, `routePlan`/`routeWalk`/`stripPlan`, `buildTurn`, `randKits`, `landingObstacle`, `forkTop`/`forkChamber`/`forkFoot`, `featFor`, `puzzlePick`/`puzzleTry`, `remoteRoll`/`remotePlate`, `guardBudget`/`snakeBudget`, `estPath`, `timerK`, `breathe`; tables `MV`, `PRIM`, `LAND`, `KITS`, `MOVE_FAM`, `PUZ_FAM`, `OBS_FAM`, `FEAT_FLAGS`, `MENU`, `REM` (sections "generator", "the route", "loops", "oatmeal spice") |
| Seed | `levelSeed(n) = hash2(S.seed, n*7919+13)`; every stream is `mulberry32` of the floor seed or of `hash2(seed, K)` |
| Output | `L.base` (tiles `WALL`, `FLOOR`, `EMPTY`), `L.feat` (one feature per cell), `L.path` (the bot's plan), `L.segs`, `L.forks`, `L.feature` and the lists below |
| Bot | `dev/tools/bot.js` replays `L.path` action by action through the game's input |
| Checks | `run2.py`, `metrics40.py`, `featurescan.py`, `featbot.py`, `forkscan.py`, `forktest.py`, `hdtest.py`, `orphanscan.py`, `mazescan.py`, `guardscan.py`, `puzzlescan.py`, `p4bot.py`, `primtest.py`, `vertscan.py`, `wellcorr.py`, `sandshaft.py`, `slabscan.py`, `lampscan.py` |
| Pictures | `forkshot.py`, `chambershot.py`, `liftshot.py`, `mapshot.py` |

Terms: a **tile** is 32 x 64 px (`TW`, `TH`), a **room** 10 x 3 tiles (`RW`, `RH`). A **band** is one room-row of the plan; band b's
floor is tile row `6+3b`. A **run** is a stretch of route along one band; a **turn** joins two runs. "Storey" below means one tile
row (64 px), as in the rest of the docs.

## A floor's route

A plan at room scale (each box a room; one floor, schematic):

```
 col:     0     1     2     3     4     5     6     7     8     9    10
 band 0 [S > ][ >  ][ >  ][ >  ][ T1 ][ T1 ]
 band 1                         [ T1 ][ >  ][ >H ][ >  ][ >  ][ T2 ][ T2 ]
 band 2                                     [ s  ][ s  ]      [ T2 ][ T2 ]
 band 3                         [D < ][ <  ][ <  ][ <X ][ <  ][ <  ][ <  ]

 S  start door           > <  a run and its heading          D  exit door (end of the last run)
 T1 a turn carrying on: one band down, a chamber of two room columns (4, 5); its foot (4, band 1) sits
    left of the next run's first room (5, band 1)
 T2 a switchback: two bands down in two room columns, the next run heading back from the far column (10)
 H  a fork's hole in the upper run's floor     s  its short way, a chamber cut in band 2 under the upper run
 X  where the short way lands on the lower run
 long way (counted as the floor's length): H > ... T2 ... < X        short way: H, s, X
```

Runs never lie directly above or below another run (`freeRun`): the band between is left for side passages (galleries above a
corridor, cellars below) and a fork's short way. Floors 1 and 2 have one-column turns and exactly one switchback.

## The pipeline from seed to floor

| Step | Function | What it does |
|---|---|---|
| 1. Spice | `featFor(n, seed)` | the floor's featured families and rare flag (below); `L.feature` |
| 2. Size | `buildLevel` | `roomsN = min(28 + floor((n-1)*2.2), 72)` rooms of route, times `padK(n)` (1.52 to floor 5, then `PADK` 1.46: room for the plain floor after each trap), plus 4 rooms on a chase floor; `routeT = roomsW0*RW - 20` tiles (floor 1: 410) |
| 3. Plan | `routePlan` | 60 walks of `routeWalk` with a budget of `routeT * (ROUTE_SLACK 1.06, +0.03 to floor 8)`; keeps the best by score: aspect near 3:1 (`ROOM_W`/`ROOM_H` units), about 60% of turns going down, room for side passages, a switchback able to hold a fork, spare rooms at the end; on a chase floor a run heading right, 70+ tiles, between 12% and 70% of the route, not the last (`chaseRun`) |
| 4. Fork choice | `lrng`, `frng` | which switchbacks carry a fork and of which kind (floor 6 on) |
| 5. Runs | loop in `buildLevel` | each run filled from its own menu, its stops (fork pieces, a remote plate) at set columns; then the turn after it (`buildTurn`) |
| 6. Flasks | `buildLevel` | no secret passage built: an alcove's flask becomes the gold flask; other flasks thinned to `FLASK_GAP` (`round(35*PKW)` tiles) |
| 7. Sand lifts | post pass | a sand lift whose shaft is not walled (26e) or whose foot storey's kept walls would cap a jump (26g) becomes the banner slide (same tiles, bot `slide`, seg `turn-bannerK`); so does one (round 41) whose way on runs past its foot's far side onto anything but plain floor, or where any move on the foot storey after the ride walks to the foot, takes a run-up from it (rjump, rjumpg, jgrab, swing) or crouches within reach of the hole (darts, crawl; round 41c); the bot's `sandlift` gets the side he gets off by (`off`, `to`) |
| 8. Open hall | post pass | one row of headroom over every floor (below) and `L.windows` |
| 8b. Spike pits | post pass (round 41) | a sand lift with no rock in the storey under its foot (three cells wide) becomes the banner slide; the others' foot is opened (`EMPTY`) and the cell under it is a floor with fixed spikes (`f.rD`, `f.yP`), only the mouth on his way opens (`f.mo`), a sky clock or flask on the foot moved along the floor |
| 9. Settle | post pass | `f.ms` (sand lift mouths), `L.base0`, platforms at the top as floor, blocks as `WALL`, `L.dyn`, saws under a ceiling at his height become spikes (bot `tiptoe`, seg `spikes`), about 62% of timed side gates made to stay open (a hash), `rebuildBlocks`, `settleLevel` (lamps, hangings) |

`genLevel` tries `buildLevel` with `att` 0 to 7 (each a different route plan, `hash2(seed + att*7919, 7717)`; the main stream restarts
each time) and keeps the first that returns a floor (`L.att`). Any check that fails returns `null` and the floor is laid out again. The
last resort (`att = -1`) is `stripPlan`: one run heading right, no forks, no remote plates, no longway flag. A save made before the
chase-length change replays its floor with `legacy` (no spice, no chase rooms, no forks or remote plates).

The generator never reads the theme. It builds by `L.gstyle = GEN_STYLE[floor((n-1)/4) % 5]` (dungeon, palace, tile, forge, crypt);
`themeOf(n)` picks a theme of that same style from `SCHED`, so a floor's theme always has the style it was built by, and a change to
themes cannot move a layout. `style` keys the style traps: roof blocks (dungeon), planks (palace), the pendulum (tile), fire vents
(forge), the skeleton (crypt).

## Runs

`MX` and `PC(c)`: a run heading left is built exactly as one heading right, in mirrored column space (`PC(c) = MX - c`); `finishRun`
mirrors back everything that holds pixels or columns (items, guards, snakes, torches, checkpoints, blocks, bot actions, darters, saws,
bars, ambushes, segs). `W(c, r)` is true for a `WALL` cell inside the run's window (`vLo..vHi`) that no earlier run reserved (`resv`,
set by `keepClear` round each finished run and turn), and not on the map's edge. Every piece checks its cells with `W` first and writes
nothing when one fails.

Each step of a run draws one piece from a weighted menu (main `rng`); a piece that does not fit becomes one tile of plain floor.

| Piece | Weight | From floor |
|---|---|---|
| plain floor (1-3 tiles) | `FLAT_K` 3 (1 on floors 1-2), x1.4 (x4 with under two tiles of run-up), x2.5 on a dense fork's long way, x1.3 on barracks | 1 |
| gap 1 / 2 / 3 tiles (`sjump`, `rjump`, `rjumpg`) | 2.2 (floors 1-2) or 1.5 / 1.3 / 0.9 | 1 / 2 / 4 |
| step up / down (toward a target row) | 3 toward it, 0.5 away; a hash turns a step into `jumpup`, `collapse` or `jumpdown` (`cT`, `jT`, `jU` by featured family) | 1 |
| spikes, cracked slab, slicer, in-line gate | 1.1, 1.0, 0.9, 0.75 (x`TK` 0.75 on barracks; the first three x`OB()`) | 2, 3, 4, 3 |
| gate puzzle | 0.22 (0.30 from floor 7) x`PZ_W` 0.75; x0.5 if the featured puzzle is timed, x3.5 on maze, 0 on a dense fork's long way | 4 |
| swing bar, saw, darts, movable block, tunnel | 0.3, 0.1 x`OB`, 0.12 (only on the band's floor, not a raised step), 0.065, 0.45 x`OB` | 6, 5, 6, 7, 3 |
| style trap | 0.9 (pendulum 0.85) | dungeon from 2, else 1 |

Also laid in a run, outside the menu, in this order of priority: a checkpoint before the chase and the chase itself (`chaseSeg`); the
secret passage (`secretAt`); the exit plate (`xplate`, after 82% of the route); the exit guard (after it, past 84%); a guard after a
solved gate (`gateDue`); a pending puzzle (`pend`); a checkpoint every `CP_GAP` (`round(45*PKW)`) tiles on plain floor. After each
piece, on its last tile: a flask (7%, poison 20% of them from floor 8) or a torch (55%, 6 tiles apart); heal flasks in alcoves at 22% and 60% of
the route (`alcove`).

The last run carries rooms in hand: it stops once the route is `LAST_EXTRA` (38) tiles past the planned length and holds
`trapTarget` traps (9.5%, 8.5% or 8% of `routeT` by floor); a last run boxed in short of that lays the floor out again. It ends on
open floor, the door (`L.door`, shut until the exit plate) and a torch three tiles before it.

## Turns and chambers

From floor 3 a turn takes two room columns (`routeWalk` reserves both, the next run starting in the second); before that, one. Turn
weights (floor 3 on): one band down 0.30, two down 0.10, switchback (two down, heading back) 0.25, one up 0.25, two up 0.10.

`buildTurn(t, nextRow, need)` fills it with a **kit**: a sequence of moves whose rows add up to the turn's `3k`.

| Table | Holds | A new move adds |
|---|---|---|
| `MV` | `dr` rows (+ down, - up), `w` width in tiles, `n` first floor, `wt` weight among moves going the same way | one line |
| `PRIM` | the builder for each move (`drop2`, `down`, `up`, `banner3/4` (or a sand lift by `sandOr`), `shaft2/3`, `wallrun`, `collapse`, `jumpdown`, `jumpup`, `hgap`, `gslot`, `lift2d/3d/2u/3u`, `chn2d/3d/2u/3u`), with floor gates (wall run and collapse 3, banners and jumps 4, shafts 5, paternoster 8) | one line |
| `LAND` | where he stands after the move, from its end column | one entry |
| `KITS` | the old fixed kits per turn (`d3`, `d6`, `d6r` for switchbacks, `u3`, `u6`): the fallback | - |

The attempts, in order: fresh kits from `randKits` (8, or 16 when a move family is featured) with landings; the old `KITS` shuffled
with landings; the old `KITS` bare. Kits holding most of the featured family go first (`byFam`). `randKits` weighs the featured family
up until it holds `SH` of each draw (0.55; tower 0.92, rotten 0.75). A switchback's last move drops two or more rows and is not a lift
(the way back runs through its foot), and nothing may stand just above the floor it returns along. A paternoster (`CYC`) is never in a
turn that holds a gate slot. Each piece is journalled (`jr`, `snap`, `restore`), so a failed kit is taken back whole.

**Landings** (between two moves): `CH_PLAIN` 0.6 of chambers are plain throughout (the moves are the challenge); otherwise each
landing is plain with `LAND_PLAIN` 0.7 (keeping at least one obstacle a chamber) or gets one obstacle from `landingObstacle`: a tile
of run-up, the obstacle, then at least two plain tiles (`breathe`). Its menu: spikes, gap 1, cracked slab (not where it would dig
into the floor a switchback returns along), slicer (4+), tunnel, saw (5+), the style trap, planks (palace). Never a gate or a guard.
Its draws come from `vrng`; which landings stay plain from `plrng`.

**Gate slots** (a remote plate's gate, `need`): `G2` the top of a kick shaft (a kit ending in a shaft, not a switchback), `G3` the foot
of a banner slide, `G4` three tiles of floor between two moves (`gslot`, `gateSlotSeg`). `slotOk` is the table; `G2` is drawn three
times as often when available.

## Forks

Floor 6 on (`LOOP_MIN`). 85% of floors want one fork, and from floor 14 half want a second (`lrng`); a longway floor wants at least
one and is laid out again without one. A candidate is a switchback whose two runs overlap by three rooms or more, not next to the chase
run or to another fork. The hole `H` lies at least 14 tiles into the upper run, with 26 after it; the short way's chamber may reach
`FZ` 24 tiles along from it, in the band between the runs (kept reserved until it is cut).

| Kind | Short way | Long way | Weights (floor 6-9 / 10-17 / 18+) |
|---|---|---|---|
| 1 | a chamber with a guard alone on a landing (`forkGuard`, tier from `frng`; in the budget) | the upper run with a puzzle pushed to `pend` | .35 / .30 / .25 |
| 2 | a damaging descent: hole is a `hurtdrop`, the kit starts with `drop2` | the safe way round, which must pass an obstacle or guard | .25 / .20 / .20 |
| 3 | dense: at least three moves and two landing obstacles (`frng`) | easy: plain floor x2.5, no puzzles past the hole | 0 / .25 / .35 |
| 4 | one-way damaging hole (`down`/`drop2` only); one in five a **grating** instead (`forkGrate`: bars over a shaft, no way down) with the violet gate (`LOOP_PAIR` 2, `PAIRN`) and a flask on the lower run, its plate (`loopPlate`) near the end of the upper run | the way round, which opens the gate | .40 / .25 / .20 |

Longway floors: kind 4 only below floor 10, kinds 3 and 4 half each from 10; gratings 0.7 of kind 4. If the drawn kind's chamber fits
no kit, `lp.order` tries the next (1: 1, 2, 4; 2: 2, 4; 3: 3, 1, 2, 4; 4: 4, 2). The short way's moves are `down`, `drop2`,
`banner3/4`, `collapse`, `jumpdown` (no lifts, no sand lift: `forkBuild`), its last a drop of two or more. Its bot actions are taken out
of `L.path` into `L.forks[i].sc`; `L.path` jumps the hole (`sjump`, `fork:1`) and takes the long way, which is the floor's length. No
checkpoint between a grating's plate and its gate (`cpHold`). A damaging way must be worth a life (`forkWorth`, below).

## The oatmeal spice and the flags

`featFor(n, seed)` walks floors 1 to n on its own stream (`hash2(base, 5557)`; `base` is the run's `S.seed` in play, so neighbouring
floors differ; a test seed otherwise), five draws a floor, so a floor never repeats the previous floor's family in any category.

| Category | Families (first floor) | How the featured family is weighed up |
|---|---|---|
| move (floor 3 on) | `plain` (3), `collapse` (3), `jumps` (4), `banners` (4: banners, shafts), `lifts` (3) | `randKits` to `SH` 55% of the draw; its kits tried first; in-run step variants by `cT`/`jT`/`jU` |
| puzzle (floor 4 on) | `slab` (4: P2, P3), `side` (4: P1), `alcove` (4: P5), `timed` (6: P4), `double` (7) | `puzzlePick` to 55% of the menu; `remoteRoll` lays a remote plate on a run with 0.34 (timed) or 0.12 (alcove, side) instead of 0.03, only of that family |
| obstacle (floor 4 on) | `spikes` (3), `loose` (3), `chomp` (4), `saw` (5), `tunnel` (3) | `OB()` x5 (saw x10) in the run, corridor-fill and landing menus; in a run's menu plain floor gains `FEAT_FLAT` 1.6 times that extra weight, so the trap share does not rise |

Rare flags (`FEAT_FLAGS`, `FLAG_P` 0.12, floor 4 on, never two in a row: about one floor in nine; `FLAG_TEXT` is the card's line):

| Flag | Effect in the generator |
|---|---|
| `tower` | move family `lifts`, `SH` 0.92 |
| `rotten` | move `collapse`, obstacle `loose`; `SH` 0.75; an in-run down step is a collapse 65% of the time, a jump down 7% |
| `barracks` | budget doubled (cap 10); spikes, cracked slabs, slicers and gates x0.75; plain floor x1.3; 45% of other traps call a garrison guard after them (budget allowing); a guard may call a reinforcement (floor 6 on) |
| `longway` (floor 6 on) | forks as above; always at least one |
| `maze` | puzzle weight x3.5; each puzzle laid queues one or two more (`pend`, up to 3), laid back to back |

Tests force them: `window.__FEAT = {flag, move, puzzle, obstacle}` (applied to floor n only); `window.__PZ` forces one puzzle (a `MENU`
name) or remote plate (`P4`, `P5`, `P1`).

## Puzzles

A plate opens a gate. The plate's shape (P) and the gate's place (G) are chosen apart: names like `P2G1`, `P4G2`, kept in
`L.puzzles` and on the gate (`g.puz`). Draws from `zrng`; a puzzle that does not fit is queued (`pend`) for the next clear stretch
(8 tiles into the run, 30 left).

| Name | Shape | Gate | Floor | Weight |
|---|---|---|---|---|
| `P1G1` | branch plate: a gallery above or cellar below, a mini level walked out and back (`detourGate`, `planBranch`, `carveBranch`) | further on the corridor; timed in 35% from floor 6 | 4 | .056 |
| `P5G1` | plate in a one-storey alcove, one obstacle (`alcovePlate`) | further on | 4 | .03 |
| `P2G1` | slab: a cracked slab in the gallery falls onto the plate and holds it; the gate is too fast to outrun (`dur` 0.2) | further on | 4 | .03 |
| `P3G1` | slab jams four closers in front of a latched gate | after the closers | 5 | .022 |
| `double` | two branch plates (gallery and cellar), the second gate timed (`pair` 0, 1: amber, teal) | two gates in a row | 7 | .05 |
| `P4` (remote) | a corridor plate 8-13 tiles before the run's end: press and run (`race`) | in the next turn (G2, G3, G4) | 6 | .4 of remote |
| `P5`, `P1` (remote) | alcove or branch 24-30 / 44-52 tiles before the end | in the next turn | 4, 5 | .3, .3 |

A remote plate is never on the last run, the chase run or a fork's runs. If the next turn has no slot for its gate, a P4 plate turns
back to plain floor; a P1 or P5 branch would be a dead-end room, so the floor is laid out again (`orphanscan.py`). In-line gates
(`gate()`, floor 3 on) put 2 to 5 tiles between the plate and the gate, with a pit to jump (floor 6 on) or a closing plate (floor 4 on).
Other shapes: the movable block that holds a plate (`blockSeg`), the gold flask's ambush and crumbling chain (secrets, below).

## Traps and their density

The owner's rule: traps per floor stay about 15% over v39's, by plain floor, never by shortening anything (unit G1). The knobs:

| Constant | Value | Meaning |
|---|---|---|
| `FLAT_K` | 3 | plain floor's weight in a run's menu (v39: 1) |
| `CH_PLAIN` | 0.6 | chance a chamber's landings are all plain |
| `LAND_PLAIN` | 0.7 | chance one landing is plain |
| `FILL_PLAIN` | 0.85 | chance a step of side-passage corridor fill is plain (`fillCorridor`) |
| `PADK`, `padK(n)` | 1.46 (1.52 to floor 5) | the floor is built this much wider to hold the old trap count with the padding |
| `FEAT_FLAT` | 1.6 | plain floor's share of the featured obstacle's extra weight |

`breathe()` follows every trap (in runs, corridor fills and landings): two tiles of plain floor (three 40% of the time), and every
3 to 5 traps a longer rest of 3 to 5 more (`prng`). It restores the run-up counter, so padding never counts as run-up. A corridor
fill (`fillCorridor`, beside a side passage) lays only what cannot dig into the cellar under it or block the gallery's drop: spikes,
slicer, tunnel, gate, saw, roof blocks, pendulum, vents. Guards and snakes are fighters, not traps: `metrics40.py` and
`featurescan.py` count them apart.

## Guards and snakes

Budgets from `gbrng` (`hash2(seed, 8317)`), so the layout streams are left alone:

| Floors | Guards (`guardBudget`) | Snakes (`snakeBudget`) |
|---|---|---|
| 1 / 2 / 3-5 | 1 / 0 / 2 | 0 / 0 / 0 (floor 5: 1) |
| 6-11 | 3-4 | 1-2 |
| 12-19 | 4-5 | 2-3 |
| 20 on | 5-6 | 3-4 |
| barracks (4 on) | double, cap 10 | same |

The budget counts guards, reinforcements, the ambush at a flask and the captain (`gSpent`, with places kept for those still to come,
`reserved`). Spots: the exit guard (captain on every fifth floor from 5, `cap`, tier 2, `ghp+2`; with a reinforcement from floor 6);
a guard just past a solved gate or puzzle (`gateDue`; at least `guardGap = max(30, routeT*0.7/GB)` tiles after the last, past 12% of
the route; on crypt floors half are skeletons); a fork's kind-1 short way; the ambush in a secret passage (from floor 5, half of floors
by `hash2(seed, 6611)`); garrison guards on barracks. Never on a turn chamber's landing (the fork's kind-1 guard is the one guard on a landing), in a corridor
fill or in a gated side passage. Snakes only in
tunnels (`tunnel`, branch tunnels), from floor 5, past 12% of the route, `snakeGap` apart. Tiers from `trng`. Check: `guardscan.py`.
Details: [guards and snakes](elements/guards-and-snakes.md).

## Secrets and the gold flask

Every third floor (`n % 3 == 0`) holds a secret passage (`secretPassage`): a side passage with no gate, tried from a point at 25-55% of the
route (`secretAt`) up to 90%, the gold flask (`type 'life'`, `hidden`, +1 maximum life) at its far end; `L.secret` marks where its climb or drop starts.
It may hold a crumbling chain of five sturdy cracked slabs and the ambush, both armed by the flask's tile (`trigger`). With no room for
it, the first alcove's flask becomes the gold flask. Other flasks: the large red flask at the end of one gated passage a floor at most
(13%, a hash), a grating's flask (always kept), heal flasks in side passages (40%). Details:
[flasks and secrets](elements/flasks-and-secrets.md).

## The damaging drop

A drop that costs health must be worth it (owner). Two places:

| Where | Built by | Kept only if |
|---|---|---|
| a chamber, floor 5 on (not a switchback, not a gate turn; rolled 50% on `vrng`) | `hgap` inserted after a landing from which exactly two rows and two or more moves remain: `hurtGapSeg` (a one-tile `hurtdrop` hole, plain floor two storeys under it), `hurtCorridor` (that floor runs on to the chamber's foot) | the safe way past it holds an obstacle (`sk2`), and it saves at least 25% of the chamber's `estPath` time and at least 10 tiles' worth (`(tL - tS)/0.34 >= 10`) |
| a fork, kinds 2 and 4 | `forkChamber` | `forkWorth`: the long way at least 10 tiles longer and 25% slower (tiles x0.34 + 4 s against `estPath` of the short way); and `forkFoot`: the long way passes an obstacle or guard |

Otherwise nothing is placed. The record is `L.hurtdrops` (chambers) or the fork's `hp`. `L.path` and the bot always take the safe way
and the floor's length is counted along it; `hdtest.py` and `forktest.py` take the damaging one (exactly one life). Its look is the
tile's own: [hurtdrop](elements/hurtdrop.md).

## The open-hall pass and look-only passes

After all runs, every open cell with stone above gets one row of headroom: that cell opens to `EMPTY`, except over a gate, a slicer
(`chomp`) or a tunnel (`low`), within 2 of the exit door, at the start door, a kick shaft's far wall (`keepWall`), a counterweight
lift's top mouth and shaft top (25d), and the walls beside a sand lift's column (26e). Each candidate cell draws `ch(0.16)` for a
window whether or not it is kept, so a kept lintel moves nothing else.

Look-only passes read the tiles and hashes, never a generator stream, so layouts do not move:

| Pass | What | Element |
|---|---|---|
| `settleLevel` -> `settleLights` -> `lampsClear` | a lamp only where both cells beside it are plain floor (no wall, step, ledge, gate, banner, bar, pendulum, lift, lift plate, shaft foot, sand column, chain), not in or beside a lift shaft, not by a checkpoint or door; moved up to 6 columns (3 from another lamp) or put out; lamps on damaged wall fall and are replaced | [lamps and light](elements/lamps-and-light.md) |
| `planHangings` | hangings, torn or down by the wear | [stonework](elements/stonework.md) |
| `wearAt`/`wearLevel`, `breaches` | wear field and breaches from hashes of the cell and `L.seed` (none in or by a lift shaft, `liftNear`) | [stonework](elements/stonework.md) |
| `looseWell`, `wellGroup` | a cracked slab's look: sand well or corridor | [cracked slabs and sand wells](elements/cracked-slabs-and-sand-wells.md) |
| `secretCues` | the gold flask's stars | [flasks and secrets](elements/flasks-and-secrets.md) |

Not look-only but stream-free (tiles and hashes): round 43's heaps and drifts (`placeHills`, last in `genLevel`: `L.hills`, nothing else changes), the sand lift's choice (`sandOr`, 37%) and its fallback to a banner, saws to spikes,
in-line timed gates, in-run step variants, side gates left open, the big flask, the ambush.

## estPath, timers and L.path

Every piece pushes bot actions onto `L.path` (`bot`): `walk`, `sjump`, `rjump`, `rjumpg`, `dashjump`, `tiptoe`, `runover`, `crawl`,
`timed`, `climb`, `drop`, `hangdrop`, `slide`, `walljump`, `wallrun`, `collapse`, `jgrab`, `swing`, `saw`, `darts`, `push`, `pull`,
`lift`, `sandlift`, `dash`, `drink`, `door`. `bot.js` plays them through the game's input. A new trap needs its action here and in
`bot.js`.

`estPath(acts, cur, careful)` adds a time per action from its table and per tile walked: 0.34 s a tile (0.2 s a walk), or with
`careful` 0.55 s (0.4 s). It sizes timers, the worth-a-life tests and the fork records (`tLong`, `tShort`).

| Gate | Timer |
|---|---|
| in-line (`gate()`, timed by a hash: 25% to 45% by depth) | `(m*TW + 16 + BW)/RUN` plus 0.2 (closer), -0.1 (pit) or 0.05, times a slack 1.15 (early) to 1.03 (`rng`) |
| side passage (`detourGate`), double's second | `estPath` (plain pace) of the way back x `timerK()` + 0.3 s; about 62% of side gates later made to stay open |
| P4 race | `estPath(..., true)` (careful pace) from the plate to past the gate x `timerK()` + 0.3 s (`g.est`) |
| slab (P2), block | 0.2 s: too fast to outrun |

`timerK() = 0.84 + 0.14 rng() + 0.1 (1 - d)`, `d = min(1, (n-1)/24)`: 0.94-1.08 on floor 1, 0.84-0.98 from floor 25. Round 32 made
`sjump` 0.18 s longer (the wind-up), round 35a `rjump`, `rjumpg`, `jgrab` and `swing` shorter (the faster running jump); layouts
unchanged, a few timers moved.

Other outputs: `L.segs` (every piece: `k`, columns, rows; `corr` 1 corridor fill, 2 landing; kinds `turn-*`, `fork-*`, `guard`,
`skel`, `secret`, `chase`, `detour`, `double`, `puzzle`, `rem-plate`), `L.detours`, `L.puzzles`, `L.forks`, `L.hurtdrops`, `L.runsInfo`,
`L.runMv` (in-run step variants), `L.lifts`, `L.guards`, `L.snakeSpecs`, `L.items`, `L.torches`, `L.windows`, `L.cps`, `L.start`,
`L.door`, `L.ext.chase`, `L.chaseInfo`, `L.ext.blocks`, `L.base0`, `L.dyn`.

## Random streams

| Stream | Seed | Draws |
|---|---|---|
| route `R` | `hash2(seed + att*7919, 7717)` | run lengths, first heading, turns (`routeWalk`), one per attempt |
| spice `R` | `hash2(base, 5557)` | flag roll and pick, move, puzzle, obstacle: five a floor for floors 1..n |
| `rng` (`rng0`) | `mulberry32(seed)` | run menus and their pieces, in-line gates' slack, `planBranch` shapes, `timerK`, side gates' timing roll, flasks, torches, windows (`ch(0.16)`), `secretAt`, the chase; its 4th draw is the chase roll (`peek` reads it before the floor's width is known) |
| `prng` | `hash2(seed, 4421)` | `breathe` rests, branch spacing |
| `gbrng` | `hash2(seed, 8317)` | guard and snake budgets, crypt skeletons, barracks reinforcements and garrison |
| `trng` | `hash2(seed, 9137)` | guard tiers |
| `crng` | `hash2(seed, 7703)` | everything in a corridor fill |
| `plrng` | `hash2(seed, 9301)` | which chambers and landings stay plain |
| `krng` | `hash2(seed, 7919)` | turn kits (`randKits`, the shuffle of `KITS`) |
| `zrng` (`zr`, `zi`) | `hash2(seed, 8209)` | puzzles: `puzzlePick`, `remoteRoll`, `remAt`, slab and alcove geometry, gallery or cellar, the gate slot and its place |
| `vrng` | `hash2(seed, 6007)` | chamber landings (`landingObstacle`), `jumpdown`/`jumpup` widths, the hurtdrop roll |
| `lrng` | `hash2(seed, 6151)` | how many forks and on which switchbacks |
| `frng` | `hash2(seed, 6451)` | fork kind, grating, short-way kits, its guard's tier, kind 3's landings |
| `lfrng` | `hash2(seed, 6389)` | paternoster slabs' phase |
| hashes | `hash2(seed + c*k1, r*k2 + n)` | stream-free choices (above) |

`rngX` redirects `rng` and `prng` while a corridor fill (`crng`) or a landing (`vrng`, `frng`) is built, so the obstacle's own draws
(a slicer's phase, a spike's width) come from that stream and the main one is left alone.

The rule: **a change that is look only uses hashes of the place, never a stream**, and a change to play draws what it drew before.
Each stream is a sequence: one draw added, removed or moved shifts every later choice on it. On the main stream that is the rest of the
floor's layout; on the spice's walk, every later floor's families. Example (round 25d): the open-hall pass now keeps the lintel over a
counterweight lift's top mouth, but still draws `ch(0.16)` for a window there; skipping the draw would have moved every later window
and everything after them on `rng`.

## Where elements may be placed

| Element | Placed | Never |
|---|---|---|
| [spikes](elements/spikes.md) | runs (2+), corridor fills, landings, branches, chase; fixed spikes under a cellar's holes; a saw under a ceiling at his height | - |
| [saws](elements/saws.md) | runs, fills, landings (5+) | under a ceiling at his height (spikes instead) |
| [slicer jaws](elements/slicer-jaws.md) (`chomp`) | runs, fills, landings (4+; twin from 10), branches (6+) | - (keeps its lintel in the open hall) |
| [pendulum](elements/pendulum.md) | tile style: runs, fills and galleries where tall enough, landings | other styles |
| [fire vent](elements/fire-vent.md) | forge style: runs, fills, landings, branches | other styles |
| [darts](elements/darts.md) | runs (6+): a step up from the band's floor, its riser shooting | turns, fills, landings |
| [roof blocks](elements/roof-blocks.md) (`stone`) | dungeon style: runs (2+), tall fills, landings, galleries, chase | other styles |
| [heaps and drifts](elements/heaps-and-drifts.md) (`L.hills`) | after the build (`placeHills`, hashes): the run menu's plain floor (`flat` segs); heaps from floor 3, drifts from 5 in the sandy themes; at least one a floor, one per 4 stretches that can take one | `breathe()`'s padding, timed stretches, the chase, fighters' ground, a lamp's cell, by a clock, flask, door, lift, block or side passage |
| [wind](elements/wind.md) (`L.winds`) | after the hills (`placeWinds`, hashes): the run menu's plain floor, 3 cells (else 1) clear of every seg that is not plain floor; steady from floor 3, gusts at a window from 13, every clear drift's; at least one a floor, one per 4 stretches | timed stretches, the chase, fighters' ground, doors, lifts, blocks, side passages, any jump's take-off or landing |
| [movable blocks](elements/movable-blocks.md) | runs (7+), holding a plate (`blockSeg`) | elsewhere |
| [hurtdrop](elements/hurtdrop.md) | chambers going down (5+), forks kinds 2 and 4 (6+) | unless worth a life; switchbacks; gate turns |
| [gates](elements/gates.md) | in-line (3+), puzzles, fills, turn slots; the violet gate under a grating | - (the open hall keeps its lintel) |
| [plates](elements/plates.md) | with their gates; `lplate` at lifts; `xplate` after 82% of the route; closers | - |
| [cracked slabs and sand wells](elements/cracked-slabs-and-sand-wells.md) | runs (3+), landings, branches, slab puzzles, collapse ledges; planks (palace) | fills (nothing that digs); a landing over the floor a switchback returns along |
| [lifts](elements/lifts.md) | chambers only: counterweight (3+), sand lift (4+, 37% of banner moves; round 41: a trap over a spike pit, so only over a storey of rock: 261 of 322 on floors 1-48 x 3 seeds), paternoster (8+) | runs, fork short ways, a switchback's last move; paternoster in a gate turn; sand lift in a G3 turn, without a shaft or without rock under its foot |
| [banners and slides](elements/banners-and-slides.md) | chambers going down (4+), fork short ways | runs |
| [kick shafts and jet streams](elements/kick-shafts-and-jet-streams.md) | chambers going up: kick shafts (5+); the wall run (3+) is a move of its own ([gameplay](gameplay.md)) | runs |
| [swing bar](elements/swing-bar.md) | runs (6+), over a four-tile pit | turns |
| [guards and snakes](elements/guards-and-snakes.md) | see Guards and snakes | turn landings, fills, gated side passages |
| [checkpoint](elements/checkpoint.md) | every `CP_GAP` tiles on plain floor; before the chase | between a grating's plate and its gate; on an item |
| [flasks and secrets](elements/flasks-and-secrets.md) | see Secrets | - |
| [the dark](elements/the-dark.md) | floor 6 on, planned on 65% of floors, on a run heading right (`chaseRun`), 26-34 tiles (+8 by depth) | - |
| [lamps and light](elements/lamps-and-light.md) | runs, corridors, branches, by the door; then `lampsClear` | see the look-only passes |
| [openings and backdrop](elements/openings-and-backdrop.md) | windows: 16% of headroom cells (`L.windows`); arches and breaches are look only | arches and breaches in or by a lift shaft |
| [doors](elements/doors.md) | start at the first run's entrance, exit at the end of the last | - |
| [stonework](elements/stonework.md) | walls, floors, steps, tunnels (`low`) | - |

## Invariants and their checks

| Invariant (owner) | Held by | Checked by |
|---|---|---|
| Floors are never shorter | `LAST_EXTRA`, `trapTarget`, rooms in hand, `return null` when boxed in; length along the long way | `metrics40.py` (against v39, the G1 reference; the release tag is its argument), `flagroute.py`; the older `metrics39.py` |
| The plain floor after each trap | `breathe()` | `metrics40.py` ("padding kept") |
| Trap density about +15% over v39 | `FLAT_K`, `CH_PLAIN`, `LAND_PLAIN`, `FILL_PLAIN`, `FEAT_FLAT` | `metrics40.py`, `featurescan.py` |
| A damaging drop is worth it and looks like one | the worth tests; the `hurtdrop` tile | `hdtest.py`, `forktest.py`, `forkscan.py` (savings) |
| Featured families hold their share; flags about 1 in 9; floors differ | `featFor`, `SH`, `OB`, 55% | `featurescan.py`, `featbot.py` (forced floors, 0 damage) |
| No dead-end side rooms | P1/P5 remote plates re-lay the floor | `orphanscan.py` (1-27, 20 seeds) |
| Maze floors 1.5x the gate puzzles; longway always a fork | `maze` weights, `pend`; longway retry | `mazescan.py` |
| Guards on budget, at meaningful spots | `guardBudget`, `gateDue` | `guardscan.py` |
| Every fork plays; every chamber move plays | `forkChamber`, `PRIM` | `forktest.py`, `primtest.py`, `vertscan.py`, `puzzlescan.py` |
| Timers beatable | `estPath`, `timerK` | `p4bot.py`, `run2.py` |
| No sand well in a corridor | `looseWell` (look only) | `wellcorr.py` |
| A sand lift stands in a shaft, over a walled spike pit | 26e/26g, 41 fallback | `sandshaft.py` |
| A slab slides into stone | open-hall lintel | `slabscan.py` |
| Lamps keep clear | `lampsClear` | `lampscan.py` |
| Layouts identical after a look-only round | hashes, no stream | `genLevel` floors 1-48 x 3 seeds against the last release (tiles, features, `L.path`, start, exit); `samelayout.py` hashes floors 1-40 x 5 seeds |

## Rules for changing it

- Levels stay fully generated. Feel or layout changes come with research first (Prince of Persia and other games), and the report
  names its sources.
- Look only: hashes of the cell (`hash2(seed + c*k, r*k + n)`), never a stream; keep every draw the play code made. Then compare
  layouts over floors 1-48 x 3 seeds.
- A play change must not shorten a floor or remove `breathe()`'s floor: run `metrics40.py`.
- A new move: one line in `MV`, one in `PRIM`, one in `LAND`; a bot action in `L.path` and `bot.js`; `estPath`'s table if it takes
  time; `vertscan.py`, `primtest.py`.
- A new trap: its piece checks every cell with `W` first, pushes its bot action and a seg, and calls `breathe()` after; add it to the
  menus where it may stand (run, `fillCorridor`, `landingObstacle`); if it can be featured, to `OBS_FAM` and `featurescan.py`'s `OBS`.
- A new puzzle: a `MENU` or `REM` line, a `puzzleTry` case, its family in `PUZ_OF`; `puzzlescan.py`, `orphanscan.py`.
- Timers: through `estPath` and `timerK`; measure the bot (`p4bot.py`) before changing a time.
- Guards and snakes come out of their budget only; never as traps.
- Never read the theme in the generator (`L.gstyle` only).

## History

- v39: the reference for trap density and floor length (`metrics40.py`).
- units GB, G1, F: fighters' budgets, trap density and remote plates (P4), the oatmeal spice and flags.
- round 16a: sand lifts as 37% of banner moves (`sandOr`, a hash).
- round 19: `lampsClear`.
- round 25d: lintels over lift top mouths, the window draw kept.
- round 26e, 26g: sand lifts only in shafts, else the banner slide.
- round 30: no sand well in a corridor (look only).
- rounds 32, 35a: `estPath` times for jumps; layouts unchanged.
- round 41 (41b): the sand lift a trap over a spike pit a storey under its foot. The pit is laid only in rock the floor as built left:
  reserving the cells while building (tried for a three-storey bottomless shaft, then for the pit) let later runs and pits go elsewhere and
  floors came out shorter (`metrics40.py` against v85: the pit's reservation floor 15's shortest route 943 for 971, for 4 more traps; the
  shaft's down to 1065 from 1179). Tiles otherwise as v85 (`metrics40.py` v85: no flags); `estPath`'s `sandlift` by its storeys.

Details in CLAUDE.md.
