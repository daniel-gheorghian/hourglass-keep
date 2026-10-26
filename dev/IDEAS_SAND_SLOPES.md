# Three ideas: difficulty notes (2026-10-26, against v84)

Owner's ideas, as asked:

1. The sand lifts become a trap: the sand drains, the door opens, but he has to jump, because the slab keeps going. The shaft is
   bottomless; the sand drains off the screen and the slab falls off the screen.
2. Every ledge sitting on sand (the cracked slabs over a well): the bottom slanted, the sand draining toward the slanted corner.
3. Some longer corridors slanted, as a slope. He can't run there: holding the arrow walks, pulsing it runs, at a slower pace.

Idea 1 is built (round 41); 2 and 3 are not. These notes say what each costs and what must be decided first.

| Idea | Difficulty | What it touches | Layouts change? |
|---|---|---|---|
| 1. Bottomless sand lift (built, round 41; a spike pit, 41b) | Medium (about round 26e's size) | generator, play, bot, hint, look | only the foot and a spike pit under it, cut into unused rock |
| 2. Slanted well floor | Easy to medium if look only; hard if he lands on it | `wellSolve`, `drawWellGroup`, `wellscan.py` | no |
| 3. Sloped corridors | Very hard (several rounds, more than the WebGL move) | almost everything | yes |

Suggested order: 1 first; settle 2's question before any work; for 3, the drift corridor below, or treat real slopes as their own
multi-round project.

## 1. Bottomless sand lift: medium (BUILT, round 41, as a spike pit in 41b)

Built in round 41 (see CLAUDE.md, "The sand lift's spike pit", and `dev/docs/elements/lifts.md`). The owner's answers: missing the window
is death; every sand lift; off by a step or a jump. Round 41 built it bottomless (three storeys of shaft under the foot, a fade to black);
round 41b (owner: "let's simplify: put spikes at the bottom instead of being bottomless") puts a spike pit a storey under the foot instead:
261 of 322 sand lifts qualify on floors 1-48 x 3 seeds (the rest, with no rock under the foot or no way off the slab, are the banner slide;
reserving the rows while building made floors shorter). The window: 0.59 s (82 px) from the foot's mouth 45% open to the slab 60 px under
the floor, a held arrow or a buffered Jump; only the mouth on his way opens; the `sandfall` hint warns. The notes below are the plan as it was.

Example: a 4-storey sand lift. The slab passes the foot storey's floor in 0.46 s (a storey 64 px at `SAND_LV` 140 px/s); the exit's
mouth slab rises over the last `SAND_MD` 28 px (0.2 s). A fair window runs from the mouth starting to open until the slab is about
a storey below the floor, where a jump with Grab can still catch the lip.

- What exists: the shaft (`sandLiftSeg`), the mouth slabs (`f.ms`, `sandOpen`, `sandMouth`), the steady sinking (`updateLift`'s
  `f.sand` branch, which stops at `f.yB`). The paternoster's step-off window (`chainWin`, in the `lift` state's chain case) is a
  pattern to copy.
- What is new:
  - control on the ride: today the `lift` state sets `P.vx=0` and reads no input for a counterweight or sand lift, so a jump (or a
    step) off a sinking slab is new play code;
  - the slab never stopping, and his death if he stays on;
  - the sand and the slab falling out of sight;
  - the bot's `sandlift` action timing the jump;
  - a new `sandlift` hint text (the current one says the slab lowers him down the shaft).
- Main problem, room below the foot: to kill him the shaft must go on at least 3 storeys (192 px; a fall of 170 px kills).
  `sandLiftSeg` only checks rows down to the foot (`r+k<=rows-2`, `W()` on the shaft and foot cells). Two ways:
  - unused rock only: a pass after the floor is built deepens only the lifts with solid rock under the foot. Nothing else moves, but
    only some lifts qualify (count them first, floors 1-48 x 3 seeds);
  - reserve the rows: every lift can become a trap, but layouts change and `metrics40.py` must be rechecked.
