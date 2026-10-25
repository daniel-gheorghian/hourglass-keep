# Dawnward reference docs

What the game is, how it plays, how floors are built, and one file per game element: how it plays, how it is drawn in Classic and
Torchlight, what each shader pass does with it, how it relates to the other elements, and what the prince and the guards can do with it.
They describe the code as of v82 (`dev/hourglass-keep.html`), checked against it function by function.

`CLAUDE.md` stays the log: the owner's rules round by round, with the reasons and numbers. These files are the state those rounds left.
Where the two disagree, the code is right, and the list at the end says where.

Example of use: to add a new trap that stands across the corridor (like the slicer), read [rendering.md#checklist](rendering.md#checklist)
for what a live thing over the room picture must do (relief rubbing, palette keys, `beamBlockers`, `glMask` carve, `fpMark`), then
[slicer-jaws](elements/slicer-jaws.md) for the nearest existing case, then [level-design.md](level-design.md) for where the generator
may place it and which stream it may draw from.

## Index

| File | Covers |
|---|---|
| [concept.md](concept.md) | what the game is, the twelve themes and their order, the owner's content rules, the two lighting modes, a floor's flow, the sands, save and Continue |
| [gameplay.md](gameplay.md) | controls and the pause menu, every move with its numbers, physics, falls, lives and flasks, what hurts, death and rewind, timed gates, fighting, the chase, hints, the bot |
| [level-design.md](level-design.md) | seed to floor: routes, runs, turns and chambers, forks, the spice and flags, puzzles, trap density, budgets, secrets, the damaging drop's test, timers, the random streams, invariants and their checks |
| [rendering.md](rendering.md) | both modes, the frame, draw order, the view and its cuts, every Torchlight pass (anchors below), floor alpha marks, the checklist for a new live element |

| Element | Covers |
|---|---|
| [prince](elements/prince.md) | states, hit box vs drawing, palettes, cuts, silhouette and shadow, fill light, beams on him (body and poses: `dev/FIGURE_SPEC.md`) |
| [guards and snakes](elements/guards-and-snakes.md) | budgets and posts, ranks, fighting, the robbers' look, snakes in tunnels |
| [stonework](elements/stonework.md) | walls, floor tiles, steps, ledges, low ceilings, wall art, wear, breaches, AO, the room picture |
| [openings and backdrop](elements/openings-and-backdrop.md) | windows, arches, breaches as views, `BGART` layers and their depths, the vertical rule, beam sources |
| [doors](elements/doors.md) | start and exit doors, the entry and the climb out on the stairs |
| [lamps and light](elements/lamps-and-light.md) | lamps and torches, placement, flames, the key light, fill, ambient floor, bounce, door light |
| [spikes](elements/spikes.md) | spikes and bronze stakes |
| [saws](elements/saws.md) | the floor saw |
| [slicer jaws](elements/slicer-jaws.md) | the slicer |
| [pendulum](elements/pendulum.md) | the pendulum blade |
| [fire vent](elements/fire-vent.md) | the fire vent and its heat |
| [darts](elements/darts.md) | the dart shooter |
| [roof blocks](elements/roof-blocks.md) | the falling roof block and the fallen block he steps over |
| [movable blocks](elements/movable-blocks.md) | blocks he pushes and pulls |
| [hurtdrop](elements/hurtdrop.md) | the damaging drop |
| [gates](elements/gates.md) | the portcullis, the iron gate, the violet gate, the fork's grating, lift mouths as gates |
| [plates](elements/plates.md) | every plate kind, closers, what presses them, the gate timer in the HUD |
| [cracked slabs and sand wells](elements/cracked-slabs-and-sand-wells.md) | the loose floor, its corridor and well looks, wells as one body of sand |
| [lifts](elements/lifts.md) | counterweight, paternoster, sand lift |
| [swing bar](elements/swing-bar.md) | the trapeze |
| [banners and slides](elements/banners-and-slides.md) | the cloth he slides down |
| [kick shafts and jet streams](elements/kick-shafts-and-jet-streams.md) | wall-to-wall kicks and the drifting-sand hint |
| [checkpoint](elements/checkpoint.md) | Nut's sky clock |
| [flasks and secrets](elements/flasks-and-secrets.md) | flasks, the gold flask, secret passages, alcoves, the cue |
| [the dark](elements/the-dark.md) | the chase |
| [the Crossing](elements/the-crossing.md) | the interlude between themes |

Every element file has the same sections: At a glance (code, generator, bot, checks, pictures), Example, In play, The prince and the
guards, How it is drawn, Light shadows and effects (one row per pass), Relations to other elements, Rules for changing it, History.

Rendering anchors: [G2D](rendering.md#g2d-and-the-replay), [light map](rendering.md#light-map), [key light](rendering.md#key-light),
[lamp shadows](rendering.md#lamp-shadows), [heat](rendering.md#heat), [silhouettes](rendering.md#silhouettes),
[relief](rendering.md#relief), [metal](rendering.md#metal), [sky beams](rendering.md#sky-beams), [atmosphere](rendering.md#atmosphere),
[floor looks](rendering.md#floor-looks), [bloom, grade, vignette](rendering.md#bloom-grade-vignette), [AO](rendering.md#ao),
[distance blur](rendering.md#distance-blur), [the dark](rendering.md#the-dark), [hit and rewind](rendering.md#hit-and-rewind-looks),
[checklist](rendering.md#checklist).

## Elements against the passes

Short answers; the element's own file has the detail. "Lamp shadow" is whether a figure's Torchlight shadow is carved out of it
(`glMask`) or lands on it; "floor looks" is round 31's embers and sheen.

| Element | Light map | Lamp shadow | Relief | Metal | Sky beams | Floor looks | Blocks beams | Hurts him | Guards |
|---|---|---|---|---|---|---|---|---|---|
| [prince](elements/prince.md) | carries a fill (r 84) | casts (silhouette, the 2 strongest lights) | rubbed under him (ellipse) | blade; carves the metal | lit side capped, cuts the haze, soft shadow down it | never painted over him | yes (figure mask) | n/a | fights them; bodies block |
| [guards and snakes](elements/guards-and-snakes.md) | fill (guards r 56, snakes r 34) | guards cast; snakes none | rubbed | guards' axe or khopesh; snakes none | guards cut and lit; snakes none | never painted over | guards yes, snakes no | 1 life a blow or bite | immune to traps |
| [stonework](elements/stonework.md) | lit; walls stop bounce | carved; the shadow falls on the back wall only | its height map | no | faces cut them; footprints on floors | yes (254 mark) | wall faces, low ceilings | falls only | walls stop guards |
| [openings and backdrop](elements/openings-and-backdrop.md) | windows, sky, bounce | never on the sky | no | no | the sources | no | no (bars streak them) | no | no |
| [doors](elements/doors.md) | the exit door's light | falls on it; none from him while he exits | none (art flattened under it) | no | no | no | no | no | ignore him in exit and entry |
| [lamps and light](elements/lamps-and-light.md) | the source | they cast it | rakes it; the flame rubbed | lights it; not in the mask | no | the sheen mirrors them | no | no | no |
| [spikes](elements/spikes.md) | | | | | | | | | |
| [saws](elements/saws.md) | | | | | | | | | |
| [slicer jaws](elements/slicer-jaws.md) | | | | | | | | | |
| [pendulum](elements/pendulum.md) | | | | | | | | | |
| [fire vent](elements/fire-vent.md) | | | | | | | | | |
| [darts](elements/darts.md) | visible shooter only | no | no (trap-light ellipse) | no (glint painted) | no | spent dart 255 | no | 1 life | no / no |
| [roof blocks](elements/roof-blocks.md) | while hanging and falling | no | falling only (ellipse) | no | footprint cut | block 255, rubble 251 | no | 1 life | stop at it / no |
| [movable blocks](elements/movable-blocks.md) | no | carved as a wall | `glRelFloors` | no | as a wall | 255 | yes, as a wall cell | no | blocked / no |
| [hurtdrop](elements/hurtdrop.md) | no | no | from the room picture | no | no footprint in the hole | 251 marks | no | 1 life (the fall) | no / no |
| [gates](elements/gates.md) | a timed gate's roundel | **lands on the slab** (not carved) | `glRelSlab` | iron gate only | no footprint | slab 255 | portcullis down | no (blocks only) | blocks guards; never pressed by them |
| [plates](elements/plates.md) | trap glint | carved (floor) | `glRelFloors` | no | footprint yes (254) | off (`FT_FLAT`) | no | no | no |
| [cracked slabs and sand wells](elements/cracked-slabs-and-sand-wells.md) | glint; warm light below while breaking | slab carved, sand not | `glRelFloors`, `glRelWell` | no | sand cut (`sandSegs`); the slab takes a footprint | off (`FT_FLAT`) | the sand | the fall (stakes, two storeys); crush 1 life | no |
| [lifts](elements/lifts.md) | trap glint | not carved | `glRelLifts`, `glRelSlab`, `glRelBox` | none (iron only with `EGP.traps` off) | no openings in shafts; sand cut out | none | the sand column only | no (an empty shaft is a fall) | no |
| [swing bar](elements/swing-bar.md) | trap glint, ready glow | not carved | no | no (wood and rope) | no | no | no | no (spikes under it do) | no |
| [banners and slides](elements/banners-and-slides.md) | none | not carved | no | no | no | no | no | no (the slide is safe) | no |
| [kick shafts and jet streams](elements/kick-shafts-and-jet-streams.md) | trap glint at the foot; the jet none | walls carved as stone | no | no | no | no | no | falls only | no |
| [checkpoint](elements/checkpoint.md) | lit: an item light (r 150) | no | no | no | no footprint (255) | no | no | no | no |
| [flasks and secrets](elements/flasks-and-secrets.md) | a coloured item light | no | no | no | no footprint (255) | no | no | poison: 1 life | an ambush guard at the gold flask |
| [the dark](elements/the-dark.md) | drains lamps (`dkDrain`) | its own 2D shadow pull (`drawShut`) | covered | covered | covered | covered | no | kills | no |
| [the Crossing](elements/the-crossing.md) | its own (sun or moon, his fill) | off | off | off | off | off | no | no | no |

## What the docs found

Found while checking the docs against the code. None of it is changed; the first table needs the owner's decision.

### In the game (possible faults)

| Finding | Where | Seen in |
|---|---|---|
| An iron chain is still drawn: six links on the back wall in about one cell in 13 under a ceiling, dungeon style (Nun, Garama, Hawara), not behind `EGP`. Round 18b: no chains | `backCell` | [stonework](elements/stonework.md) |
| A figure's lamp shadow lands on a lowered portcullis and on lift mouth slabs as if they were the back wall: `glMask` carves walls, floors, low ceilings and the jaws only (the fault round 37b fixed for the jaws) | `glMask` | [gates](elements/gates.md) |
| The falling roof block hurts through invulnerability: `hurt(1,'crush')` without the `P.inv` test `trapHit` makes | roof block update | [roof blocks](elements/roof-blocks.md) |
| A fallen roof block gets no relief rubbing, so Torchlight may emboss the wall's art on it (round 35c's fault, for tiles and pushed blocks) | `glRelFloors` | [roof blocks](elements/roof-blocks.md) |
| The damaging drop's lip may be grippable: `edgeBelow` skips a `hurtdrop`, `findLedge` (Grab held while falling) does not (unverified in play) | `findLedge` | [hurtdrop](elements/hurtdrop.md) |
| A rewind does not undo a banner's cut: the cut record `bn` is shared by reference and `snapAll` copies shallowly | `snapAll` | [banners and slides](elements/banners-and-slides.md) |
| Beside a sand lift the `lift` hint says "Step on the plate", and there is no plate; riding a sand lift learns `lift` | `checkHints` | [lifts](elements/lifts.md) |
| Once a sand lift's slab has left, its top mouth's play plane shuts (`f.gT` 0) with no slab drawn there | sand lift update | [lifts](elements/lifts.md) |
| Roof blocks hang again after a respawn (it rebuilds the floor); a rewind and a Continue restore them fallen. The code's comment says a respawn restores them | respawn | [roof blocks](elements/roof-blocks.md) |
| The fork's grating takes no beam footprint (no `fpMark`) | grating draw | [gates](elements/gates.md) |
| The recruit's HUD hearts and rank name are light blue (`#8fa3d8`) under the rule "no guard in blue or white" (HUD only; the dress is ochre) | `TIERS[0]` | [guards and snakes](elements/guards-and-snakes.md) |

### CLAUDE.md against the code

| CLAUDE.md says | The code |
|---|---|
| the checkpoint is the water clock (Karnak clepsydra) (Themes; round 37c; `cpscan.py`'s wording) | Nut's sky clock from round 8 (`nutClock`); the game's words are "sky clock"; round 7's barque clock is for pictures only |
| `estPath` times a careful pace (`WALK_T`); every timer is `estPath` at that pace x 0.84-1.08 | no `WALK_T`. Three ways: P4 `estPath(...,true)` (0.55 s a tile); detours and double gates the plain pace (0.34) x `timerK()` + 0.3 s; in-line gates `(m*TW+16+BW)/RUN` + extras x 1.15-1.03 |
| themes turn every 48 floors | `SCHED` repeats every 180 floors (CLAUDE.md says so elsewhere too) |
| longway: forks all kind 3 or 4, mostly with a grating | floors 6-9 kind 4 only; from 10 half 3, half 4; a grating on 70% of kind 4; `lp.order` can fall back to kinds 1 and 2 |
| forks drawn from `frng` | which switchbacks get forks comes from `lrng` (`hash2(seed,6151)`) |
| the spice from floor 3 | the move family from 3; puzzle and obstacle families from 4 |
| the damaging drop saves 25% "by `estPath()`" | in forks `forkWorth` times the long way as tiles x 0.34 + 4 s |
| "check with `metrics39.py`"; `metrics40.py` "edit the two files at its top" | the suite runs `metrics40.py`, which takes the baseline tag as its argument (default v39) |
| guards never on a landing | the kind-1 fork's guard stands on a landing of the short way |
| the captain has a reinforcement from floor 6 | it drops in as a veteran (`TIERS[2]`) with the captain's hit points |
| snakes only in tunnels | true, including the tunnels of side passages' corridor fills |
| lift gates keep their bars | with `EGP.traps` on (default) lift mouths are `egSlab` stone in the theme's stone; bars only with it off |
| the roof block is `egStone`, `egBlock`; the well's sand `drawWellSand` | `egRoofSlot`, `egRoofHang`, `egRoofFall`, `egRoofLying`, `roofStone`; `drawWellGroup` |
| plates are pressed only by him (round 37a) | movable blocks and falling slabs press them too (`updateBlocks`, `jamAt`); 37a's conclusion holds (neither reaches a lift's foot) |
| doors: a lintel under a cavetto cornice | a flat lintel block, a winged sun disc over palace, tile and crypt doors, a torus frame on palace and tile |
| arches, doors and windows are post and lintel | windows only in palace and tile; the dungeon's is a slit, the forge's a round hole, the crypt's a star |
| the near band is in the ten open looks | nine (`wells` has none) |
| `glRelLifts` rubs the sand slab at rest (round 37a) | `glRelLifts` skips sand lifts; separate `glRelBox` calls do it |
| the no-kick-in-a-shaft rule is v60 | v59 (`wallTouch`'s comment, `liftkick.py`) |
| `lampsClear` puts a lamp out | removes it from `L.torches` (no scar, no fallen lamp); `broken` lamps are `settleLights`' worn-wall case |
| Classic's wide glow at the checkpoint (round 37c) | drawn only with Graphics > Lighting off; with it on, Classic's room light comes from `lightPass` |
| `crossscan.py quick` about 20 s | about 2 min (its header, `suite.py`'s comment) |
| a far jackal among the Crossing's animals (36a) | none in the code |
| Rokkitt for HUD numbers | the floor timer is Jost; Rokkitt for FLOOR, the gate timer, the banner |
| (not stated) | Torchlight also needs Graphics > Lighting on (`shaderOn()`); a snake's bite costs a heart even crouched |
| `dev/FIGURE_SPEC.md`'s body table: standing 50.5 px, neck 2.0 "since 23c" | `R23B.nk` 3.518 (round 23d): 51.5 px |
| the darts are forged metal (section heading) | not in `METAL`; their glint is painted |

### Stale comments in the code

Torchlight's header (falls back to Classic over ~22 ms: since v63 only `GLP.rs`); the shafts' march "jittered" (same steps every pixel);
caustics "round the Cistern's arches" (`LFX.caus` is nun and foggara); `krng` "the puzzles' stream" (it draws turn kits; `zrng` is the
puzzles'); timed side gates latched "two in five" (`%100<62`); `CYC` keeps the paternoster out of turns with a timed gate (any gate slot);
the dark drawn in Classic's emissive pass (after `hazePass`); `doorHead`'s "pointed" kind (a flat lintel); every rank its own weapon
(soldier and veteran both the axe); `drawBar`'s pull "drawn only" (`swingPlace` uses it).

### Checks that the suite does not run

`suite.py` runs none of `doorscan.py`, `stairscan.py`, `openscan.py`, `tilescan.py`, `beamwall.py`, `lampscan.py`, `slabscan.py`,
`wellscan.py`, `figscan.py`, `sandshaft.py`, `swingfeel.py`: they are run by hand when their round's element changes. `guardscan.py` is in
the suite but not in CLAUDE.md's table. There is no standard tool for "layouts identical on floors 1-48 x 3 seeds" (rounds did it ad hoc;
`samelayout.py` hashes floors 1-40 x 5 seeds and has old paths).

## Keeping them current

A round that changes an element updates that element's file in the same commit (its rules, passes and relations), and adds its History
line; CLAUDE.md keeps the round's entry as before. A new element gets a file on the template above and a row in both tables here.
