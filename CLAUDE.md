# Hourglass Keep

A single-file HTML5 canvas platformer in the manner of Prince of Persia (1989), played as an
offline PWA on an iPhone in landscape. GitHub Pages serves `main` at
https://daniel-gheorghian.github.io/hourglass-keep/

## Layout

| Path | What |
|---|---|
| `dev/hourglass-keep.html` | The source of truth. Edit this, never `index.html`. |
| `index.html`, `sw.js` | Build output that Pages serves (made by `dev/tools/build.py`). |
| `manifest.webmanifest`, `icons/` | PWA files. |
| `dev/tools/bot.js` | The test bot: plays a floor through the game's own input (`runBot(n, seed, opts)`). |
| `dev/tools/*.py` | Build, regression and measurement scripts. Many are one-off debug scripts kept for reference. |
| `dev/tools/hk_vNN_release.html` | Source of each past release, the baseline for comparisons. |
| `dev/localize.py` | Run once per new machine (see below). |

## Setup on a new machine

```
python3 dev/localize.py        # the tools carry the cloud session's absolute paths; this points them here
pip install playwright         # add --break-system-packages on Debian-style Pythons
playwright install chromium
```

The scripts drive the page in headless Chromium through Playwright. Run them from `dev/tools`:
they load `bot.js` by a relative path and write their output next to themselves.

## Build

From the repo root, with N the release number (current release v61, next v62):

```
python3 dev/tools/build.py dev/hourglass-keep.html index.html sw.js N
```

It stamps `APP_VERSION`, wraps the page with the PWA head and service-worker boot, and sets the
service worker's cache to `hourglass-keep-vN`, which is what makes installed copies update.

## Release routine

1. Change the source, then build with the next N.
2. Run the regression suite from `dev/tools` with `python3 suite.py release`. It runs every test below spread over the
   machine's cores and prints one line per test, ending in `ALL OK` or `FAILURES`, then the five slowest jobs. The bot and render
   runs are split one floor (and seed) per job; each of the N workers (`suiteworker.py`) starts ONE Chromium and runs its jobs
   in turn, each in a fresh browser context, so nothing leaks between jobs. The test scripts are unchanged and still run
   standalone. A job over its 25-minute limit, or one that kills its browser, fails with a message and the worker is replaced.
   `run2`, `featbot`, `p4bot`, `forktest` and `rendersmoke` also fail a run whose page CPU time per game frame is over budget
   (`slowguard.py`, 0.3 ms/frame; healthy runs are 0.02 to 0.1), naming the floor and seed: a leak like v41's particles shows
   up as a failure, not as a long wait. `HK_MS_PER_FRAME` and `HK_RUN_WALL` override the budgets.
   Tiers: `suite.py quick` (bot with one seed plus the unit tests, ~4 min) while working; `suite.py` (bot with four seeds,
   forks, flag and family floors, metrics, unit tests, ~6 min) before each commit; `suite.py release` (adds the fight runs
   and the render check, ~15 to 20 min) before a release (times on an 8-core laptop, longer if it is busy). Run long suites in
   the background rather than polling them. The default process count is the number of physical cores; more only slows a
   laptop down. A new test should take a floor
   range so `suite.py` can split it, and be added to its list. The tests it runs:

| Command | Checks | Pass |
|---|---|---|
| `python3 run2.py 1 27 4` | the bot finishes floors 1 to 27, 4 seeds each, without fighting | all passed, 0 runs with damage |
| `python3 run2.py 1 27 2 fight` | the same, fighting every guard | all passed |
| `python3 rendersmoke.py 1 27 both` | every floor renders without errors, played once with the sampled frames alternating between Classic and Torchlight (shader live, WebGL frame not blank); `torch` or no argument: one mode only | no errors |
| `python3 forkscan.py`, `forktest.py` | forks are built (kinds per floor band); every fork's shortcut branch is played to the door: kind 1 fighting its guard, kinds 2 and 4 stepping off the broken lip (exactly one life lost), kind 3 through its traps; a grating is solid, its gate open and its flask in place | all ok |
| `python3 metrics40.py` | route length, trap count and trap spacing against the last release (edit the two files at its top) | no floor shorter, padding kept |
| `rewindrooms.py` | after a rewind over a hole knocked in the floor and new rubble, the room's picture equals one drawn from scratch (a rewind redraws only the rooms that changed) | all ok |
| `respawnplates.py`, `puzzlescan.py`, `slabresume.py` | plates stay pressed after a respawn; the puzzle menu's pairs are built; a slab-jammed plate is restored | all ok |
| `primtest.py`, `hdtest.py`, `vertscan.py`, `lifttest.py` | every chamber move works for the bot; the chamber's damaging drop (hgap) costs exactly one life where it is placed; counts of vertical moves; both kinds of lift ride | all ok |
| `p4bot.py lo hi [seeds]` | the bot plays floors forced to timed remote plates (P4, run for a gate in the next turn); the timers carry no extra factor | every run passes, 0 damage |
| `orphanscan.py`, `mazescan.py` | no gate side passage is left without its plate (floors 1 to 27, 20 seeds); maze floors hold at least 1.5 times the gate puzzles of ordinary floors of the band, longway floors always a fork | 0 orphans, ratio >= 1.5, forks >= 1 |
| `featurescan.py [file]`, `featbot.py` | a floor's featured families hold their share of their category (mean and minimum), flags come about one floor in nine, floors differ more than before (sameness); the bot plays floors forced to every flag and family (`window.__FEAT`) | shares near or over 40%, 0 damage |