- Fairness: a first-time player dies on the first ride. The opening mouth and the hint have to warn them.
- Checks to update or add: `lifttest.py` (sand3, sand4), `sandshaft.py`, `liftscan.py` (the foot's pit and flush checks assume the
  slab rests there, round 37a), `hinttest.py`, `run2.py`, `layoutcmp.py` (differs on purpose if rows are reserved), `metrics40.py`.

Questions for the owner:
- Missing the window: death, or one life?
- Every sand lift, or only some (for example from a certain floor on)?
- Jump only, or can he also step off as on the paternoster?

## 2. Slanted well floor: depends on what "bottom" means

The well's bottom is the floor of the storey below: `wellGroup` sets `g.yb[j]` to `SURF(r+k)+HY`, where `k` is the storeys from
`looseWell`. When a slab breaks he falls onto that floor and walks out.

Example: a 3-slab well whose floor slopes 20 px across its 96 px. He lands near the middle slab, so his feet float or sink by up to
10 px. For him to stand on a slope, it needs idea 3's slope code.

- Look-only version (easy to medium):
  - a sloped stone fill against the back wall, behind the line he walks on at mid-depth, with the outlet in its low corner;
  - the sand's surface tilting toward that corner (mass flow: the bed slides toward the outlet, instead of round 21b's funnel-flow
    craters and the residual heaps by the walls).
  - `wellSolve`'s volume solve, `wellAt`'s surface, the outlets in `drawWellGroup` and `wellscan.py`'s slope and volume rules change.
- Conflict with play, in that version too: each slab breaks 0.5 s after he steps on it, because each slab opens its own outlet
  when triggered (round 16a, 21b). With one outlet in a corner the sand drains from that corner first.
  - Example: 4 slabs, the outlet under slab 1. He comes from the right and steps on slab 4. In play it breaks at 0.5 s, but its sand
    would go last; slab 1, untouched, would lose its sand first and should fall.
  - To match, either the drawing shows something play doesn't do, or play changes: one step brings down the whole row, starting at
    the corner. That is a new trap, with bot and timer work.

Questions for the owner:
- The pit's floor (where he lands), or the shape of the sand as it drains?
- Should one step bring down the whole row?

## 3. Sloped corridors: very hard

The game has three tile types (`EMPTY`, `FLOOR`, `WALL`, plus features), and a floor's height is `SURF(r)` for every tile on row r
(142 uses in the source, besides `solidBelow`, `clampMove`, `land`, `jumpSpan`, `findLedge` and the rest).

Example: a slope up one storey over 6 columns is 64 px over 192 px, about 18 degrees. The ceiling has to rise with it, so the
corridor over it is two storeys tall, which nothing else in the game is. Rows can't stay flat.

- What it touches:
  - play: standing, falling off an edge, landing on a slope, jump arcs ending on it, ledge grabs, guards and fights, every trap's
    placement;
  - drawing: the room picture (stages 0-2), every Torchlight tile map (lamp shadow carve, beams and their footprints, `floorFx`,
    relief), round 39's front-plane cuts (`nearCut`, `onFace`: rectangles and fixed slab shapes);
  - level building: `routePlan`/`routeWalk` lay every run out level, turns between runs are the vertical moves;
  - bot and timing: `bot.js`, `estPath`, the gate timers.
- The controls work against the idea:
  - in `stRun` a held direction already accelerates him from 35 to `RUN` 100 px/s, and a tap gives a short burst and a stop. Making
    tapping the faster way means the harder input gives the faster pace, and quick repeated taps are imprecise on a phone pad;
  - there is no walk in play today (only the Crossing has one, `CROSS_WALK`);
  - downhill should probably differ from uphill (faster, or sliding).
- Purpose: if a slope only slows him down, it adds walking time to the floor. It needs a job, such as making the dark's chase or a
  timed gate harder.

Cheaper alternative with the same play idea (medium): a flat corridor of deep drift sand where he can't run and wades. No new
ground shape, and it fits the sand already in the game. Still new: the wading move and its pose, its hint, the bot and `estPath`
pace, gate timers over it, the generator placing it (and keeping it off timed stretches and the chase unless that is its purpose).

Questions for the owner:
- Real slopes, or the drift corridor?
- What should the slow stretch do in play?
- Uphill and downhill the same?
