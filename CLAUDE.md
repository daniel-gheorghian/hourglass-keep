# Dawnward (repo: hourglass-keep)

Dawnward (working title from the egypt branch; formerly Hourglass Keep) is a single-file HTML5 canvas platformer in the manner of Prince of Persia (1989), played as an
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
they load `bot.js` by a relative path and write their output next to themselves. Many (run2, rendersmoke, featbot, glauto,
respawnplates and others) open the main checkout's `dev/hourglass-keep.html` by absolute path, so in a git worktree they test
main's file, not the branch: run them from a copy of `dev/` with that path rewritten to the copy.

## Build

From the repo root, with N the release number (current release v69, next v70):

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
   standalone. Jobs that draw Torchlight (`rendersmoke`, `liftscan`: software WebGL in headless Chromium, several cores a frame) run at most three at a time (`HK_GPU_JOBS`); eight at once took four times as long each for no gain and tripped rendersmoke's 240 s wall budget (v67). A job over its 25-minute limit, or one that kills its browser, fails with a message and the worker is replaced.
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
left untouched. Its dropped-frame column (round 16d) counts frames over 1.2 refresh intervals of the screen it runs on: at the start the
bench times 40 rAF callbacks, takes the median and snaps it to 30, 60, 90, 120 or 144 Hz (`BENCH.hz`, `BENCH.thr`), and the header
names both, e.g. `>20 ms @60Hz` (the old fixed 20 ms) or `>10 ms @120Hz`. iOS: Safari tabs on ProMotion run rAF at 60 Hz while the
default-on feature flag 'Prefer Page Rendering Updates near 60fps' is set; home-screen web apps were held at 60 in 2024 (the flag did not
reach them) and run at 120 on iOS 26; Low Power Mode throttles rAF to 30 (WebKit bugs 280183, 272226, 215745). The game's own scaling thresholds do not
follow it. `?bench=75`, `?bench=auto` (the game's own resolution scaling), `?bench=classic`. `bench.py [arg] [floors]` (e.g. `bench.py 1,17`) runs the
same on this Mac's GPU (Chrome's costs differ from Safari's: compare Mac runs with Mac runs). `?prof` times each stage in place.
The pause menu's Tools… screen (v63) has buttons that reload the page with `?bench`, `?bench=classic`, `?bench=auto` or `?prof`;
the bench's table and the profiler each have a button back to the game. Its Show FPS toggle (v64, `S.set.fps`, off by default) puts a small
readout under the pause button: fps and frame time from glTime's half-second average, and the Torchlight scale when under 100%.
Lighting mode (v63, owner): only the player switches between Torchlight and Classic (Graphics). Slow frames only scale Torchlight's
scene down (`GLP.rs` 1, .75, .5), and only when two 2 s windows in a row average over 38 ms (v65, owner; was 18.5); they never switch to Classic. It steps back up one level after three 2 s windows with no
dropped frame (`UP_MS` 17.2 ms); a step up that turns slow again within 10 s doubles the windows the next try needs (up to 30), reset each floor. A missing or lost WebGL context still falls back to Classic (`glKill`),
as the screen would otherwise be black; `glauto.py` checks this, and that windows between 18.5 and 38 ms keep the full scale (round 16d).

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
- The gold flask's cue (round 17, owner): where the climb or drop to a secret passage's gold flask (`L.secret`; or an alcove's gold
  flask) starts, a few small gold four-point stars twinkle on the lip's top face along its edge in depth (`secretCues`, found once per
  floor from the tiles and kept in `L._scue`; `drawSecretCue` in `drawDynamic`): an ascent on the ledge he grabs, lifting a little; a
  descent on the floor edge he hangs from, slipping toward the hole. Gone once the flask is taken. Look only, both modes, no allocation a
  frame; the hint is `secret` (up) or `secretdn` (down). Pictures: `egyptr17.py`.
- No chains (round 18b, owner): every chain drawn in play is rope: the swing (above), the pendulum's pivot lashing, Siwa's hanging lamp
  (a palm cord and a sling), fallen lamps' scars and the fallen lantern's cord (`ropeEnd`), the Nun and Meroë backdrops (`ropes`
  layer: knots, jar slings, baskets); the lifts were rope from round 13. Iron chains remain only behind `EGP.traps`/`EGP.lamps` off
  (the v61 looks). A new hanging thing uses rope (`barRope`, `ropeOf`). Pictures: `egyptr18b.py`.