Speed: `?bench` in the game's URL (on the phone too) makes the bot (`bot.js`, fetched for the run; `botGen` steps it from the
game's own frame loop) play six fixed floors live, 20 s each, and shows a table of frame times with a Copy button; the save is
left untouched. `?bench=75`, `?bench=auto` (the game's own scaling and fall back), `?bench=classic`. `bench.py [arg]` runs the
same on this Mac's GPU (Chrome's costs differ from Safari's: compare Mac runs with Mac runs). `?prof` times each stage in place.

Pictures: `forkshot.py out.png n seed [index]` draws a fork for a look; `chambershot.py` and `liftshot.py` do the same for chambers and lifts.

3. Commit as `vN: what changed`, push to `main`.
4. About two minutes later, check that https://daniel-gheorghian.github.io/hourglass-keep/sw.js shows `hourglass-keep-vN`.
5. Copy the source to `dev/tools/hk_vN_release.html` as the next baseline.
6. From a claude.ai session only: republish the artifact mirror https://claude.ai/artifact/Lwe65enpj3TkDEkiCWETTQ from the source.

## Rules the owner has set

- Levels stay fully generated: no hand-made levels or rooms.
- A drop that costs health must be worth it and must look like one (owner, 2026-10-14). It has its own look, made from the tile
  type (`hurtdrop`: a ragged, broken lip with nothing to grip, a darker shaft, a pile of rubble on the floor it lands on), never
  like a spiked pit or a plain gap. The generator keeps one only if it skips at least one landing with its obstacle or guard and
  saves 25% of the chamber's (or the fork's) route by `estPath()` and at least 10 tiles of walking; otherwise nothing is placed.
  Route length is counted along the safe way and the bot always takes the safe way; `forktest.py` and `hdtest.py` take the
  damaging one.
- A change must not make floors shorter or remove the plain floor left after each trap (`breathe()`).
  Check with `metrics39.py` whenever the generator changes.
- Changes to feel or level design are usually asked for with research first: how the Prince of Persia
  games (and other games) handled it. Report what a change was based on, with sources.

## Conventions in the code

- Tiles are 32 by 64 px (`TW`, `TH`); a room is 10 by 3 tiles. `GRAV=700`; the floor surface of row r is `SURF(r)=(r+1)*64-4`.
- Falls: under 100 px is safe, 100 px or more hurts, 170 px or more kills (two storeys = 128 px).
- The generator: `routePlan`/`routeWalk` lay out runs and the turns between them; `buildLevel` fills each run.
  Runs heading left are built as if heading right, in mirrored column space through `PC()`.
  `W(c,r)` means a wall cell inside the current run's window that no earlier run has reserved.
- From floor 3 a turn between runs is a chamber of two room columns (`routeWalk` reserves both). `buildTurn` draws a kit of
  moves from the weighted table `MV` (`randKits`; a new move such as a lift is one line there, one in `PRIM`, one in `LAND`),
  lays one obstacle and plain tiles on each landing (`landingObstacle`, own stream `vrng`), and falls back to the old `KITS`.
  New moves: `collapse` (loose ledge drops him a storey), `jumpdown`, `jumpup` (bot action `jgrab`: Grab held in the air), and
  `hgap`, the damaging shortcut (the bot jumps it; `hdtest.py` drops in). Checks: `vertscan.py`, `primtest.py`, `hdtest.py`.
