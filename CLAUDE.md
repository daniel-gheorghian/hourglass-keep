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
| `dev/tools/hk_vNN_release.html` | Source of each past release, the baseline for comparisons. In git up to v48; later ones are kept locally, untracked (`figscan.py` needs v69's, `layoutcmp.py` takes the newest it finds). |
| `dev/localize.py` | Run once per new machine (see below). |
| `dev/docs/` | Reference docs: concept, gameplay, level design, rendering, the layers (`layers.md`: what may cover what), and one file per game element (play, drawing in both modes, each shader pass, relations, the prince and the guards); `README.md` indexes them. A round that changes an element updates its file in the same commit. |

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

From the repo root, with N the release number (current release v89, next v90):

```
python3 dev/tools/build.py dev/hourglass-keep.html index.html sw.js N
```

It stamps `APP_VERSION`, wraps the page with the PWA head and service-worker boot, and sets the
service worker's cache to `hourglass-keep-vN`, which is what makes installed copies update. The source's own `APP_VERSION` ('23')
is a placeholder: only the built `index.html` carries the release number.

## Release routine

1. Change the source, then build with the next N.
2. Run the regression suite from `dev/tools` with `python3 suite.py release`. It runs every test below spread over the
   machine's cores. Every job belongs to one of three suites by its group (`SUITES` in suite.py; a group in none stops the run before
   it starts): `play` (the bot and play checks: run2, featbot, p4bot, forktest, hinttest, grablabel, swingtest, liftkick, chimtest, lowceil,
   r38b_tests, sawceil, hilljump, primtest, hdtest, lifttest, respawnplates, slabresume, gratepeek, tellscan), `gen` (generator and layout scans: metrics40,
   guardscan, forkscan, puzzlescan, vertscan, featurescan, orphanscan, mazescan, wellcorr, lampscan, slabscan, sandshaft, wellscan, hillscan, windscan, courtscan, wearscan) and
   `render` (drawing checks: rendersmoke, liftscan, crossscan, cpscan, shadowscan, doorscan, openscan, tilescan, beamjag, heapscan, solidscan, contourscan, viewscan, panscan, stormfair, glauto,
   metaltest, rewindrooms, figscan). The tier chooses the jobs; `--suite play,render` runs only those suites, in that order (default
   all: play, gen, render). The suites run in sequence (owner): each has the whole pool of workers and GPU slots, finishes, writes and
   prints its summary with its own wall time, then the next starts; `--stop-on-fail` skips the suites still to run once one fails
   (reported as SKIPPED; default: carry on, so every suite reports). `--only REGEX` runs only the jobs whose group and argv match. Each run writes
   `dev/tools/suite_logs/<YYYYmmdd-HHMMSS>-<tier>[-<suites>]/` (gitignored; its path is printed first and last): `progress.log` (a line
   as each job starts and finishes, `[done/total]`, suite, ok/FAIL, argv, seconds, summary; the finish lines also go to stdout:
   `tail -f` it while it runs), `jobs/<suite>/<job>.log` (each job's whole output), `journal.jsonl`, `summary-<suite>.txt` (written and
   printed as that suite finishes) and `summary.txt`: per suite its verdict, job count, wall and job time and the table
   of one line per test, failing jobs with their key lines and log path, then the five slowest jobs, ending in `ALL OK` or `FAILURES`
   (exit 1). `--resume DIR` carries on an interrupted run dir (`--resume FILE` or `HK_SUITE_JOURNAL` a journal file): finished jobs
   are skipped and reported with the rest, and the suites carry on in sequence (a failed job in the journal stays failed). The bot and render
   runs are split one floor (and seed) per job; each of the N workers (`suiteworker.py`) starts ONE Chromium and runs its jobs
   in turn, each in a fresh browser context, so nothing leaks between jobs. The test scripts are unchanged and still run
   standalone. Jobs that draw Torchlight (`HEAVY` in suite.py: rendersmoke, liftscan, crossscan torch, cpscan, shadowscan, doorscan, openscan, tilescan, beamjag, heapscan, solidscan) run in a second shared browser per worker launched with the GPU flags (`--use-angle=metal --enable-gpu --ignore-gpu-blocklist --force_high_performance_gpu`: WebGL through ANGLE on Metal, the Radeon; without flags headless Chromium draws WebGL in SwiftShader on the CPU, several cores a frame), at most four at a time (`HK_GPU_JOBS`, default 4). Measured idle on the 8-core i9 (Radeon Pro 5500M), software against GPU: `liftscan.py 15 20` 495 s (100 CPU-min) against 83 s (2), `shadowscan.py 13 18` 533 s against 127 s; eight shadowscans at once 285 s each, 4.9 min in all, four at a time 150 s each, 5.2 min at 40% less CPU. `HK_SUITE_GPU=0` runs them in software as before, `HK_SUITE_GPU=igpu` on the Intel UHD 630. The light render jobs stay in software: a 2D canvas drawn on the Radeon is not bit-exact between two redraws (rewindrooms finds 13 values off). The GPU shows one fault software hides: shadowscan's sky clock on floor 29 seed 1 (c367 r57, 125 px of his shadow, both GPUs; the clocks on floors 10 and 22 fail either way). A job over its 25-minute limit, or one that kills its browser, fails with a message and the worker is replaced.
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
| `python3 metrics40.py [vNN]` | route length, trap count and trap spacing against a release's source (`hk_vNN_release.html`; default v39, the trap density rule's reference) | no floor shorter, padding kept |
| `guardscan.py` | the guards' and snakes' budgets and posts (Fighters, below) | `guardscan OK` |
| `rewindrooms.py` | after a rewind over a hole knocked in the floor and new rubble, the room's picture equals one drawn from scratch (a rewind redraws only the rooms that changed) | all ok |
| `respawnplates.py`, `puzzlescan.py`, `slabresume.py` | plates stay pressed after a respawn; the puzzle menu's pairs are built; a slab-jammed plate is restored | all ok |
| `primtest.py`, `hdtest.py`, `vertscan.py`, `lifttest.py` | every chamber move works for the bot; the chamber's damaging drop (hgap) costs exactly one life where it is placed; counts of vertical moves; both kinds of lift ride | all ok |
| `p4bot.py lo hi [seeds]` | the bot plays floors forced to timed remote plates (P4, run for a gate in the next turn); the timers carry no extra factor | every run passes, 0 damage |
| `orphanscan.py`, `mazescan.py` | no gate side passage is left without its plate (floors 1 to 27, 20 seeds); maze floors hold at least 1.5 times the gate puzzles of ordinary floors of the band, longway floors always a fork | 0 orphans, ratio >= 1.5, forks >= 1 |
| `featurescan.py [file]`, `featbot.py` | a floor's featured families hold their share of their category (mean and minimum), flags come about one floor in nine, floors differ more than before (sameness); the bot plays floors forced to every flag and family (`window.__FEAT`) | shares near or over 40%, 0 damage |
| `wellcorr.py lo hi [seeds]` | no sand well stands in a corridor: every well's pit is walled on both sides down to its floor (round 30) | `wellcorr: ok` |
| `cpscan.py lo hi [seeds]` | no pixel of the sky clock (the checkpoint) over a wall's front face, a step or a low ceiling beside it, both modes (round 37c) | `cpscan: ok` |
| `chimtest.py [file] [lo hi] [seeds]` | round 48b's locked chimney, every kick shaft (floors 1-48 x 3: 236): climbed by a running Jump, a standing Jump or Up at the foot, then one Up a stance, every stance on its grid to the pixel, the Y landing 12 px past the lip with the standing landing; Up held gives one kick; Jump does nothing; Down at each stance lets go at once with a fall's damage; a rewind in mid-kick restores his own copies; walking in does not lock; no plant, kick or lock off a single wall elsewhere | `chimtest: ok` |
| `r38b_tests.py` | round 38b's play faults, one check each: the roof block and `P.inv`, the damaging drop's lip, a banner's rewind, the sand lift (no banner since round 49a, `sandfall` learned on getting off) and its top, the recruit's colour, the timed gates' waits | `r38b: ok` |
| `tellscan.py [file] [lo hi] [per=K]` | round 49b's tells: at up to K spots a floor of each kind (reach, edge, stakes, flask, low) none before 0.5 s still, full by 1.2 s, the pose changed, the weight 0 the frame Grab is held and the pose back 0.35 s later, P.x/P.y/state identical with `TELL.off`; none while he moves; no spot in a wind zone (none there by design) | `tellscan: ok` |
| `wearscan.py [file] [lo hi] [seeds]` | round 49c's wear marks and bones (floors 1-48 x 3): scuffs on every wall run up and nowhere else, drawn inside its face; grooves on every cell of each block's track and nowhere else, drawn inside the floor's top face; one set of bones a kind at the first trap of its kind by the route's order (its own list of the traps), every kind on a floor with the trap; on a route tile every pixel behind his walking line and under 6.5 px | `wearscan: ok` |
| `hinttest.py lo hi` | round 49a: no banner while the bot plays a floor, the moves it uses learned (`S.learned`), and at every remote plate the glance (one when its gate is out of view, none in view or twice, he stays in view, the view goes toward the gate and back, the timer at its rate); floor 1 the old-save migration | `FAILURES 0` |
| `sawceil.py lo hi [seeds]` | no saw under a ceiling at his height: each one turned into spikes is tiptoed, and the bot plays its floor (round 38c) | `sawceil: ok` |
| `layerscan.py lo hi [classic]` (by hand) | nothing in the corridor drawn over the front plane: each kind drawn and left out, the faces' and lips' pixels unchanged (round 39, `dev/docs/layers.md`) | `layerscan: ok` |
| `lampscan.py`, `slabscan.py`, `sandshaft.py`, `wellscan.py`, `figscan.py` | lamps keep clear (round 19); a slab slides up into stone (25d); every sand lift in a shaft (26e); the wells' sand (21b); the body's poses against v69 (round 23; only where `hk_v69_release.html` is) | `ok`, `slabscan: ok`, `sandshaft: ok`, `ok`, `figscan: ok` |
| `hillscan.py lo hi [seeds]` | round 43's heaps and drifts: only on a run's plain floor (`flat` segs, never `breathe()`'s padding), off timed stretches, the chase and fighters' ground, a heap open above, sizes, themes; at least one a floor from floor 3; counts and the time they add | `hillscan: ok` |
| `hilljump.py [file] lo hi [seeds] [step=N]` | round 47a: no jump onto a hill: running (every 4 px 2-122 px before its foot), standing (2-50) and from on it, by the game's physics; no flight but the low leap lands on or past a hill's foot or leaves the floor on one, no crossing beats its pace by over 0.1 s, no crawl enters one | `hilljump: ok` |
| `windscan.py lo hi [seeds] [nopush] [noease]` | the wind (round 44; round 45c's placement by openings): every zone on headroom over plain floor or a one-storey gap he jumps, every seg there calm or a gap jump and no other within a cell, off timed stretches, the chase, fighters' ground, doors; against the run; 3-8 cells; gusts only from floor 7 with the peak by band, a lull of 1.8 s or more; a steady zone over a jump made at its strength; he stands in every gust 9 s and stays in it; a death eases a zone to 0.6, a rewind keeps it, a second death 0.3 | `windscan: ok` |
| `courtscan.py lo hi [seeds] [nodrown]` | round 45's courts: 4-8 cells of headroom under stone (a light well 2), 7-8 a floor from floor 3, none on 1-2, never two in view (3 rows, 14 cells), none by a lift or door, kinds by theme, every one-storey spiked pit inside a court a pool (and every pool one), no window, arch or breach beam, own opening, wall lamp or hanging left inside one; a walk off a pool's coping drowns him at its surface; each court's two jambs of its theme's kind, 3 cells open between them, none intact beside a breach | `courtscan: ok` |
| `shadowscan.py lo hi` (release) | no figure's lamp shadow on what stands before the back wall, Torchlight (round 38a) | `shadowscan: ok` |
| `beamjag.py [file] [lo hi]` | no staircases in the sky beams (round 46a, rules S1-S7): static (highp where world positions are read, no `NEAREST` on the beams' textures), then every theme at every hour and the forced cases (low ceiling, floor shadow, blocker, prince, sand in a beam), both modes, `GLP.rs` 1, .75, .5 and Battery saver | STEP <= 0.012 (0.03 saver), `beamjag: ok` |
| `heapscan.py [file] [lo hi] [seeds] [torch\|classic\|both]` (release) | heaps and drifts are opaque solids (round 46b, `dev/docs/layers.md` R5-R7): each hill's drawn pixels (the frame with it less without it, eroded a world px) unchanged with the back wall's art flattened, the sky beams, the lamp shadow or the relief off, both modes, the bloom held out; floors 3-48 x 2 seeds in four GPU jobs | `heapscan: ok` |
| `solidscan.py [file] [lo hi] [seeds] [torch\|classic\|both] [per=K] [things=]` (release) | the other solids are opaque too (round 46c, layers.md R5-R7): a pushed block, a fallen roof block laid down, a court's jambs, a lift at its foot, the sky clock: drawn pixels (inside its own box, a lift's shaft back left out) unchanged with the wall's art flattened, the beams (not the clock), the lamp shadow or the relief off, both modes; floors 1-48 in four GPU jobs | `solidscan: ok` |
| `contourscan.py [file] [lo hi] [seeds] [torch\|classic] [kinds=] [per=K] [nofigures]` (release) | the contour rule (rounds 46c, 46d): no prop's or figure's edge a fixed near-black ink; each kind's edge pixels (a world px in from its outline) under 60 are within 40 levels of `selOut` (k .45-1.15) of its fill 2-3.5 px in, under 2% failing a view (and 80 px); Classic, floors 1-48 in four light jobs; the figures (guard, snake, the prince standing clear of walls) judged alike since round 46d | `contourscan: ok` |
| `viewscan.py [file] [lo hi] [seeds]` | one horizon per storey (round 47b): a window, an open arch or breach and a court on one storey place each layer of the view at the same screen y (the camera at rest and 40, 100 px over and 40 px under it), and the court's own art on the windows' horizon | spreads <= 0.5 px, `viewscan: ok` |
| `panscan.py [file] [lo hi] [seeds]` (release) | the courts' layers at their true depths (round 47b): each court layer alone panned 32 px, every band at its f within 0.01 (the floor's rows at theirs), the theme's view in its bays no nearer than the far side; every theme and hour, Classic | `panscan: ok` |
| `doorscan.py lo hi`, `openscan.py lo hi`, `tilescan.py lo hi views=2` (release) | no wall art over a doorway (round 15), a window, gate or lift mouth (16c), a floor tile (35c), both modes | every count 0, `tilescan: ok` |

Run by hand, not in `suite.py`: `layoutcmp.py` (layouts identical against a release, for look-only rounds; a generator round differs on
purpose), `layerscan.py` (about 4 min a floor in Classic here), `stairscan.py` (about 3 min a floor here), `beamwall.py`, `beamshot.py` and `wgl_cmp.py` (compare two builds' pictures),
`swingfeel.py`, `bench.py` (measurements), and each round's `egyptrNN.py` pictures.

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
Lighting mode (v63, owner): only the player switches between Torchlight and Classic (Graphics; Torchlight also needs Graphics > Lighting on, `shaderOn()`). Slow frames only scale Torchlight's
scene down (`GLP.rs` 1, .75, .5), and only when two 2 s windows in a row average over 38 ms (v65, owner; was 18.5); they never switch to Classic. It steps back up one level after three 2 s windows with no
dropped frame (`UP_MS` 17.2 ms); a step up that turns slow again within 10 s doubles the windows the next try needs (up to 30), reset each floor. A missing or lost WebGL context still falls back to Classic (`glKill`),
as the screen would otherwise be black; `glauto.py` checks this, and that windows between 18.5 and 38 ms keep the full scale (round 16d).

Pictures: `forkshot.py out.png n seed [index]` draws a fork for a look; `chambershot.py` and `liftshot.py` do the same for chambers and lifts.

3. Commit as `vN: what changed`, push to `main`.
4. About two minutes later, check that https://daniel-gheorghian.github.io/hourglass-keep/sw.js shows `hourglass-keep-vN`.
5. Copy the source to `dev/tools/hk_vN_release.html` as the next baseline.

## Rules the owner has set

- Levels stay fully generated: no hand-made levels or rooms.
- A drop that costs health must be worth it and must look like one (owner, 2026-10-14). It has its own look, made from the tile
  type (`hurtdrop`: a ragged, broken lip with nothing to grip, a darker shaft, a pile of rubble on the floor it lands on), never
  like a spiked pit or a plain gap. The generator keeps one only if it skips at least one landing with its obstacle or guard and
  saves 25% of the chamber's route by `estPath()` (a fork's long way by `forkWorth`: its tiles x 0.34 s + 4 s) and at least 10 tiles of
  walking; otherwise nothing is placed.
  Route length is counted along the safe way and the bot always takes the safe way; `forktest.py` and `hdtest.py` take the
  damaging one.
- A change must not make floors shorter or remove the plain floor left after each trap (`breathe()`).
  Check with `metrics40.py` whenever the generator changes (its argument is the baseline release, default v39, the standing reference
  of the trap density rule G1; `metrics39.py` is the old v38/v39 comparison).
- Changes to feel or level design are usually asked for with research first: how the Prince of Persia
  games (and other games) handled it. Report what a change was based on, with sources.
- Contours and accents (round 46, owner: "as a rule, if you add contours or accents always use a darker shade of the pixels that are closer
  to the edge or lighter if light hits it - with some tinting of course"; "For the outline rule: apply it everywhere"). An edge, seam or
  accent line is never a fixed ink: it is the fill on its inner side at the line, darker and moved toward the theme's shadow tint,
  `selOut(c,k) = mix(c, theme.lo, 0.28 (1-k)/0.45) k` (k < 1), or lighter toward the light's tint where the key light (`keyLight` sx) or
  light from above falls on it (k > 1, toward warm white by 1.5 (k-1)); opaque. k .55-.65 a silhouette edge in shade, .68-.75 an inner groove
  or seam, 1.05-1.12 a lit edge, .42-.5 a hole's rim or a void's edge in a solid. `selOut(c,k)` takes `[r,g,b]`, `selC(css,k)` a CSS colour
  (cached per theme tint, colour and k: nothing allocated a frame). Near-black stays only for real holes, slots, voids and interiors, the
  dark, the HUD; translucent darker marks (wear, cracks, grit) may stay; where a thing meets the floor the darkest accent is a contact
  shadow, not a line. Every prop and the world's edges since round 46c; the figures since round 46d (the prince, the robbers and the
  captain, the skeleton, the snakes, both levels of detail: each outline `selC` of the shaded fill at the line, `FIG_K` .58; seams and folds
  .62-.84, the eye and kohl the skin's deepest shade .42, lit edges 1.12-1.15; the silhouettes, `o.mono`, unchanged; the dark's jackal stays
  black). `contourscan.py` checks it (rendering.md "Contours").
  Round 46c also extends round 46b's solids (layers.md R5-R7) past the heaps: a slab that is down (portcullis, lift and sand lift mouths),
  a fallen roof block lying, a pushed block, a lift's platform and paternoster slabs and a court's jambs take the scene alpha mark in
  Torchlight (`solidMark`, `jambMark`, `HILL_A` 253: the composite leaves the sky beams' S and M passes off them, `hlGate`); Classic cuts
  blocks and lying roof blocks out of the haze (`rySolids`, `RYSO`); the relief is rubbed off the sky clock (`glRelClock`) and the lifts'
  ropes (`glRelLifts`); the slab's groove up the back wall is opaque. Round 47e (the release suite on round 47d: solidscan's relief on a
  lying roof block 6.3% on floor 23, on the clock 0.63% and 0.86% on floors 24 and 47): the rubbing missed parts drawn live on the floor
  round them, the pedestal's rubble chips (`drawHgPedestal` records their boxes, `hgChipsOf`, a WeakMap a checkpoint; `glRelClock` rubs
  them) and the lying block's two sand heaps and wear chips (`glRelRoofRubble`: `egHeap`'s cone in a trapezoid, `wearRubble`'s stream
  replayed); v88 had the same specks (3.6%, 0.18%, 0.44%) and round 47c's brighter ambient took them over the line; now 0. `solidscan.py` checks them; `LIFT_DBG.noback` leaves a lift's shaft back and counterweight (L1) out of its frames. Pictures
  `egyptr46c.py old.html new.html [outdir]` (r46c_props_<mode>.png: each prop changed, three themes and hours, v87 | 46c at 3x;
  r46c_phone_<n>.png).
  Round 46d's pictures `egyptr46d.py old.html new.html [outdir]` (r46d_figs_<mode>.png: the prince standing, running, hanging, crawling and
  on guard, the four ranks on guard, the skeleton and a snake, on a dark stretch and by a lamp on floors 10, 22 and 34, v87 | 46d at 3x;
  r46d_lowdetail.png; r46d_phone_<n>.png).

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
- Forks (floor 6 on): a switchback gets one of four forks (which switchbacks get one: `lrng`, `hash2(seed,6151)`; the kind and its
  build: its own stream `frng`): 1 a guard on the short way, traps on
  the long one (PoP1 level 2); 2 a damaging descent beside the long safe way (PoP1 levels 5 and 7); 3 a short dense way against
  a long easy one (Unexplored); 4 a one-way damaging hole, one in five with a grating and a flask behind a violet gate for
  whoever goes the long way. The short way is a chamber of the turns' own moves cut under the upper run (`forkChamber`); its
  bot actions are taken out of `L.path` and kept in `L.forks[i].sc`. Floor length is counted along the long way.