- No arrows in the world (round 18, owner): the paternoster's brass chevrons are gone, and the kick shaft's chevrons became the jet
  stream hint: `jetStream(ctx,path,strength,speed,width,seed,view,wall)` blows the floor's sand (`SAND_LOOK`, sprites `jsSprites`) along a
  path built once with `jsPath`/`jsAdd`/`jsQuad` (a chimney's draft: drawn in slowly at the entry, quickening, fanning out, slowing and
  rising at the exit). Organic since round 18c (owner: "needs to be more organic"; after Ghost of Tsushima's vorticles, curl noise, incense
  plumes, saltation streamers, Journey's glitter): up to 200 fine grains (1 to 2.5 px, 30% fainter wider dust) carried round 2 to 12
  drifting counter-rotating eddies (`JSE`, `jsTwirl`: weak at the entry, strong further on) and a slow sway, riding in puffs (`JS_PUFF`)
  with a dense head and a stretching tail; each a soft sprite stretched along its own motion over 0.05 s (`jsStamp`: a transform and its
  inverse); faint added haze wisps that grow; rare glints; in a shaft a soft clamp keeps grains off the walls (`wall`: they hug and peel).
  Everything is a pure function of the clock (no state, no allocation a frame, rewind-safe); three sprite batches a stream; only in view.
  Used by `drawJetHints` (in `drawDynamic`, places found once per floor in `L._jet` by `jetPlaces`): every kick shaft, either side (full
  until `shaft` is learned, then 0.65); the swing's throw while `P.swRdy` (`jsSwingPath`, the release's own numbers: lands within ~7 px);
  the jgrab jump only until `jgrab` is learned. Not on gap jumps, lifts, banners, hurtdrops or secrets (clutter, or against their look).
  A new place is one entry in `jetPlaces` and one call. Pictures: `egyptr18.py`; videos before/after `egyptr18c.py`.
- Lamps keep clear (round 19, owner: "sometimes lamps or torches are placed just like that"): a lamp burns only where both cells beside
  it are plain floor (no wall face or step, ledge, gate, banner, bar, pendulum, lift or lift plate), no lift shaft is beside it and no water
  clock or door near (`lampClear`); `lampsClear` (first in `settleLights`, no generator stream) moves one that is not along its row to the
  nearest such tile within 6 (3 from another lamp), else puts it out; replacements for fallen lamps use the same rule. `lampscan.py`
  (floors 1-48, 3 seeds) must print `ok`: 0 of about 9,600 lamps (2,165 before).
- Behind a wall's face (hanging from, jumping up to, climbing onto or down from a ledge on its near side) he is hidden but for his
  hands, as PoP1 does (SDLPoP `draw_tile_fore`, `clip_char`): no ghost through the wall (round 19, owner). Torchlight's figure shadow
  (`glShadow`) is carved out of the stone as drawn (wall front faces HX left, tops, right sides; floor lips and tops) and his hidden
  part casts none; carving at the cell left a prince-shaped stripe on a lit face. (round 20a, owner) A low ceiling's front face (and its side face at
  the tunnel's right end) is carved too: a lamp on the back wall behind him cannot light a near face, so no shadow lands there; the
  shadow still falls on the back wall under the ceiling. Guards share the code.
- The sand lift's slab (`sandSlab`, round 19) is a floor tile: lip over the whole cell from X-HX, top along the depth diagonal, no
  side face or outline; the next column's nearer stone cuts it once it leaves a landing; the shaft's back is seen through the hole only.