- Forks (floor 6 on): a switchback gets one of four forks, drawn from its own stream (`frng`): 1 a guard on the short way, traps on
  the long one (PoP1 level 2); 2 a damaging descent beside the long safe way (PoP1 levels 5 and 7); 3 a short dense way against
  a long easy one (Unexplored); 4 a one-way damaging hole, one in five with a grating and a flask behind a violet gate for
  whoever goes the long way. The short way is a chamber of the turns' own moves cut under the upper run (`forkChamber`); its
  bot actions are taken out of `L.path` and kept in `L.forks[i].sc`. Floor length is counted along the long way.
- Oatmeal spice (`featFor(n,seed)`, own stream, floor 3 on; recorded as `L.feature`): each floor features one family of vertical
  moves (plain steps, collapse, jumps, banners and kick shafts, lifts), one of puzzles (slab, side passage, alcove, timed remote
  plate, double) and one landing obstacle; the featured family is weighed up until it holds about half of its menu (`randKits`,
  `puzzlePick`, `remoteRoll`, `OB()`), its kits are tried first, and the extra obstacle weight comes out of plain floor so trap
  counts do not rise. A floor never repeats the families of the floor before it (the walk runs on the game's seed). Rare flags
  (one floor in nine, from floor 4, never two in a row): tower (lifts everywhere), rotten (collapses and loose floors), barracks
  (many more guards, fewer other traps), longway (forks are all kind 3 or 4, mostly with a grating), maze (gate puzzles chained
  back to back). `window.__FEAT={flag,move,puzzle,obstacle}` forces them in tests; the card between floors names a flag.
- Fighters (unit GB): guards and snakes are not traps; each floor has a small budget (`guardBudget(n,x,barracks)`, `snakeBudget`, own
  stream `gbrng`, seed constant 8317). Guards per floor: floor 1: 1, floor 2: 0, floors 3-5: 2, 6-11: 3-4, 12-19: 4-5, 20 on: 5-6; the
  budget counts the guards, the reinforcements they call, the ambush at a secret passage's flask and the captain. A barracks floor
  doubles it (cap 10). Guards stand only at meaningful spots: before the exit (the captain on every fifth floor from 5, with a
  reinforcement from floor 6), just past a solved gate or gate puzzle (`gateDue`), in a fork's short way (kind 1), at a secret passage's
  flask (ambush); a barracks floor also posts garrison guards after other traps. Never on a landing, in a corridor fill or in a side
  passage. Snakes (floor 5 on: 1, 6-11: 1-2, 12-19: 2-3, 20 on: 3-4) only in tunnels, spaced along the route. `guardscan.py` checks it;
  `metrics40.py` and `featurescan.py` no longer count guards or skeletons as traps and print them as their own columns.
- Trap density (unit G1): traps per floor are held to about +15% over v39 (floor 12 about 77, floor 27 about 107), not by shortening
  anything. `LAND_PLAIN`, `CH_PLAIN` (a chamber's landings left plain), `FILL_PLAIN` (a stretch of side-passage corridor left plain, in
  `fillCorridor`) and `FLAT_K` (weight of plain floor in the run's menu) set it; check with `metrics40.py`. A remote plate (P1, P5) whose gate
  finds no room in the turn makes `buildLevel` lay the floor out again, so no dead-end side room is left behind. Timed gates (P4 too)
  are `estPath()` times `timerK()`; `estPath` times a careful pace (`WALK_T` and the action table, measured against the bot) so that the tightest factor 0.84 is still beatable. A longway floor always holds a fork (else it is laid out again, and the last resort drops the flag).
- Torchlight's scene is drawn by WebGL2 (unit WGL, v61; plan and research in `dev/WEBGL_PLAN.md`). Until v60 it was drawn in 2D and
  copied into WebGL every frame, and on the iPhone that copy (Safari waits for the 2D canvas, reads it back, uploads it: WebKit bug
  294602) was most of the frame. Now the same drawing functions draw through `G2D`, a recording Canvas2D look-alike (`GLS.F`): paths
  flattened in screen pixels, fans, earcut (inlined), stencil-then-cover for self-crossing and even-odd fills, strokes with joins, caps
  and dashes, stencil clips, gradients evaluated per pixel (stops in a ramp texture), composite modes, one indexed vertex buffer a
  frame, 4x MSAA resolved into the scene texture (`GLS.scene.tex`). `Path2D` inside the game is `HKPath` (records its commands);
  gradients and patterns remember how they were made (prototype hooks), so the same objects work on both contexts. The masks
  (effect mask, silhouettes in one target of 192 px slots, metal, beam occluders) are drawn the same way into their own targets and
  copied into the atlas on the GPU (`glAtlasGL`, same layout as `glAtlas`), so the shaders are unchanged and nothing waits: the frame
  is drawn at once (no frame of delay). Images are uploaded once: rooms when first drawn or two frames after they are built
  (`g2Warm`), the relief reading a room's mip level 1; a canvas redrawn every frame must be marked `_glv=1` (the dissolve's first frame; after it the dissolve runs on the GPU,
  `G2D._diss`, from the same noise and ramp).
  `GLP.rs` is now the scene target's scale. Classic is untouched. Without WebGL2, or with `GLFX.wgl=false` (`?prof` step '2D scene',
  `?bench=2d`), Torchlight takes the v60 path (2D scene copied one frame late through `glPrep`/`glSubmit`/`glScene`/`glAtlasUp`).
  Tests that compare the picture of one exact state set `GLP.pipe=false`. `wgl_cmp.py`, `wgl_maskcmp.py` and `wgl_parity.py` compare
  frames, mask atlases and single drawing functions against main or the real 2D context. The HUD canvas above WebGL is redrawn only
  when its list of drawing calls changes (`hudKey`).