- Oatmeal spice (`featFor(n,seed)`, own stream; the move family from floor 3, the puzzle and obstacle families from floor 4; recorded as `L.feature`): each floor features one family of vertical
  moves (plain steps, collapse, jumps, banners and kick shafts, lifts), one of puzzles (slab, side passage, alcove, timed remote
  plate, double) and one landing obstacle; the featured family is weighed up until it holds about half of its menu (`randKits`,
  `puzzlePick`, `remoteRoll`, `OB()`), its kits are tried first, and the extra obstacle weight comes out of plain floor so trap
  counts do not rise. A floor never repeats the families of the floor before it (the walk runs on the game's seed). Rare flags
  (one floor in nine, from floor 4, never two in a row): tower (lifts everywhere), rotten (collapses and loose floors), barracks
  (many more guards, fewer other traps), longway (forks are kind 4 on floors 6-9, half kind 3 and half kind 4 from floor 10, a grating on 7 in 10 kind-4 forks; a kind that fits
  no kit falls back through `lp.order` to kinds 1 or 2), maze (gate puzzles chained
  back to back). `window.__FEAT={flag,move,puzzle,obstacle}` forces them in tests; the card between floors names a flag.
- The gold flask's cue (round 17, owner): where the climb or drop to a secret passage's gold flask (`L.secret`; or an alcove's gold
  flask) starts, a few small gold four-point stars twinkle on the lip's top face along its edge in depth (`secretCues`, found once per
  floor from the tiles and kept in `L._scue`; `drawSecretCue` in `drawDynamic`): an ascent on the ledge he grabs, lifting a little; a
  descent on the floor edge he hangs from, slipping toward the hole. Gone once the flask is taken. Look only, both modes, no allocation a
  frame (the hint `secret`/`secretdn` went in round 49a: the stars are the cue). Pictures: `egyptr17.py`.
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
  until `shaft` is learned, then 0.65; round 48b: nothing learns it now, so 1 but for saves that learned it before; the zigzag on the chimney's stances); the swing's throw while `P.swRdy` (`jsSwingPath`, the release's own numbers: lands within ~7 px);
  the jgrab jump only until `jgrab` is learned. Not on gap jumps, lifts, banners, hurtdrops or secrets (clutter, or against their look).
  A new place is one entry in `jetPlaces` and one call. Pictures: `egyptr18.py`; videos before/after `egyptr18c.py`.
- Lamps keep clear (round 19, owner: "sometimes lamps or torches are placed just like that"): a lamp burns only where both cells beside
  it are plain floor (no wall face or step, ledge, gate, banner, bar, pendulum, lift or lift plate), no lift shaft is beside it and no sky
  clock or door near (`lampClear`); `lampsClear` (first in `settleLights`, no generator stream) moves one that is not along its row to the
  nearest such tile within 6 (3 from another lamp), else removes it from `L.torches` (no scar, no fallen lamp; a `broken` lamp is
  `settleLights`' own case, on worn wall); replacements for fallen lamps use the same rule. `lampscan.py`
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
  Rows of three or more (round 26d, owner: "more organic and less mechanically domino. On two columns of sand it works, on more than two it
  doesn't"; `g.org`, n >= 3; rows of two are drawn exactly as in 21b): the level sags over each open outlet (`g.sa`) with a low swell (`g.nz`),
  craters, level and heaps are joined by soft max/min (`wSmax`, `wSmin`: never steeper than either), a crater is a funnel (`WELL_FL`: the
  angle of repose at the throat, flatter outward), each outlet is off centre (`g.ox`) with its own wall slope (`g.sl`) that slumps flatter in
  four avalanches of its own (`g.sc`, only ever flatter, so the sand never grows back), the heaps between outlets are low rounded mounds
  (`g.rs`). Each slab's lean, onset and tip-on (`wellTip1`), its crack (`wellCrk`, 85%: `slabCrack`, two uneven pieces, the near one turning
  on the crack), the fall's lag and turn, the unequal halves of the first slab (`slabHalves`'s `q`), the sand pouring through its seams before
  it goes (`wellPour`), the tongues sliding down the crater walls (`wellSlides`) and the dust from each hole are seeded hashes of its column
  and row (`wellH`): no stream, rewind-safe. Look only: every break time, hit box and the bot unchanged. wellscan also checks the rewind on the
  longest row. Pictures `egyptr26d.py`.
  No sand in a corridor (round 30, owner: "a corridor above another corridor doesn't use sand tiles, but instead regular tiles"): a cracked
  slab beside another skipped its side test on every row, so in a run of five over a lower corridor the three inner slabs leaned on each other
  and stood as a column of sand down through his corridor (floor 9 seed 802, slabs 140-142 on row 16 over the corridor on row 18). `looseWell`
  now tests the whole run of slabs at once: each slab's pit (its k storeys down to its floor) must be walled on both sides on every row down to
  that floor, by stone or by the pit of a neighbour of the run that is itself a well and reaches that row; a slab that fails takes its
  neighbours' support away until none fails (the rest take the corridor look). Tiles only, kept on each slab's feature (`f.wl`): look only.
  `wellcorr.py [lo hi seeds]` (in suite.py; floors 1-48, 3 seeds) must print `wellcorr: ok`: well groups with a side open beside the pit 40
  before (all walkable corridors), 0 after; groups 2096 to 2056 (slabs 3003 to 2883). Pictures `egyptr30.py` (r30_sandcorr.png, v76 | 30).
- Arms up (round 19, owner: "a hump"): `torsoG` narrows the back near the shoulders (up to 1.3 px) and the raised arm rises from the
  back of the shoulder, so the back line runs from the waist into the arm. Pictures for round 19: `egyptr19.py`.
- The prince's body and poses come from motion capture (round 23, owner: "Start from those clips and build the athletic teen prince body
  and scrap the current skeleton and proportions"; rule and tables in `dev/FIGURE_SPEC.md`; rounds 22b-22d's ANSUR fit and PoP-kid fit are
  superseded). The CMU Graphics Lab Motion Capture Database (mocap.cs.cmu.edu; cite "The data used in this project was obtained from
  mocap.cs.cmu.edu. The database was created with funding from NSF EIA-0196217.") gives the bones (subjects 09, 13, 14, 16) and every
  pose; ANSUR II's 17-20 year old men give the trunk's lengths and depths (BMI under 23) and the limbs' girths (all 422); the head is 1/6.5
  of his height (6.57 measured, 7.98 px; real is 7.7 heads, the 1989 kid 5.86) so the face reads at 52 px. `dev/tools/r23poses.py`
  generates the source's block between `// <R23-MOCAP>` and `// </R23-MOCAP>`: `R23B` (LEN: th 11.4, sh 13.8, to 14.0, nk 3.5 (4.5 before round 23c, 2.5 in 23c), hd 3.37,
  ua 8.2, fa 7.7; standing 51.5 px (52.4 before round 23c, 50.5 in 23c) against v69's 53.0), `R23D` (the drawing's widths: BQ/Fo/Bo, NJ, limbs, foot, kilt; robbers 1.15 times
  as broad), `MCP` (single poses) and `MCK` (16-key run and walk cycles with each key's foot clearance `cl`, the crawl, the drink's
  keys, the swing's 12 phase bins). Never edit the block by hand. A pose is the game's angles measured from one clip frame in the side
  view of the body's facing (`dev/tools/mocap.py`: ASF/AMC parser, forward kinematics, `sheet`/`strip`/`video` to look at a clip); its
  placement (air, hy, sw, rot, kn) and timing are gameplay's and unchanged. Hands that hold something (ledge, floor, hilt, flask, the
  fight's sword) go to v69's places (`hold`/`hb`/`mh` with the grips `gFx,gFy,gBx,gBy,gMx,gMy` from `r23grips.json`, read from v69 by
  `r23grips.py`); where the new arm cannot reach, r23poses.py turns the trunk toward the grip and logs it; `climbFrame` puts the hands
  on the lip and then on the floor. To add or change a move: find a clip in `dev/tools/ref/cmu/index.tsv`, fetch its .amc/.asf into
  `ref/cmu/` (gitignored), look with `mocap.py sheet`, add its line to `SEL` (or a cycle in `build()`), run `r23poses.py`, then
  `figscan.py` (must print `figscan: ok`: held hands, no crown over v69's standing crown, nor over v69's own in the crawl and low leaps,
  soles on the floor, hands on the bar and at the mouth) and `egyptr23.py moves` (clip | new | v69). Pictures `egyptr23.py`
  (body, moves, game, clips).
  The running jump's stride (round 26c, owner: "the stride is too large ... for smaller gaps looks silly"): every running jump flies the same
  arc on a level floor (97.6 px), so the flight is drawn for the distance the jump is for: `jumpSpan` at take-off (the arc to the first floor or
  wall, or a pit/trap's far lip + 12 px), `P.jS` = (D - 48) / (level arc - 48); `leapPose` blends `MCK.leap` S (09_01's stride flight) and L
  (49_04's leap, v72's arms) over 9 keys by the arc's phase (`MCK.leapLow` pitched for the low leaps). Look only; `egyptr26c.py`.
  (Round 32 supersedes the flight's keys: `flightPose` blends S into 127_21's long jump, `MCJ.D`, by 0.3 + 0.7 s, not 49_04's L; `P.jS` is
  still the distance's measure. `leapPose` stays for the tools. Round 34 puts the running flight back on `leapPose`'s S and L.)
  The jump's height (round 27a, owner: "he moves up too much"): the running arc rises 25.8 px (half his height, 0.88 m at 1.75 m; the game's
  gravity is 2.4 g; PoP1's runjump rises 14 px of a 63 px storey, an elite long jumper's centre of mass about 0.5 m) and he was drawn on it.
  Now he is drawn on a lower arc of the same shape: `P.yo` = (1 - `P.jK`) times his rise over the take-off floor (0 at take-off, touch-down and
  below the take-off level, so grabs and landings are where the arc puts them). `jhK` at take-off (in `jumpSpan`): the drawn top `JH_S` 8 px
  (s 0) to `JH_L` 14 (s 1; round 32: 6 and 13, the dive's pitch keeping the head down and the legs tucked showing the arc; the feet tested
  as `flightPose` draws them, turned with the figure), raised until the drawn feet clear each spike needle and saw blade (where the blade is at that moment) as on the
  full arc or by `JH_M`; k 1 (the full arc) where the arc meets a wall standing over the take-off floor, lands higher up or passes a swing bar,
  and for the standing jumps. Look only: arc, P.y, hit box, reach, grabs, bot, estPath unchanged (the arc's reach is 2 vx vy / g, so lowering it
  would change play). `egyptr27a.py` (r27a_jump.png, r27a_jump.gif).
  Muscle bulk (round 23b): `MUS` in r23poses.py is the upper arm's girth over ANSUR's median (round 23c, owner: "1.28 is fine": the game
  draws 1.28; 1.0 is round 23's look); every other width grows at its own rate per unit of it (`GROW`, from ANSUR II's lean 17-20 year olds by muscle
  percentile; `TRUNK_G` lays the trunk's growth in front or behind), joints, bones, skeleton, poses and hit boxes never. The block also
  carries the levels `R23MUS` [1, 1.10, 1.18, 1.28] and their tables `R23DV`; `window.__MUS` before load or `__HK.setMus(m)` draws one
  (pictures, tests); above 1.0 a faint deltoid V and pectoral border (`RD.mh`) and the calf's growth behind the shank (`RD.cb`). Pictures
  `egyptr23b.py` (bulk, game); a new level must pass figscan and lowceil with `__MUS` set.
  Arms up, held hands (round 26b, owner: "a hump of sorts ... reduce with 1px the back"): a held hand's upper arm is drawn where skel's
  two-bone solve puts it, so the trunk's arms-up shaping (`ra`), its twist and `armG` read the arm as drawn (`armDrawn`), not the clip's
  aF/aB (the hang's 1.81/1.98 vs 2.69/2.83 drawn had shaped the trunk for arms half down since round 23: the standing back behind raised
  arms). And r23poses.py's `BO_CUT` takes 1 px off the arms-up back (Bo) at its fullest (U .62-.76; 0.55 and 0.2 above; scaled (m-1)/(MUS-1));
  arms down (BQ) and the robbers (R23DR) unchanged. Picture `egyptr26b.py` (r26b_back.png).
  Arms down, no hump (round 28a, owner: "I don't think the upper back sticks out as much in a muscular teen seen from the side"): round 24's
  growth behind the trunk kept its full share up to the shoulder joint (BQ 4.8 px behind the spine at U .62-.96, 4.5 at the joint: fullest
  0.7 px under it, 2.1 px behind the nape) and the deltoid's root grew round its centre (its cap 0.8 px over the chin). r23poses.py's `BT_TOP`
  keeps 90/80/67/51/57% of the growth behind at U .62/.76/.88/.96/1 and `TR_K` 0.6 of the trapezius' bulge on the slope from C7, so the back
  rounds over from the blades into the trapezius (behind the nape 1.6 px, on the seat's line, fullest 3.2 px under the joint); `RD.dd` (`DD`:
  the half-width the deltoid gained over 1.0, 1.56 px at 1.65) drops its root down the humerus times cos of the arm's angle (arms down only),
  so its cap stays under the chin. Bo is built from the full BQ (the arms-up back is 26b's); robbers unchanged. Picture `egyptr28a.py` (r28a_back.png).
  Heroic range (round 24, owner after v70: "Still too lean: make it bulkier"): the game draws **MUS 1.65**, the middle of three stylised
  levels past the natural near-limit `NAT` 1.28 (1.45, 1.65, 1.85 in `R23MUS`; v70 drew 1.28). Up to NAT the measured `GROW`, past it
  `GROW2` (deltoid 1.2, arm and above the elbow 1.0, forearm 1.15, calf 0.95, chest 0.85, lats 1.0, thigh 0.8, waist 0.06: each level adds
  about 0.5-1 px at 1x to every muscle, the waist stays) and `TRUNK_G2` (more of the upper back behind, so it runs nape to lats as one slope,
  no hump); `RD.du` moves the biceps' point down the arm past NAT (the deltoid tapers); `RD.mh` 0.76. Robbers never grow with him: they draw
  `R23DR` (v70's 1.28 table; `drawFigureHD` swaps it in for any figure that is not the prince); at 1.65 the prince's deltoid, arm and chest
  pass a robber's, the robber keeps the heavier waist. Pictures `egyptr24.py` (bulk, game).
  The neck (round 23c, owner: "make the neck 2px shorter and keep everything else as is"; round 23d: "Too short, one pixel longer"):
  `NECK_CUT` (1.0 since 23d; 2.0 in 23c) in r23poses.py comes off ANSUR's shoulder-joint-to-chin span (4.0 to 3.0 px; `LEN.nk` 4.518 to
  3.518), so the head sits 1 px lower on the same body in every pose (standing 51.5 px); the body's neck points (NJ th, c7, bk, nb), widths,
  poses (the low leaps' lean is found with the old neck), grips and hit boxes are unchanged; the drinking hand follows the mouth (`mh`).
  The nape `NJ.km` comes down `KM_DROP` (0.5, half the cut: 4.61 to 4.11 along the neck's axis; all the way it would sit 0.15 px over
  C7 and fold the back edge). Pictures `egyptr23c.py`, `egyptr23d.py` (23b | 23c | 23d).
  A supple run (round 25a, owner: "The prince is somewhat stiff when running. Humans are somewhat flexible"): the side view kept only ten
  angles, so the trunk was one rigid line, both arms hung from one point and the feet were flat. r23poses.py (`extras`) now also writes, per
  run and walk key from the same clips: `sb` (the thorax's pitch less the pelvis's, 2 to 12 degrees, drawn as the spine's curve: the torso's
  control point gets -LEN.to/2 tan(sb/2); the chord `lean` is unchanged), `soF`/`soB` (each shoulder joint fore and aft, +-0.78 px: the
  girdle's counter-rotation, 20 degrees peak to peak; the arm moves with it, and `sm` 1 fades the drawing's swing-driven shoulder shift),
  `fpF`/`fpB` (the foot's pitch from the clip's foot-flat angle, +6 to -114 degrees: the foot turns about the ankle `R23B.ah` 1.95 px up the
  shank; `cycPose` puts the hip over the turned foot's lowest point `footLow`, so he rises onto the ball at toe-off as the clip does). The
  kilt's hem trails the thighs by `KH_LAG` 0.035 of a stride (`khF`/`khB`, set in `runPoseHD`: a pure function of the phase). These keys are
  0 in every other pose; a part stride (stairs, push, pull) keeps the feet flat. Measured but too small at 1x: the hip joints' shift, the
  pelvis's drop, the wrist. Numbers and pictures `egyptr25a.py` (measure, keys, gif); see `dev/FIGURE_SPEC.md`.
  (round 25b, owner) Jumps move both arms together: the standing jumps (jumpS, jumpLowS) are 13_11's forward jump (arms swung forward in
  flight; 16_05 held the elbows bent by his sides, one forearm read as a raised arm). Crawling he looks ahead, never at the floor: the neck line
  `CRAWL_NECK` and the skull's own pitch on it, pose value `hp` (`CRAWL_HP`; drawn by the head, eye and hair only, 0 in every other pose).
  Pictures `egyptr25b.py`.
  No stiff moves (round 25f, owner: "check all his movements for stiffness and make adjustments based on research"). The rule for every move:
  overlap (parts arrive at different rates: `followPose` with `PKR`, the arms, forearms and head after the trunk, the legs too in the air; only
  toward held poses and short transitions, `LAGM`; clip cycles and held grips at the full rate); anticipation and settle around events,
  measured where a local clip has one (`MCK.set_land` from 16_05, `MCK.set_stop` from 16_08: g toward the clip's peak plus each angle's residual,
  `settlePose`, keyed by the time from the event, `P.stK/stT/stS`), else a pure function of that time (`turnSettle`, the hang's pendulum swing
  about the hands `HG_*` in `livePose`, the fall's limbs); round 25a's extra joints where the clip shows them. Look only: never a timer, grip,
  hit box or contact. The standing jump crouches with both arms back (`PS.jumpCrouch`, 13_11; round 32: a keyed wind-up, `prepPose`); the crawl's face is 7 degrees under the
  horizontal (`CRAWL_NECK` 0.64, `CRAWL_HP` -0.52). Audit table and sources: egypt_themes.html round 25f; pictures `egyptr25f.py`.
- The jumps (round 32, owner: "The current one is too stiff too mechanical"; after the research: "Do everything; keep the motion capture body
  and borrow PoP's structure"). Measured on v77 (`egyptr32.py --measure`, r32.json): no gather or push-off, and he left the floor from any stride,
  so in 14 of 40 take-offs over the run's phases the thighs crossed in the air (scissoring: the leap's first key had the other leg forward); the
  trunk upright through the flight (lean 2-12 degrees) while the whole figure rode the arc; the standing jump one held pose (4 of 26 air frames
  still); a 40% step toward the landing pose in one frame at vy 60; the arms in lockstep (their velocities correlated +1.00 in the two-tile jump
  and the standing jump); the take-off stretch dead (`updActorLook` read vy on a frame P.y had not moved); the lead knee straightening at
  contact (43 to 23 to 16 degrees: the settle began at standing) and the hip dropping 0.8-1.8 px; the run back from a stop at 35 px/s; a frame
  with no drawn motion at every launch. PoP 1989 (SDLPoP `seqtbl.c` runjump and standjump, `seg006.c` frame_table_kid; Mechner's Apple II
  `SEQTABLE.S`, `FRAMEDEF.S`): the running jump gathers tall and narrow (frame 38), drives the free knee up (39), dives (the trunk near level at
  the apex, the legs split; the head within 6 px of its running height while the feet rise 14), lands in a crouch with the arms trailing and runs
  on; the standing jump winds up (a deep bow, both arms back, held two ticks, 0.58 s), launches along one diagonal from the rear toe to the
  reaching hands, flies flat out and lands in three ticks of squash (the head 16 px down, a small recoil). The rule now, PoP's structure on the
  clips' bodies: new keys come from CMU clips through `dev/tools/r32jump.py` (the block `// <R32-JUMP>`, `MCJ`; never by hand; it reads the BVH
  conversion with `bvh.py`, checked against round 23's ASF numbers within 1-4 degrees by `r32jump.py check`): 127_21 (run, jump, stop, run:
  `tk` the take-off stance f56-81, `D` the flight f81-129 (unused since round 34), `rl` the landing f129-177) and 13_11 (forward jump: `sw` the wind-up f150-240, `sf`
  the flight f240-289, `sl` the landing f289-349); `Dlow`/`sfLow` pitched by round 23's low-leap rule (`Dlow` unused since round 34). Shaped by hand on top (constants by
  `flightPose`): the running dive (`DV_*`: the figure turned forward by `rot`, the trunk further, the trail thigh back and the lead knee up, by s,
  as sin^2 of the flight's phase; `DV_K0` of it even for a one-tile hop; removed in round 34, below), the standing launch's diagonal and reaching arms (`SJ_TILT`, `SJ_ARM`)
  and flat-out flight (`DS_*`), the landing squash (`LD_*` on `landSeq`, x1.35 after a run; `LR_*` on a run carried through, `landRun`),
  peaking `LD_TP` 0.055 s after contact. Take-off: while Jump is pending (`P.jLe`, the lip) the run's drawn phase is steered over `ST_D` 40 px
  so the stance `tk` (the last `TK_D` 16 px) starts on the take-off foot, and the flight's keys are mirrored when the other foot takes off
  (`P.jMir`): no scissoring (0 of 40). Flight: `flightPose`, the near arm `ARM_LAG` behind and swinging through as the far one goes back
  (`ARM_SW`, opposed: +0.29 two tiles, -0.18 one; round 34 put the running flight back on `leapPose` and dropped `ARM_SW`), the hip on the feet's heights at take-off and touch-down; past the level arc an eased
  40% blend toward PS.land. The drawn x (`P.pose.ox`, `poseOx`, look only): the launch frame carries the run's step and the drawn speed ramps
  into the arc's (`OX_T3`); in the wind-up the feet stay where they stood while the hip goes forward over them, the flight takes that lead
  back (`OX_T2`); after a landing the feet stay planted 0.12 s, then the hip's lead eases back (the recoil). Followed with ease in as well as
  out (the follow's rate rises over 0.08 s in the wind-up and take-off, not at an impact); the take-off stretch reads P.vy. After: lead knee
  19-30 at the last air frame, 21-30 at contact, 77-91 three frames on (v77: 40-51, 22-27, 13-16); the head (its centre) 8.5-8.9 px down after a running landing, 8.7
  after a standing one (v77 under 1.2); no still frames (v77's standing jump 4 of 26). Gameplay: the standing jump's wind-up `JP_T` 0.28 s (was 0.1; 13_11's own drive from its deepest
  crouch to toe-off is 0.28 s, PoP's 0.58 s felt laggy for touch), and `estPath`'s `sjump` is 0.18 s longer (layouts unchanged on floors
  1-48, 3 seeds; 37 gates' timers longer); a running jump that lands on its own level (dist <= 40) with the way held and Grab not held runs
  straight on (`land`: vx kept at RUN, the stride carried on from the landing foot, phase 0 or 0.5), as PoP's runjump ends in the run; let
  go, he stops in the crouch. The bot lets go in the air (rjump, dashjump, jgrab) and stops as before; the chase (`dash`) and `saw` hold the
  way and run on (`sawSafe` simulates that). Checks: figscan (now also the keyed poses: no crown over v69's standing crown on the floor, no
  sole under it, the low flights under v69's low leaps), lowceil, stairscan, run2, p4bot, forktest, hdtest, metrics40. Pictures and numbers
  `egyptr32.py` (r32_jump.png: PoP | v77 | round 32 onions and strips; r32_jump.gif; PoP's sprites from ref/pop1/, local).
- The jump's drawn apex (round 33a, owner after v78: "the prince is raised too high, the arc of the jump has a too high apex. Compare to
  the original PoP animation"): measured on v78, the drawn crown rose 8-10 px over standing in a running jump, 15 in the standing jump (502 of
  1,189 jumps on floors 1-27, drawn on the full arc) and 21 in a running jump to a ledge (full arc). PoP 1989 (SDLPoP seqtbl.c runjump/standjump,
  sprites bottom-anchored at Char.y): the running crown at most 1 px of 41 over standing, the feet's rise a tick .21 .86 1 .21 of its top; the
  standing crown 7 px under standing, the feet 6 up. Now the drawn rise over the take-off floor is `D = k ap sin^2(pi t/T)` (`jhK`, `jumpYo`;
  sin^2 fits PoP's ticks, a parabola does not), its top `JH_S` 4 to `JH_L` 7 px running (round 34: 2.5 to 4, the figure upright), `JH_SJ` 3 standing; where the hands must meet the arc
  (a ledge's top passed coming down, a floor higher up, a swing bar: `P.jKe` from `jumpSpan`) the drawing rises onto it over the last `JH_RT`
  0.2 s (round 34: 0.16) instead of flying the full arc; spikes and saws keep round 27a's clearance (by k or a share `P.jKr` of the arc, whichever draws lower);
  D never exceeds the true rise. Crown over standing: running +8.4 to +3.6, standing +15.3 to +1.7, to a ledge +21.1 to +10 (at the catch); no
  jump draws higher than v78. What is left of the gap to PoP is in the pose (13_11's tuck against PoP's flat-out frames 24-25). Look only.
  `egyptr33a.py` (r33a_jump.png, r33a.json).
- The careful step (round 33b, owner after v78: "the tiptoe animation: research this also against the PoP animation"). v78 blended one pose
  (PS.step) in and out while P.x eased 13 px: the feet slid on the floor (7.6 and 11.0 px in one step, 21.4 and 46.9 px over four held steps),
  lifted under 1.2 px and never turned, and the arms moved together (0.97). PoP 1989 (SDLPoP seqtbl.c step1-step14 and testfoot, Mechner's
  SEQTABLE.S "step11 ;corresponds directly to filmed sequence"): a step-to in 12 ticks: weight on the rear foot, the lead lifted and reaching
  low, set down toe first (125-126), weight over it with the body 3-4 of 41 px lower, the rear foot carried through and set down beside it;
  short steps skip the widest frames; at the lip pressed again the toe tests the edge (frame 86). Now PoP's structure on CMU 139_29's sneak:
  `dev/tools/r33step.py` writes `// <R33-STEP>` (`MCS`: body keys, each foot's swing progress, clearance and pitch, the events, the hip's
  progress at each; never by hand). `stepPose` places both feet by two-bone IK where they stand (`tpLeg`: the foot turned about its ankle as
  drawn), so no foot slides; the events go where P.x's ease has brought the hip as far as the clip's (`TP_EV`); each foot lands toe first
  (`TP_TOE`); the trailing foot is carried higher (`TP_LB`); the hip dips in one bump (`TP_DIP`), lower only where the planted legs need it
  (`tpDrop`, a table made once a step); trunk, head and careful arms are the clip's; after the last step the stance eases to standing
  (`tipSettle`, P.stK 'tip', `TP_REL`). A step under `TT_D` toward a drop is PoP's test foot (`TT_*`). Steps over `TP_DMAX` (off a lift, aside)
  and edgeWalk walk by the distance. After: planted feet slide 0.1-0.6 px, the ball lifts 3-3.5 px, arms correlate 0.17. Look only: P.x (ease
  over `STEP_T` 0.3 s; PoP's step is 1.0 s, the clip's 0.65), reach, hit box, bot, estPath unchanged. Checks: figscan (the keyed steps), run2.
  Pictures and numbers `egyptr33b.py` (r33b_tiptoe.png/.gif, --measure).
- From the hang onto the hanging (round 33c, owner, floor 16: "the prince is hanging and we need a short animation that plays when the prince is
  transitioning from hanging to the slide down position"). Look only, drawn on `P.pose` after the follow (`handsIn`, right after `poseOx`), so
  shadows follow. Letting go of any hang (`HF_*`, `P.lgo`): each hand stays on the lip until `HF_R` (0.03 / 0.07 s), slips off with the body over
  `HF_S`, rides with the arms up `HF_H` 0.08 s, then eases to the fall's arms over `HF_W` 0.25 s, carried through `land`/`stand` when he lands at
  once (PoP1's hangfall, SDLPoP seqtbl.c: frame 81, arms up, 3 ticks; CMU 01_10: the hands on the bar 0.1 s after the hips start down, 0.05 s
  apart). Taking the cloth (`SI_*`, `P.slI`): the physics still snaps `P.x` to the hanging's middle; the drawn body carries the offset and swings
  in over `SI_T` 0.2 s (a decaying offset: Bollo, inertialization, GDC 2018); the hands go from where they are drawn to `PS.slide`'s grips, one
  first (from a hang the sword hand, from a fall the nearer), the other 0.06 s later, each over max(`SI_H`, 1.875 d / `SI_V` 300 px/s); the blade
  shows as the sword hand closes and sinks in to `SL_BLADE` (`slBlade`); the knees fold at `SI_RATE` 24 with the slide's overlap (`LAGM` slide:2).
  Gameplay: Grab held with Down in a hang over a hanging takes the cloth at once (before, he let go and caught the same lip again). Largest move
  in a frame, v78 to 33c: hands 15.2 / 22.0 to 3.5 / 3.4 px, head 9.6 / 9.1 to 3.6 / 3.2 px, the 9-9.5 px x jump to 0; the bot's frames
  identical, estPath unchanged. Low-detail figures do not draw the offset. Pictures and numbers `egyptr33c.py`.
- The running jump's flight (round 34, owner after v79: "The standing jump is fine, the running jump is not: him tilting his head and rotating
  like that is not natural. The previous movement was fine, except the apex"). v79 flew round 32's dive: the whole figure turned forward up to
  38 degrees (`rot`), the trunk to 59 and the head to 52 degrees forward of upright (lean + rot + head; the low leap 97 and 90), the trail thigh
  back and the lead knee up by hand, even on a one-tile hop, on 127_21's long jump keys. The running flight (rjump, low leaps, dash jumps,
  running jgrab) is v77's again: `leapPose`'s S (09_01's stride) and L (49_04's leap, v72's arms) by the distance `P.jS`, upright (rot 0; the
  head 12 degrees at most, the trunk 13, as v77's 13 and 15), the low leaps on `MCK.leapLow` with v77's hip height; `DV_*`, `ARM_SW` and
  `J32.D`/`Dlow` are gone (`MCJ.D` stays in the generated block). Kept from round 32: the stance `tk` and the steered phase, the flight mirrored
  by the take-off foot (`P.jMir`; 0 of 40 take-offs scissor, v77 14), the near arm `ARM_LAG` behind and the far one `ARM_LEAD` ahead (the
  opposed swing `ARM_SW` is dropped: on v72's raised arms it threw the near arm overhead), the hip on the feet at take-off and touch-down
  (`J32.S`, `J32.L`), poseOx, the eased landing blend, the landing keys and squash, running on. New: the flight eases out of `tk`'s last key
  (the lead knee driven up) over `LP_TK` 0.45 of it (not the low leaps), so the knee is not dropped at toe-off and a hop over spikes lifts its
  lead foot clear without a higher apex. Round 33a's apex is kept, its tops lowered for the upright figure (it stands about 1 px taller over
  the hip): `JH_S` 2.5, `JH_L` 4, the reach onto the arc for a catch over `JH_RT` 0.16 s. Crown over standing (bot, floors 1-27, seed 1;
  v77 / v79 / round 34): level running jump +12.2 / +3.5 / +3.5 (highest, over spikes and saws, +14.8 / +13.5 / +13.3), caught at the far
  lip +13.6 / +4.0 / +4.0, to a ledge +24.9 / +10.0 / +9.3, the low leaps (highest) +3.7 / +1.4 / +0.9 (their head 36 / 90 / 39 degrees forward, ducked under the ceiling as v77); the swing bar's catch +23.9 / +18.4 / +23.6
  (the dive had pitched the head down at the bar; the swing itself draws the crown to +27 within 0.2 s in all three). The standing jump's
  drawn poses (to 5 decimals) and the bot's frames are identical to v79's (`egyptr34.py --bot`, floors 1-27). Look only. Checks: figscan, lowceil,
  stairscan, run2.
  Pictures and numbers `egyptr34.py` (r34_runjump.png: v77 | v79 | round 34 onions and strips; r34_runjump.gif; r34.json).
- The running jump's tempo (round 35a, owner after v80: "again the jump, just the running jump: the prince hangs too much in air while jumping.
  Tweak the timings so it is shorter. The prince running speed doesn't match the running jump, the fact that the prince hangs too much in air
  breaks the tempo"). Measured on v80 (`egyptr35a.py`, the bot on floors 1-27, seed 1): a level running jump was 0.533 s in the air (32 frames;
  the arc 2 vy/g = 0.543 s) at 183 px/s, 1.83 times `RUN` (100): already faster across than the run, but 2.5 of the run's steps (a step 0.22 s)
  with the drawn apex only 4 px (round 33a), so he glided. PoP 1989 (SDLPoP seqtbl.c; 12 ticks a second, 14 x-units to a tile): runcyc1 is
  26 units in 8 ticks (89 px/s here, a step in 4 ticks, 0.33 s); runjump's frames 40-43 are in the air, 39 to 44 floor to floor is 5 ticks
  (0.417 s, 1.25 steps) and 36 units (82 px) at 2.2 times its run; its gather (frames 35-39) 1.6 times. Celeste (NoelFB/Celeste Player.cs:
  MaxRun 90, JumpHBoost 40, the air speed reduced back toward MaxRun at RunReduce 400 x AirMult .65) carries about its run speed across.
  Now a running jump (rjump, the low leap, dash jumps, jgrab, a run onto the swing bar: `P.jumpKind` 'run') flies the same path in `RJ_K`
  0.75 of the time: velocities over RJ_K, gravity and the fall cap 480 over RJ_K^2 and RJ_K (`rjK()` in stAir, `launch`), until he lands,
  grabs, catches a bar or kicks; `RJ_DV` (g STEP (1/RJ_K - 1)/2, 1.94 px/s on vy) puts the frames on v80's discrete parabola, so every 3rd
  frame is v80's every 4th and a level jump lands on v80's very pixel (97.6 px, frame 24 for 32). Level running jump 0.533 -> 0.400 s
  (PoP 0.417), 183 -> 244 px/s (2.44 x RUN; PoP 2.2), 2.4 -> 1.8 steps; the low leap 0.350 -> 0.267 s (212 -> 283 px/s); caught at the far
  lip 0.750 -> 0.567; to a ledge a storey up 0.500 -> 0.367; to the swing bar's catch 0.233 -> 0.183. Unchanged: reach (level 97.6 px, the
  low leap's 74.2 lands 75.4: its 21st frame falls between samples, +1.2 px), rise (hit box 24.2 px, low 10.6 -> 10.7), every landing within
  one frame's step of the arc as before (4 px of arc against 3), beamOverhead, jumpSpan's geometry, the run's speed, the take-off stance (by
  distance), the landing keys and running on, the standing jump (bit for bit: rjK() is 1). On the flight's clock too: P.jT and P.jKe
  (times RJ_K), JH_RT, the saw's blade in jhK and the bot's `sawSafe` (`__HK.RJ_K`, `RJ_DV`), the air follow's rate (/ RJ_K) and its
  0.08 s / 0.15 s eases; the swing's catch and the landing squash read the arc's own speed (x RJ_K: runCatch 0.73 -> 0.72). estPath:
  rjump -0.13, rjumpg -0.18, jgrab -0.13, swing -0.05 s (both paces, the time saved in the air): layouts identical on floors 1-48, 3 seeds
  (tiles, features, L.path, start and exit; metrics40 against v80 the same), 49 of 1,438 gate timers 0.1-0.3 s shorter. The chase is
  0.1-0.5 s quicker for the bot, the dark's speed unchanged. Checks: run2 (1-27, fight 5-10), primtest, hdtest, lowceil, figscan, forktest,
  p4bot, metrics40, swingtest. Pictures and numbers `egyptr35a.py` (r35a_jump.png: v80 | 35a on one clock with the run before and after;
  r35a_jump.gif real time; r35a.json).
- No wall art over a floor tile (round 35c, owner after v80: "wall decorations over the tiles"; screenshot: The Green Hall of Osiris, a cracked
  slab at the end of a ledge over a lower corridor, as on floor 18 seed 4418 cell 201,11). A tile drawn live (a cracked slab, a plank, a plate,
  xplate, lplate, closer, grating: `drawRoomStatic` leaves its cell to `drawDynamic`) has no slab in the room's picture, so the back wall's art
  (the arch posts, the dado's band, the frieze of the storey below) runs on under it there, and Torchlight's relief, which reads that picture,
  embossed it on the tile's top and lip. `glRelFloors` rubs the relief back over every run of live tiles in view, over exactly its top face and
  lip (`glRelQ`: a quad at full strength to its edges, which are the tile's own, so the wall beside it keeps its relief; over a sand well too,
  where `glRelWell`'s soft box left the corners half rubbed), and over a pushed block (`drawBlock`: front, top, side; its cell is drawn from
  `blockUnder`, so the open hall's posts behind it were embossed on it); the relief pass now takes `GLREL_Q` 160 quads (64 before). And the cracked slab's
  lip crack was a lone '>' (out 1 px and back 1.5, away from the top's cracks) that read as one of the wall's chevrons: its two lip cracks now run
  on from where the top's cracks reach the front edge, near straight. Classic drew no art over the tiles. Look only. A new tile or block drawn
  live over the room's picture needs its rubbing in `glRelFloors` (`glRelLive` for a tile type). `tilescan.py [file] [lo hi] [views=K] [sheen]` frames up to K live tiles a floor (seed 4400+n) and
  compares every floor tile in view, live or plain, top face and lip, with the frame drawn with the back wall's art flattened and its openings
  left open (`EGP.noart='atop'`); must print `tilescan: ok` (floors 1-48, 2 views a floor: 154 of 2,064 tiles before, all Torchlight: 36 of 41 cracked slabs over
  a corridor, 61 of 64 over a well, 19 of 20 planks, 37 of 45 plates of all kinds, 1 block; Classic 0; 0 after). Torchlight's wet sheen (round 31) is
  off in it unless `sheen`: it mirrors lit wall art (a pale post in a sky beam) onto wet floors by design, a reflection. Pictures `egyptr35c.py`
  (r35c_wallart.png: v80 | round 35c, both modes).
- The slicer's jaws (round 37b, owner after v81, Torchlight, the Blue Chambers: "The shadow of the prince over the guillotine jaws. Also the
  guillotine jaws needs to look more metallic"). The jaws (`drawJaws`) are two plates standing across the corridor's depth (`plane`), in front
  of the back wall, but Torchlight's lamp shadow (`glShadow`, effect mask r) was carved only out of walls, floors and low ceilings, so his
  shadow (and a guard's) was painted across their face as if they were the wall; and the relief, which reads the room's picture, embossed the
  wall's bands and tiles behind them on their face, so with the pale flat steel fill and two white streaks they read as a glass panel. Now
  `glMask` carves each jaw out of the shadow by its outline as drawn this frame (`JAWP`, now recorded in both modes, inside the plane's visible
  part: the wall seen between open jaws keeps the shadow), and `glRelJaws` rubs the relief back over each jaw's plate to half way down its
  teeth (as beamBlockers takes them). The look (`jawPath`, `jawGrad`): bronze in the Egyptian looks (`METAL_EG`, `metalOf`: `metalPal` and the
  metal mask's `msKind` read it; `METAL_EG` holds only the jaws, so saws and the pendulum stay steel or iron; with `EGP.traps` off the jaws'
  metal is each style's v61 steel or iron, their drawing still this one), opaque; across the face a dark near rim, the body, a crisp
  reflection band (`JAWG`) and the far edge catching the light; faint brushing along the plate; a riveted spine `JAW_SP` back from the teeth
  that slides into the slot with the blade; verdigris and tarnish toward the root (hashes of the cell); the honed bevel along the teeth (a
  dark line where it meets the face, the edge bright; Classic adds a glint where Torchlight's metal shader lights it); the root in the slot's
  shade; the key light (`keyLight` sx) shades the face when the lamp is beyond the plate and lights its near edge when it is on our side. The
  near half laps `JAW_OV` over the far one (`planeClip`'s `ov`), so no wall shows through their seam. Look only: silhouette, hit box, timing,
  beamBlockers, layouts and the bot unchanged. Pictures `egyptr37b.py` (r37b_jaws.png: v81 | 37b, the owner's case, shut, closing and open in
  six themes and hours and with EGP.traps off, both modes, 3x; r37b_jaws.gif: a slice cycle in Torchlight).
- The checkpoint keeps clear of the walls (round 37c, owner after v81: "The timer checkpoint over the front wall"; iPhone screenshot: the sky
  clock at the end of a run, its right half over the brick front face of the wall block beside it). The clock stands at mid-depth in its cell
  (`cp.x`, the cell's middle), about 32 px wide at s 1.9; a wall's front face (a step's, a low ceiling's) stands HX nearer and HX to the left of its
  cell, so with a wall in the next cell Nut's feet, the arch, the pedestal's rubble and the halo lay up to 7 px over that face, and with one in the
  cell before it the lit halo (30 px) spilled 6 px onto that face. Now it is drawn at `cpX(cp)`: moved along its cell until its foot is `CP_GAP`
  short of the face (`CP_HL`/`CP_HR`, its reach either side; as wallPress presses a figure against a face; 7.8 px for a wall on the right, never
  out of its cell), and everything it draws is cut by the faces beside it on its row (`cpCut`, as figures and lifts are cut: a light at mid-depth
  cannot reach a face in front of it). Classic's wide glow (the room light it gives, as a lamp's sprite; drawn only with Graphics > Lighting off, else Classic's room light is
  `lightPass` from the same `gatherLights`) and Torchlight's light map are room light, not cut; both take the drawn x, as do the sparks when it lights. Look only: the trigger (within 14 px of `cp.x`), the respawn spot, the hint and
  every timing keep `cp.x`; layouts identical (genLevel floors 1-48 x 3 seeds against v81), the bot unchanged. `CP_DBG.off` draws only the room
  glow, `CP_DBG.old` v81's placement and no cut. `cpscan.py [file] [lo hi] [seeds] [torch|classic|both] [old]` (in suite.py, four jobs) frames
  every checkpoint with a face beside it on floors 1-48 (seeds 1-3; 88 of 2,136: 40 with the wall on the right, 48 on the left), lit, with and
  without the clock, and the face's pixels must not change: must print `cpscan: ok` (v81: 88 of 88 in each mode; 0 after). Pictures
  `egyptr37c.py` (r37c_checkpoint.png: v81 | round 37c, both modes, 3x).
- The faults the reference docs found (round 38, owner: "Correct all Claude.md and all of the faults, then release"; `dev/docs/README.md`
  lists each finding and what v83 did with it).
  Round 38a, look faults. No chains (round 18b): `backCell`'s dungeon fitting under a ceiling (one cell in 13, v61's six iron links) is
  `backRope`, a short laid rope in the theme's fibre (`BARM`, `BARF`, worn with the wall), knotted with a frayed tail or a sling of three
  cords holding a small jar (a bare loop read as a noose); the chain only with `EGP.lamps` and `EGP.traps` off. Lamp shadows (round 37b did
  the jaws): `glMask` carved walls, floors, low ceilings and the jaws only, so a figure's shadow was painted across what stands in front of
  the back wall. Now each such thing records its outline as drawn this frame in `SHC` (typed arrays, rings of points with the drawing's rect
  clip; recorded only while Torchlight's shadow runs, `SHC.on`), cut by `shcCarve` after the jaws: a portcullis or lift/sand lift mouth slab
  that is down (recorded whole: two half clips meeting at X+16 left a line), the stakes, a saw's blade, the pendulum's blade and arm, a
  falling or lying roof block, the sky clock and pedestal (the wall inside the arch keeps it), flasks, a lift's platform, its ropes and
  sling legs, the paternoster's slabs and ropes, the sand lift's slab; thin things 1.2 px wider than drawn (the mask is a quarter size, read
  blurred). Not carved: the hanging roof block (inside the wall's carved face), the counterweight (in the back wall), banners, lamps, doors,
  the swing bar, `EGP` off. `SHC.off` draws v82's. `shadowscan.py [file] [lo hi] [seeds] [kinds=] [per=K]` frames the prince beside each
  kind with a torch behind him, Torchlight with the shadow on and off: the thing's pixels (1.7 px in) must not change; must print
  `shadowscan: ok` (floors 1-48 seed 1: v82 266 of 300 things, 0 now). A fallen roof block (lying or falling) is rubbed out of the relief
  (`glRelRoof`, from `glRelFloors`; the dado was embossed on 31 of 32, 0 now). The fork's grating takes a beam's footprint on its bars
  (`fpMarkGrate`, `FPM_A`; the gaps stay 255; Classic already lit them). Beam blockers: lift and sand lift mouth slabs that are down block
  beams in both modes (`blkSlab`; 224 stood in a beam's haze, floors 4-48 seeds 1-2); the shafts' shader tests up to `GLC_BK` 8 (four
  before), those in a beam's haze first (`GLCBL`, `ryBlkLit`; 79 views had a lit one past the first four), and `blkC` skips a blocker
  outside its box (same pixels); no cost measurable here (interleaved timing, against a v82 control). Look only: layouts identical
  (`layoutcmp.py`, floors 1-48 x 3 seeds against v82), the bot unchanged. Pictures `egyptr38a.py` (r38a_rope.png, r38a_shadow.png,
  r38a_roof.png, r38a_grate.png, r38a_blk.png; `cost`).
  Round 40 (the release suite's shadowscan on v84: the clock on floors 10, 22 and 29 seed 1, 105-156 of ~4,300 px shadowed): the clock bobs
  1.6 px over its pedestal, so between the earth's outline and the top slab's the wall shows for 0 to 1.3 px; `shcClock` took the earth 0.4 px
  past its outline, so a gap of 0.4 to 1 px left a sliver of wall under a texel of the quarter-size mask uncarved, and its shadow, read
  blurred, lay across the earth and the slab's top. A gap under `SHC_TEX` (1 px, a texel at the game's view) is now carved with them.
  shadowscan kinds=clock floors 1-48 (per=5, 240 clocks) ok on the GPU; floors 10, 22, 29 ok on the GPU and in SwiftShader. Look only.
  Picture `egyptr40.py` (r40_clockshadow.png).
  Round 38b, play faults, each shown in play on v82 and checked by `r38b_tests.py` (one check per fault, must print `r38b: ok`). A falling
  roof block (any `L.debris`) respects his invulnerability as `trapHit` does: none while `P.inv` runs, a hit gives 0.9 s (v82: `P.inv` 1.2
  still cost a life). A damaging drop's broken lip has nothing to grip from a fall either: `findLedge` skips a `hurtdrop` as `edgeBelow`
  does (v82: 64 of 64 falls with Grab held caught a lip and let go 71 px unhurt; 0 now). A rewind undoes a banner's cut: `snapAll` copies
  the shared `bn`, `applySnap` puts its values back into the same object. The sand lift has its own move hint, `sandlift` ("This slab rests
  on sand. Step onto it and the sand runs out, lowering you down the shaft."), shown on its top row while its slab waits and learned by
  riding it; `lift` is the plate lifts' alone (a save that saw the old sandlift hint counts it learned; one whose sand ride learned `lift`
  keeps it, so the plate lift's hint stays away for it). Its top mouth's plane (`f.gT` 0) stands only while the slab is within the top
  storey; after that the top is an open hole (he can step in, a killing drop, or hang from its edge). The recruit's HUD hearts and rank are
  rose (`#e894a4`, line `#f6c6cf`; were `#8fa3d8`). Gate timers against the bot's waits (floors 1-48 x 3 seeds, and P4 forced): no timed
  stretch holds a saw or darts; the slicer, vents (`timed`) and crawls that do occur already have `estPath` entries, and the bot passed all
  23 such gates with 1.7-5.5 s left, so no timer changes (`estPath` has no `saw` entry and needs none). The roof block's comment now says
  what a respawn does (it rebuilds the floor, so blocks hang again, as every trap resets; a rewind restores their state, a Continue brings
  them back fallen): not a fault. Layouts and the bot's frames identical (floors 1-48 x 3 seeds, timers too).
  Round 38c: the stale comments the docs found are corrected (14, and `drawBar`'s pull, which is the ropes' own swing `f.ps`: `barPos`, so
  `swingPlace` hangs him from it). `sawceil.py [file] [lo hi] [seeds] [nobot]`: no saw left under a ceiling at his height, each one turned
  into spikes has spikes on its run, a tiptoe action over it and no saw action or seg, and the bot plays its floor with no damage; must
  print `sawceil: ok` (4 conversions on floors 1-48 x 3 seeds; a build without the conversion fails 4). `layoutcmp.py [baseline] [lo hi]
  [seeds] [file=] [notimers]` holds round 38b's layoutcmp_play.py (gone): tiles, features at any depth, the bot's path, start, exit, lights,
  windows, checkpoints, items, guards, snakes, lifts, `L.dyn`, forks and hurtdrops; must print `layoutcmp: same`; run by hand for look-only
  rounds (a generator round differs on purpose). `hinttest.py` checks the moves the bot uses are learned (round 49a: and that no banner shows).
  The release suite then found three more. `liftscan.py`'s flush check (round 37a) failed on seven worn lifts in Classic (floors 7, 17, 24,
  37, 40, 43, 57; v82 fails the same on those tried, 17, 40 and 43: it was committed 31 min after 37a's check, less than a full suite run):
  the platform sits flush, but a worn lip's chips are as dark as the pit's floor and read as uncovered (floor 40 seed 45240: 0.51 worn, 1
  unworn), so the check now draws the platform unworn (`f.wl` 0; wear is look only). Round 38a's mouth slab blocker (`blkSlab`) cut the
  beam's haze only below the ceiling's edge, so where a shut slab rises past that edge beside a lift's shaft the haze left on it lit round
  26a's wedge again (floor 15 seed 49884, Classic: 14 over 10); the quad's top now follows that edge (`pl.ce(b)-3`). And `suiteworker.py`
  refused the GPU flags that `cpscan.py`, `doorscan.py`, `openscan.py`, `tilescan.py` and `shadowscan.py` pass to `launch()` (so `cpscan`
  never ran under the suite since round 37c): it now ignores `args`; since the suite's GPU change the worker picks the browser per job (suite.py's `HEAVY` jobs the GPU one).
- The layering rule (round 39, owner: "We need a layering rule ... background, back wall, corridor, front wall ... take each of the game
  elements and assign them to one layer ... check that we draw correctly the game elements"; `dev/docs/layers.md`). Far to near: L0 the
  backdrop (seen only through openings), L1 the back wall and what is fixed on it, L2 the corridor (depth 1 at the back wall to 0 at the
  front plane: things against the back wall, things across the depth with far and near halves, mid-depth where the figures walk, the
  floor's top faces, the air), L3 the front plane (wall blocks' front faces, low ceilings' faces, floor slabs' lips, all drawn `HX` left of
  their cell), L4 the overlay (the dark's rip, HUD, grade, vignette). A part is assigned, not a whole element (a floor's top is L2, its lip
  L3). R1: a part covers only farther parts; the room picture holds L1 and L3 and every live thing is drawn after it, so L3 in front of a
  live part is always a cut (`nearCut(ctx,c0,c1,r0,r1,fl)`, `onFace(x,y)`, `airCut`, `faceGap`, besides `wallPress`/`figClip`, `CUT_AT_WALL`,
  `liftOccl`, `cpCut`). R2: L1 covers L0 but at its openings. R3: the lamp shadow falls on L1 only; the relief belongs to the room picture's
  stone; beams light L2's air and floor tops, never L3; the fill never lands on L0. Owner's rulings: a banner covers the back wall, so it may
  lie over windows and wall art ("Banners cover the back wall, so they can be over windows or wall decorations in the back wall"); hanging
  over open space the ledge's lip and the near half of its top hide all but his hands ("Cut the arms at the lip, keep only the hands",
  `figClip` modes 3 and 4). Four audits split every element into parts (230) and checked them in code with a census of floors 1-48 x 3 seeds;
  fixed (front-plane px changed in a test frame, v83 -> v84): a banner's runner 7 px over the next wall's face (1,503 of 2,379 tiles;
  10,648 -> 0) and the relief on the cloth (`glRelBanners`); the start door 18 px over the next wall's face on floors whose first run heads
  left (38 of 96; `startDoorX`, `DOOR_HW`: look only, `L.start.x` kept, the entry's walk 14 px there); a sky clock on a sand lift's foot
  covered by the lift after the ride (33 of 96; `cpOnLift`); the left lift mouth slab drawn whole before the figures (`liftMouthL`: its
  front face after them); the falling roof block and its trickles over the ceiling's face (411 of 411 for 0.15 s; `roofFallClip`,
  `glRelRoofFall`); falling slabs, planks, chunks and billow over the walls beside the hole (740 of 1,838 corridor slabs, 181 of 697 planks;
  `debrisCut`); dead and dying figures (`deadCut`; the last press kept, `g.rdx`); faces on the left (`wallPress` presses and cuts both sides,
  `wallRows`, `figReach().left`; crouching 18 px into a left wall before); a pushed block's drawn face for the cut; drop-in guards through
  the ceiling (`dropCeil`); `drawShut` clipped to where the back wall shows; lamp flames under a slab (136 of 6,525; `lampCeil`); `rlEnd`
  clips rubble by the faces, the hurtdrop's dark shaft drawn in stage 0 (it covered the next lip, a wall's face in 6 layouts and openings
  in 12 of 77); air (`onFace` skips particles on a face, `airCut` soft sprites, mist cropped to its floor, glints tested at the face); the
  front stake drawn again after the figures (`drawNeedles`, `SPK_NEAR` 0.45); darts were clipped to an 81 px window and vanished 80 px into a
  131 px flight while still hitting (all 91 shooters; now cut on the mouth's side only); a hidden flask's stars, the kick shaft's jet stream
  (limit `X+TW-HX`), Classic's footprint over the clock and lamp stands (`ryStand`), one gate's slot. Side effect: in a kick shaft the
  corridor at mid-depth is 24 px, narrower than his planted pose, so the walls cut him (measured in round 42a: 60 px a planted frame, up to
  174; round 42a's chimney fits him between them). Left as they are (listed in
  layers.md): the slab's top piece over the lintel's side face (round 14), glows over the sky, the relief on lamps (round 46c rubbed it off the clock), passes at
  a figure's play x (round 42b fixed the swing bar's near pole, the uncarved standing things and the vent's back row). `LAYER_DBG` (`hide` a Set of kinds, `glow` false) and `setGT` serve `layerscan.py [file] [lo hi] [seeds] [torch|classic|both]
  [kinds=] [phases=K]`: each kind drawn and left out at its rest, the front plane's pixels must not change; must print `layerscan: ok`.
  Look only: layouts identical, hit boxes, timing and the bot unchanged.
- The kick shaft's chimney (round 42a, owner: "Kick shaft: great idea with the chimney pose. Research and let's implement"). The shaft
  shows 24 px at mid-depth (`X` to `X+TW-HX`, 0.82 m), narrower than v85's plant (soles on the wall, knees to the chest, leaning off it), so
  since round 39 both faces cut him: `egyptr42a.py measure` (the bot's climbs of the 13 kick shafts on floors 7, 9, 11, 13, 14 seed 1) found
  36,906 px x frames of him past a face, every planted frame (60 px mean, 174 max), the jump in 93 px mean. Climbers take a chimney of that
  width back and foot (Climbing.com, "How to climb chimneys" and Rob Pizem's tips; the Night Climbers of Cambridge, "On Chimneys"): back on
  one wall, soles on the other, palms pushing on the back wall by the hips; to go up the hands and one foot tucked under the seat push the
  hips up, then the feet walk up the far wall. Games kick between the walls (Tomb Raider: Underworld's chimney jump, Prince of Persia: The
  Sands of Time's wall-to-wall jumps, Celeste's wall jump: a squash and a sprite flip) and draw no brace; PoP 1989 has no shaft. No CMU clip
  climbs a chimney (the database's climbs are a playground, ladders and steps), so like the plant before it the stance is two-bone IK on the
  motion-capture body (constants `CHM_*` outside the generated blocks; r23poses.py unchanged). Play was unchanged then (he kicked wall to wall on
  Jump, `P.face` flipping each kick; round 48b, below, locks him in); the drawing reads the two halves of the kick as the climber's two pushes: in a shaft column (`chimShaft`: a wall
  each side, `chimWall`) a session `P.chm` draws him facing `F`, the ledge's side (`chimLedge`; else the first wall's), seated `CHM_HB` 8.6 px
  from the wall behind him (`chimX`); planted on the ledge's wall both soles are flat on it (`chimLeg`: the foot turned toes up, `fp` pi/2, its
  sole `CHM_GAP` 1.4 px off the face, by the drawn foot `FOOTP`), stance 'f'; planted on the wall behind, his near foot is tucked under the seat
  on it (toes down, `CHM_BK`), 'b'; the palms on that wall by the hips (`hold` grips, within reach so skel never lowers him); a kick is the push
  (each sole and palm stays on the stone until its limb is straight, `CHM_PUSH` 0.085 s, from the stance he was drawn in: kickOff's pose
  reset is undone, `CHLP`), a tuck (`CHM_TUCK`) and the reach for the next stance as the wall nears (kickPose's distance), the feet moved along
  a line, not by angles (which swung them through the wall); the jump in from the foot eases him back onto the seat (`CHM_IN`; the wind-up's
  lead `poseOx` stops at the face ahead there); within reach of the lip (`CHM_LIP`) the hands go for it, so the hang takes them from there;
  where the wall behind ends (the foot storey) he leans off the wall his feet are on, as v85 did; a slip slides the stance down; he lands or
  hangs facing as play has him (one turn on a landing after a slip from the wall behind). The drawn facing is `P.dF` (only while `P.face`
  differs: `drawActor`, `glSilhouette`, `drawShut`, `handsIn`), the drawn hip `P.rdx` (set, not eased, by `updateLook`), the faces still cut
  him (`chimClip`) and the plant's squash is kept to `CHM_SQ` 0.975 (1/sq widened him into the faces). His lamp shadow, beam cut and light,
  fill cut and the shadow's figure carve take the drawn x in a shaft (`chimSX`; before they sat at his play x, up to 20 px off). After:
  651 px x frames (98% less), plants 0.65 px mean (max 4.4), kicks 0.46 (max 6), the jump in 0.32 (max 2.8). Look only: the bot's frames
  identical on 21 floors with and without shafts (`botcmp`), layouts untouched. Checks: figscan, lowceil, liftkick, run2 5-27, layerscan
  floors 5-14 kinds shaftfoot,jet both modes, shadowscan 9-11. Pictures `egyptr42a.py old.html new.html [measure|nogif|gifonly|quick]`
  (r42a_chimney.png: each phase of a climb before | 42a, both modes, 3x, Torchlight with a lamp up the shaft, phone size; r42a_chimney.gif).
  The locked chimney (round 48b, owner: "run jump in the chimney, then lock in the kicks positions, jump button does nothing, control the prince
  with the up/down buttons to perform one kick and climb a bit, pressing down disengages and the prince falls. When at the top pressing up again
  uses the Y leap to land"; his answers on the research, .claude/research/r48chimney2). v89 kicked on Jump with a tic-tac's timing (a plant of
  0.11-0.45 s, then a slip), off any wall; a running Jump at a shaft was a wall run, which on a two-storey shaft caught the lip and skipped the
  kicks. Now: three ways in lock him (`P.lock`): a running Jump at a kick shaft's wall (`stRun`, `chimLaunch`, in place of `startWallRun`), a
  standing Jump at its foot facing the ledge's wall, or Up at its foot either way (`chimPrep`: the standing jump's wind-up, then `launch` hands it
  to `chimLaunch`); the foot is `chimFoot` (a `shaftfoot` cell under an open column walled both sides, the ledge on one side at the top), so a
  lift's shaft never locks; walking or falling in does not. The jump in (`CHM_IN_T` 0.3 s) goes straight to the first stance, where both walls
  are. The stances stand on a fixed grid, feet `CHM_G0` 50 + `CHM_GS` 46 n px over the foot's floor (`chimH`), on the ledge's wall and the wall
  behind in turn, whatever the way in: two storeys 50, 96; three 50, 96, 142. Every flight is scripted (`chimFly`: vx even, vy so the game's own
  steps end on the stance's height to the pixel). He rests in a stance as long as he likes; each new press of Up (`took('u',0.15)`: held Up does
  not repeat, a press up to 0.15 s before a plant is kept, the pad's dead zone and out again is a new press) is one kick (`kickOff(lk,sd)`,
  `KICK_VX` 62, 19 frames, after `PLANT_MIN` 0.11 s planted); Down lets go at once (`chimAir`: no hold, `jumpKind` 'slip', `P.fallY` there, the
  usual fall damage: from 50 and 96 px unhurt, 142 one life); Jump and Grab do nothing (`#bJump.dim`, `#bGrab.dim`, `updateGrabLabel`). At the
  top stance (the lip within `CHM_YD` 50 px, `chimTop`) Up is the Y (`chimY`): `CHM_YP` 0.18 s gathering (stance 'y': the near foot under the
  seat on the wall behind, the hands on the lip), then from his drawn hip (`P.x` takes `P.chm.hx`) a push straight up until his feet pass the
  wall's top, then across to land `CHM_YX` 12 px past the lip at the top of a rise `CHM_YC` 12 px over it; flown on the standing jump's keys
  (`flightPose('stand')`, `P.yLeap`, `P.yo` 0), cut by the faces (`chimClip`, the session kept) until his feet clear the lip, landed with
  `landSeq 'sl'`. Press to standing on the ledge: two storeys 1.93 s (a running Jump 1.65), three 2.43 (2.15); the Y about 0.5 s. Kicks off a
  single wall anywhere else are gone (`stAir`); the wall run outside shafts stays. The hints `shaft` and `walljump` are gone (no hint; the jet
  stream stays, its zigzag on the grid, `jetPlaces`). A rewind keeps him in the chimney: `cloneE` copies `P.lock`, `P.plant`, `P.chIn`, `P.chm`
  (its `ct`, `kp`) whole. The look of the stances and kicks is round 42a's. Bot `walljump`: a standing Jump at the foot (`opts.chimIn` 'u' or
  'run'), then one Up in each new stance. `estPath` walljump (1.6 + 0.9 k) kept: `layoutcmp.py` against v89 same (144 of 144, timers too).
  Checks: `chimtest.py` (new, suite.py play, three jobs), liftkick (Jump and Up in the air plant, kick or lock nowhere; Up and Jump at a lift's
  foot do not lock), run2 5-27 x 2 and fight 6-12, primtest, vertscan, figscan, lowceil, hinttest, grablabel, r38b, layerscan 5-14
  shaftfoot,jet both modes, shadowscan 9-11. Pictures `egyptr48b.py old.html new.html [outdir] [quick]` (r48b_keys_<shaft>.png, r48b_old_,
  r48b_down_, r48b_phone_, r48b_climb_<shaft>.gif v89 | 48b, floor 11 seed 1 two storeys and floor 7 seed 1 three).
- Three overlaps off layers.md's list (round 42b, owner: "Fix the drawing overlaps you choose are most noticeable"). (1) The lamp shadow:
  what stands before the back wall but was still not recorded in `SHC` (round 38a) is now, as drawn this frame (`SHC_E` 128, `SHC_PN` 4096,
  thin parts 1.2-2 px wider): the swing bar's log, ropes and pole (`bar`), a counterweight lift's hoist beam, brace, hanger and sheave (`rig`),
  the paternoster's level runs and corner wheels (`loop`), lamp flames (`shcFlame`: light is never shaded) and a free lamp's stand before
  an opening, where the sky takes no shadow (`shcStand`; `lamp`), the sand of wells and sand lifts (`sand`, `sandSegs`' outline: round 35b's
  sand stands before the room's whole depth), falling slabs and planks (`debris`, the box growing as a well's slab folds), the vent's flame
  (`vent`) and darts in flight (`dart`, on the mouth's side). Left by choice: banners and the wall lamps' bodies hang flat on the back wall
  (drawn with no depth, like the `TAP` hangings), so a shadow on the wall falls on them at the same place. `shadowscan.py` (new kinds; him
  swinging up beside the bar, jumping on a lift's top landing, dropping beside a well; the caster beyond him; HK_GPU=1 for the Radeon; a
  kind an older build does not record takes the ref build's outlines; a thing counts only by pixels darker with the shadow on, as GPU noise
  on fine detail ran both ways) floors 1-48 seed 1: before 361 of 397 (bar 39/40, rig 24/24, loop 10/14, lamp 83/96, sand 91/91, debris
  80/92, vent 12/16, dart 22/24), after 0 of 952 things of all kinds (`shadowscan: ok`). (2) The swing bar (`drawBar(ctx,o,f,near)`): the
  log, the far rope and the pole from the rawhide grip back (`BAR_G` -6.5) before the figures, the pole's near part, its end grain, the
  near rope with its turns and frayed tail and the ready glint after them, with the gates' near halves (R1). In the pole's frame a line of
  constant u is upright on screen, so the parts meet on a vertical under the grip's near edge; his hands close on the grip (far pass) and
  read over it; facing left swung back the end grain lies over his face, as a trapeze bar's end would. (3) The vent's back row of jets
  (depth .7) is drawn before the figures (`drawVentFire(...,0)` in the `L.dyn` loop, G2D `na` so the scene's alpha is left as
  `drawEmissive` leaves it), the glow, merged sheet, front row, licks and sparks after them as before; in the pilot and the die-down the
  back tips show behind his feet; in Classic the back row now lies under the light pass, where the vent's own fire light keeps it near full.
  Look only: layoutcmp against 42a's file same (144 of 144), the bot's per-tick trace with rendering identical on floors 6 (502), 10, 13,
  16. Checks: shadowscan 1-48 ok, layerscan floors 13-16 vent and 6-12 bar both modes ok, swingtest 6-20 FAILURES 0, run2 6-16 x2 (22/22,
  0 damage). Pictures `egyptr42b.py old.html new.html [outdir]` (r42b_shadow.png, r42b_bar.png, r42b_vent.png: before | after, 3x crops and
  phone size, both modes where it applies).
- Heaps and drifts (round 43, owner: "build something like 'hills' in straight stretches, the purpose is to slow him down"; after
  research_hills.md and r43's pictured alternatives: "Looks: your recommendation"; `dev/docs/elements/heaps-and-drifts.md`). Two kinds of
  slowing terrain, `L.hills` (not features, not traps: G1 untouched), laid by `placeHills` last in `genLevel` from hashes only (no stream:
  `layoutcmp.py` against v86 same, 144 of 144; `metrics40.py` v86 identical): a rubble heap (2 tiles, crest 22-25 px; B1 tumbled dressed
  blocks of the theme's stone on a dark grit mound, B2 a rain-washed mudbrick slump in Kerma and Shali, B3 a fallen papyrus-bundle column
  one heap in four) he clambers over at `HILL_CLIMB` 35 px/s, drawn on its surface (`hillLift`, look only as round 16a's block; since
  round 47a no jump carries him onto it, below); a sand drift (C2: 3-6 tiles, a dune; round 43b, owner: "Wind truly against him, to justify the slowing down": the
  wind blows from ahead, so he meets the slip face at 34 degrees first, wades up it (leaning harder, look only) and goes down the long windward
  back, the brink curving across the depth, sand streaming off the crest toward him (`hillStream`, the jet stream along a path made once); banked against the back wall, ripples, grain-flow streaks; one in
  three with half-buried blocks, C4) he wades at `HILL_WADE` 42 px/s, drawn `HILL_WD` 13 px deep (the near sand over his shins), with no
  jump of any kind (`tryJump`, `startJump`, `stRun`; a heap too since round 47a); wading or clambering he is drawn on the clip's walk cycle (43 px a cycle) with a lean.
  Placement: the run menu's plain floor only (`flat` segs; `breathe()`'s padding never, but it may serve as the margins `HILL_M0` 1 before,
  `HILL_M1` 3 after, so no run-up is slowed), never between a timed gate's plate and its gate (by the route's segs; so estPath and the timers
  are unchanged), never in the chase, on fighters' ground, a lamp's cell, by a clock, flask, door, lift, block or side passage; heaps from
  floor 3, drifts from 5 in the sandy themes (`HILL_SANDY`: all but Nun, Osiris, Aksum; 60% of stretches of 3+); at least one a floor,
  one per `HILL_RATIO` 4 stretches that can take one. Floors 1-48 x 3: 2.2 (floors 3-4) to 4.2 (37-48) hills a floor, every floor from 3 has
  one; +2.6 to +5.4 s a floor at the held pace (max 10.1); the bot 813 -> 817 s mean (run2 3-48 x 3). Guards keep to their side (`hillGuard`).
  Drawn (`hillPaint`) as a height field on the floor's top face (quads by slope against `keyLight` sx) into one canvas a half at `VS`
  (`hillCanvas`): the far rows (d >= 0.5), column, crest line before the figures, the near rows, stones and ripples after them (L2x;
  the canvas ends at the floor's front edge, L3 never covered); `SHC` kinds heap/drift (`hillSil`), the relief rubbed by hard-edged quads
  (`hillRel`), Classic's footprint cut (`ryStand`). Checks: hillscan (in suite.py, gen), run2 3-48 x 3 and fight 3-27 (0 damage), p4bot,
  figscan, layerscan kinds=heap,drift floors 3-48 x 2 both modes, 0 (measured with the bloom held out, `NOBLOOM`: with it, 7 of 262 Torchlight
  heap views changed the lip's glow, 0 with `GLFX.bloom` false, still 4 of 132 with the sky beams off: light, not a draw-over), shadowscan kinds=heap,drift (0 of 128). Pictures `egyptr43.py` (r43_hills.png,
  r43_phone.png, r43_hills.gif).
  Opaque, one outline (round 46b, owner on a B3 heap before an opening, the Waters of Nun at night: "it looks transparent, the background
  wall art seems drawn over it, the shadow renders just over the far left of the heap, and that center circle/oval doesn't look right ...
  Probably need to revise the layering rules also"; his choices on the research's report: opaque against the beams in both modes, all three
  column ends, one outline for every pass, the contour rule). v87: (F1) the sky beams' haze, with the window's bars, rim and pane, lay over
  every hill (`ryBeams2D` and the shafts' shader cut walls, low ceilings and sand only; heapscan, floors 3-48 x 2 seeds, 178 hills: Torchlight 98 over 0.5% of their pixels, mean 26%, up to 100%; Classic 93, mean 22%, up to 95%); (F2) B3's drum joint and four of
  its nine flutes were drawn over the hidden far half (a loop seen through the stone), its outline the fixed ink `#0b0812`, as the B1/B2
  crest line and every stone's edge; (F3) its broken end the palest thing on it whatever the light, with a flat near-black square; (F4)
  `hillSil`, the outline the lamp shadow's carve, the relief's rubbing and Classic's footprint cut used, was the mound alone and took the
  column 8 px right of where it is drawn (`ux = u - HX`), so his shadow lay on its left end and on every stone above the mound; (F5) the
  relief embossed the back wall's art there. Now: `hillSil` is THE outline of everything a hill draws (`hillMeshTop` and its crest line,
  every stone and block with its edge, the column's rings and edge band, a buried end's tongue and blocks; the stones' and blocks' numbers
  shared with the drawing, `hillStoneList`, `hillBlkList`, `hillTongue`), taken by `SHC` (every point), `hillRel` (each quad to the
  outline's highest point over its span) and `sandSegs` (`hillSegs`, made once, after the sand's: `SDS.nw`; `SDMAX` 64, was 24). The
  beams (layers.md R7): Torchlight marks a hill's pixels in the scene's alpha (`HILL_A` 253, `hillMark`: its canvas drawn again with
  `destination-out`) and the composite and bright pass leave the S pass (light, haze, rim, pane, footprint, caustics, the arch water's
  glints), the M pass (mist, looks) and `floorFx` off them at full resolution (`hlGate`, `u_fg.w`); a first try cut them in the S and M
  passes by the outline (`sdC`) and its two-texel ramp left a dark band of unhazed air along every crest in a beam: that cut is kept for
  the `?wgl=0` path only (`u_hm`). Classic cuts `hillSegs` with the walls (`rySandCut`, the beam's clip; `ryStand` no longer boxes hills).
  The column (`hillDrum`): only its near half (the outline's tangents at tan t = 3), seven seams and the joint on it, each a groove with a
  lit lip; its edge a band of the fill darker toward the theme's shadow, lit along the top; the end shaded by the key light's side and one
  of three looks by a hash of its cell (`hillEnd`, owner: "use all three"): A a fracture (facets of the end's stone, the bundle's lobes),
  B the joint face with a dowel socket (a recess with a dark back, a shaded wall, a lit lip), C buried (a grit tongue and two tumbled
  blocks, `hillBury`); floors 3-48 x 3 (46000+97n+13s): 36, 24, 29. The contour rule (owner: "if you add contours or accents always use a
  darker shade of the pixels that are closer to the edge or lighter if light hits it - with some tinting of course"; `selOut(c,k,lt)`,
  `selTint`, rendering.md "Contours", for round 46c to apply everywhere): the stones' and blocks' edges (`stoneBox`'s `o.ink`), the B1/B2
  crest (now before the stones, lit where its slope faces the key light), the column, the tongue. Also: C4's sand round each block is
  the drift's own shade there rising to a lit lip (`hillShAt`), not a flat pale oval; B1's grit in the Blue Chambers is its blocks'
  limestone darkened (in the faience blue it read as glass). Layering rules R5 solids, R6 one outline (a test measures a thing by its drawn
  pixels, never by the outline the pass uses), R7 beams and solids in `dev/docs/layers.md`. Tests: `heapscan.py` (new, suite.py render,
  release, four GPU jobs; floors 3-48 x 2 seeds, 178 hills a mode): v87 480 faults (Torchlight beam 98, wall art 103, relief 94, shadow 68; Classic beam 93, wall art 24), round 46b `heapscan: ok` (every share at most 0.3%); `shadowscan.py` measures heap and drift by their drawn pixels (frames with the beams, mist, looks,
  caustics and bloom off, with it less without it): floors 3-48 seed 1: v87 76 of 128 (heaps 68 of 85, drifts 8 of 43), round 46b 0 of 128 (floors 3-48, seed 1; the bloom, the wind's dust and the sand stream held out, air or light); `beamjag.py` gains a heap in a beam (floor 17 and the first on 4-60):
  STEP 0 at every `GLP.rs`, 0.0081 Battery saver, `beamjag: ok` (floors 1-24, 72 frames). Look only: `layoutcmp.py` against v87 same (144 of 144); hillscan ok; figscan ok; layerscan kinds=heap,drift floors 3-14 and
  37-48 both modes 0 of 180 views; rendersmoke 13-15 both ok (0.59 ms/frame mean, a heapscan running beside it). Test switches: `HILL_DBG` (`stream` off for heapscan; `end` forces a look). Pictures
  `egyptr46b.py old.html new.html [outdir]` (r46b_<case>_3x.png and _phone.png: the owner's B3, B1, B2, a drift before an opening, C4, B1
  in the Blue Chambers, before | after, both modes; r46b_ends_3x.png: v87 and the three ends on two columns).
  No jumping over them (round 47a, owner: "the hills/heaps/drifts - you shouldn't be able to jump over them, only way is to walk at the pace
  they let you"; his choices on r47's research and pictured alternatives: A2, the checked leap; at the foot PoP's stop with the test foot, "I
  always liked that in PoP"; no crawling on a hill; no words; the low leap keeps its way). v88 (`hilljump.py`, floors 3-48 x 2 seeds, 344
  hills): a running jump from the floor before cleared every heap (saving up to 1.57 s of its 1.83 s clamber) and landed half way into every
  drift (up to 2.2 s), a standing jump landed inside every one, Jump on a heap was a standing jump off it (up to 1.5 s), the crawl (42 px/s)
  beat the clamber (35): 341 of 344 hills broken (the 3 others have no floor before them). Now: no jump of any kind while his feet are on
  a hill, no crawl into one (`stCrouch`); Jump whose level arc would carry him onto a hill ahead on his row (`hillAhead`: his half width BW
  over its foot) is checked (`hillCheck`, `startJump`): the carry is cut in `launch` so he lands `PB_GAP` (BW+2) short of its foot (a pit
  or trap before it still cleared, its far lip + `JS_FOOT`), with no run-on (`P.pbQ`), and there he tests it with his foot; with less than
  `PB_MIN` 24 px (running) / `PB_MINS` 16 (standing) of carry left there is no leap at all: he brakes to the foot (PoP's runstop, SDLPoP
  seqtbl.c frames 53-56 and 49-52, 9 x-units of slide; drawn on CMU 16_08's sudden stop, `settlePose('stop')`, P.x eased to a stop at
  it) or steps up to it (standing, the careful step). The test foot (state `probe`, `PB_T` 0.62 s, `startProbe`, `pbA`, `pbHx`, `tpTgt`'s
  edge 2): PoP's testfoot (seqtbl.c: frames 121-126 reach the lead foot out, 86 tests, 116-119 stand back up, net dx 0) on the
  motion-capture body (`stepPose`: 139_29's careful stance and round 33b's envelope; no new keys): he sinks on the rear leg (`PB_H`), leans
  (`PB_L`), the drawn hip lunges toward it with the rear foot planted (`pbHx`, `P.pose.ox`, look only) and the lead foot's ball goes onto
  the surface where it first stands `PB_HS` 3 px high (`P.pbR`, at most `PB_RMAX`; a drift's toe eases in), pitched with the rubble's
  slope (`PB_P`) or `PB_SINK` into the sand, held and drawn back; a trickle of grit or sand at the toe and its footfall (`pbTouch`) are the
  only cue. P.x never enters the hill; he then stands, and the arrow held takes him in at its pace. The low leap (a ceiling at his height)
  is left as it was (355 of 17,272 tries in hilljump). Layouts, `L.path`, estPath, the timers and the bot unchanged (it never jumps at a
  hill): `layoutcmp.py` against v88 same (144 of 144), `metrics40.py` no flags, the bot's frames on floors 3-48 x 2 identical to v88's (92
  of 92). `hilljump.py` (suite.py play, four jobs, not quick): no flight but the low leap lands on or past a hill's foot or leaves the
  floor on one, no crossing beats its pace by over 0.1 s, no crawl enters one; v88 FAIL 341 of 344, round 47a `hilljump: ok`. Pictures
  `egyptr47a.py old.html new.html [outdir]` (r47a_<case>_<mode>.png: v88 | 47a strips at 3x, the checked leap, the braking stop and the
  careful step, each with the test foot, at a heap and a drift; r47a_<case>_phone.png; r47a_<case>.gif).
- Wind (round 44, owner after r44's alternatives W1-W5: "your recommendation"; `dev/docs/elements/wind.md`). `L.winds` (not features, not
  traps), laid by `placeWinds` after `placeHills` from hashes only (layouts, `L.path`, timers unchanged: `layoutcmp.py` v86 same, 144 of 144;
  `metrics40.py` v86 identical), on `plainRuns`' stretches (round 43's finder, shared) and `WIND_JM` 3 cells clear of every seg that is not
  plain floor on its rows (1 where 3 leaves none: 7 of 138 floors), so no generated jump, fall, grab or swing flies in it: a steady draught
  (`s`, 3-8 cells, one per `WIND_RATIO` 4 stretches, at least one a floor from floor 3), gusts (`g`) where a window of the back wall stands over
  it from floor `WIND_G0` 13, and every clear drift's wind (`d`, round 43b's, over the drift and up to 3 cells of his approach); never on a timed
  stretch (estPath unchanged), in the chase or on fighters' ground; it may share a heap's cells. It blows against the run only (owner: no
  tailwind). Strength e: steady 1 (`WIND_MS` 16 m/s, Beaufort 7-8), a gust's peak `WIND_GP` 1.375 (22 m/s), a drift's `WIND_DE` 0.875; the
  run into it `RUN` (1 - 0.35 e) = 65, 40 at a gust's peak, 70 on a drift's approach, the wade 33 (`windCap`, owner's numbers); the gust's
  cycle `WIND_GT` 4.4 s (lull 2.0, warning 0.6, gust to 4.0, fade 0.4; Celeste's on/off wind, DKC2's breeze before a gust); standing in a gust
  he is pushed back at up to `WIND_PUSH` 16 px/s, ramped to nothing inside the zone (`windPush`; `windscan.py`: 228 stands, none left it),
  crouched he holds. Jumps into it (owner: "Should be affected. Research by how much. It should feel realistic"): the drag a person meets,
  rho Cd A / 2m ((v+w)^2 - v^2) (`WIND_CDA`, Cd A 0.44 m^2, 70 kg; UCLouvain's wind-tunnel walkers, 60 N at 15 m/s), with v and time on the
  flight's own clock (its gravity against g, 29.4 px a metre) (`windDrag`, only toward the wind): a running jump 89.5 -> 77 px (-14%), 68-69
  at a gust's peak (-23 to -24%), a standing jump 57.2 -> 48-50 (-13 to -16%), 42-44 (-23 to -27%) (`egyptr44.py measure`; long jumps gain little in flight at 2 m/s,
  de Mestre 1991, Ward-Smith, Murrie; the drag grows with (v+w)^2). Look (`windDraw`, L2 air after the figures and the drifts' near halves,
  `airCut` from under the lip of a slab over the row; soft sprites of the theme's sand, source-over, never added light: r44's prototype's light
  lines read as white scratches): dust veils (what reads at phone size), streamers (sand snakes riding a hill's surface), hopping grains,
  leaves in Nun, Osiris and Aksum, sand pouring in at a gust's window; his lean, the kilt blown back and in a gust the forearm over his eyes,
  stepping back when pushed (`windTgt`); hangings over a wind billow (`drawWindHangs`, live, left out of the room picture, relief rubbed by
  `windRel`); lamps lean and gutter (`windGut` in `flame` and `gatherLights`); the kick shafts' updraft dust (`windUpdraft`, W5, look only);
  `Snd.wind` (`windSnd`). Pure functions of the clock and hashes, nothing allocated a frame. Checks: windscan (in suite.py, gen), run2 3-48 x 2
  and fight 3-27 (0 damage), p4bot 6-27 x 2, forktest, featbot 276/276, figscan, lowceil, r38b, layerscan kinds=wind 3-48 x 2 both modes (0),
  layoutcmp, metrics40, hillscan. Pictures `egyptr44.py old=FILE` (r44_wind.png, r44_phone.png, r44_jump.png, r44_gust.gif, r44_jump.gif).
  Round 45c (owner: "wind follows openings ... random, not predictable"; "wind may blow over jumps"; gusts "earlier, gentler at first"; "wind weaker
  after a death"; `dev/docs/elements/wind.md`, top). `placeWinds` (after the courts, hashes only) puts a zone at an opening over the route's floor:
  a window (`WIND_P.win` 2%, three in four gusts), a large open breach of 4+ cells (18%, mostly steady), a small one (6%, half and half), a court's
  open side (25%, gusts), each times the floor's mood (`WIND_MOOD`: calm, light, normal, windy by a hash); the drifts keep theirs; no minimum a
  floor (floors with none: 4-10 of 36 a band from 13). Zones lie on plain floor and over gap jumps (gap1-3, spikes, bridge), a cell clear of any
  other seg (swings, saws, chambers and kick shafts, lifts, timed traps), off timed stretches (timers unchanged). Gusts from floor `WIND_G0` 7, the
  peak by floor (`windPeak` 1.15 / 1.25 / 1.375), each zone its own cycle (lull `z.gl` 1.8-2.8 s, warning 0.6 s, gust `z.gg` 0.9-1.8 s, fade
  0.4 s). Over jumps: a steady zone is checked (`windJumpE`: the flight's reach with drag, `windReach`, normal and low leap, against the gap +
  `WIND_JS` 10 px) and weakened to 0.75 or 0.5 or ended short (none needed on floors 1-48 x 3); gusts are fair in the lull, and the bot waits for it
  (`windLull`; bot.js `lull()` before sjump, rjump, rjumpg, jgrab, dashjump), playing at full wind; the push never takes him over an edge. Deaths
  ease a zone (`windDeath` in `die()`, `windEase`): 0.6 after one, 0.3 after two, in the save (`S.windDeaths`, cleared at the next floor), so a
  rewind, respawn or Continue keep it; play, dust, sound and lamps follow `windE`. Floors 1-48 x 3: steady 0.5-1.2 a floor, gusts 0.4-1.4, jumps
  under steady 48, under gusts 81. Checks: windscan (new rules, 451 stands, the ease kept through a rewind), run2 3-48 x 2 92/92 and fight 3-27
  25/25 (0 damage), p4bot, forktest, featbot 276/276, layoutcmp v86 same (winds are not in it).
- Courts (round 45, owner: outdoor play "as courts mixed into the halls ... a portico or pergola overhead is enough"; after r45's alternatives:
  one kind per theme family, the pool as the courts' water, the light well for the interiors; `dev/docs/elements/courts.md`). A court is 4-8
  cells of a corridor (part of a stretch) with headroom under stone whose back wall gives way to the sky: he walks the covered side of a court.
  `L.courts` laid by `placeCourts` after the hills and before the wind from hashes only (no stream): `layoutcmp.py` against v86 same (144 of
  144); tiles, features, path, lamps and windows untouched. 7 or 8 a floor from floor 3 (`CT_WANT` + a hash), never two in view (`CT_DR` 3 rows,
  `CT_GAP` 14 cells), none by a lift (2) or door (3), over a kick shaft's foot, banner, lift or damaging drop. Kinds (`CT_KIND`): 'peri' a
  closed-bud papyrus peristyle (Luxor, Medinet Habu; West, Blue, Hawara), 'perg' a vine pergola over a whitewashed garden wall, the canopy's edge
  on the ceiling's face, tendrils hanging in front of him, dapple (Nebamun, Sennefer's arbour; Shali, Kerma), 'fore' a portico onto a court open
  from the sill, its far side by look (`CT_FAR`: a Kushite pylon with pennants and ram sphinxes in Napata and Meroe, a mudbrick pylon in Garama,
  a rock-cut cliff in the Well Corridors, Aksum's stelae behind a rubble-and-timber wall), 'well' a light well (a 2-cell recess lit from far
  above, a shaft of light and motes; Nun, one Meroe court in three); Osiris takes peristyle or pergola by a hash a floor. Inside a court
  `inOpening` holds: no window, arch, decor or hanging, its lamps free (`lampFree`); no sky beam from a court (`ctBox` in `ryOps`), broad `sky`
  lights instead (`ctLights`, x0.5 in Torchlight). Layers: the cut and what stands on the back plane L1 (room picture, after the AO, `ctBack`),
  the ceiling's face over it L3 (`ctOver`), the court beyond L0 (the theme's view in its bays, then `ctBake`'s layers at their true depths on the
  storey's horizon since round 47b, below; moonlit rims by `crossRim`; `ctBg` in `drawBackdrop` under `G2D.na`), live pennants
  in the wind. The pool (owner: "a fall into water kills"): a one-storey spiked pit inside a court off the route's way is a sunken pool (`L._ctP`,
  stakes not drawn), water `CT_PD` 11 px under the coping, L2x (far half before the figures, near half and the cut at the front plane after,
  down to the pit floor's lip), lotus, rings, `SHC` pool, relief rubbed (`ctRel`); falling through its surface is `die('drown')` (card "Drowned
  in the pool", `Snd` splash) and he sinks: the one play change, the pit's own death a storey (53 px) sooner. The court's open side is a gust
  source from floor 13 (`ctGustSrc`; a wind stretch holding a court takes the wind first); vine, pennants and dapple move with `windAt`.
  Guards may fight in courts. No sky above the storey (the ceiling's stone stays a portico or canopy: opening it would need the rows above).
  The arch dust (`LFX` archdust) softened (owner: "blotchy"): rotated, lower frequencies and a wide ramp. Checks: courtscan 1-48 x 3 ok (7.44-7.50 courts a floor on 13-48, 41 pools, a walk into a pool drowns at its surface; 1-60 seeds 4-6 ok), layoutcmp v86 same (144 of 144), metrics40 v86 identical (no flags), windscan ok (a court is a gust source; 237 stands), hillscan, lampscan, wellcorr, guardscan ok, doorscan 0 of 192, openscan 0 (windows 96, gates 89, lifts 422, both modes), tilescan 3-48 ok (0 of 2,020), run2 3-48 x 2 92/92 and fight 3-27 25/25 (0 damage), p4bot 6-27 x 2 44/44, forktest 39/39, featbot 276/276, primtest, hdtest, hinttest FAILURES 0, r38b ok, crossscan quick ok, layerscan kinds=court,pool,vine,dapple,lwell 3-48 x 2 both modes 0 (the dapple measured without the bloom, as the heaps: its light blooms onto the lip), kinds=lamp,wind,heap,drift 3-25: the 3 lamp flames over low ceilings are the same in the round 44 build, shadowscan 3-48 ok (0 of 1074, pool 0 of 12), rendersmoke 13-18 both ok (0.58-0.61 ms/frame mean against the round 44 build's 0.61, the same machine). Pictures
  `egyptr45.py old=FILE` (r45_courts.png, r45_phone.png, r45_pool.png, r45_gust.gif, r45_vine.gif).
  Round 45c (owner's choices on r45b's alternatives). Thresholds (C, "respecting the theme: no standard single way of doing it"): at each end of a
  court a near jamb on the front plane that he and the guards pass behind, the layering rule's one exception (an L3 part in a cell that is not a
  wall, drawn live after the figures and the air, `ctJambs`, exactly its own width), in the theme's architecture (`jambKind`, `JAMB_W`, two forms
  by a hash of the court and the end): a papyrus anta or papyrus-bundle column (West, Blue, Hawara, Osiris), a Kushite pylon's battered edge with
  its torus (Napata, Meroë), a mudbrick pier or palm-log post with a whitewashed reveal (Garama, Kerma, Shali), a monkey-head timber frame
  (Aksum), a rock-cut jamb (Well Corridors), a papyrus-bundle post or lotus pier (Nun's wells). Worn with the stone beside it (owner: "respect any
  damage in their immediate vicinity"; `ctJambsOf`: `wearLevel`, a breach, a fallen lamp's scar, rubble): chips, cracks, a broken capital, at wear 3
  one in two broken off with a jagged top and beside a breach always (`jambClip`, `jambPieces`); 1,951 worn, 668 broken on floors 1-48 x 3. SHC
  kind `jamb`, relief rubbed (`ctRel`), a beam blocker (`beamBlockers`), back in Classic's fill (`fillCut`), the dapple and the well's light clipped
  inside them; layerscan kind `jamb` (its own lips, `OWN`), shadowscan kind `jamb`. Minimum 4 cells: at least 100 px stay open. Meroë (G2 and a
  true per-court grade): its courts show their own sky with its pyramids (`ctOwnSky`), and Torchlight's composite mixes to the court's own grade
  inside up to four court boxes (`u_cgb`, `ctGradeU`, `CT_GRADE`; feathered), Classic matches it after its light pass (`ctGrade2D`). Aksum (S1):
  the court beyond in layers (ambas, stelae at three depths with shade sides and long shadows, a rubble-and-timber wall, the fallen Great Stela,
  converging paving). Courts' gusts come from the wind's openings rule (below). Pictures `egyptr45c.py old=FILE` (r45c_jambs.png,
  r45c_jambs_phone.png, r45c_meroe.png, r45c_aksum.png, r45c_gust.gif).
  Round 47b (owner: "the courts - the background they show isn't in sync with what the windows show, different scenery and it is moving way
  too fast"; chose C, one horizon per storey; the keep's rise as proposed; "Do NOT move the windows' anchor"; the far side lit as in v88;
  depths 40 m, 19 m, 21 m; `dev/docs/elements/courts.md`, top). v88 (33 courts, every theme but Nun at every hour, a window of the same storey
  beside each): the court's strips slid at 0.70 (ground), 0.50 (trees) and 0.18 (far side) against the windows' 0-0.25, each drawn at another
  depth than it moved (the pylon drawn at 0.12 moved 0.18, Aksum's ambas drawn at 0.004 moved 0.18, Meroë's pyramids moved with the walls);
  its own lit scene covered the theme's land; its eye line stood 44 px over the floor (67.2 px from the view's top at rest) on every floor
  while the theme's land in its own bays stood at 89-133 px on floor 5 and off the screen (200-250) from floor 53 (`sink`); and a window,
  anchored on its headroom row, showed the land 51.2 px above an arch or court of the same storey. Now: every opening of a storey takes the
  window's anchor (`bgFoot`: the others count their foot a storey up); one horizon, the floor's eye (`BG_EYE`, `bgEyeY`), the land under it
  by perspective, 29.4 f Hc px for a layer of depth f (`bgHc`: 9 m + 0.6 m a floor to 60 m; it replaces `sink`, kept for the interiors,
  `BGART` `inner`); the sky's horizon stop, sun, stars, moon and clouds on it (`BG_SKY`). A court's bays show the theme's view less the layers
  nearer than its far side (`ctViewOf`; Meroë `BGART.meroeCt`, its grade kept; `ctOwnSky` gone); over it `ctBake`'s lit layers, one a depth,
  drawn at that scale and moved at it (`ctLayersOf`): far side `CT_FARF` (peristyle, pylon and rock courts 0.12, a 40 m court; gardens 0.22;
  Aksum 0.2), in the court 0.15-0.24 (sphinxes, palms, sycomores, small stelae), the floor a plane 44 f px under the horizon with rows only,
  its joints, Aksum's converging paving and stones live at their rows' f (`ctFloorLive`). `CT_DBG` (`only`, `noview`) for the tests.
  `viewscan.py` (window, arch and court on a storey: each layer's y within 0.5 px, the court's eye on the windows' horizon; v88 54.4 px and
  40-101 px, 1,928 views failing; 47b 0.00 in 2,520 views on floors 3-48 x 2) and `panscan.py` (each court layer alone panned 32 px: every
  band at its f within 0.01, the floor's rows at theirs, the view no nearer than the far side; v88 fails all 33 cases) in suite.py, render.
  `beamjag.py` draws the view through the openings as its sky alone (`BGV.flat`): with Meroë's furnaces now in an arch's view the haze over
  their blurred silhouettes (weighted by the scene's darkness at full resolution, not the S pass) read as steps on floor 13 (STEP 0.026 at
  `GLP.rs` .5); v87 still fails 39 frames on floors 1-24, 47b ok. Checks: courtscan, viewscan, panscan, openscan, crossscan quick, solidscan
  things=jamb, beamjag 1-24 ok; rendersmoke 13-18 both ok (0.59 ms/frame mean); egyptr25e the view's slide in descents at most 0.65 px a frame.
  Look only: `layoutcmp.py` against v88 same (144 of 144). Pictures `egyptr47b.py old.html new.html [outdir]` (r47b_<look>_phone.png,
  r47b_<look>_3x.png: v88 | 47b, Napata, Aksum, Meroë, Shali and Kerma at each hour on a low and a high floor; r47b_pan_<look>.gif).
- The sand lift's spike pit (round 41, owner: "The sand lifts become a trap: the sand drains, the door opens, but he has to jump, because the
  slab keeps going"; answers: missing it is death, every sand lift, off by a jump or a step; round 41b, owner: "let's simplify: put spikes at
  the bottom instead of being bottomless"). The slab does not stop at the foot: it sinks on at `SAND_LV` 140 px/s through the foot (now a hole,
  `L.base` `EMPTY`) into a pit one storey under it (row `rD` = rB+1, a floor with fixed spikes, walled both sides) and comes to rest among the
  spikes (`f.yP`, `f.s` 2, a thud). One storey because a landing on spikes kills at any height (`land`: spikes before fall damage), so the pit
  is the generator's own spiked pit and every fall into it (riding on, stepping into the hole after, letting go of the lip) is the usual
  impaling (`die('spikes')`, its sound, sparks and card); riding the slab to the bottom he is impaled as it comes to rest (`sandRide`). Getting
  off (the `lift` state now reads input for a sand lift): the arrow toward its open foot mouth, or Up, or Jump (kept `SAND_BUF` 0.3 s), from
  the mouth `SAND_OPS` 0.45 open (it starts up `SAND_MD` 40 px over the floor, 28 before; open at 22 px over it) until the slab is `SAND_WE`
  60 px under the floor (a storey down, 64, it rests): a window of 82 px, 0.59 s, its cue the mouth's first 0.13 s. Within `SAND_STEP` 20 px
  of the floor a step onto the landing (`step`, drawn eased up from the slab, `P.syo`); deeper a jump up to the lip (`jumpUp` onto the hang,
  the move that catches a ledge a storey up; the arrow or Up still held climbs at once, `P.sandUp`). A held arrow steps him off at the
  window's first frame, so a phone pad needs no timed press (Celeste's Player.cs forgives 0.1 s of coyote time and buffers Jump 0.08 s; a
  simple visual reaction is about 0.25 s; here a held key or a 0.3 s buffer, as a first ride is a surprise; PoP 1989 has no ride to time, its
  jump up to a ledge a storey above, SDLPoP's jumpup/jumphanglong, is the late window's move). Only the mouth on his way opens (`f.mo`,
  `sandOpen(f,s)`, plays `f.gB`/`f.gF`): on a two-mouth lift the other side is a dead end behind the hole after the ride, so it stays shut
  (round 41's open issue). The warning (round 49a: the words are gone, the mouth and the shaft remain): the hint `sandfall` (replacing round 38b's `sandlift` on its trigger, by the slab while it waits:
  "This slab sits on running sand and will not stop at the bottom: there are spikes below it. When the door at the foot opens, step off
  through it, or jump for the edge."), learned by getting off one, not by boarding, so a save that learned the old `sandlift` still sees it;
  and the mouth starting up before the window. Generator (post pass, after the open-hall pass): the storey under the foot must be rock three
  cells wide (pit and walls) in the floor as built; else the banner slide (`sandBanner`, `bn.fb` 1). Reserving those cells while building
  (tried for round 41's three bottomless storeys, then again for this one) let later runs and pits go elsewhere and cut floors short
  (`metrics40.py` v85: floor 15's shortest route 943 for 971; three storeys: floors 4-27, down to 1065 from 1179) for 4 more of 265, so it is
  not done. Where the route runs on past the foot's far side (the turn's last move: the next run starts at the foot, `LAND`, and heads back;
  every two-mouth lift) he gets off on that side (`f.mo`, the bot's `off`, `to`), which must be plain floor with nothing after starting at the
  foot or crawling beside it (Down there hangs him into the hole), else the banner slide (`bn.fb` 2). Floors 1-48 x 3 seeds (`sandshaft.py`'s):
  322 built, 261 traps (bottomless round 41: 218), 16 no rock (60), 20 the way on (19), 25 unwalled or a jump under the kept walls (26e/26g, as
  before). `metrics40.py` v85: no flags, identical. `layoutcmp.py` v85 (floors 1-48, seeds 1-3; 50 of 144 floors identical) differs only in
  the 294 traps' foot and pit cells (588) and spike features, the 37 new banners (top cell, features, bot `slide`), the bot's `sandlift`
  actions (`off`; `to` on the 122 far-side ones), 42 sky clocks moved off a foot (to the first plain cell on the side he gets off by), lamps
  on 7 floors (`lampClear` reads `liftCell`, which runs down to the pit) and one gate timer of 1,438 by `estPath`'s `sandlift` (careful
  2.83, else 1.23, + (64k - 22)/`SAND_LV`: k 3 4.04 / 2.44, k 4 4.50 / 2.90; was 4.0 / 2.2; the bot: 1.77 / 2.23 s from boarding to
  standing off, 133 rides). Look (`drawSandLift`): the shaft's back and the sand run on down into the pit, no outlet; the pit's spikes stand
  in the sand, hidden under the slab's top while it is above them (`drawNeedles`, the feature's `sl`), and at rest the slab lies among them,
  drawn before them so they stand through it (both modes, the spikes' own shadow carve and relief; the sand in `sandSegs` and rubbed by
  `glRelBox` down to the pit, the slab at rest too). Bot: `sandlift` holds toward `off` from boarding (`opts.sandJump` presses Jump instead,
  for tests). Checks: `lifttest.py` (sand3/sand4: missed, impaled 64 px under the floor; stepped off with the slab 20-22 px over the floor;
  Jump at 40 and 54 px under it climbs out, at 62 too late), `sandshaft.py` (the foot a hole over a walled spike pit; the fallbacks
  counted), `liftscan.py` (a third place, the slab at rest on the spikes with him on the landing; near column and arches down to the pit;
  floors 4-51 x 2 Classic, 6-11 Torchlight), `r38b_tests.py` (`sandhint`, `sandtop`), `hinttest.py` (learns `sandfall`), `run2.py` floors
  4-27 x 4 (96 of 96, 0 damage) and fight 5-16, the bot on 45 floors with sand lifts (133 rides, 0 damage), `layerscan.py` floor 5 (lift and
  spikes) both modes. Pictures `egyptr41.py` (r41_sandfall.png: the mouth opening with him on the slab, the step off, the slab going down
  into the pit, at rest among the spikes, a miss onto them, a far-side lift, both modes; r41_sandfall.gif).
  Round 41c (the release suite on 41b: the bot timed out hanging from the hole's lip on 7 jobs, run2 floors 32/33, featbot 13/24/27,
  rendersmoke 14; v85 passed them, its foot was floor after the ride). The way-on check looked only at the first move after the ride and
  only for a crawl, so two cases got through: a swing (also rjump, rjumpg, jgrab) whose run-up starts two cells back, on the foot (he ran
  into the hole and caught its lip: floor 32 seed 703130, swing from 512 heading left, the foot 514), and darts beside the hole (the bot
  crouches to duck them 8 px toward the hole, and Down within 26 px of an edge, `edgeBelow`, climbs down: floor 33 seed 703201). Now every
  move on the foot storey after the ride up to the next vertical move (`SL_HZ` and `swing`) is checked: none may walk to the foot, start a
  run-up on it (`SL_RUNUP`: from-2*dir to from) or press Down within 27 px of the hole (darts at their wait, crawls); else the banner slide
  (`bn.fb` 2), as a player could not get past it either. Floors 1-48 x 3 seeds unchanged (261 traps, 20 the way on); x 23 seeds (adding
  run2's 700000+97n+13s, s 0-19) 6 of 2,047 traps become the banner slide (fb 2 177 to 183): exactly the 6 floors the bot failed on 41b
  (floors 12, 28, 32, 33, 41, 48; five swings, one darts), all passed now. `metrics40.py` v85: no flags.
  Round 41d (the release suite on 41b: `liftscan.py` failed 9 sand lifts at its third place, all faults of the test's new place, none of
  the drawing): he was stood three cells off the hole on the open mouth's side blindly, so on floors 4, 9 and 15 inside a wall block (his
  whole figure, 2,061-2,305 px, counted as lift pixels over stone) and on floors 6, 20, 28, 29, 30 and 32 on a cracked slab that broke under
  him in the settling ticks (9-542 px "over a grating", his figure and the falling slab). He now stands on the farthest plain floor cell (no
  feature) up to three cells off, a wall or a hole stopping the search: all 18 cases pass, no lift drawing changed. And v85's lone failure
  (floor 40 seed 53159 lift 11, `wedge` 11 over 6, Classic, software GL only): a drifting glow of `ambientGlow`'s lay over the shut left mouth
  slab's piece above the ceiling's edge at gameTime 10-16 s only, which the earlier cases on the page had reached (alone it measured 4 over
  6); the wedge is now measured on a frame without the `atmo` layer (mist, motes, moths, fireflies, wisps; round 26a's fault was the beams'
  haze, the light pass's). `liftscan.py` floors 3-20, 27-32 and 40 both modes `ALL OK`.
  Round 41e (owner: "Fix the spikes thing"): the pit's stakes showed through the sinking slab for its last ~25 px: `drawNeedles` cut all
  four at the slab's front edge (`sl.y+HY`), but a stake stands at its own depth, its root up to 2.2 px up the depth diagonal, so the far ones
  were drawn over the slab's top while it was still above their tips (on floor 6 seed 91266 a tip over the slab with its top 22.7 px over the
  pit's floor, the 21 px stake's height). Options weighed: the slab resting on the tips (but riding it he is impaled as it comes to rest, so
  it must reach the floor: it would contradict play); hiding the stakes until it rests (they would pop up 10-21 px in one frame); the stakes
  driven up through it (chosen: it is what kills him, it ends exactly in 41b's look at rest, and needs no change to play). Each stake is now
  cut at the slab's top face at its own depth (`sy+(0.5-d)DY`, onFloor's line), so it shows only once the top has sunk past its tip, and where
  it breaks through a dark puncture as wide as the stake there with a pale lip of broken stone on its near side; at rest the puncture is the
  stake's own foot shadow and the lip stays, so nothing pops. The lamp shadow's carve (SHC) takes each stake only above that line. Both modes.
  Look only: `layoutcmp.py` against 41d's file same (144 of 144), play unchanged. Pictures `egyptr41e.py old.html new.html` (r41e_spikes.png:
  41d | 41e, both modes, 3x for the slab's top 30 to 0 px over the pit's floor on two lifts, and phone size; r41e_spikes.gif).
- The Crossing (round 36a, owner, after the research in `dev/INTERLUDE_RESEARCH.md`: "an interlude between themes"; answers: at each
  theme change, after Climb on, he moves only while the pad is held, wordless but skippable, all twelve themes in their setting,
  Torchlight's glow and a Classic version, the hour from `progOf`, named "the Crossing"). At each change of theme (`crossDue(n)`:
  `themeOf` differs from floor n-1's, so every fourth floor from 5) the order is exit (into the light), the card, Climb on, the
  crossing, the next floor's entry (round 26f's E1). `nextFloor()` runs `startLevel` as before (save, rewind ring, hours and floor clock
  are what they always were) and `crossBegin()` puts `mode='cross'` on top; `loop()` steps `crossStep` (60 Hz) and `render()` hands the
  frame to `crossRender`; `crossEnd()` returns to 'play' with the entry restarted (`L.enG`). gameTime runs; levelTime, the save, S and
  the rewind ring are untouched. Control: Right held walks (`CROSS_WALK` 40 px/s, the exit's pace); held on for `CROSS_RUNT` 1.6 s he
  runs (`RUN`, as the game's run is a held direction); let go, he stops; Left turns him to look back; after `CROSS_CUE` still the
  pad's right arrow pulses (`#pad.cue`). Skip: Jump from `CROSS_SKIP0` 0.5 s, every time (the Jump button shows a skip glyph; Grab and
  pause are hidden), black over `CROSS_SKIPF`. Never on Continue, Restart, a checkpoint, a respawn or the title (only `nextFloor`
  starts one), under `?bench`, the bot or test loads (`crossOn`: `quiet`), with the pause menu's "Crossings" off (`S.set.cross`
  false) or `?cross=0`. Look only, from the floor's seed by hashes (`CR.seed`), no generator stream: layouts unchanged.
  Structure for the next rounds: `CROSS_LOOK[look]` names the setting (dunes: blue, foggara, napata; oasis: meroe, deffufa,
  shali; garden: west, osiris, hawara, nun; wadi: wells; highland: aksum); `CROSS_SETS[setting](cr)` returns its layers
  `{kind, z, f, ...}` (a setting not built plays `plain`: sky, ground, the theme's BGART far layers through `bgPaint`, the
  doorway); `CROSS_KINDS[kind]` has `bake(ly,cr)` (once, one layer a frame under the fade from white; into a canvas, uploaded once
  by G2D) and `draw(ctx,ly,cr)` (every frame, view units). The view: the path is the play plane (f 1, his feet at `CROSS_GY` 134),
  the horizon at `CROSS_HZ` 96, ground at depth factor f at y = HZ + 38 f, a layer moving f of the camera's travel (round 27b's
  f = Z0/Z = h/(s H)); `crossZ(f)` orders the land behind him, 50 the doorway, 60 is he, 70 the foreground (f 1.9-2.25, faster than
  him, never over him). Kinds: `sky` (BGART sky by `todSky`, its horizon stop at eye level; sun low left at dusk, right at dawn and a
  little higher at each dawn crossing toward sunrise at floor 60, `crossSun`; moon and stars at night), `ground` (haze to near sand,
  ripple crests in perspective rows; `firm` for a path), `bgart` (a theme's far layer, hazed by `crossHazeK(f)`, its ground band cut;
  `span`: one stand, e.g. palms near the doorway), `erg` (dunes: convex windward backs, slip faces at `CROSS_LEE` 0.67 = 34 degrees,
  the shaded wedge from the brink; `bar` barchans with horns; `near` ripples and sand streaming off the brinks by `jetStream` with the
  crossing's own sprites, `crossSprites`), `gate` (a mesa across the end of the path with the next floor's start door: posts,
  lintel or vault, `doorArch`), `fore`. The wind blows left to right: dusk's slip faces are dark, dawn's backs, night's crests silver
  (`crossCols`). The beat: as he passes `CROSS_BEAT` of the way a gust (`crossGust`, `CROSS_GUST`) flares the plumes and sends a sheet
  of sand along the path. At the doorway he turns into its depth (EN_DX, EN_DY reversed), cut by `doorHead` and darkened by
  `drawPTint` (now any actor), the wind cuts off, a thud (`crossdoor`), black, the entry. He is the game's figure (`walkPose` blended
  into `runPoseHD` by the hold, `followPose`, `updActorLook`, `drawActor`) in his palette under the hour (`crossPal`), a long soft
  shadow away from the sun. Torchlight: the scene through G2D (all but him with `G2D.na`, as the sky) and `crossGL` (glFrame's light
  map with `CR.amb` and the sun or moon as one broad light plus his fill, bloom, grade, vignette; no shadow, heat, storm, metal,
  relief, beams or mist: those read a floor's tiles); Classic a glow at the sun and the vignette. Sound: `Snd.wind(k)` (looped noise,
  a rising bandpass), `sandstep`/`sandrun`. The next floor's rooms are built meanwhile (`roomWork`). Rounds 36b-36d: oasis (built in 36b), garden (36c),
  wadi and highland (36d) as `CROSS_SETS` entries with their own kinds (pools, palms near, pergolas, scree, terraces); animals only (geese,
  a heron, ducks, ibis, fish, ravens, a flock), no people. `crossscan.py` (in suite.py; every theme's crossing in both modes: starts and ends, the pad
  needed, skip, save/S/levelTime/rewind unchanged, never off/Continue/Restart/respawn/ordinary floor/bot/`?cross=0`, render ms against
  `HK_CROSS_MS` and a play frame) must print `crossscan: ok`. Pictures `egyptr36.py` (r36a_dunes.png, r36a_all.png, r36a_cross.gif).
  Round 36b (owner's review of r36a_dunes.png: "the near dune is a straight-edged triangular wedge that reads as a PYRAMID"; the ground
  "flat and empty"). Dunes (`erg`): a convex windward back flat at a rounded crest (radius `R`), a sharp but soft brink (a smooth minimum),
  the slip face at `CROSS_LEE` bending concave into its apron, soft feet (a soft maximum with the corridor's floor), the crest line swelling
  and sagging in whole periods; the slip face drawn as a crescent seen obliquely (its edge on the back a curve from the brink bulging
  upwind and sweeping down to the horn: never a straight arris from a point), grain-flow streaks and a lighter foot; small dunes riding the
  near seifs' backs; ridges in five depths. Ground relief (`dfield`, a strip per depth: f 0.45, 0.8 behind him, 1.3, 1.7 in front, never
  above his feet's line): low swells lit by their slope with ripples following them, stones with their shadows, tufts of halfa, sized
  29.4 f px a metre and footed in the ground's own colour there (`crossGroundAt`). The oasis (`CROSS_SETS.oasis`, `CROSS_LOOK[...].ov`:
  meroe `hafir`, Musawwarat's and Meroë's rain-fed reservoirs with the spoil bank behind, acacias, the pyramids; deffufa `nile`, the
  river across the view, palms and acacias on the far bank, empty round huts, the Deffufa; shali `spring`, a round spring in a dressed
  stone rim with its upwelling, date palms in four depths, olives, mudbrick garden walls, the Aghurmi rock (`butte`) and Shali; the
  report's mapping kept: Napata stays dunes, its barchans before Gebel Barkal, and Garama dunes): the water (`pool`, an outline in world x
  and depth placed by the pinhole `crossPX`, so its far shore moves slower than its near one) shows the sky of its hour at the mirrored
  height, the sun's or moon's glow and glitter path, every layer behind it marked `refl` mirrored about its own ground line (the soft
  reflection, 0.4), darker toward the near shore; damp ground round it. `stand`: palms (trunks with the leaf bases' crossed pattern, crowns of
  pinnate fronds with gravity's sag, dead fronds, dates; the crown swaying about the trunk's top), acacias (umbrella crowns), olives, huts,
  walls, each drawn once into one atlas per layer (`crossCrown`, `crossTrunk`, `crossThing`). `reeds` (papyrus, common reed, reedmace)
  along both shores, swaying by a shear; `ofore` (f 2.1): a frond's tip hanging in from above (never below his head's line) and reeds from
  the screen's foot; the doorway in mudbrick (`gate.mud`, `crossMudFace`). The beat (`birds`): Egyptian geese resting on the water lift
  off as he passes `CROSS_BEAT`: a run over the surface with splashes, then climbing away ahead of him, the white forewing showing; before,
  they drift and bob with rings round them (no crouch: he never loses control). Sound: `firmstep`/`firmrun`, `frond`, `blip` (while the
  water is in view), `geese` (honks and wingbeats). Look only, hashes of the floor's seed; layouts and the bot unchanged. crossscan:
  `quick` (Classic, one theme per setting, about 2 min, in `suite.py quick`), `classic` and `torch` (every theme, the default and release
  tiers run both as two jobs, Torchlight among the heavy ones); it also checks each setting's layer kinds (`SETX`) and that every layer is
  baked within the fade from white, and prints the longest bake frame (script ms a frame, 36a | 36b measured alike: Classic median
  0.7 | 0.8, p95 2.6 | 2.4; Torchlight median 1.6 | 1.8; the longest bake frame 20 ms Classic, 28 ms Torchlight, under the fade). Pictures `egyptr36.py r36b` (r36b_dunes.png before | after,
  r36b_oasis.png, r36b_oasis.gif).
  Round 36c (the garden, `CROSS_SETS.garden`, `CROSS_LOOK[...].gv`; Egypt's own gardens after INTERLUDE_RESEARCH.md, never the Babylonian
  "hanging gardens"; regular where people keep them: rows, edges, channels). West `pool`: Nebamun's pool garden (BM EA 37983): a T-shaped
  pool (`pool` with `poly`: straight edges in world x and depth, the stone coping: the far wall's inner face, the kerb's face toward him,
  the side walls' faces where the eye sees them, lit on the light's side), blue and white lotus in clumps, fish gliding under the surface
  and the rings where one rises; sycomore figs, date and doum palms planted evenly in rows, each in its watering basin (`pit`), a
  whitewashed enclosure wall with a gateway, pomegranates, an idle shaduf (Ipuy's, TT217, no one at it), a vine pergola with grapes, beds
  in square plots between mud ridges (`band` 'beds'), a runnel; the beat: a grey heron on the coping crouches and lifts off, slow
  wingbeats, legs trailing (`fauna`, `crossHeron`). Osiris `field`: the Field of Reeds as Sennedjem's tomb (TT1) paints it: a canal and a row
  of palms, sycomores and doums beyond (the obelisks and shrines mirrored in it), ripe grain and flowering flax in rows (`grain`: one row's
  strip drawn at every row's own depth, scaled; `crossCrop`) cut by receding channels every 11 m; the field lies a metre below the bank he
  walks (`sk` on a flat layer: its y scaled about the horizon; `sink` on rows and animals), so it is seen from above; the bank's face and the
  canal in front of him with lotus and ducks (`dyke`); the beat: a breeze runs through the grain as a travelling wave, the ears lit at the
  crest, a trough behind (`crossWave`/`crossWaveF`, `CROSS_WAVE`: a front along world x from where the camera's left edge is at the beat,
  so no state). Hawara `shore`: Lake Moeris' edge in the Fayum: the lake with the pyramid and the labyrinth's walls mirrored, the far shore's
  reeds (`thicket`), sacred ibis wading and feeding (`crossIbis`), green plots (`grain` 'green' within `xr`) with a shaduf at their corner by
  the water, reeds at the shore, a ditch; the beat: the breeze through the reeds (`reeds` `wave`) and a cat's paw across the lake (`paw`: a
  ruffled patch in the sky's own colour, ripples flickering). Nun `marsh`: papyrus thickets far off (`thicket`) and clumps standing in still
  water with their reflections (`clumps`, `crossPapyrus`), blue lotus, the path on a raised earth dyke with the water on both sides (`dyke`);
  the beat: ducks burst out of the papyrus with the swimming ones (`fauna` 'duck', `crossGoose`'s shape). The eye is 1.3 m up, so anything
  standing in front of ground-level water or a field hides it: the pools are kept clear in front, the fields sunk. Foreground `gfore` (a
  vine with grapes and the beds' cornflowers, poppies and mandrakes; ears of grain; reeds; papyrus), never over him. Fixes from the owner's
  review of 36b: the geese rest on the near half of the water and come toward him as they climb away (their size still by the depth rule);
  Siwa's mudbrick walls (`wall`, shared with the garden) have courses, buttresses with stepped tops, palm-log ends, a gateway or a breach
  (hashes of their place). Sound: `earthstep`/`earthrun` (a beaten earth path), `rustle` (grain, papyrus), `breeze` (the wave), `heron`,
  `ducks`, `duckcall`, `ibis`, `birdcall` (a hoopoe), `blip` (a fish). crossscan also checks the garden's layers and each garden theme's
  features (`SETL`: tpool, lotus, fish, heron; grain, dyke, sunk; wave, paw, ibis; clumps, ducks). Script ms a frame (36b | 36c, measured
  alike on this machine): Classic median 0.8 | 0.9, p95 2.4 | 2.5; Torchlight median 1.8 | 2.0 (unchanged floors measured 10-25% slower in the same run: the machine's) (software WebGL; its p95 spikes are the
  machine's); the longest bake frame 19 ms Classic, under the fade. Look only: layouts and the bot unchanged. Pictures `egyptr36.py r36c`
  (r36c_garden.png, r36c_garden.gif, r36c_fixes.png).
  Round 36d (the last two settings and the audit of all twelve). The wadi (`CROSS_SETS.wadi`, the Well Corridors; owner: a limestone wadi):
  the workmen's path over the Theban hills: pale cliffs in level beds cut back by gullies, each gully's cleft lit on the light's side and its
  scree fan at the angle of repose below it (`cliff`, three depths), el-Qurn beyond (the theme's layer; its lit tomb doorways left out),
  acacias and tamarisks in the wadi's bed, fallen boulders, the dry channel (`band` 'wash'), a well head with a stone trough far off (`stand`
  things tamarisk, boulder, well); the path rises gently: `cr.tilt` 0.045 makes the ground a plane tilted along the way, so every layer on it is
  sheared about the view's middle (full on the ground, fading out with depth), his feet ride it (`crossFY`), the sky stays level and the doorway
  is placed on it unsheared. The beat: stones trickle down a scree fan off a spur of the near cliff, with dust (`rockfall`, its world x set so
  it is in view at the beat), and two brown-necked ravens lift off a boulder (`fauna` 'raven', `crossRaven`). The highland (`CROSS_SETS.highland`,
  Aksum; owner: terraced highland fields): the hill falls toward him, so the terraces behind the path step up with their dry-stone risers facing
  him and the crop on each lip (`terr`: ripe grain, green, fallow fields along it; the eye is 1.3 m up, so the highest lip is a near skyline a
  little over the horizon and the valley beyond is hidden), the riser down from his terrace's edge to the field below in front (`tfront`), far
  hillsides terraced in contours with junipers (`slope`), Aksum's storeyed stelae on a skyline far off, the Great Stela lying broken (`slope`'s
  `st`; nothing Christian), the ambas beyond, junipers, wild olives and granite tors (`juniper`, `wolive`, `tor`); a cooler, clearer light (`crossK`:
  the low sun's warmth halved; less haze). The beat: a flock of small birds bursts out of the grain of the terrace above him and wheels away
  (`flock`). Sound: `gravelstep`/`gravelrun`, `rockfall`, `raven`, `ravenfar`, `cliffwind`; the highland's earth footfalls, `flock`, `dove`.
  The audit (owner's review of 36a-36c's pictures): night had no read of its own: `crossRim` lays a silver rim on every edge of a baked layer
  that faces the moon (the drawing less itself shifted away from the moon, source-atop, at bake only: stands, reeds, clumps, thickets, the
  far layers, cliffs, slopes, terraces, the doorway), the moonlit side brighter and silver, the shade darker and cooler, the sky lit round the
  moon (a wide soft halo, a brighter one close in, the horizon paler under it), never day. The water read thin from his eye height: the Nile at
  Kerma, the hafir, Siwa's spring and Lake Moeris reach nearer (to f 0.86-0.91), the mirrored sky kept brighter with a middle stop, the near
  shore's darkening lighter, the moon's light a pale column on the far water, a light line under the far shore. The doorway was one sloped block
  in every theme: now each setting's own (`gate` `gv`), framed as the next floor's start door: 'ruin' (the dunes: a temple wall of coursed
  sandstone, its top broken in steps, a stretch of cavetto cornice over the door, a low rounded drift against it, a fallen block, column
  drums), 'pylon' (the oasis and the garden: a mudbrick gateway between two battered towers with torus and cornice, the enclosure wall on;
  whitewashed in Nebamun's garden), 'rock' (the wadi: cut in the cliff as the Valley's tombs are, a rebate round it, a cleared step, the
  cliff's end face and its scree), 'granite' (Aksum: a wall of rubble courses between timber beams with their round 'monkey head' ends, in
  projections and recesses, the doorway in dressed granite on a granite step). Osiris's shrines (BGART's glowing doorways in nothing) are left
  out of the crossing. Nun's papyrus kept green under the low sun (`crossLitG`, the light's warmth halved for living green). The dark grass
  band in front (West, Hawara) got soft patches, clods and stones, rosettes of leaves among denser tufts. The light's side was reversed in
  several drawings (lit on the side away from the light): the palm crowns, acacias and olives, the reeds, the huts' thatch, the ground's
  swells, stones and tufts (`dfield`): all corrected. Every crossing:

  | Theme | Setting | Beat | Doorway |
  |---|---|---|---|
  | Halls of the West | garden: Nebamun's pool | a heron lifts off the coping | whitewashed pylon |
  | Blue Chambers | dunes: low dunes at Saqqara | a gust off the crests | ruin in the sand |
  | Forges of Meroë | oasis: the hafir | geese lift off | mudbrick pylon |
  | Green Hall of Osiris | garden: the Field of Reeds | a breeze through the grain | mudbrick pylon |
  | Foggaras of Garama | dunes: a seif corridor | a gust | ruin in the sand |
  | Deffufa of Kerma | oasis: the Nile | geese lift off | mudbrick pylon |
  | Well Corridors | wadi: limestone wadi, the path rising | stones down a scree fan, ravens | cut in the cliff |
  | Labyrinth of Hawara | garden: Lake Moeris' shore | a breeze through the reeds, a cat's paw | mudbrick pylon |
  | Salt Fortress of Shali | oasis: Siwa's spring | geese lift off | mudbrick pylon |
  | Pyramids of Napata | dunes: barchans, Gebel Barkal | a gust | ruin in the sand |
  | Stelae of Aksum | highland: terraced fields, the stelae far off | a flock out of the grain | granite in rubble and beams |
  | Waters of Nun | garden: the papyrus marsh | ducks burst out | mudbrick pylon |

  crossscan: `SETX` for the wadi and the highland, each setting's doorway (`gate-<gv>`), `SETL` for every theme with its own features (wells:
  raven, tilt, cliff; aksum: stelae, terr, flock). Script ms a frame (36c | 36d, measured alike on this machine): Classic median 0.9 | 0.9-1.0, p95
  2.5 | 2.6-2.9 (two runs); Torchlight median 2.0 | 2.1 (software WebGL; its p95 spikes are the machine's); the longest bake frame 19 | 40 ms Classic, 41 ms Torchlight
  (the moonlit rims and the bigger doorways; still one layer a frame, all under the fade from white). For a phone: everything new is baked once
  (the rims too; no per-frame allocation), the wadi's shear is one transform a layer, the reflections only draw inside the water's box, the
  layers stay under 20 a crossing and their atlases under 4000 px. Look only: layouts identical (genLevel floors 1-48 x 3 seeds against
  origin/main), the bot's frames on floors 3-6 identical. Pictures `egyptr36.py r36d` (r36d_all.png: every theme at every hour in floors 1-180,
  start | beat | doorway, both modes; r36d_wadi_highland.gif; r36d_audit.png: 36c | 36d for each fix).
  Round 36e (owner's three fixes before v81). The wadi's rockfall ("subtle at its distance"): the spur stands at f 0.3 (was 0.15, twice as
  near; `hm` 3.2 m of fan), placed at
  `RF_SX` 0.55 of the view at the beat; 0.15 s after the beat `RF_BIG` 6 big stones (0.3-0.46 m, lit on top and the light's side) and 10 gravel break off at
  the gully's head, drop down it and bound down the fan in hops that shrink, each big one trailing a dust streak and kicking up dust where it
  lands; a plume (`RF_PL` puffs of one soft sprite baked once) rises off the fan and drifts on the wind over ~4 s; the stones stay where they
  rest (a pure function of the clock since the beat). Nothing in the wadi's bed at f 0.5 stands in front of the fan while the camera runs
  `RF_CW` 200 px on from the beat (`rfClear` moves a tamarisk or boulder aside; the acacia from xb+250 to xb+390, the ravens' boulder to
  xb+200). Sound: `rockfall` gained a low rumble that swells and dies over 1.8 s and the big stones' thuds. The geese in flight ("white
  squiggles at small size"): `crossGoose` in flight is a solid bird: a full body, tail, a thick neck and head (darker in flight, `ly.cf`) with
  the eye patch and a pink bill, and broad wings (root chord `GW_C` 0.36 of its length, stations `GW_S`/`GW_L`/`GW_T`) that turn about the
  body's axis by `GW_A` flap and are seen a little from below (`GW_E`: the near tip higher than the far), so both strokes are whole shapes; on
  each wing the white forewing is one panel over the inner half's front, the flight feathers dark behind it and at the pointed tip; the far
  wing in shade behind the body. Shared by Meroë, Kerma and Siwa, and the garden's ducks (their speculum in the panel). The tilted path ("a
  small dark wedge bottom right"): the shear lifted the ground and the foreground off the screen's foot at its right edge; both now reach
  `crossTiltX` past it. crossscan checks the void (the page's dark) in the bottom corners of every wadi crossing's hours at the start, the
  middle, the beat, the doorway and going into it, both modes (36d: 834-858 px of 6,144; 0 now). Look only, hashes: layouts identical
  (genLevel floors 1-48 x 3 seeds against release-v81). Pictures `egyptr36.py r36e` (r36e_fixes.png: 36d | 36e at phone size and at 3x, both
  modes; r36e_wadi.gif).
  Second pass (owner's review: shapes in the wadi read as built monuments): nothing in the wadi may read as a pyramid, tower or door but the
  real doorway. The spur is an irregular limestone outcrop out of the near cliff's foot, its top at about the cliff's height so it is seen
  against the cliff, not the sky: leaning, higher and steeper on its far side, its outline broken by ledges at different heights on each
  side (`RF_SP`, jittered along every edge), broken beds, joints and hollows; a jagged gully runs down it on the diagonal (`RF_GC`,
  `RF_GW`), widening to its mouth; spur and fan are baked once (`ly.c`). Scree is never a peaked cone: a fan comes out of a gully's mouth
  with concave flanks (steep under the mouth, flattening into the ground), one longer than the other, its top as wide as the mouth and in
  the gully's shade; the cliffs (`cliff`) also lay a talus apron along their whole foot that the fans merge into; the rock doorway's scree is
  a talus leaning on the cliff's end face, fed by a jagged chute down it, its long flank toward the step.
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
  reinforcement from floor 6: a veteran, `TIERS[2]`, with the captain's hit points), just past a solved gate or gate puzzle (`gateDue`), in a fork's short way (kind 1), at a secret passage's
  flask (ambush); a barracks floor also posts garrison guards after other traps. Never on a turn chamber's landing (the kind-1 fork's
  guard stands on a landing of the short way: `forkGuard`), in a corridor fill or in a side passage. Snakes (floor 5 on: 1, 6-11: 1-2,
  12-19: 2-3, 20 on: 3-4) only in tunnels (the route's and a side passage's corridor fill's), spaced along the route; a bite costs a heart
  even when he is crouched (crouching only skips the `hurt` state). `guardscan.py` checks it;
  `metrics40.py` and `featurescan.py` no longer count guards or skeletons as traps and print them as their own columns.
- Trap density (unit G1): traps per floor are held to about +15% over v39 (floor 12 about 77, floor 27 about 107), not by shortening
  anything. `LAND_PLAIN`, `CH_PLAIN` (a chamber's landings left plain), `FILL_PLAIN` (a stretch of side-passage corridor left plain, in
  `fillCorridor`) and `FLAT_K` (weight of plain floor in the run's menu) set it; check with `metrics40.py`. A remote plate (P1, P5) whose gate
  finds no room in the turn makes `buildLevel` lay the floor out again, so no dead-end side room is left behind. Timers are sized three
  ways: P4's race by `estPath(acts,cur,true)`, the careful pace (0.55 s a column, a walk +0.4 s, the action table's careful times, measured
  against the bot) times `timerK()` (0.84 tight to 1.08) + 0.3 s, so the tightest is still beatable; P1 detours, double gates and G2
  gates by `estPath` at the plain pace (0.34 s a column) times `timerK()` + 0.3 s; in-line gates (`gate()`) by the run, `(m*TW+16+BW)/RUN`
  + 0.2 s over a closer, -0.1 over a pit, +0.05 on plain floor, times a slack from 1.15 down to 1.03. There is no `WALK_T`. A longway floor always holds a fork (else it is laid out again, and the last resort drops the flag).
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
- Nothing a figure carries lands on the sky (round 25c, owner: "what is that haze around the prince?"): the fill light every figure
  carries (`gatherLights` kind `fill`, `FILL_COL`) lit the backdrop seen through openings, a pale halo that went with him and stopped at
  the sill. Torchlight: the light map keeps the fill's share in its alpha; the scene's alpha is how much of a pixel is not the backdrop
  (the void and `drawBackdrop` are drawn with `G2D.na`, which leaves alpha alone; on the main scene erasers keep it too, `ke`), and the
  composite and the bright pass take the fill off where it is under 1; the figures' shadows (mask r) are scaled by it too. A figure in
  front of the sky covers it, so he keeps his fill to his outline. Classic: `fillCut` draws the fills apart and cuts them where the room
  images are clear, except over the figures' silhouettes. A new full-screen draw on the scene after `drawDynamic` stays under `na`; a new
  dst-alpha blend on the main scene must not read that alpha. The ?wgl=0 fallback still lights the sky. Pictures: `egyptr25c.py`.
- Every figure's silhouette (`glSilhouette`: its lamp shadow, the cut it makes in the sky beams, the beam's capped light on it, the metal
  carve, Classic's beam cut and fill cut) is drawn in its own palette (`silPal`: `guardPal` for a guard). (round 27c, owner: "Soldiers don't
  seem to cast shadows and the light beams are drawn over them") From round 7 to 27b the robbers' head cloth needed a `khat` colour the old
  `PAL_GSIL` lacked, `figDraw` threw inside the try and every guard's silhouette was null: no shadow, beams drawn over them, both modes. A
  new palette key read by `drawFigureHD` must exist in every palette that reaches it. Pictures `egyptr27c.py` (r27c_guards.png).
- The Blue Chambers' glaze and faience walls (mist pass, `u_lx.y`, `u_lx.w`; round 27d, owner's screenshot: "slanted bars ... moving ...
  drawn over windows and light beams") are soft noise patches in the lamps' light that swell in place, times the scene's alpha (never on the
  sky); they were a sine of x and y: bright slanted bars sliding along the dado, cut into dark bars by his lamp shadow, and laid over the
  openings. No travelling bands in a look effect; sharp single glints stay in 2D (`lampGlints`). Pictures `egyptr27c.py` (r27d_bars.png, .gif).
- The floor's own looks (round 31, owner, floor 13: "I love the effect of the floor, but it doesn't look correct in the perspective ... And it is
  drawn on top of things including the prince"): the Forges' embers (meroe) and the wet flagstones' sheen (dungeon, crypt) were in the mist
  pass, a band from the slab's front edge to its back edge wherever a noise of screen x alone was high, added over the finished scene at a
  quarter of the resolution: upright bars over his feet, a saw's blade and its slot. Now they are the composite's (`floorFx`, `GLSL_FL`; full
  resolution, no new pass) and lie only on the floor's own top face as the scene still shows it: the room's picture marks that face with
  alpha 254 (`slab(...,mark)`, room pictures only), anything drawn over it in the scene makes the pixel 255, so a figure, trap, slot, rubble or
  shadow is never painted over (the ?wgl=0 path has no mark and keeps the old overdraw). A thing lying on the floor uses its coordinates: `d`
  across the slab, `s` along it at the front edge, so it leans along the depth diagonal. The embers glow in the flagstones' joints as slab()
  draws them (`FLOOR_FT`, `glcFloorFt`: each tile's joints and its top face; unit 8): a hot thread, its glow and a warm pool, lumps that pulse.
  They keep v76's strength (owner: "I love the effect"): the mean light they add over the floor's face stays within 20% of v76's
  (`egyptr31.py --measure`: Torchlight 10.4 / 11.1, Classic 0.23 / 0.25 R+G+B levels a pixel).
  The sheen is a reflection, so its streak stays upright under the light (in this view world vertical is screen vertical: the plane of the
  light, the eye and the vertical draws as a vertical line); the light is mirrored about the wall's foot, brightest at the front edge (the
  eye meets every point of the floor at the same angle here), and its wet patches lie on the floor. Classic's embers (`classicEmbers`) lie in
  the same joints, off trap tiles and saw slots, cut where a figure stands. A new floor look goes in `floorFx`, never back in the mist pass.
  Pictures and numbers `egyptr31.py` (r31_sheen.png).
- Torchlight's ambient light never drops under `AMB_MIN` (0.45 of full on its brightest channel, `glAmbK`; owner, v56 and v57: the Forge by
  Moonlight fell to 0.26). Round 47c (owner: "increase the minimum brightness of the levels. 5-10%"; "Go with C"; night darker "but not so
  dark that you don't see traps"; the sky "Stay as is") adds `AMB_LIFT` [dusk .10, night .075, dawn .10] of full to the ambient's brightest
  channel in both modes, the colour kept, each mode from its own level (Classic stays brighter): Torchlight's floor is .55 at dusk and dawn,
  .525 at night. It lights what the rooms draw only, never L0: Torchlight adds it in the composite times the scene's alpha (`u_ad`,
  `ambLift`), Classic fills its light map with it and takes it back where the sky shows (`ambUp`, `ambSkyCut`, `skyMaskDraw`, shared with
  `fillCut`); the light map keeps v88's ambient (the shafts', embers' and bloom's tests unchanged). `__HK.AMB_LIFT` for tests. And each sky opening adds a soft bounce light where its beam meets the floor (`gatherLights`, Torchlight only).
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
  (`beamBlockers`, quads from drawJaws'/egSlab's geometry): Torchlight tests them exactly in the shader (`u_bk`, `blkC`: up to four, `GLC_BK` 8 since round 38a, those in a beam's haze
  first; a lift's or sand lift's mouth slab that is down blocks too, both modes, `blkSlab`; the march softens them over at least its step, or a thin blade leaves a staircase), so the beam behind them is shaded and only the near half
  of the haze lies over them, no footprint, no figure light; Classic clips them and their shadow (`ryHull`: the
  quad swept along the light, a clip; only for one in a beam's haze, `ryBlkLit`) out of haze and footprint. Pictures and numbers: `egyptr20a.py`.
  Round 20b (owner: the wedge to the floor read crude): Classic draws such a beam `RY_SH` (5) times at a fifth of its strength, each cut by
  its own hull (the quad swept 12 to 72% of the way to the floor and spread 8 to 70%), so the shadow is whole at the blade and fades and
  widens to nothing short of the floor (an area light's penumbra); clips only, never a scratch canvas.
  (round 28b, owner: "jaggies in the light beams") A figure's shadow down the haze is soft: its edge was narrower than a texel of the
  shafts' quarter-size pass, so the bilinear upsample stepped it (the figures' mask, `glcOcc`, was an eighth, and the march multiplied a dozen
  readings of it into T). The mask is a quarter now; each step reads it 1-2-1 across the light (`figC`, at least 1.25 texels apart, wider
  with distance: a penumbra like the walls') at a quarter step either side along it; the figure shades by the most any step saw (`cf`, one
  occluder), walls and blades still multiply; the haze over him is cut from 0.35 of the mask (inside his outline: no dark fringe); `u_of` skips
  the taps when no figure is near a beam. No jitter, no new pass; Classic draws no figure shadow. Pictures and cost: `egyptr28b.py`.
  (round 35b, owner after v80, floor 17: "light beam through sand", "light beam in front of the saws") Sand stands in front of the room's
  whole depth like a wall's front face: a well's body and a sand lift's column (its slab's front edge down) take no beam light, haze, rim, pane
  or footprint, and no floor mist or wall look either (an arch or breach in a pit's back wall, drawn behind the sand, had its lit rim and streaks
  laid on the sand halfway down the column, floor 17 seed 19). Their outline this frame (`sandSegs`: the surface as drawn, wellSolve's S, flat
  stretches merged, at most `SDMAX` 24 segments) goes to the shafts' and mist shaders (`u_sd`, `u_sf`, `sdC`) and to Classic's cut with the walls
  (`ryBeams2D`, `rySandCut`); above the surface the pit is air (a drained well is lit). The footprint is light on the floor's top face, never on
  what stands on it: Torchlight's composite and bright pass add it only where the scene's alpha shows the floor (`fpGate`, `GLFX.fpgate`):
  round 31's mark (254), what the room's picture lays on the face (`RL_A` 251: breach rubble, fallen things, spike holes, a broken end, drawn on
  a scratch canvas and marked where they cover the face, `rlBegin`/`rlEnd`) or a flat thing drawn live (`fpMark`, `FPM_A` 254: plates, cracked
  slabs, planks, closers, a vent's grate; its tile 128 in FLOOR_FT, `FT_FLAT`, so floorFx keeps off it as before); 255 (a saw's blade and slot,
  stakes, a flask, a lamp stand, a fallen block) is left out, a soft shadow under 254.5 is not. Classic cuts the same things' boxes
  (`ryStand`, `ryStandCut`). Look only. Beam frames away from sand and things on the floor (beamshot's floors, frozen): Torchlight 0 to 0.1% of
  pixels differ by more than 4 levels (feet, lamp stands, flasks), Classic 0 to 0.07%. Pictures `egyptr35b.py` (r35b_beams.png).
  No staircases (round 46a, owner: "The jagged light beams. I think we fixed this at least half a dozen times. Let's try to specify it
  better and to document and enforce it"; rules S1-S7 in `dev/docs/rendering.md`, "Low-resolution passes (S, M): no staircases"). The S
  pass (and M) is a quarter of the canvas, read bilinearly, at every `GLP.rs` (a texel 4 device px on the phone, 8 with Battery saver): an
  edge it draws narrower than that is a staircase, so each fix of one edge (v61b, 15, 20a, 20b, 28b, 35b) left the next. v87 had three:
  (A) `ryProfile` stored each line's first and last open pixel as its entry and exit, so at each pier of a run of arches the entry jumped
  ~19 px and the haze with it (a dark stepped wedge from each pier's top: the owner's shot, floor 26 at night), read `NEAREST`, the five
  coverage taps too; (B) the floor between a pixel and the opening cut by `if(t>tm)break;`; (C) a low ceiling's lower edge soft over 1.5 px
  under a march stepping 5-10 px, its ends three hard taps, walls' `e` under the step. Now: `ryPrefilter` once per shape and floor (lines
  within 3.5 sigma take the nearest line's entry and exit, `a` 255 `r` 0; `r` and the entry blurred across the lines by `RY_BLUR` 1.4 world
  px; the exit never, S5: blurred, the rim rose into the air), read `LINEAR` (Classic shares the profile); penumbra taps at least a texel
  apart (`4 u_cam.z`); the pane's edges over `max(1, 4 u_cam.z)`; the floor by a weight `smoothstep(tm+EZ, tm-EZ, t)`, `EZ = max(6, 16
  u_cam.z)`; walls `e = max(.07 + ts .0022, st/32)`; a low ceiling's lower edge over `max(1.5, st, 8 u_cam.z)`, its ends ramped (`lowS`)
  and its top toward the wall above. The rules: S1 no branch, threshold, step, break, continue or `NEAREST` read on a per-pixel value unless
  ramped over two texels (`8 u_cam.z` world px); S2 every transition at least two texels at Battery saver; S3 discrete samples overlap (soft
  width at least their spacing); S4 the profile prefiltered, read `LINEAR`, its exit not blurred; S5 the lit rim and pane stay sharp along
  the axes and the light, never blurred into the air; S6 the same for M and any future low-resolution pass; S7 shaders that work out world
  positions (`wpos`, `u_cam`, `tile(`) in highp (`GLCHEAD`'s guard; `?prof` and `?bench` show the device's fragment highp, `glPrecStr`).
  Test switches: `window.__RYOFF` (no beams, both modes), `GLFX.ryClean` (no haze drift, motes or dither, `u_cau.z`). `beamjag.py` (in
  suite.py, render, four GPU jobs) measures STEP (the share of lines along the light whose residual over a Gaussian of three texels crosses
  zero three times at over 2 levels): every theme at every hour and the forced cases, both modes, `GLP.rs` 1, .75, .5 and Battery saver:
  pass at STEP <= 0.012 (0.03 saver; the research's 0.005 / 0.02 sit inside the GPU's run-to-run noise of +-0.002 on two dawn arch runs):
  v87 fails 71 of 164 frames (15 of 82 saver), up to 0.115 (Garama by moonlight, a low ceiling's ends); round 46a: worst 0.0095 (0.0199 saver), 162
  of 165 under 0.005, 246 frames in 5.8 min. Also from the full run: the haze takes a smoothed exit (`soA`, read 1-2-1 two texels
  apart: at a pier the exit jumps 10-17 px, the haze's side followed it), the profile runs `RY_PEN` 36 px past the shape (the penumbra
  taps' reach, `sp` at most 18) so its ends never cut them; beamjag fails if the shafts' shader does not compile (a scoping slip in this
  round fell back to Classic's beams silently). Cost +2 to 4% of the S pass. Look only:
  `layoutcmp.py` against v87 same. Pictures `egyptr46a.py old.html new.html [outdir]` (r46a_f26.png, r46a_f50.png, r46a_f7.png,
  r46a_f11.png: before | after, 3x crops at each `GLP.rs`, Battery saver and Classic; r46a_f<N>_<mode>_phone.png).
- The view through openings (round 25e, owner: "the backgrounds seen through the windows sometimes change wildly ... especially when
  going downwards") follows the keep, not the screen: each opening (window, open arch, breach) looks out at the eye level of its own storey.
  Its view is placed as it was when the camera rests on the floor under the opening (`bgAnchor`: openings that touch share the anchor of the
  largest, found once a floor in `L._bgA`), and moves with the keep but for a vertical parallax of `BG_VK` (0.2) of the camera's travel away
  from that rest for the farthest layer, (1-f) of it for a layer of depth f (`bgLayerY`); the sky's gradient and the dawn sun go with the
  farthest layer (`BG_FSKY`). Horizontal parallax is unchanged (f). Before, the view was pinned to the screen vertically (0.18 f, clamped at
  22 px, the sky not at all), so every opening slid over it at the camera's full speed. A pure function of the camera and the opening:
  never key the backdrop to the player, a row he is in, or anything the view culls. The strips carry on past their edges (ground below,
  what hangs from above above); the moon is a layer of its own drawn only for the storey the camera is at (crossfading over `BG_MOONW`
  48 px), so stacked openings do not each show one. The screen shake moves the view with the keep. Check with `egyptr25e.py` (the computed
  view through each opening must move under 1 px a frame in descents; it measures the pixels too).
  Each layer's factor is the depth it shows (round 27b, owner: "The background moves too fast ... keep the illusion of distance between that
  background and our walls and windows"): a layer Z away from a camera Z0 from the play plane moves f = Z0/Z of the walls' screen motion and
  slides past the openings by 1-f; a thing H m high drawn h px gives f = h/(s H), s = 29.4 px/m (the prince 1.75 m = 51.5 px), so a factor is
  checked against the drawing's own size and what it shows (Z0 5.65 m, a 60 degree view of the 6.5 m frame, only to name depths). Before, the
  factors were 3-10 times too large (el-Qurn at 0.05: a 37 m hill 107 m off; palms at 0.3: 9 m shrubs 13 m off). Now: sky, stars, moon, sun 0;
  clouds 0.002 (+ drift); far land 0.004-0.012; monuments 0.021-0.11; walls, huts, mounds 0.02-0.13; palms and trees 0.12-0.155; a near band
  (`near`, `v` stone/scrub/reeds: blocks, drums, piers, halfa, papyrus; 1-4 m things at 17 m) at 0.25, the nearest anything in the view may be, in
  nine open looks (not `wells`); a far ridge (`farridge`, `haze`: mixed into the sky's horizon stop, `bgHaze`) at 0.002 where the farthest land was near
  (meroe, osiris, deffufa, napata, hawara); interiors keep their hall's depths, ropes 0.25. A new layer takes f = h/(s H) from what it shows, kept
  in order far to near. Outlines repeat in whole periods over the strip (`BGK`; random walks closed by `bgClosed`; rows in whole steps) and the
  strip's copies join on whole target pixels (`sn` in paintBackdrop): no seams. Distance blur keys on log depth (`bgBlurR`). The vertical stays
  25e's (BG_VK 0.2: the view moves 0.8-0.85 with the keep up and down, its slide held under 1 px a frame). Look only, both modes.
  `egyptr27b.py` (table of layers, the equation, screen speeds, pan strips, the cost; r27b_parallax.png/.gif).
  One horizon per storey (round 47b, with the courts, below): every opening of a storey shares the window's anchor (`bgFoot`: a window's foot
  is in the headroom row; arches, breaches and court bays count theirs a storey up); at the camera's rest on the floor every layer's eye line
  is the floor's eye, 44 px over its back edge (`bgEyeY`, `BG_EYE` 67.2), and a layer of depth f lies 29.4 f Hc px under it (`bgHc`, the keep's
  height over the land, 9 m + 0.6 m a floor to 60 m), replacing the uniform `sink`; the interiors (`inner`) keep their old place. `viewscan.py`.
- Doors are drawn live, but Torchlight's relief reads the room's picture: the back wall's art is flattened under each doorway and its
  frame (`drawRoomStatic`). `doorscan.py` checks every door (floors 1 to 48, both modes) for art over the opening. At the exit he
  climbs the doorway's stairs tread by tread (`EX_*`, `P.exS`). (round 26f, owner: "the prince climbs the wall, he should instead
  disappear on the stairs"; exit D "into the light") He walks to the doorway's middle facing his way, turns to the stairs if he came
  facing left (`EX_TURN`; the stairs recede right, `P.exX` never takes his facing), and from the first rise (`EX_CUT`) is cut at the
  opening's head and jambs (`doorClip`: the lintel's line or the round vault, `doorHead`; SDLPoP `clip_char`): never at the ceiling's
  edge. His own pixels then warm and whiten toward the stair light and fade (`drawPTint`: the figure drawn whole into a buffer, tinted
  source-atop, laid down at an alpha; never a glow, haze or bloom round him), gone at `EX_GONE`; the doorway's light swells
  (`exitSwell`: the door light in `gatherLights` in Torchlight, `drawDoor`'s additive sprite under him in Classic) and the card comes at
  `EX_N` (about 1.7 s from Up). Footfalls on the treads, `stairsaway` (his steps on, out of sight, 0.5 s), `exitlight`. `EXF.look` off
  draws him plain (stairscan's feet). Entry (E1, PoP's start door, `start_level_door`): on a fresh floor only (`startLevel(n,-1,true)`:
  next floor, new run, Restart; never a checkpoint, respawn, Continue or rewind; no rewind snapshot or floor time while `P.state` is
  `enter`) he comes out of the entrance's dark opening (`EN_DX`, `EN_DY` of depth, a silhouette taking its colours, `P.enK`), walks to
  `L.start.x`, control at `EN_CTL` 0.62 s; the leaf (`entryOpen`, from `L.enG`, a function of the clock) drops from `EN_DROP` over
  `EN_FALL`, speeding up, with `doorslide`, a `thud`, a small shake and a landing dust cloud (`entryTick`). The bot waits out the
  state (`opts.entry` plays it). (round 16c) The stairs are the
  same in every style; his first step also lifts him `EX_UP` (from the floor's middle depth onto the tread, which starts inside the
  doorway), and his stride moves only while he rises (`P.exQ`), so a planted foot stays put; `stairscan.py` measures feet against the
  drawn treads on floors 1 to 48 (both facings since round 26f), checks no pixel of his outside the opening's head and jambs during the
  exit (both modes and facings) and the entry (control, the leaf, never replayed, the bot from the entry). Pictures `egyptr26f.py`. Stone slabs (portcullis, lift mouths) are rubbed out of the relief whenever they are down
  (`glRelSlab`: the back wall's courses and friezes were embossed on them); `openscan.py` checks windows, gates and lift mouths for
  wall art over the opening (floors 1 to 48, both modes; `EGP.noover` leaves out the hangings and lamp scars drawn after windows).
- A dart shooter firing left sits on a wall's hidden left face: no head is drawn and its darts come from behind the front face.
- Lifts (v60, owner): no wall plant or kick inside a lift's shaft (`inLiftShaft` in `wallTouch`, from v59; since round 48b only a kick shaft's foot locks him into the chimney, `chimFoot`; `liftkick.py`). Lift parts are cut
  out behind the walls' front faces in front of them (`liftOccl`), the counterweight runs in the back wall behind the platform, and
  they follow the stonework's wear (`liftWear`). Paternoster slabs and a counterweight platform stopped mid-shaft are solid to him in
  the air (`liftAir`); a slab coming down on him at the foot steps him aside, never hurts. A ride held on Down ends standing (`P.liftHold`).
  A mouth grating on a shaft's right edge is drawn after the shaft's contents, the rider is cut by `liftOccl` too, and the shaft's
  back-wall parts are cut by the side faces beside it (v61); `liftscan.py` checks every lift for pixels over walls and gratings.
  Mouth slabs (round 16c): a slab on the shaft's left edge is drawn after the shaft's back plane (shade, channel, counterweight) and
  before the ropes, beam and platform (its broad face is the shaft's side); the call plate's cell is cut round the slab (`liftMouthCut`)
  instead of the slab's foot being drawn again; a slab's cast floor shadow falls only on floor, not into the shaft; wear chips on a
  slab are capped in px (`stoneWear` cap: a share of its height made a slit that sheared it).
- A slab always slides up into stone (round 25d, owner: "lift slab with no ceiling above it"): the open-hall pass (headroom over
  every floor) keeps the lintel over gates, blades and a counterweight lift's top mouth and shaft top (it opened those two cells on every
  lift, so the shut top slab stood free in the hall); it still draws their random number, so nothing else moves. The sheave turns in a slot
  in the lintel (`liftRig` by = top-9). `slabscan.py` (floors 1-48, 3 seeds, every portcullis and lift mouth) must print `slabscan: ok`;
  pictures `egyptr25d.py`.
- Lifts drawn clean (round 26a, owner: "windows or walls or wall trims are drawn over the lift mechanisms", "at the top the lift slab is
  drawn in front of the wall", "when at the bottom the slab digs into the tile floor", "part of the door slab doesn't respect the shadow"):
  no arch (recess or opening) and no breach in a lift shaft's back wall, nor a breach in the cells beside one (`liftCell`, `liftNear`:
  every cell of a shaft from its top row to its foot; look only, hashes, no generator stream). Torchlight's relief is rubbed back over
  every lift part that moves (`glRelLifts`: slabs, platform, counterweight, wheels), as over mouth slabs and sand. Everything a lift draws
  is cut by what stands nearer in the column right of its shaft (`liftNearCut`: walls' whole front faces, strip under a floor's lip
  included, and each floor tile's top and lip); a paternoster's bottom run is a pit: the foot floor's lip stands in front of a slab there
  (it shows only its top, flush). An egSlab's piece above the ceiling's edge (round 14's top pass) is in the ceiling's shade (0.9).
  `liftscan.py` also checks these (near, foot, wedge, relief, and arches/breaches in shafts on the tiles; the paternoster at a slab on its
  bottom run and at the top beside the right landing); pictures `egyptr26a.py`.
- The lift's foot (round 37a, owner after v81: "The lift shafts, at the very bottom the floor tile should be missing because the moving tile
  of the lift will replace it"). Until v81 the room's picture drew an ordinary floor tile in the foot cell of every shaft (its feature or base is
  FLOOR, for play), and the platform resting there was drawn over it: with the platform up (and the bottom mouth slab shut) a plain floor
  stood at the shaft's foot, and the sand lift's foot showed that tile's lip under the sand. Now the counterweight platform and the sand
  lift's slab are the floor there: the room's picture draws no tile in the foot cell (`liftPit`, `liftPitDraw` in `drawRoomStatic`; not in
  `aoFloor` or Classic's embers) but a shallow pit `LP_D` 5 px deep, the platform's own thickness: the shaft's back wall going on down into it,
  the end of the floor (or the wall) beside it as its left face with a lit top arris, a dark stone floor with its front edge on the front plane
  in the lips' shade; resting at the foot, the platform's top and lip are exactly a floor tile's (`SURF(rB)`, lip 5 px), and Torchlight's
  relief is rubbed back over the sand slab at rest there as over the platform (the platform by `glRelLifts`, the sand lift by its own `glRelBox` calls). The sand goes on down into the pit (`sandCut`,
  `sandSegs`, its relief box) and the outlet sits on the pit's floor. Look only: the foot cell stays FLOOR in play, and nobody stands on it
  while the pit shows: a counterweight lift's bottom mouth is shut while the platform is away, he rides inside the shaft in state `lift` and
  leaves it only at an end, plates are pressed only by him, a movable block or a falling slab (`updateBlocks`, `jamAt`; none reaches a lift's foot), and the far side of the foot is wall in 714 of 716 lifts (floors 1-48, 3 seeds);
  the 2 whose far side opens on a drop (floor 37 seed 60685, floor 44 seed 53683: he could climb onto the foot from the storey below) keep
  their floor tile. A sand lift's foot is held by its mouth slabs (`f.ms`) until its slab has come down for good. The paternoster's foot
  keeps its two tiles: its slabs never rest there and he walks into its foot and lands on it (`chainGround`, lifttest (c)), so a pit there
  would have him stand on air. `liftscan.py` also checks the foot (pit: no floor tile drawn in a pit lift's foot cell, `LIFT_DBG.tiles`, one
  in the others' and the paternoster's; flush: the platform at rest covers the floor lips' rows and the rows above them and nothing under,
  against the frame with no lift). Pictures `egyptr37a.py` (r37a_liftfoot.png: v81 | 37a, both modes, each lift kind at and away from the foot).
- A ceiling at his height (a WALL, or an upper floor's slab, `ceilY`) makes any floor jump the low leap (v60, owner), and the head
  clamp holds every frame; a saw that would sit under such a ceiling becomes spikes in place (the low leap cannot clear it).
  Check with `lowceil.py` (the jumps) and `sawceil.py` (the saws, round 38c: 4 of 519 saws on floors 1-48 x 3 seeds, the bot played over each).
- The chase is the dark (round 29, owner: "instead of a sandstorm I want a storm of darkness ... think of Anubis"; "100% black opaque,
  like rips in the scene, and on that background the eyes, the jackal"; the granite plug and the sandstorm (v60's boiling dust, `STB`, its
  bakes) are gone). The burial ground's night drives the thief out; its material is Tutankhamun's Anubis (Cairo JE 61444: black over the
  wood, gold leaf in the ears and round the eyes, calcite and obsidian eyes). Opaque black, never a haze: a rip in the picture with a torn
  edge (`dkTear`, `dkSplint`: piecewise-linear noise, straight runs and corners, crawling), gilded here and there (`DK_GOLD`) and a gold crest
  along each floor at the kill line. One table a frame (`dkTable`: the front per world px of height, the ragged top and foot per px of
  width) feeds both modes: Torchlight's `glStorm` draws it over the finished frame at full resolution (analytic coverage, no MSAA on the
  pass; the composite's vignette), Classic's `stormLayer2D` after the haze (`drawDark2D`), so it stays black. It opens from a crack as it
  wakes (`dkOpen`). Its edges (owner: "take care at the edges, some kind of blend or lens effect ... tatters at the edges ... in both modes"):
  a soft dark falloff just outside the tear (both modes); tatters (`dkTatters`, `dkTatterPath`; `DK_TN` 32, the shader's `u_ta`): ragged
  ribbons torn from its edge, fluttering, each drawing back or tearing loose and flying on ahead, shrinking, opaque, only from the head
  height and up of each row (d 44 to 62) and above the top row, never from the feet to the waist; and in Torchlight a lens: the composite
  reads the scene beside it from nearer the rip (the veil's ramp cubed), so it stretches and bends into it. The jackal (`dkArt`, `dkJackalPath`: black, gold inside the near ear, a calcite eye ringed in gold with a kohl line, a
  gold collar and a gold edge where light would catch) slides out of it at his height, its jaw just over his head and its neck back in the
  dark, when it wakes (0.3-3.2 s) and whenever it is within about two tiles of him (`dkLook`, a pure function of the chase, his height and
  the clock); otherwise pairs of eyes open, blink and close in it. It eats light: lamps ahead dim at most `DK_DRAIN` and gutter, behind
  it they are out (`dkDrain` in `gatherLights`); the air before it greys and darkens (the composite's veil, `u_sd`; Classic a shade); his
  shadow is pulled back along the wall toward it (`drawShut`: three leaning copies of his silhouette, never on the sky through an
  opening). At the arch dawn breaks it: black tatters with gold edges fly past and part round him, holes burn through it with gold edges, a
  warm flash; flakes settle as ash. A jackal howls far off as it wakes (`howl`). Fair as before (death `P.x < wx+4`): `stormfair.py` checks
  the rip on every storm row without the jackal and eyes (`stormProbe(torch, look)`), and with them on his own row. Look only: speed,
  rows, kill line and bot unchanged. Pictures `egyptr29.py`.
- Themes (branch egypt, owner): twelve themes of Egypt, Kush and the Sahara, four floors each (`THEMES`, `themeOf`; the order repeats every 180
  floors, below); time of day and wear still turn every 20 (`progOf`). A theme has a drawing `style` (dungeon, palace, tile, forge, crypt: the
  style-keyed tables) and a `look` (its backdrop `BGART`, hangings `TAP`, Torchlight light `lk`, effects `LFX`). The generator never
  reads the theme: it builds by `L.gstyle`, the old five-theme turn (`GEN_STYLE`), so floors stay as they were. Arches and doors
  are post and lintel (the dungeon style's vaults stay round); windows are too in the palace and tile styles (the dungeon's is a slit, the
  forge's a round hole, the crypt's a star). A door's head is a flat lintel block (a winged sun disc over palace, tile and crypt doors,
  a torus frame on palace and tile); the cavetto cornice is the arches' (`drawArch`). No churches, crosses or the Ark, no living peoples as enemies
  or decoration. Pictures and sources: `egyptshot.py`, `egyptfx.py`, `egyptpage.py` (egypt_themes.html).
  Built in (owner, round 3): the themes' lamps (`drawLampEg`) and the re-skinned traps are on by default: granite portcullis
  (`egSlab`; the lift mouths are `egSlab`s too, in the theme's own stone `THEME_STONE`, bars only with `EGP.traps` off; no metal mask; modelled by the key light: lit narrow face, a crisp arris, a core-shadow band and
  dark far edge on the broad face, a cast shadow on floor and wall, raised in round 16c so the edge reads in every theme), sliding roof block with sand (`egRoofSlot`, `egRoofHang`, `egRoofFall`, `egRoofLying`, `roofStone`), sand floor, pale
  polished bronze stakes (`SPK_C`, round 47d, owner: "I am constantly missing spikes"; before, bronze tips on acacia shafts) (the chase was a granite plug from round 4 to v75; round 29 made it the dark, below).
  Look only: hit boxes, timing, generator and bot unchanged. `EGP={lamps,traps}` turns them off for debugging (metaltest's
  gate scene tests the iron gate that way). Nut's sky clock
  (`nutClock`, round 8; round 4's Karnak clepsydra and round 7's barque clock, `barqueClock`, kept for pictures, were rejected) replaces
  the hourglass as look and words ("sky clock", "hours"): the checkpoint (`drawHourglass`), the HUD's measures and gate
  timers (`drawGlass`), the rewind's grade and words; `S.sands` and every timing are unchanged. Theme order: `themeOf(n)` takes the
  block's generator style (`GEN_STYLE[block%5]`) and picks the theme by light and 60-floor turn from `SCHED` (repeats every 180
  floors), so a floor's theme always has the style it is built by; `egyptaudit.py` keeps a copy of `SCHED`. Title
  Dawnward; fonts Rokkitt (display: FLOOR, the gate timer, the floor's banner) and Jost (text, the floor's time). Not renamed: the cache key `hourglass-keep-vN`, the save key,
  the repo and its URLs.
  Round 16a (owner): a fallen roof block (10 px high) is a low obstacle he steps over with no key: it no longer stops him in
  `clampMove` (guards still keep to their side) and `blockStep` lifts his drawing onto it in `updateLook`; the bot runs over it
  (`runover`). A cracked slab (`loose`) has two looks chosen by `looseWell(o)`: over a pit walled in on both sides it sits on a sand
  well (round 16a's `drawWellSand`, since round 21b `drawWellGroup`: the level falls at a steady `WELL_V` 150 px/s, Beverloo; a funnel crater; the slab sags and folds in two,
  `slabHalves`), anything open beside the space under it is a corridor (grit, `slabChunks` in four pieces, `dustCloud` at the hole
  and the landing cloud `DUSTC`). Play is unchanged for both (0.5 s, `DROP_G`). The sand lift (`sandLiftSeg`, a lift with `f.sand`):
  a `banner3`/`banner4` move is built as one about 37% of the time (`sandOr`, a hash: no random stream, so layouts are identical;
  never in a fork's short way or a G3 gate turn; segs `turn-sand3/4`); stepping on its slab starts it, it sinks at `SAND_LV` 140 px/s
  after `SAND_LW` 0.25 s and stays down; bot action `sandlift`; `estPath` times it as the slide. Checks: `lifttest.py` (sand3, sand4
  and its own case), `liftscan.py`; pictures `egyptr16.py`.
  Always a shaft (round 26e, owner: "sand lifts must always work within a shaft otherwise they don't make sense"): wall beside the sand on
  every storey above the foot (the open-hall pass keeps the cells either side of the shaft from its top row to its foot as walls, its window
  draw made all the same, as round 25d's lintel: no stream moves), and the foot storey shut by granite mouth slabs (`f.ms`: the exit side
  always, the far side where a corridor runs on there; `sandMouth`, `sandOpen`: up over the ride's last `SAND_MD` 28 px, a function of `f.y`;
  play already held the exit by `f.gB`, the far mouth now holds too). Where a later run, passage or fill opened a side, or left a drop
  beside the foot (16 of 322 on floors 1-48, 3 seeds), the move is the banner slide instead (same tiles, bot action `slide`, seg
  `turn-bannerK`). (round 26g) The walls kept over the foot storey's cells beside the shaft are a ceiling at his height (`ceilY`): a jump the
  route takes on the foot storey after the ride whose full arc meets them (beamOverhead's test) would be the low leap and fall short, so that
  move is the banner slide too (13 more of 344 on floors 1-48, 3 seeds). `sandshaft.py` (floors 1-48, 3 seeds) must print `sandshaft: ok`; pictures `egyptr26e.py`.
- The closing plate gives no warning (round 48a, owner: "The red tiles that slam shut the doors: they shouldn't be red and have a different
  design. They should look the same and have no warning"; chose B): a `closer` is drawn by the `plate` case (`th.top` washed 18% white, the
  same press), both modes; no approach hint (a slab closer shows `slabplate`, true for it too), `closer`/`slabcloser` reworded and shown only
  after the slam; the Grab label's `hazardEdge(64, true)` leaves closers out (no 'Step'), while standing and running Jump still edge-walk to
  its lip (bot `dashjump`, the in-line timers); the jam message and help page neutral; `plateClick` plays `plate` (a stone click) as a foot
  first comes down on either kind. Glint, `CTL_WATCH`, `FT_FLAT` were already the same. Generator, `L.path`, timers and the bot unchanged
  (`layoutcmp.py` v89 same). Pictures `egyptr48a.py old.html new.html [outdir]` (r48a_closer_<mode>.png, r48a_phone.png).
- No hint messages (round 49a, owner: "the Dark Souls thing ... the part where you discover how and what works. I would drop all hint
  messages, rely only on subtle graphic hints ... I would keep the how to play screen that describes what the buttons do"; his answers on
  the research in .claude/research/r49hints; `dev/docs/gameplay.md` "No hints; learned moves"). Gone: `HINTS` (53 texts), `checkHints`,
  `hint()`, its queue, the 'hint' banner kind, round 48a's post-slam `closer`/`slabcloser` and every message that told what to do or what
  happened: the flask names, the rewind's "N hours left", the sky clock's "...If you fall, you rise here.", "No room to draw a sword..." (the
  `bump` alone), "Sealed..." at a shut exit (a rattle, `Snd` `sealed`), `gateMsg` and the exit plate's line, the slab's jam, the crumbling
  chain's "Run!", the dark's waking and dawn, the ambush, the death card's spikes tip. Kept: the Grab button's word, the floor's banner and the
  card's `FLAG_TEXT`, the Crossing's pad cue, the death card's cause, Rewind and rise lines, `msg` itself (the bench's lines). `learn()` and
  `S.learned` stay (`LEARN_IDS`) for the looks that read them (jgrab's jet stream until learned, the swing's 0.75 and the kick shaft's 0.65
  after; `shaft` is learned at the Y, `chimY`, since nothing learned it after round 48b); `S.hints` stays in the save unused;
  `__HK.HINTS` is an object of `LEARN_IDS` (`__HK.HINT_MOVE` their Set), so the tools' `for(const id in H.HINTS)` loops still set every
  learned flag. In place of `gateMsg` and the door's line (`gateCue(g, big)`, from `pressPlate`, `jamAt` and the `xplate`): the gate's sound
  from where it stands (`Snd.playAt(n,x,y)`: `grind` for a timed gate, `door` for one that stays open and the exit; a lowpass, gain and
  `StereoPanner` between the sound and the master: pan dx/280 to 0.9, gain 1.15 - d/900 to 0.35, cutoff 9000/(1+d/220)/(1+0.7 storeys)) and,
  if it is out of view, a glance (`glanceAt`, `GLN`, `GL_T` 1.6 s: the camera's target eased toward it over `GL_IN` 0.35 s and back over
  `GL_OUT` 0.5 s; input stays live and he is kept `GL_M` 44 px inside the view's sides and wholly in it, so it costs no time and no timer is
  held; once a plate; never in a chase, a fight, dead, a test load (`__HK.load` sets `GLN.off`) or `?bench`; a rewind or new floor ends
  it). PoP 1989 has neither (SDLPoP: a plate's door opens off screen in silence); Zelda and Metroid Prime cut or pan to a door a switch opened,
  Dark Souls plays its far sound. How to play (`#how`) keeps the buttons and the short rules: Run; Jump; Up, Down (with 48b's chimney: Up
  kicks higher, Down lets go, Up at the top leaps out); Grab (its word, catching a ledge or tapestry, the careful step, push, pull, drink,
  strike, Up blocks and Down sheathes); after a fall; the three hours; the flasks' colours; keys. Tests: `hinttest.py` reworked (above, the
  same suite jobs), `r38b_tests.py` `sandhint` checks no banner and `sandfall` learned, `vs_ui.py`'s banner scenes removed. Look and sound only:
  `layoutcmp.py` against v89 same (144 of 144), the bot's runs unchanged. New cues come in rounds 49b and 49c. Pictures
  `egyptr49a.py old.html new.html [outdir]` (r49a_how.png, r49a_death.png, r49a_glance.gif and .png: old | new at phone size, Classic).
- Tells, grit and the swing's beat (round 49b, owner after the round 49 research, "Dark Souls"-style discovery with no words: "rely only on
  subtle graphic hints"; his choices among the research's cues, three built here; `dev/docs/gameplay.md` "Tells"). Look and sound only:
  layouts (`layoutcmp.py` against v89 same), play, the bot and every timer unchanged.
  (1) The tells (Limbo's lesson: the boy's body turns toward what can be used; `tellTgt`, `tellKind`, `TELL`, `tlP`): standing still `TL_D`
  0.5 s (`tellIdle`: nothing held, no live foe, not the chase, no wind, no stumble) his body points at what the spot offers, eased in over
  `TL_IN` 0.55 s (s32), on the target pose before `followPose` (its overlap carries the arm and head after the trunk), dropped the frame any
  input comes (followPose eases it out): `reach` under a ledge he can climb, facing it (`canClimbUp`): the head back 0.48, the front hand by
  skel's two-bone solve (`hold`, `gFx/gFy`: `tellGrip`) toward the lip where his hands would hang (PS.hang's grip from the hang's x and y),
  shortened to `TL_RF` 0.96 of his reach in the drawn hip's frame (P.rdx, the feet on P.y), so it stops short with a soft elbow; `edge` at
  an edge he can hang from (`edgeBelow`): the head down 0.42, a little lean, the back arm out; `stakes` within a step ahead on his floor or
  in the pit before him: the head down 0.4; `flask` a flask on his row up to 44 px ahead: the head down 0.36, the hand a little forward;
  `low` at a low tunnel's mouth (not under it): a stoop (lean 0.36, both knees) with the front hand on the lintel's end 10 px over its
  underside (facing right its front face's edge, facing left its end face at mid depth), looking in; `chim` locked in the chimney (round 48b,
  `P.lock`, planted) `TL_CD` 0.5 s with nothing held: the head up 0.34 more. Order: flask, stakes, edge, reach, low. The prince only; the
  silhouette, lamp shadow and beam cut read P.pose, so they follow. No generated keys: the angles are offsets on the clip's poses.
  `tellscan.py` (play suite, three jobs). Checks: figscan, lowceil ok (the tells are not poses of the table).
  Round 49d (the release suite on round 49c: tellscan failed 4 spots on floors 25, 42 and 48, run only on 3-16 before): every one stood in
  a wind zone (`windAt` 0.12-1.0), where `tellIdle` rightly gives no tell; the test now takes no spot in or within 16 px of one
  (`windZoneAt`). The game unchanged; tellscan 1-16, 17-32, 33-48 ok.
  (2) Grit over a slab's plate (`drawGrit`, `gritList`, `GRIT`): where a cracked slab can jam the plate or closer under it (P2G1, P3G1,
  `f.slabF`; found once a floor, `L._grit`), while it lies (`f.s` 0) single grains sift from its underside at mid depth: `GRIT_N` 14 grains,
  each its own period `GRIT_P` 1.7-3.6 s and fall `GRIT_T` 1.05-1.35 s from rest (y = 0.22 u + 0.78 u^2 of the drop), one cycle in `GRIT_GAP`
  0.35 skipped (hashes of the cell, the grain and the cycle), 1-1.6 px, alpha .4-.75 at the ends faded, `sandC().heap`, and six grains lying
  on the plate's top (at its lift, 2.4 or 1 pressed). Faint, sparse and steady: never the roof block's threads that thicken (sandFlow). A
  pure function of the clock and `f.s` (rewind-safe; nothing allocated a frame). L2 air in `drawDynamic` before the figures: clipped to its
  column and cut by `nearCut` on the rows from the slab's to the one above the plate (fl: the slab's own lip hides a grain until it drops
  below it), never by the plate's row. Not recorded in `SHC` (air). `GRIT.off`; layerscan kind `grit`.
  (3) The swing's beat (`swbeat`, `SWB`): at each turn of the swing (`swingStep`: om changes sign) over `SWB.A0` 0.05 rad the ropes creak on
  the log (two bandpassed noise groans as round 18b's `swing`, which it replaces; that one played only over 0.1 rad), volume 0.022-0.034 and
  pitch x1-1.18 by the amplitude to `SW_CLEAR` (`SWB.k`); while a pump is armed (`P.swArm`) brighter, pitch x1.22 more, +0.006, with a breath
  of air (bandpass 1500 to 800 Hz, 0.16 s): the turn the press must follow is heard. Under the ready chime (0.05). `SWB.log` (an array, null in
  play) records each beat for the pictures. Checks: swingtest. Pictures and numbers `egyptr49b.py old.html new.html [outdir]` (r49b_tells_3x.png:
  each tell old | new, both modes, 3x; r49b_tells_phone.png; r49b_reach.gif; r49b_grit_3x.png, r49b_grit_phone.png, r49b_grit.gif;
  r49b_swing.png and .txt: the swing's angle with each beat's loudness, armed or not, the pumps and the chime).
- Wear marks and the bones of earlier thieves (round 49c, owner after the round 49 research: "rely only on subtle graphic hints"; "All five
  you suggested": the last two built here, to the research mocks' look; `dev/docs/gameplay.md` "Wear and bones"). Look only: layouts
  (`layoutcmp.py` against v89 same, 144 of 144), play, the bot and every timer unchanged; placement from the layout alone (`D0`, `L.segs`,
  `L.lifts`, features, hashes of cells), found once a floor (`wearList`, `L._wear`), no generator stream.
  (1) Sandal scuffs (`wearFace`): on the front face of every wall the route runs up (each `wallrun` seg: the wall the run-up meets, its row
  and the one over it), at the heights his feet strike it (`WR_STEPS` 6, 27, 48 px and `WR_TOP` 69 over the run's floor, fainter): a dark
  translucent sole smudge (the theme's `lo` in shade, `selC` .5) with older fainter ones about it, a pale scratch over it, 4.6 px in from the
  face's edge on the side he runs at (his foot meets the wall's side plane at mid depth, behind that edge; the mock's place). Part of the
  face (L3), in the room's picture after `wallCell`. Kick shafts take none: their chipped grips and jet stream already mark them (the optional
  stance wear was left out as clutter). (2) Drag grooves (`wearFloor`): on every cell of a movable block's track (`lo..hi` on its row, not
  wall: the cells it can stand on), two shallow grooves where its bottom edges scrape (`WG_D` d .2 and .8), a dark line with a lit lower lip,
  worn unevenly (hashes), a small ridge of grit at each end of the track; on the floor's layer of the room's picture (`rlBegin`/`rlEnd`: cut
  by the faces in front, marked as the floor's face for the footprint), so the block, drawn live, stands over them where it is: they never
  cross its face (the mock drew them after the block). (3) Bones of earlier thieves (`bonesDraw`, `bnBone`, `bnSkull`, `bnRibs`): one set at
  the FIRST lethal trap of each kind on the floor by the route's order (the first seg of `L.segs` whose box holds it: a cell either side, a
  row over, three under): a walled spike pit met only by a fall (remains among the stakes: a kilt's rag, a thigh bone and a shin, fallen
  ribs, the skull; not a court's pool, not the sand lift's pit), a banner shaft's foot (at the back of the cell: a torn strip of the
  runner in the theme's cloth, a thigh bone, ribs, the skull), a slicer (a skull and bones at the back on the side he comes from, clear of
  the jaws' plane and slots), a sand lift's spike pit (half in the sand on the pit's floor, `wearSand`, live in `drawSandLift` after
  `sandCut`, below the slab: seen while he rides down, under the slab at rest). Why the first of a kind: the lesson where the kind is first
  met on a floor, not a signpost at each (Dark Souls' corpses mark where others failed, sparsely); 3.5 sets a floor. Lying, partial,
  scattered, bleached and dusty (`WB_C` mixed 22% toward the floor's top), edges the fill in shade (`selC` .58), sockets the deepest shade
  (.42), lit on top (1.12); never upright, no sword, no blood: unlike the skeleton guard in every read. On a route tile (banner foot,
  slicer) every part lies behind his walking line (d >= `WB_DR` .55: he walks in front of them, never over them) and under `WB_HR` 6.5 px.
  In the room's picture (pit, banner, slicer: drawn once; the relief reads them as raised, as the stone; the lamp shadow keeps off the
  floor's top face as before) or with the sand (inside its `SHC` outline and relief rubbing): nothing allocated a frame, rewind-safe.
  Floors 1-48 x 3 (run2's seeds): 47 walls scuffed, 46 block tracks (184 cells), bones 144 pits, 131 banner feet, 134 slicers, 101 sand
  lifts (every floor with the kind). `WEAR.off`; layerscan kinds `scuff` (its own wall faces are its own: marks on L3), `groove`, `bones`
  (the room's picture: the rooms are cleared around their frames); contourscan kind `bones`. `wearscan.py` (gen suite) checks the rules.
  Pictures `egyptr49c.py old.html new.html [outdir]` (r49c_<case>_3x.png and _phone.png, old | new, Torchlight over Classic: scuff, groove
  (and the block pushed a cell), pit, banner, slicer, sand; r49c_all_3x.png).
- Every trap pushes a bot action onto `L.path`; the bot replays that list, so a new trap needs its action in `bot.js`.
- Gate timers are sized three ways (Trap density, above); only P4's race uses the careful pace.
- Pose angles are measured from straight down; positive means forward.