- Sand wells (round 21b, owner: "sand has wall motif"; "the edge between them cannot be vertical"): cracked slabs side by side over one
  pit are one body of sand (`wellGroup`, kept on each slab's feature as `f.wg`; drawn once, `drawWellGroup`). `wellSolve` finds its surface
  from the slabs' own `f.s`/`f.tm` only (rewind- and respawn-safe; a chain's slab counting down below zero is not open): a crater over each
  open outlet with walls never steeper than the angle of repose (`WELL_SL` 0.67, 34 degrees; depth `WELL_CD`), heaps below that angle stay,
  the rest sinks level so the sand left equals what was there less what ran out (the whole body in the time one storey took). A slab whose
  neighbour opened first leans into its hole on its far edge (`wellTip`: up to `WELL_TIP0` while still floor, to `WELL_TIP1` once set off) and
  falls turning as one piece; the first of a row folds in two as in 16a. Look only: no slab falls sooner. The sand's face is one tile per
  theme (`sandTex`: grains, packing, broken laminae; never ruled courses or cell seams), the shaft's dark a cached ramp (`sandShade`); the
  sand lift uses it too (`sandCut`). Torchlight's relief is rubbed back over the sand (`glRelWell`, `glRelBox`), else it embosses the back
  wall's art on it. `wellscan.py` (floors 3-30, 3 seeds: slope, volume, break timing, rewind) must print `ok`; pictures `egyptr21b.py`.
- Arms up (round 19, owner: "a hump"): `torsoG` narrows the back near the shoulders (up to 1.3 px) and the raised arm rises from the
  back of the shoulder, so the back line runs from the waist into the arm. Pictures for round 19: `egyptr19.py`.