- Torchlight's ambient light never drops under `AMB_MIN` (0.45 of full on its brightest channel, `glAmbK`; owner, v56 and v57: the Forge by
  Moonlight fell to 0.26), and each sky opening adds a soft bounce light where its beam meets the floor (`gatherLights`, Torchlight only).
  The fire vent burns over its whole grate (`VJETS`: a jet per slot, back and front rows, merging into one sheet); its timing and
  hit test are unchanged.
- The swing bar is a trapeze (v57, owner): his swing is a damped pendulum (`P.swTh`, `P.swOm`; `swingStep`) that dies down to a still
  hang in about 4 s (`SW_TAU`, `SW_FR`); holding left or right pushes that way (`SW_K`), so alternating in step pumps it up (to `SW_MAX`) and
  holding one way only leans him; the catch keeps `SW_ETA` of his speed (a running catch clears at once); Jump's throw grows with his speed,
  and from `SW_CLEAR` it carries him over (the grip creaks, the bar glints). The chains swing too (`f.ps`, `f.pw` on the feature, so a rewind
  restores them). The bot pumps to 0.8 and lets go moving forward at 0.15 to 0.3 rad. Check with `swingtest.py`.
- Sky beams (v58, owner: they looked painted): the moon's light has depth (`SKYB.q`): it comes through an opening in the back wall
  toward the viewer and lands on the floor's top face in the opening's shape; the wall it comes through gets none. The shaft is haze
  (in-scatter: fades in at the opening, out over the floor, soft edges, shown against the dark only, motes inside it), never a flat
  sheet; the floor patch and the opening's rim are its brightest parts and the only parts that bloom. Forge and crypt windows are lit
  from inside: a glow at the window, no shaft. Classic draws the same shapes from sprites (`ryBeams2D`). Check with `beamshot.py`.
  A figure in a beam (v59, owner: hard white stripes) gets only a weak, capped cool light on the side toward it (`RY_FIG`, `RY_FIGC`,
  feathered by the figures' mask); figures never bloom from the beam and the floor patch, pane and rim are not drawn on them.
- A dart shooter firing left sits on a wall's hidden left face: no head is drawn and its darts come from behind the front face.
- Lifts (v60, owner): no wall plant or kick inside a lift's shaft (`inLiftShaft` in `wallTouch`; `liftkick.py`). Lift parts are cut
  out behind the walls' front faces in front of them (`liftOccl`), the counterweight runs in the back wall behind the platform, and
  they follow the stonework's wear (`liftWear`). Paternoster slabs and a counterweight platform stopped mid-shaft are solid to him in
  the air (`liftAir`); a slab coming down on him at the foot steps him aside, never hurts. A ride held on Down ends standing (`P.liftHold`).
  A mouth grating on a shaft's right edge is drawn after the shaft's contents, the rider is cut by `liftOccl` too, and the shaft's
  back-wall parts are cut by the side faces beside it (v61); `liftscan.py` checks every lift for pixels over walls and gratings.
- A ceiling at his height (a WALL, or an upper floor's slab, `ceilY`) makes any floor jump the low leap (v60, owner), and the head
  clamp holds every frame; a saw that would sit under such a ceiling becomes spikes in place (the low leap cannot clear it).
  Check with `lowceil.py`.
- The sandstorm's surface boils (v60, owner): a two-phase flow map in the shader, baked looping frames crossfaded in Classic (`STB`).
- Every trap pushes a bot action onto `L.path`; the bot replays that list, so a new trap needs its action in `bot.js`.
- Gate timers are sized from `estPath()` at a careful pace, times 0.84 to 1.08.
- Pose angles are measured from straight down; positive means forward.
