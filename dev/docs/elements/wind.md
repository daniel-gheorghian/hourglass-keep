# Wind

Wind that blows along a run, against the way he goes, and slows him (round 44). The owner asked for wind "as a force", "as an additional to
the hills", and chose it from round 44's alternatives (W1 to W5):

- **W1:** a steady headwind on a plain stretch.
- **W3:** the drift's own wind.
- **W2:** gusts through a window of the back wall, from floor 13.
- **W5:** the kick shafts' updraft, look only.

The wind is never a help (no tailwind). Jumps into it are shorter ("It should feel realistic"). A gust pushes him back while he stands, and
crouched he holds his place. Hangings on the back wall billow and lamps gutter.

Wind is not a trap or a feature. It is a list of its own, `L.winds`, laid by a pass that uses hashes only after the hills, so layouts,
`L.path`, the trap counts and the timers do not change.

## Round 45c: wind from the openings (owner)

Round 45c (owner: "wind may blow over jumps", "wind follows openings", "random, not predictable", "gusts start earlier, gentler at first", "wind weaker
after a death so a stretch never becomes impossible") replaces round 44's placement. What changed:

| | Round 44 | Round 45c |
|---|---|---|
| Where a zone comes from | any plain stretch, one per 4 stretches, at least one a floor | an opening over the route's floor: a window (`WIND_P.win` 2%, three in four gusts), a large open breach of 4+ cells (`big` 18%, mostly steady: 15% gusts), a small one (`small` 6%, half and half), a court's open side (`court` 25%, gusts); the drifts keep their wind. Each chance times the floor's mood (`WIND_MOOD`, a hash: calm 0.2 for 15% of floors, light 0.6 for 20%, normal 1.0 for 45%, windy 1.7 for 20%), so some floors are still and some blow hard; no minimum a floor |
| Gusts | from floor 13, peak 1.375, one cycle 4.4 s for all | from floor `WIND_G0` 7, the peak by floor (`windPeak`: 1.15 on 7-12, 1.25 on 13-24, 1.375 from 25); each zone its own cycle (`z.gl` lull 1.8-2.8 s, the warning 0.6 s, `z.gg` gust 0.9-1.8 s, fade 0.4 s, `z.T`, `z.ph`, by hash) |
| Jumps | none in the wind (3 cells of clearance from every seg that is not plain floor) | a zone may lie over gap jumps (segs gap1-3, spikes, bridge) and calm segs (flat, puzzle, rem-plate, detour, secret, block, double, skel), a cell clear of any other seg (swings, saws, chambers and kick shafts, lifts, timed traps); a steady zone over a jump is checked by `windJumpE` (the flight's reach in the headwind, `windReach`, normal and low leap, against the gap plus `WIND_JS` 10 px) and weakened to 0.75 or 0.5 or ended short (none needed on floors 1-48 x 3: the gaps under steady winds are 1-2 cells); a gust zone needs no check: in its lull (0.15) every jump is made, and the lull is longer than any run-up and flight (1.6 s) |
| The bot | walks through | waits for the lull before a jump in a gust zone (`windLull(r,c0,c1,need)`: the lull with at least 1.6 s left for a running jump, 1.1 s for a standing one), then plays at full wind |
| A gap under him | no gaps | the push in a gust never takes him over an edge (`windPush` stops at it) |
| After a death | the same | the zone eases: 0.6 of its strength after one death in it, 0.3 after two (`windEase`, `S.windDeaths["floor:zone"]`, counted by `windDeath` in `die()` for the zone he is in or left within 2.5 s); kept in the save, so a rewind (which never restores `S`), a respawn or a Continue keep it; cleared at the next floor. Play (`windAt`, `windCap`, `windPush`, `windDrag`), the dust (`windDraw`), the sound (`windSnd`), the warning's pour (`windWarn`) and the lamps all read `windE`, so all ease together |

Floors 1-48, seeds 1-3 (`windscan.py`):

| Floors | Steady | Gusts | Drifts' | From windows / breaches / courts | Floors with none | Jumps under steady / gusts |
|---|---|---|---|---|---|---|
| 1-12 | 0.53 | 0.42 | 0.19 | 0.47 / 0.22 / 0.25 | 20 of 36 (6 are floors 1-2) | 14 / 8 |
| 13-24 | 0.97 | 1.39 | 0.44 | 0.75 / 1.25 / 0.36 | 4 of 36 | 13 / 23 |
| 25-36 | 0.53 | 1.28 | 0.42 | 0.92 / 0.53 / 0.36 | 6 of 36 | 4 / 19 |
| 37-48 | 1.19 | 1.25 | 0.25 | 0.97 / 1.17 / 0.31 | 10 of 36 | 17 / 31 |

451 stands in gusts (9 s each, no key): none left its zone or fell (pushed 22 px on average, 54 at most). The ease (one gust zone a floor band):
1 -> 0.6 after a death, 0.6 after the rewind, 0.3 after a second death, on all four.

The sections below describe round 44; where they differ, the table above holds.

## At a glance
| | |
|---|---|
| Code | `L.winds` (`{k, c, n, r, dir, ph, src, jm}`): `k` is `s` steady, `g` gusts, `d` a drift's. `c..c+n-1` are its cells on row `r`. `dir` is the way it blows (minus the run's way). `ph` is the gust's phase, `src` the gust's window, `jm` the clearance it was placed with. Placement: `placeWinds`, `placeWinds1`, `plainRuns` (shared with `placeHills`), `WIND_JM`, `WIND_G0`, `WIND_RATIO`. Play: `windE`, `windGust`, `windAt`, `windCap` (`stRun`), `windPush` (`stStand`), `windDrag` (`stAir`), `WIND_MS`, `WIND_GP`, `WIND_DE`, `WIND_PUSH`, `WIND_CDA`. Look: `windTgt` (`updateLook`), `windDraw`, `windSprites`, `windCols`, `drawWindHangs`, `windHangCanvas`, `windRel`, `windGut` (`flame`, `gatherLights`), `windUpdraft` (`drawJetHints`). Sound: `windSnd` with `Snd.wind` |
| Layer | Air in L2, drawn after the figures and the drifts' near halves. It is cut at the floor's front edge and by the front plane's faces (`airCut`), from under the lip of a slab over the row. The hangings are L1, drawn live first in `drawDynamic`. See [layers](../layers.md) |
| Generated by | `placeWinds`, after `placeHills`: hashes of the seed and the cells (no generator stream) |
| Bot | no new action. `walk` holds the arrow through at the capped pace. No take-off or landing lies in the wind |
| Checks | `windscan.py` (placement rules, counts, time added, a stand in every gust), `run2.py`, `p4bot.py`, `forktest.py`, `featbot.py` (0 damage), `layoutcmp.py`, `metrics40.py`, `layerscan.py kinds=wind`, `figscan.py` |
| Pictures | `egyptr44.py old=FILE`: r44_wind.png (before and after, 3x, both modes), r44_phone.png, r44_jump.png (the arcs), r44_gust.gif, r44_jump.gif; `egyptr44.py measure` gives the jumps' reach |

## Example

Floor 13, seed 45261, the Forges of Meroë: a window in the back wall stands over three cells of a run heading left.

1. In the lull he runs through at 96 px/s. The dust drifts along the floor, and the flames lean.
2. In the warning, 0.6 s, sand starts to pour in through the window and down onto the floor. The flames bow and the wind's sound rises.
3. In the gust he is capped at 40 px/s and runs with his near forearm over his eyes.
4. If he stands still in the gust, he is pushed back about 13 px a gust (at most 45 px over two gusts in `windscan`), stepping back on the
   walk's cycle.
5. If he crouches, he holds his place.

On floor 13, seed 45391, the steady draught along five cells caps his run at 65 px/s. A running jump taken into it flies about 77 px instead
of 89.5 px from the first frame in the air.

## In play

| Rule | Number | Why |
|---|---|---|
| Strength `e` | steady 1 (`WIND_MS` 16 m/s, Beaufort 7-8: "inconvenience felt when walking"); a gust's peak `WIND_GP` 1.375 (22 m/s, Beaufort 9); a drift's `WIND_DE` 0.875 | the owner's speeds (below) |
| The run into it | `RUN` (1 - 0.35 e) up to e 1, so 65 px/s; then down to 40 at a gust's peak; a drift's approach 70; the wade 42 (1 - 0.25 e) = 33 | the owner's numbers |
| With it | no change | owner: against him only |
| A jump into it | the drag a person meets, `a = rho Cd A / 2m ((v + w)^2 - v^2)` (`WIND_CDA`: rho 1.2, Cd·A 0.44 m², 70 kg), with v the flight's speed and the time on the game's clock (its gravity, `GRAV / rjK()^2`, against g, at 29.4 px a metre). It slows the flight's speed toward the wind, never reverses it | physics, below |
| The gust's cycle | `WIND_GT` 4.4 s: a lull of 2.0 s (e 0.15), a warning of 0.6 s (to 0.4), the gust (1.375 within 0.25 s, held to 4.0 s), a fade of 0.4 s; each zone has its own phase | Celeste's on/off wind (2-3 s on, 2-3 s off) and its 0.8 s ramp; DKC2's breeze before a gust |
| Pushed back | standing in a gust, no key: `WIND_PUSH` 16 px/s times the share of the gust over the steady draught, downwind, by `clampMove`; it ramps to nothing over the zone's last 20 px, so he never leaves it | owner; Celeste's push (40 to 80 px/s against a run of 90) slowed for a touch pad |
| Crouched | holds his place (not `stand`) | owner; Celeste's `DuckWindMult` 0 |
| Look only | his lean, the kilt and the forearm (`windTgt`), the dust, the hangings, the flames | |

The jumps (`egyptr44.py measure`; reach from his first frame in the air, floor 13):

| Jump | Still air | Steady draught (e 1) | A gust's peak (e 1.38) |
|---|---|---|---|
| running | 89.5 px | 76.7-77.2 px (-14%) | 68.1-68.7 px (-23 to -24%) |
| standing | 57.2 px | 48.3-49.6 px (-13 to -16%) | 41.7-43.9 px (-23 to -27%) |

(The two runs, `measure` and the pictures, take off a frame apart in the gust's cycle and the run-up.)

Sources for the numbers:

- **Drag on a person:** treadmill walkers in a wind tunnel met about 60 N at 15 m/s
  (https://research.dial.uclouvain.be/bitstreams/08429213-c31d-49d4-b961-71a647e2e199/download). A frontal area of 0.139 h², about 0.44 m²
  at 1.77 m (https://research.dial.uclouvain.be/handle/2078.5/245796).
- **The Beaufort scale:** Met Office, https://weather.metoffice.gov.uk/guides/coast-and-sea/beaufort-scale. Penwarden 1973: over 10 m/s is
  unpleasant, over 20 m/s can be dangerous (https://swov.nl/en/publicatie/acceptable-wind-speeds-towns).
- **Long jumps:** most of the wind's effect on a long jump comes through the run-up, and the drag in flight is small at the legal 2 m/s
  (de Mestre 1991,
  https://resolve.cambridge.org/core/services/aop-cambridge-core/content/view/832F203D6E7C071FBD583E5D2204C850/S0334270000008626a.pdf/a-mathematical-analysis-of-wind-effects-on-a-long-jumper.pdf).
  Carl Lewis's jumps gain 0.031 m per m/s of tailwind (Murrie, https://ojs.ub.uni-konstanz.de/cpa/article/view/2720). Ward-Smith's model
  puts Beamon's +2 m/s at +0.31 m. The drag grows with (v + w)², so in a gale it is no longer small. Here the run-up is already capped, and
  the flight loses what its drag takes.
- **Celeste** (decompiled `WindController.cs`, `Player.cs`, https://github.com/TheCyndaquilDecompilers/Celeste_Decompiled):
  - The push is applied to position, not velocity: 40 px/s for weak wind, 80 for strong, against a run of 90. It acts in the air too.
  - The wind ramps in at 1000/s.
  - Crouching cancels it, a wall within 3 px upwind shelters her, and there is no push while climbing or just after a respawn.
  - Here the force is a drag (only into the wind) and the run's cap, not a push, so the wind never carries him anywhere he did not go.

## Placement

`placeWinds(L,n,seed)` runs last in `genLevel`, after `placeHills`. It uses `plainRuns` (round 43's stretch finder, shared): FLOOR with no
feature and no wall over it, on a `flat` seg off every timed stretch, clear of the chase, fighters, clocks, flasks, doors, lifts, blocks and
side passages. Unlike the hills, the wind may cover a lamp's cell. On top of that:

- **Clearance:** every cell of every seg that is not plain floor, widened by `WIND_JM` 3 cells on its rows, is out. So no generated jump,
  fall, grab or swing takes off, flies or lands in the wind, and the drag touches only jumps he chooses to take in it. Where that leaves no
  stretch on the floor (7 of 138 floors, 3-48 x 3), the clearance is one cell (`z.jm` 1). A generated jump's flight lies within its own seg's
  cells, so only a run-up may start in the wind; its take-off, a cell out of it, is reached at the run's speed again.
- **Drifts:** every drift whose cells are clear takes its wind (`d`), over the drift and up to three plain cells of his approach.
- **Steady and gusts:** on the stretches left, one wind per `WIND_RATIO` 4 stretches and at least one a floor from floor 3. Each is 3-8 cells,
  steady (`s`), or from floor `WIND_G0` 13 a gust (`g`) where a window of the back wall (on its row or the one above) stands over it.
- **Sharing:** a wind may share its cells with a heap.
- **Timers:** no wind lies on a timed stretch, so `estPath` and every timer are unchanged. The placement comes after the build, so nothing the
  generator decides reads it.
- **Hangings:** a hanging of the back wall over a wind (its foot within a storey above the row) billows (`hg.wz`).

| Floors 1-48, seeds 1-3 (`windscan.py`) | Winds a floor | Steady | Gusts | Drifts' | Hangings | Added to a held run, s a floor (mean, max) |
|---|---|---|---|---|---|---|
| 1-2 | 0 | | | | | |
| 3-4 | 1.00 | 6 | 0 | 0 | 0 | 0.7, 1.2 |
| 5-12 | 1.29 | 24 | 0 | 7 | 0 | 0.9, 3.2 |
| 13-24 | 1.72 | 19 | 27 | 16 | 2 | 2.3, 6.0 |
| 25-36 | 1.64 | 22 | 22 | 15 | 3 | 1.9, 7.0 |
| 37-48 | 1.78 | 28 | 27 | 9 | 3 | 2.3, 6.2 |

Steady and gust lengths: 3 cells 85, 4 45, 5 24, 6 16, 7 5. In a stand in every gust (228 stands, 9 s each) he stayed in the zone on his
feet; he was pushed 13 px on average, 45 at most.

## The prince and the guards

| Situation | What happens |
|---|---|
| Running into it | capped (`windCap`); leaning forward up to 0.24 more, head up, the kilt's hem blown back (`khF`, `khB`) |
| A gust's peak | the near forearm comes up over his eyes (running or standing) |
| Standing in a gust | pushed back slowly, stepping back on the walk's cycle by the way he moves (`P.wph`), so his feet do not slide |
| Crouching | holds his place; the crouch is unchanged |
| A jump into it | its speed toward the wind is slowed by the drag (`windDrag`); the arc's height is unchanged. At a gust's peak the run is capped at 40, under a running jump's 45, so Jump there gives the standing jump |
| Going with it | nothing changes |
| Sound | `Snd.wind`, the Crossing's looped noise and rising bandpass, at the strongest wind within 220 px of him (`windSnd`); off when not in play |
| Guards | none are posted on or near a wind (fighters' ground is excluded); they are not affected |
| Bot | its `walk` holds the arrow through at the capped pace; `goto` walks back to a target a gust moved him off |

## How it is drawn

All of it is air: soft sprites of the theme's sand (`windSprites`: a light veil, a mid streamer, a dark grain, each a radial blob made once per
look), drawn with source-over, never as added light. The prototype's lines and streamers were light and read as white scratches, worst across
a moonbeam. Everything is a pure function of the clock and hashes of the zone; nothing is allocated per frame (`jsStamp`'s transform and its
inverse). It moves along `dir` at the wind's strength and fades over 26 px at each end.

| Part | Drawn |
|---|---|
| Dust veils | about one per 9 px of the zone: soft puffs 26-56 px long, 9-17 px high, stretched along the wind, from the floor up to about 47 px, thicker low; at 0.38-0.72 alpha, a third stronger in Torchlight. This is what reads at phone size |
| Streamers | 2 + one per 80 px: sand snakes of 9 soft blobs (14 by 4.4 px, a faint shadow under each) running low over the floor's top face at a depth that wanders, riding a hill's surface where one shares the zone (`hillH`) |
| Grains | one per 5 px: dark grains hopping in arcs 12-26 px long and 2-6 px high (saltation) |
| Leaves | in Nun, Osiris and Aksum (no sand there): papyrus shreds, chaff, olive and juniper leaves tumbling along, one per 40 px |
| A gust's window | in the warning and the gust, 34 soft puffs pour in through it and fall to the floor along a curve, growing as they go |
| Hangings | painted once into a canvas at `VS` (`windHangCanvas`) and laid down in 12 strips, each moved along the wind more the lower it hangs (6.5 e px at the foot, a wave down the cloth). Not drawn in the room's picture (`drawHangings` skips `hg.wz`) |
| Lamps | the flame leans downwind (`flame`'s shear: 7 e px) and its height and light flicker by up to 30% (`windGut`, in `flame` and `gatherLights`) |
| Kick shafts (W5) | fine dust rising up the shaft's light beside its jet stream (`windUpdraft`); look only |

## Light, shadows and effects

| Pass / effect | This element |
|---|---|
| Light map (`gatherLights`) | lamps in the wind flicker (`windGut`); the dust has no light of its own |
| Lamp shadow mask (`glShadow`, `SHC`) | not carved: the dust is air, as the jet streams and motes are; the hangings hang flat on the back wall as before |
| Relief (`GLFX.relief`) | rubbed back over each billowing hanging's box (`windRel`), since the room's picture has the wall behind it |
| Sky beams | the dust is lit by the scene, not a blocker; nothing added to the beams |
| Floor looks | the streamers are drawn over the floor's face (255): no embers or sheen under them |
| Classic | the same drawing, under the light pass |

## Relations to other elements

| Element | Relation |
|---|---|
| [heaps and drifts](heaps-and-drifts.md) | a drift's wind is round 43b's made a force; a wind may share a heap's cells; the streamers ride their surface |
| [kick shafts and jet streams](kick-shafts-and-jet-streams.md) | the updraft's dust beside the jet stream (W5, look only) |
| [lamps and light](lamps-and-light.md) | flames lean and gutter in it |
| [stonework](stonework.md) | the back wall's hangings over it billow |
| [the Crossing](the-crossing.md) | the same wind sound (`Snd.wind`) |
| [the dark](the-dark.md), [gates](gates.md), [plates](plates.md) | never in the chase or on a timed stretch |
| [guards and snakes](guards-and-snakes.md) | never on their ground |

## Rules for changing it

- Placement stays stream-free (hashes) and after the hills. Layouts, `L.path`, features and timers must stay identical (`layoutcmp.py`).
- No wind within `z.jm` cells of a seg that is not plain floor: a generated jump must never fly in it. If a wind may ever lie on a timed
  stretch, `estPath` must count the slower pace first.
- Against him only: `windCap` and `windDrag` act only toward the wind.
- The push ramps to nothing inside the zone: he never leaves it by the wind alone (`windscan.py`'s stands).
- The dust is air: cut at the floor's front edge and by the faces (`airCut`), never added light.
- Checks: `windscan.py`, `run2.py`, `p4bot.py`, `forktest.py`, `layoutcmp.py`, `layerscan.py kinds=wind`.

## History

- round 45c (owner): placement by openings with random moods, gusts from floor 7 with a ramped peak and per-zone cycles, wind over gap jumps
  (steady checked and weakened, gusts fair in the lull, the bot waits for it), deaths ease a zone (60%, 30%, `S.windDeaths`). See the top of this file.

- round 44 (owner, after r44's alternatives W1-W5): "your recommendation", against him only, steady 65, gust 40, drift run 70, wade about
  33; pushed back standing in a gust, crouched he holds; jumps affected and realistic (researched); wind on any plain stretch from floor 3
  at the hills' frequency, sharing with heaps; sand in the sandy themes, dust and leaves in Nun, Osiris and Aksum; hangings billow and lamps
  gutter. Fixes from the prototype: soft sand-toned dust instead of light streaks, readable at phone size, the wind's sound.