- The prince's proportions follow the 1989 Prince of Persia kid (DOS) (round 22d, owner: "I like best the proportions in the original PoP
  sprite. Replicate the proportions from there in our prince"; rounds 22b/22c's ANSUR II youth is background only, `dev/FIGURE_SPEC.md`).
  The kid, measured from his frames (`dev/tools/ref/pop_kid.png`/`.json`, PrinceJS assets; frame numbers as SDLPoP's `types.h`; DOS pixels
  are 1.2x taller than wide: horizontal measures divided by 1.2): 41 rows, head 7 = 5.86 heads; chin 0.83 of the height; the deltoid's top
  one row (0.024) under the chin, the shirt's shoulder line level with it (sloping shoulders, a slim neck 0.08 deep, one row of throat);
  shoulder joint 0.77, elbow 0.60, fingertips 0.39; trunk 0.15-0.16 deep with a straight back (head, back and seat on one line); foot 0.14.
  Ours (52.75 px): `LEN={th:12,sh:12,to:15,nk:4.66,hd:3.52,ua:8.9,fa:8.6}` (head 9.0 px, 5.86 heads; v69's trunk 15 and arm 17.5, so held
  hands and overhead reach are v69's); `NJ` puts the pit of the neck and the deltoid's top ~1.2 px under the chin, C7 just under it,
  `NJ.hn` scales the neck's top with the head; the outline is slim (`BQ`/`Fo`/`Bo`, limb widths, foot 0.78 long). Legs are gameplay's
  (knee 0.25 against the kid's 0.28). The crown stays at 27.7 px over the hip and never rises above v69's. Hands that hold something (ledge,
  floor, hilt, flask, the fight's sword) keep v69's places: pose keys `hold` (front hand), `hb` (back), `mh` (follow the mouth) make `skel`
  solve the arms to v69's hand (`F69`), lifting an airborne body when a grip is out of reach. A new holding pose sets `hold`/`hb`; a new
  head-up pose near low stone must keep the crown under v69's. Robbers share the skeleton with their own heavier build. Measure with
  `r22dmeasure.py` (the kid and our figure side by side; `r22cmeasure.py` has the neck landmarks); check with `figscan.py` (must print
  `figscan: ok`); pictures `egyptr22d.py` (the kid beside v69/22c/after, every pose, in game).
- Lift ropes (round 21a, owner: "holes in the slab with the rope threaded through"): all lift ropes are `barRope` in the theme's fibre
  (`liftRope`; `barRope`'s `ph` makes the lay travel with a running rope). The counterweight platform hangs on two bridles (`liftSling`: an
  eye seized `LS_J` above the slab, legs down through two holes near the front and back edges along the depth diagonal, `ropeHole` drawn in
  the view's oblique); the counterweight by a hole through its top; a paternoster slab on its rope through a hole in its middle with a seized
  stopper (drawn while the rope runs upright). The sand lift has no rope. Look only, inside `liftOccl`. Check with `liftscan.py`.
- On all fours (round 20b, owner: "the prince's ass showing"): once both hips flex (`lean+h` 0.8 to 1.2) the shendyt gets a seat point
  (`KS`) on its back edge at the hip, out until the curve clears the thighs' round tops by 0.4 px, and a faint tension fold; other poses
  unchanged. The prince's straight blade (round 20b, owner: "transparent sword": a 1.5 px sliver in the floor's own tan, only its outline
  read) is a leaf-shaped bronze blade about 3 px wide drawn as two bevels, the upper one lit, the lower dark bronze, a bright lit edge and
  a pommel: it reads on pale floors and dark walls at every scale. Pictures: `egyptr20b.py`.
- The key light (`keyLight`, round 20b, owner: the slab flicked between lit faces): not the nearest lamp within its flickering radius but
  the balance of all lamps in reach, each weighed by a smooth falloff over its steady radius (`r0`, `a0` on torches) with a weak pull from
  the left (the old default): `sx` -1..1, continuous and still in time; `dir` is its sign, `m` how much a lamp carries it. Figures take
  `sx` as their lit side; `egSlab`'s faces and cast shadow cross-fade by it (`uL`). Never key a look on a flickering radius or on one
  nearest light.
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
- Torchlight's scene is drawn by WebGL2 (unit WGL, v62; history in `dev/WEBGL_PLAN.md`, how to work on it in `dev/WEBGL_LESSONS.md`).
  Until v60 it was drawn in 2D and copied into WebGL every frame (Safari waits for the 2D canvas and reads it back: WebKit bug
  294602). Now the same drawing functions draw through `G2D`, a recording Canvas2D look-alike (`GLS.F`): paths flattened in screen
  pixels, fans, earcut, stencil-then-cover for self-crossing and even-odd fills, strokes with joins, caps and dashes, gradients
  evaluated per pixel (stops in a ramp texture), composite modes, one indexed vertex buffer a frame, 4x MSAA. `Path2D` inside the
  game is `HKPath`; gradients and patterns remember how they were made (prototype hooks), so the same objects work on both contexts.
  `g2Replay` draws the recorded targets in order: the backdrop, the silhouettes (192 px slots), then the masks (effect mask, beam
  occluders, metal) straight into their places in one multisampled atlas of fixed size (`GLA.G`, laid out by `glAtlas`; `glAtlasGL`
  only hands it on), then the scene; each target is resolved once (`blitFramebuffer`) with its depth and stencil dropped first. On
  this path `glPrep` and `glSubmit` run in the same frame: no frame of delay, and `GLP.pipe` does nothing (it only delays the v60
  path). An axis-aligned rectangle clip is a scissor box plus each pixel's covered share in the shader, not the stencil. Textures the
  CPU writes every frame (gradient parameters, gradient rows) are used three in turn; a gradient's stops are kept over their largest
  alpha (`g._am`), so a fading glow is one row. Rooms are uploaded once: whole when needed now, else in strips of 80 rows a frame
  two frames after they are built (`g2Warm`/`g2Stage`, a staging canvas per strip); the relief reads a room's mip level 1. A
  canvas redrawn every frame must be marked `_glv=1`. The gradient ramps follow the browser's 2D canvas (`g2GradPM`: Safari mixes
  radial gradients premultiplied). The shaft's shadow march takes the same steps for every pixel (a jitter per pixel made blocky
  edges). `GLP.rs` is the scene target's scale. Classic is untouched.
  Fallback: `?wgl=0` in the URL (and `?bench=2d`, `?prof` step '2D scene (v60)', or no WebGL2) takes the v60 path (2D scene copied
  one frame late through `glPrep`/`glSubmit`/`glScene`/`glAtlasUp`).
  Tests that compare the picture of one exact state set `GLP.pipe=false` (for the v60 path) and a frozen clock, render a few
  times and read the WebGL canvas back: `wgl_cmp.py` (frames against another build), `wgl_maskcmp.py` (mask atlases),
  `wgl_parity.py` (single drawing calls against the real 2D context). `WK=1` runs the wgl_* tools in Playwright's WebKit (serve
  dev/ with `python3 -m http.server 8765 --bind 127.0.0.1`). `?bench&floors=17` benches chosen floors; `__BENCH_TRACE` holds each
  floor's first 6 s frame by frame (`wgl_trace.py`). The HUD canvas above WebGL is redrawn only when its drawing calls change (`hudKey`).
- Torchlight's ambient light never drops under `AMB_MIN` (0.45 of full on its brightest channel, `glAmbK`; owner, v56 and v57: the Forge by
  Moonlight fell to 0.26), and each sky opening adds a soft bounce light where its beam meets the floor (`gatherLights`, Torchlight only).
  The fire vent burns over its whole grate (`VJETS`: a jet per slot, back and front rows, merging into one sheet); its timing and
  hit test are unchanged.
- The swing bar is a trapeze (v57, owner): his swing is a damped pendulum (`P.swTh`, `P.swOm`; `swingStep`) that dies down to a still
  hang in about 4 s (`SW_TAU`, `SW_FR`). A press is a pump (round 16b, owner: too hard to pump; it was a held push that braked him
  whenever the switch came after the turn): a new press of left or right arms one pump (`P.swArm`) that fires as he next passes the bottom
  going that way within `SW_PRE` (0.8 s) of the press, or at once just past the bottom (`SW_LATE`) or from a still hang: a kick of
  `SW_KICK` amplitude over 0.12 s (`swingKick`). Wrong or late presses do nothing and never brake (the held lean `SW_K` only helps); two
  opposite presses within `SW_MASH` cancel (mashing does not pump); holding one way gives one pump. Within 1.2 s of a kick the damping
  is lighter (`SW_TAUP`, `SW_FRP`). From a still hang about 3 presses, 1.4 s, at human timing (`swingfeel.py` simulates touch players:
  before 5 s, or never at 0.35 s reaction or with taps). The catch keeps `SW_ETA` of his speed (a running catch clears at once); Jump's
  throw grows with his speed, and from `SW_CLEAR` it carries him over: a chime (`swready`) over the ropes' creak (`ropecreak`), a glint
  running up the near rope, and a warm glow at his hands while
  ready (full on the forward swing), with hysteresis down to 0.5. Each pump whooshes (`swpump`). Down lets go only held 0.15 s with no side
  (a thumb crossing the pad's lower sector used to drop him). The ropes swing too (`f.ps`, `f.pw` on the feature, so a rewind
  restores them). Its look (round 18b, owner: "replace the chains with rope, and make the whole thing Egyptian"; `drawBar`): a wooden pole
  hung on two taut laid ropes (`barRope`: S-plied lay as diagonal grooves, each strand lit on its left; three strands for palm fibre)
  from a round timber set front to back under the ceiling, its end grain 3 px proud of the lintel's face; everything above the lintel's
  edge is clipped (the view sees no ceiling's underside), so the far rope comes out from behind the lintel. Fibre and timber per theme
  (`BARM`: papyrus, halfa or palm; cedar, sycomore, acacia, tamarisk, juniper; `BARF`, `BARW`), worn by `wearLevel`; rawhide grip. No
  metal (not in the metal mask). `ropeOf()` gives the theme's rope colours to other drawings. The bot pumps to 0.8 and lets go moving forward at 0.15 to 0.3 rad. Check with `swingtest.py` (also: cue from a
  still hang within 2 s, mashing never clears) and `swingfeel.py`; pictures `egyptr16b.py`.
- Sky beams (v58, owner: they looked painted): the moon's light has depth (`SKYB.q`): it comes through an opening in the back wall
  toward the viewer and lands on the floor's top face in the opening's shape; the wall it comes through gets none. The shaft is haze
  (in-scatter: fades in at the opening, out over the floor, soft edges, shown against the dark only, motes inside it), never a flat
  sheet; the floor patch and the opening's rim are its brightest parts and the only parts that bloom. Forge and crypt windows are lit
  from inside: a glow at the window, no shaft. Classic draws the same shapes from sprites (`ryBeams2D`). Check with `beamshot.py`.
  A figure in a beam (v59, owner: hard white stripes) gets only a weak, capped cool light on the side toward it (`RY_FIG`, `RY_FIGC`,
  feathered by the figures' mask); figures never bloom from the beam and the floor patch, pane and rim are not drawn on them.
  (v66 round 15, owner: light round corners) No beam light, haze, footprint or rim lands on a wall block's front face (drawn HX left of
  its cell): the shader takes the face's coverage across each quarter-size pixel, Classic (`ryBeams2D`) cuts the faces where they are
  drawn, and a beam's bounce light is dropped when a wall stands between the opening and its landing. Check with `beamwall.py`.
  (round 20a, owner) The same for a low ceiling's block (a tunnel's roof, `low`: the top `LOW_H` 30 px of its cell, its face HX left): it is
  `LOW_R` in the tile map's r (walls 255; under .5, so mist and looks read it as open), read exactly (`lowC`) for the face cut and as an
  occluder in the march; Classic cuts it (`ryLow`: the space under it too, past the tunnel's first cell) and drops footprints there; the
  bounce light tests `solidFront`. A slicer's blades and a granite portcullis that is down stand across the corridor's whole depth
  (`beamBlockers`, quads from drawJaws'/egSlab's geometry): Torchlight tests them exactly in the shader (`u_bk`, `blkC`: up to four; the
  march softens them over at least its step, or a thin blade leaves a staircase), so the beam behind them is shaded and only the near half
  of the haze lies over them, no footprint, no figure light; Classic clips them and their shadow (`ryHull`: the
  quad swept along the light, a clip; only for one in a beam's haze, `ryBlkLit`) out of haze and footprint. Pictures and numbers: `egyptr20a.py`.
  Round 20b (owner: the wedge to the floor read crude): Classic draws such a beam `RY_SH` (5) times at a fifth of its strength, each cut by
  its own hull (the quad swept 12 to 72% of the way to the floor and spread 8 to 70%), so the shadow is whole at the blade and fades and
  widens to nothing short of the floor (an area light's penumbra); clips only, never a scratch canvas.
- Doors are drawn live, but Torchlight's relief reads the room's picture: the back wall's art is flattened under each doorway and its
  frame (`drawRoomStatic`). `doorscan.py` checks every door (floors 1 to 48, both modes) for art over the opening. At the exit he
  climbs the doorway's stairs tread by tread (`EX_*`, `P.exS`), cut by the posts and the ceiling's edge. (round 16c) The stairs are the
  same in every style; his first step also lifts him `EX_UP` (from the floor's middle depth onto the tread, which starts inside the
  doorway), and his stride moves only while he rises (`P.exQ`), so a planted foot stays put; `stairscan.py` measures feet against the
  drawn treads on floors 1 to 48. Stone slabs (portcullis, lift mouths) are rubbed out of the relief whenever they are down
  (`glRelSlab`: the back wall's courses and friezes were embossed on them); `openscan.py` checks windows, gates and lift mouths for
  wall art over the opening (floors 1 to 48, both modes; `EGP.noover` leaves out the hangings and lamp scars drawn after windows).
- A dart shooter firing left sits on a wall's hidden left face: no head is drawn and its darts come from behind the front face.
- Lifts (v60, owner): no wall plant or kick inside a lift's shaft (`inLiftShaft` in `wallTouch`; `liftkick.py`). Lift parts are cut
  out behind the walls' front faces in front of them (`liftOccl`), the counterweight runs in the back wall behind the platform, and
  they follow the stonework's wear (`liftWear`). Paternoster slabs and a counterweight platform stopped mid-shaft are solid to him in
  the air (`liftAir`); a slab coming down on him at the foot steps him aside, never hurts. A ride held on Down ends standing (`P.liftHold`).
  A mouth grating on a shaft's right edge is drawn after the shaft's contents, the rider is cut by `liftOccl` too, and the shaft's
  back-wall parts are cut by the side faces beside it (v61); `liftscan.py` checks every lift for pixels over walls and gratings.
  Mouth slabs (round 16c): a slab on the shaft's left edge is drawn after the shaft's back plane (shade, channel, counterweight) and
  before the ropes, beam and platform (its broad face is the shaft's side); the call plate's cell is cut round the slab (`liftMouthCut`)
  instead of the slab's foot being drawn again; a slab's cast floor shadow falls only on floor, not into the shaft; wear chips on a
  slab are capped in px (`stoneWear` cap: a share of its height made a slit that sheared it).
- A ceiling at his height (a WALL, or an upper floor's slab, `ceilY`) makes any floor jump the low leap (v60, owner), and the head
  clamp holds every frame; a saw that would sit under such a ceiling becomes spikes in place (the low leap cannot clear it).
  Check with `lowceil.py`.
- The sandstorm's surface boils (v60, owner): a two-phase flow map in the shader, baked looping frames crossfaded in Classic (`STB`).
- Themes (branch egypt, owner): twelve themes of Egypt, Kush and the Sahara, four floors each (`THEMES`, `themeOf`), turning every 48
  floors; time of day and wear still turn every 20 (`progOf`). A theme has a drawing `style` (dungeon, palace, tile, forge, crypt: the
  style-keyed tables) and a `look` (its backdrop `BGART`, hangings `TAP`, Torchlight light `lk`, effects `LFX`). The generator never
  reads the theme: it builds by `L.gstyle`, the old five-theme turn (`GEN_STYLE`), so floors stay as they were. Arches, doors and
  windows are post and lintel (the dungeon style's vaults stay round). No churches, crosses or the Ark, no living peoples as enemies
  or decoration. Pictures and sources: `egyptshot.py`, `egyptfx.py`, `egyptpage.py` (egypt_themes.html).
  Built in (owner, round 4): the themes' lamps (`drawLampEg`) and the re-skinned traps are on by default: granite portcullis
  (`egSlab`; lift gates keep their bars; no metal mask; modelled by the key light: lit narrow face, a crisp arris, a core-shadow band and
  dark far edge on the broad face, a cast shadow on floor and wall, raised in round 16c so the edge reads in every theme), sliding roof block with sand (`egStone`, `egBlock`), sand floor, bronze-
  tipped stakes, and the chase drawn as a granite plug (`drawPlug`; the storm shader, veil and Classic bakes are off behind it).
  Look only: hit boxes, timing, generator and bot unchanged. `EGP={lamps,traps,plug}` turns them off for debugging (metaltest's
  gate scene and stormfair test the iron gate and the storm that way). The plug is one passage-sized block per corridor row of the
  chase, its leading face at `wx` (the kill line stays `wx+4`), with a dust veil marking the line where no floor is. The water clock
  (the Karnak clepsydra) replaces the hourglass as look and words: the checkpoint (`drawHourglass`), the HUD's measures and gate
  timers (`drawGlass`), the rewind's grade and words; `S.sands` and every timing are unchanged. Theme order: `themeOf(n)` takes the
  block's generator style (`GEN_STYLE[block%5]`) and picks the theme by light and 60-floor turn from `SCHED` (repeats every 180
  floors), so a floor's theme always has the style it is built by; `egyptaudit.py` keeps a copy of `SCHED`. Title
  Dawnward; fonts Rokkitt (display, HUD numbers) and Jost (text). Not renamed: the cache key `hourglass-keep-vN`, the save key,
  the repo and its URLs.
  Round 16a (owner): a fallen roof block (10 px high) is a low obstacle he steps over with no key: it no longer stops him in
  `clampMove` (guards still keep to their side) and `blockStep` lifts his drawing onto it in `updateLook`; the bot runs over it
  (`runover`). A cracked slab (`loose`) has two looks chosen by `looseWell(o)`: over a pit walled in on both sides it sits on a sand
  well (`drawWellSand`: the level falls at a steady `WELL_V` 150 px/s, Beverloo; a funnel crater; the slab sags and folds in two,
  `slabHalves`), anything open beside the space under it is a corridor (grit, `slabChunks` in four pieces, `dustCloud` at the hole
  and the landing cloud `DUSTC`). Play is unchanged for both (0.5 s, `DROP_G`). The sand lift (`sandLiftSeg`, a lift with `f.sand`):
  a `banner3`/`banner4` move is built as one about 37% of the time (`sandOr`, a hash: no random stream, so layouts are identical;
  never in a fork's short way or a G3 gate turn; segs `turn-sand3/4`); stepping on its slab starts it, it sinks at `SAND_LV` 140 px/s
  after `SAND_LW` 0.25 s and stays down; bot action `sandlift`; `estPath` times it as the slide. Checks: `lifttest.py` (sand3, sand4
  and its own case), `liftscan.py`; pictures `egyptr16.py`.
- Every trap pushes a bot action onto `L.path`; the bot replays that list, so a new trap needs its action in `bot.js`.
- Gate timers are sized from `estPath()` at a careful pace, times 0.84 to 1.08.
- Pose angles are measured from straight down; positive means forward.
