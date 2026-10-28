# Dawnward reference docs

What the game is, how it plays, how floors are built, and one file per game element: how it plays, how it is drawn in Classic and
Torchlight, what each shader pass does with it, how it relates to the other elements, and what the prince and the guards can do with it.
They describe the code as of v84 (`dev/hourglass-keep.html`), checked against it function by function; round 39's layering rule is
[layers.md](layers.md).

`CLAUDE.md` stays the log: the owner's rules round by round, with the reasons and numbers. These files are the state those rounds left.
Where the two disagree, the code is right, and the list at the end says where.

Example of use: to add a new trap that stands across the corridor (like the slicer), read [rendering.md#checklist](rendering.md#checklist)
for what a live thing over the room picture must do (its rows in [layers.md](layers.md) and its cut by the nearer stone, relief rubbing, palette keys, `beamBlockers`, its outline in `SHC` for the lamp shadow, `fpMark`), then
[slicer-jaws](elements/slicer-jaws.md) for the nearest existing case, then [level-design.md](level-design.md) for where the generator
may place it and which stream it may draw from.

## Index

| File | Covers |
|---|---|
| [concept.md](concept.md) | what the game is, the twelve themes and their order, the owner's content rules, the two lighting modes, a floor's flow, the sands, save and Continue |
| [gameplay.md](gameplay.md) | controls and the pause menu, every move with its numbers, physics, falls, lives and flasks, what hurts, death and rewind, timed gates, fighting, the chase, hints, the bot |
| [level-design.md](level-design.md) | seed to floor: routes, runs, turns and chambers, forks, the spice and flags, puzzles, trap density, budgets, secrets, the damaging drop's test, timers, the random streams, invariants and their checks |
| [rendering.md](rendering.md) | both modes, the frame, draw order, the view and its cuts, every Torchlight pass (anchors below), floor alpha marks, the checklist for a new live element |
| [layers.md](layers.md) | the layering rule (round 39): L0 backdrop, L1 back wall, L2 corridor with its depths and air, L3 front plane, L4 overlay; what may cover what, what each light pass may touch, the approved exceptions, and every element's parts with their layer and the cut that keeps the nearer stone in front |

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
| [heaps and drifts](elements/heaps-and-drifts.md) | slowing terrain on plain runs: the rubble heap he clambers over, the sand drift he wades (round 43) |
| [wind](elements/wind.md) | a headwind on plain runs, gusts at windows, the drifts' wind: slows the run and jumps into it; hangings billow, lamps gutter (round 44) |
| [courts](elements/courts.md) | stretches open to the sky: a peristyle, a vine pergola, a pylon court, a light well; a court's spiked pit is a pool that drowns him (round 45); a near jamb of the theme's architecture at each end that he passes behind, worn with the wall; Meroë's own sky and grade (round 45c) |
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

Every element file has the same sections: At a glance (code, layer, generator, bot, checks, pictures), Example, In play, The prince and the
guards, How it is drawn, Light shadows and effects (one row per pass), Relations to other elements, Rules for changing it, History.

Rendering anchors: [G2D](rendering.md#g2d-and-the-replay), [light map](rendering.md#light-map), [key light](rendering.md#key-light),
[lamp shadows](rendering.md#lamp-shadows), [heat](rendering.md#heat), [silhouettes](rendering.md#silhouettes),
[relief](rendering.md#relief), [metal](rendering.md#metal), [sky beams](rendering.md#sky-beams), [atmosphere](rendering.md#atmosphere),
[floor looks](rendering.md#floor-looks), [bloom, grade, vignette](rendering.md#bloom-grade-vignette), [AO](rendering.md#ao),
[distance blur](rendering.md#distance-blur), [the dark](rendering.md#the-dark), [hit and rewind](rendering.md#hit-and-rewind-looks),
[checklist](rendering.md#checklist).

## Elements against the passes

Short answers; the element's own file has the detail. "Lamp shadow" is whether a figure's Torchlight shadow is carved out of it
(`glMask`, `SHC`) or lands on it; "floor looks" is round 31's embers and sheen. Each element's layer is in its At a glance table and in
[layers.md](layers.md).

| Element | Light map | Lamp shadow | Relief | Metal | Sky beams | Floor looks | Blocks beams | Hurts him | Guards |
|---|---|---|---|---|---|---|---|---|---|
| [prince](elements/prince.md) | carries a fill (r 84) | casts (silhouette, the 2 strongest lights) | rubbed under him (ellipse) | blade; carves the metal | lit side capped, cuts the haze, soft shadow down it | never painted over him | yes (figure mask) | n/a | fights them; bodies block |
| [guards and snakes](elements/guards-and-snakes.md) | fill (guards r 56, snakes r 34) | guards cast; snakes none | rubbed | guards' axe or khopesh; snakes none | guards cut and lit; snakes none | never painted over | guards yes, snakes no | 1 life a blow or bite | immune to traps |
| [stonework](elements/stonework.md) | lit; walls stop bounce | carved; the shadow falls on the back wall only | its height map | no | faces cut them; footprints on floors | yes (254 mark) | wall faces, low ceilings | falls only | walls stop guards |
| [openings and backdrop](elements/openings-and-backdrop.md) | windows, sky, bounce | never on the sky | no | no | the sources | no | no (bars streak them) | no | no |
| [doors](elements/doors.md) | the exit door's light | falls on it; none from him while he exits | none (art flattened under it) | no | no | no | no | no | ignore him in exit and entry |
| [lamps and light](elements/lamps-and-light.md) | the source | they cast it | rakes it; the flame rubbed | lights it; not in the mask | no | the sheen mirrors them | no | no | no |
| [spikes](elements/spikes.md) | trap glint | stakes carved (`SHC`) | glint rubbed; holes in the picture | no (stakes painted bronze) | footprint on the holes, off the stakes | off holes and stakes | no | kills (landing on them, running in) | never placed or hit |
| [saws](elements/saws.md) | a glint rides the blade | blade carved (`SHC`) | glint rubbed | yes (the spun disc) | footprint off blade and slot | off (255) | no | 1 life | never placed or hit |
| [slicer jaws](elements/slicer-jaws.md) | trap glint | carved (`JAWP`) | `glRelJaws` | yes (bronze, `METAL_EG`) | a blocker | off (255) | yes | kills | never placed or hit |
| [pendulum](elements/pendulum.md) | a glint on the blade | blade and arm carved (`SHC`) | glint rubbed | yes (steel, gold fittings) | no | n/a | no | 1 life (not crouched) | never placed or hit |
| [fire vent](elements/fire-vent.md) | fire light (110 px) | casts shadows; not carved | glint rubbed | no (lights the metal) | footprint on the grate | off its tile (`FT_FLAT`) | no | 1 life (no height test) | never placed or hit |
| [darts](elements/darts.md) | visible shooter only | no | no (trap-light ellipse) | no (glint painted) | no | spent dart 255 | no | 1 life | no / no |
| [roof blocks](elements/roof-blocks.md) | while hanging and falling | falling and lying carved (`SHC`) | `glRelRoofFall` (falling, as clipped), `glRelRoof` (lying) | no | footprint cut | block 255, rubble 251 | no | 1 life | stop at it / no |
| [heaps and drifts](elements/heaps-and-drifts.md) | lit as the scene | carved (`SHC` heap, drift) by the one outline `hillSil` | `hillRel` (hard-edged quads, the same outline) | no | none on them: a solid (round 46b; Torchlight the alpha mark `HILL_A` 253, `hlGate`; Classic and `?wgl=0` `sandSegs`) | off (`hlGate`) | no | no (slows him: 42 / 35 px/s; no jump in a drift) | stop at its edge |
| [wind](elements/wind.md) | lamps in it flicker (`windGut`) | not carved (air) | `windRel` (billowing hangings) | no | lit as the scene | streamers 255 | no | no (slows him: 65 / 40 px/s, jumps into it shorter by its drag) | never posted near it |
| [courts](elements/courts.md) | broad `sky` lights along it; lamps there free | L1 parts take it; pool, vine and jambs carved (`SHC` pool, vine, jamb); the sky none | stone as any wall; `ctRel` over a pool and the jambs | no | no beam from a court; the jambs block beams | as the scene | the jambs | a pool drowns him at its surface | allowed |
| [movable blocks](elements/movable-blocks.md) | no | carved as a wall | `glRelFloors` | no | as a wall | 255 | yes, as a wall cell | no | blocked / no |
| [hurtdrop](elements/hurtdrop.md) | no | no | from the room picture | no | no footprint in the hole | 251 marks | no | 1 life (the fall) | no / no |
| [gates](elements/gates.md) | a timed gate's roundel | down slabs carved (`SHC`) | `glRelSlab` | iron gate only | no footprint; the grating's bars take one | slab 255 | portcullis and lift mouth slabs down | no (blocks only) | blocks guards; never pressed by them |
| [plates](elements/plates.md) | trap glint | carved (floor) | `glRelFloors` | no | footprint yes (254) | off (`FT_FLAT`) | no | no | no |
| [cracked slabs and sand wells](elements/cracked-slabs-and-sand-wells.md) | glint; warm light below while breaking | slab carved, sand not | `glRelFloors`, `glRelWell` | no | sand cut (`sandSegs`); the slab takes a footprint | off (`FT_FLAT`) | the sand | the fall (stakes, two storeys); crush 1 life | no |
| [lifts](elements/lifts.md) | trap glint | platform, ropes, slabs carved (`SHC`); the counterweight not | `glRelLifts`, `glRelSlab`, `glRelBox` | none (iron only with `EGP.traps` off) | no openings in shafts; sand cut out | none | the sand column; mouth slabs down | no (an empty shaft is a fall) | no |
| [swing bar](elements/swing-bar.md) | trap glint, ready glow | not carved | no | no (wood and rope) | no | no | no | no (spikes under it do) | no |
| [banners and slides](elements/banners-and-slides.md) | none | not carved | `glRelBanners` | no | no | no | no | no (the slide is safe) | no |
| [kick shafts and jet streams](elements/kick-shafts-and-jet-streams.md) | trap glint at the foot; the jet none | walls carved as stone | no | no | no | no | no | falls only | no |
| [checkpoint](elements/checkpoint.md) | lit: an item light (r 150) | clock and pedestal carved (`SHC`) | partly: its lights' ellipses (`glRelEx`) | no | no footprint (255) | no | no | no | no |
| [flasks and secrets](elements/flasks-and-secrets.md) | a coloured item light | flasks carved (`SHC`) | its light's ellipse (`glRelEx`) | no | no footprint (255) | no | no | poison: 1 life | an ambush guard at the gold flask |
| [the dark](elements/the-dark.md) | drains lamps (`dkDrain`) | its own 2D shadow pull (`drawShut`) | covered | covered | covered | covered | no | kills | no |
| [the Crossing](elements/the-crossing.md) | its own (sun or moon, his fill) | off | off | off | off | off | no | no | no |

## What round 46b found

The owner's heap (a B3 before an opening, the Waters of Nun at night: "it looks transparent, the background wall art seems drawn over it,
the shadow renders just over the far left of the heap, and that center circle/oval doesn't look right ... Probably need to revise the
layering rules also"). New rules R5 solids, R6 one outline, R7 beams and solids in [layers](layers.md); the contour rule in
[rendering](rendering.md#contours-round-46b).

| Finding (v87) | Where | Round 46b | Seen in |
|---|---|---|---|
| F1 the sky beams' haze, with the window's bars, rim, pane and footprint, laid over every heap and drift, both modes: `heapscan.py` floors 3-48 x 2, 178 hills, beams changed over 0.5% of a hill's pixels on 98 in Torchlight (mean 26%) and 93 in Classic (mean 22%) | shafts' shader, `ryBeams2D` | Torchlight: the hill's pixels marked (`HILL_A` 253) and the composite leaves the S and M passes and `floorFx` off them (`hlGate`); Classic and `?wgl=0`: `hillSegs` in `sandSegs` (`SDMAX` 64) | [heaps and drifts](elements/heaps-and-drifts.md) |
| F2 B3's drum joint and four flutes drawn over the hidden far half; every heap's edges (column, crest, stones, blocks) the fixed ink `#0b0812` | `hillDrum`, `hillPaint`, `stoneBox` | only the near half; `selOut` edges (the contour rule); `stoneBox`'s `o.ink` | heaps and drifts |
| F3 the column's end the palest thing on it whatever the light, a flat near-black square | `hillDrum` | shaded by the key light's side; three looks by a hash (fracture, socket, buried) | heaps and drifts |
| F4 `hillSil` (the carve's, the relief's and Classic's footprint's outline) the mound alone, B3's column 8 px right of where it is drawn: his shadow on its left end and every stone above the mound | `hillSil` | the one outline of everything drawn (`hillMeshTop`, stones, blocks, column, tongue) | heaps and drifts |
| F5 the relief embossed the back wall's art where that outline missed | `hillRel` | the same outline, each quad to its highest point | heaps and drifts |
| `shadowscan.py` masked heaps by the carve's own outline, so it could not see F4 (0 of 128 on v87) | `shadowscan.py` | heap and drift measured by their drawn pixels: v87 76 of 128 (heaps 68 of 85, drifts 8 of 43), round 46b 0 of 128 (floors 3-48, seed 1; the bloom, the wind's dust and the sand stream held out, air or light) | heaps and drifts |
| C4's sand round a half-buried block a flat pale oval; B1's grit in the Blue Chambers in the faience blue | `hillBlocks`, `hillCols` | the drift's own shade rising to a lit lip; the blocks' limestone darkened | heaps and drifts |

Left: a test of R5 over the other solids (`solidscan`: blocks, roof blocks, jambs, lift parts) and the contour rule on the older props
(the audit's 131 fixed inks in 57 functions, the figures) are round 46c's.

## What round 46a found

The sky beams' staircases, fixed six times one edge at a time, are now a rule with a check: [rendering](rendering.md#low-resolution-passes-s-m-no-staircases), rules S1-S7.

| Finding (v87) | Where | Round 46a | Seen in |
|---|---|---|---|
| Edges narrower than a texel of the quarter-size S pass, drawn as staircases at every `GLP.rs`: the profile's entry jumped ~19 px at each pier (a dark stepped wedge down a run of arches, the owner's shot, floor 26 at night) and was read `NEAREST`; a floor's shadow cut hard (`if(t>tm)break;`); a low ceiling's edges soft over 1.5 px or three hard taps under a march stepping 5-10 px. `beamjag.py`: STEP up to 0.115 on v87 (Garama by moonlight) | `ryProfile`, `glcRy`, `GLCSH.s` | fixed: `ryPrefilter` (`RY_BLUR` 1.4), `LINEAR`, the floor by a weight over `EZ`, `lowS` and the low ceiling's lower edge over the march's step, walls' `e` over a 32nd of it, the pane's edges over a texel; `beamjag.py` in `suite.py` (render) | [openings and backdrop](elements/openings-and-backdrop.md) |

## What round 39 found, and what v84 did

Round 39 (owner: "We need a layering rule ... background, back wall, corridor, front wall ... take each of the game elements and assign
them to one layer ... check that we draw correctly the game elements"). [layers.md](layers.md) states the rule (L0 backdrop, L1 back wall,
L2 corridor with its depths and air, L3 front plane, L4 overlay; R1 order, R2 openings, R3 passes per layer) and every element's parts.
Four audits checked the code against it (the back wall and what is fixed on it; floor things; things across the depth and hanging;
figures and air); v84 is rounds 39d (figures, falling things), 39e (hanging, across the depth, floor things) and 39f (the back wall and
the air). Look only: layouts identical against v83 (`layoutcmp.py` floors 1-24, seeds 1-2); hit boxes, timing, `estPath` and the bot
unchanged. Each element's file has a Layer row and a round 39 History line.

### In the game

Pixels are the audits' counts over the front plane in their frames (v83 -> v84).

| Finding (v83) | Where | v84 | Seen in |
|---|---|---|---|
| A dead prince, a dying or dead guard and its crumbling were never cut by a face; the press was dropped, so a pressed guard slid up to 20 px into the face as he died | `drawDynamic`, `figClip` | fixed (39d): the last press kept (`P.rdx`, `g.rdx`), cut by the faces within 28 px (`deadCut`; grains `midHid`); dead prince 1,878 px -> 0 | [prince](elements/prince.md), [guards](elements/guards-and-snakes.md) |
| A face on a figure's left never cut it (crouching at a left wall, head and hands up to 18 px past it; hanging with the wall below on his left pulled him 6 px into its side face) | `wallPress` | fixed (39d): `wallPress` two-sided (`wallRows`, `figReach.left`), pressed right up to `HX`+4; the hang pulls 2 px; crouch 3,713 px -> 0, run 1,243 -> 0 | [prince](elements/prince.md) |
| Pushing or pulling, he was cut at the block's two cells, not its drawn face (hands 13 px over it, or arms 18 px short) | `wallPress` | fixed (39d): `wallRows` takes the moving block's drawn face; the press holds at -13.1 px (v83 -8 to -20) | [movable blocks](elements/movable-blocks.md) |
| A guard dropping in was drawn over the ceiling's stone for about 0.35 s | `drawDynamic`, `glSilhouette` | fixed (39d): `dropCeil` clips him and his silhouette at the ceiling's lower edge; 7,952 / 6,525 px -> 0 | [guards](elements/guards-and-snakes.md) |
| Hanging over open space, his forearms and head lay over the ledge's lip | `figClip` | owner: "Cut the arms at the lip, keep only the hands": `figClip` modes 3 and 4 (39d), his shadow too; 425 px -> 0 | [prince](elements/prince.md) |
| `drawShut`'s copies lay over the wall he hides behind in a chase and the faces beside him | `drawShut` | fixed (39d): only where the back wall shows; the smear only on floor tops; 2,089 px -> 0 | [the dark](elements/the-dark.md) |
| A falling plank and a corridor's cracked slab (chunks, billow) went over the next cell's lip and the pit wall's face | debris loop | fixed (39d): `debrisCut`; plank 1,031 px -> 0, slab 7,070 -> 0; the landing cloud in `airCut` (39f) | [cracked slabs](elements/cracked-slabs-and-sand-wells.md) |
| A banner's runner, rod and fringe ran 7 px onto the next column's face, the landing's top and lip (floor 4 seed 1, column 85) | `case 'banner'` | fixed (39e): cut at that column's front plane (`nearCut`); 10,648 px -> 0 Classic, 9,275 -> 0 Torchlight. Owner: a banner covers the back wall, so it may be over windows and wall art | [banners](elements/banners-and-slides.md) |
| A banner had no relief rubbing: the wall's art was embossed on it | `glRelief` | fixed (39e): `glRelBanners`; 1,324 px -> 0 | [banners](elements/banners-and-slides.md) |
| A lift's left mouth slab was drawn whole before the figures, so a figure on the landing covered its front face | `drawLiftCounterweight`, `drawSandLift` | fixed (39e): its front face after the figures (`liftMouthL`); 1,901 px -> 0, sand lift mouth 1,278 -> 0 | [lifts](elements/lifts.md) |
| The falling roof block was unclipped: over the ceiling's face round the slot for 0.15 s (411 of 411), over a wall's face under a high ceiling (floor 41); the hanging block's trickle crossed the next column's face | `egRoofFall`, `egRoofHang` | fixed (39e): `roofFallClip`, the trickles cut, the `SHC` record from the hole's top, `glRelRoofFall`; 2,207 / 5,934 / 5,720 px -> 0 | [roof blocks](elements/roof-blocks.md) |
| A sky clock on a sand lift's foot (33 of 96 floors) was drawn before the lift: after the ride the shaft's back covered half of it | `drawDynamic` | fixed (39e): `cpOnLift`; the clock's visible px 4,475 -> 7,863 | [checkpoint](elements/checkpoint.md) |
| Darts vanished about 80 px into a 131 px flight (an 81 px clip window) while they still hit | dart loop | fixed (39e): cut on the mouth's side only; a dart 100 px out 391 -> 1,187 px drawn | [darts](elements/darts.md) |
| A hidden flask's stars reached past a wall's face beside it (23 of 48) | `drawDynamic` | fixed (39e): a rectangle at the face; 112 px -> 0 | [flasks](elements/flasks-and-secrets.md) |
| The front stake (depth .26) was drawn before him, so he covered it | spikes | fixed (39e): `drawNeedles`, `SPK_NEAR`: drawn after the figures; it covers 454 px of him | [spikes](elements/spikes.md) |
| A gate's far half and slots lay over a floor's lip beside its lintel (floor 33 seed 2, 1 of 1,438); `glRelSlab` flattened 8 px of the lintel's face | `drawGate`, `glRelSlab` | fixed (39e): cut at the lip (`nearCut`); the rubbing from the ceiling's edge; 397 px -> 0 | [gates](elements/gates.md) |
| On floors whose first run heads left the start door's frame lay 18 px over the next wall's face (38 of 96 floors) | `drawDoor`, the entry | fixed (39f): `startDoorX` (`DOOR_HW` 18) for the door, the cut-out, the entry and `doorClip`; `L.start.x` unchanged; `doorscan.py` frames it there | [doors](elements/doors.md) |
| A lamp's tongues, embers, smoke and glow lay over the slab's lip and top above it (136 of 6,525 lamps with a floor overhead) | `drawLight` | fixed (39f): `lampCeil` (260 lamps take its even-odd path) | [lamps](elements/lamps-and-light.md) |
| What the room picture lays on a floor ran onto the faces (a breach's rubble 7.5 px, 199 of 2,450 breaches; specks; the hurtdrop's heap); the hurtdrop's dark shaft darkened every right neighbour's lip, put a black band on a wall's face (6 layouts) and blacked out 12 of 77 shafts' openings | `rlEnd`, `drawRoomStatic` | fixed (39f): `rlEnd` cuts the scratch layer at the faces; the shaft's dark is its back wall, in stage 0 (a window in it now shows the sky) | [stonework](elements/stonework.md), [hurtdrop](elements/hurtdrop.md) |
| Classic's beam footprint lay over a sky clock's pedestal and a free lamp's floor stand | `ryStand` | fixed (39f): their boxes | [checkpoint](elements/checkpoint.md), [lamps](elements/lamps-and-light.md) |
| Air was drawn over the faces: motes, gusts, petals, bats, ash, moths, flies, sparks, wisps, FX particles, the sword's rings, smoke, the landing cloud, trickles, drips, the floor mist | `ambientLit`, `atmoPass`, `ambientGlow`, `drawEmissive` | fixed (39f): `onFace`, `airCut`, `faceGap`, the mist cropped | [rendering](rendering.md#cuts), [stonework](elements/stonework.md) |
| `lampGlints` and the granite crystals tested the cell, not the face (a face's left `HX` px kept them) | `lampGlints`, `classicLookFx` | fixed (39f): `onFace` | [lamps](elements/lamps-and-light.md), [stonework](elements/stonework.md) |
| The kick shaft's jet stream ran 6 px onto the right wall's face (236 of 236) | `jetPlaces` | fixed (39f): `wx1` `X+TW-HX` | [kick shafts](elements/kick-shafts-and-jet-streams.md) |

`layerscan.py` (round 39, by hand; floors 3-8, Classic): banner 86 bad views -> 0; air 238, door 1, lamp 6 -> 0; lift, clock, stone and
gate 0. `liftscan.py` floors 3-8 Classic and 6-8 Torchlight `ALL OK`.

Side effect: in a kick shaft (24 px at mid-depth) he is now cut by both walls (v83 drew him 19.5 px into the far wall). Round 42a's
chimney (he is drawn back and foot between the walls) makes him fit: see [kick shafts](elements/kick-shafts-and-jet-streams.md).

Left as they are (decisions or low): the gate slab's top piece above the ceiling's edge over the lintel's side face (round 14's look; the
owner's call); (round 42b fixed the swing bar's near pole and rope, the vent's back row and the uncarved standing things; banners and wall lamp
bodies stay uncarved by choice, a let-go flask too); additive glows drawn in
`drawDynamic` over the sky raise Torchlight's scene alpha; the relief on lamp bodies, free stands and the clock (only their lights'
ellipses rub them); blocks' beam tile map rebuilt every 40th call and both cells carved
during a move; the hint streams and the descending cue brushing a face's end by a few px; a figure's shadow, beam cut, fill cut, relief and
trails at its play x, not its pressed x; the lamps' and the exit's glow sprites (light); in Classic a lamp's light band on the foot of a
face; `graniteGlints` never called.

### The docs against the code (round 39)

| The docs said (v83) | The code (the docs now say so) |
|---|---|
| spikes: "He is drawn after the stakes, so he stands in front of them" | v83's draw order, not a rule; now the front stake is drawn after him and covers him |
| flasks: the relief "not rubbed" | the soft ellipse round its `item` light (`glRelEx`) covers the flask |
| checkpoint: the relief "not rubbed (no `glRel*` names it)" | partly: its lights' ellipses (`glRelEx`) cover most of it |
| checkpoint: Classic's footprint "not in `ryStand`" | it is now (round 39) |
| banners: "Nothing cuts the banner" | the next column's front plane does (round 39) |
| gates: "What cuts it: its own clips only" | and a floor's lip beside the lintel (round 39) |
| doors: `doorscan.py` and `stairscan.py` "Neither is in `suite.py`" | `doorscan.py` is in the release tier since round 38c; `stairscan.py` by hand |
| rendering, lamps and light: `graniteGlints` among the 2D glints drawn in both modes, and among `keyLight`'s readers | defined but never called; the granite crystals are `classicLookFx`'s (`fx.granite`) |

## What the docs found, and what v83 did

Found while checking the docs against v82's code. The owner's answer was "Correct all Claude.md and all of the faults, then release":
v83 is rounds 38a (looks), 38b (play) and 38c (comments and checks); CLAUDE.md's round 38 entry has the numbers.

### In the game

| Finding (v82) | Where | v83 | Seen in |
|---|---|---|---|
| An iron chain is still drawn: six links on the back wall in about one cell in 13 under a ceiling, dungeon style (Nun, Garama, Hawara), not behind `EGP`. Round 18b: no chains | `backCell` | fixed (38a): `backRope`, a knotted rope or a sling holding a jar | [stonework](elements/stonework.md) |
| A figure's lamp shadow lands on a lowered portcullis and on lift mouth slabs as if they were the back wall: `glMask` carves walls, floors, low ceilings and the jaws only | `glMask` | fixed (38a): each thing before the wall records its outline in `SHC`, cut by `shcCarve`; `shadowscan.py`: 266 of 300 things took his shadow, 0 now | [gates](elements/gates.md) |
| The falling roof block hurts through invulnerability | roof block update | fixed (38b): it tests `P.inv` and gives 0.9 s, as `trapHit` | [roof blocks](elements/roof-blocks.md) |
| A fallen roof block gets no relief rubbing | `glRelFloors` | fixed (38a): `glRelRoof` (the wall's art was embossed on 31 of 32, 0 now) | [roof blocks](elements/roof-blocks.md) |
| The damaging drop's lip may be grippable from a fall with Grab held | `findLedge` | confirmed (64 of 64 falls caught it) and fixed (38b): `findLedge` skips a `hurtdrop` | [hurtdrop](elements/hurtdrop.md) |
| A rewind does not undo a banner's cut (`bn` shared, `snapAll` shallow) | `snapAll` | fixed (38b): the cut record is copied and put back | [banners and slides](elements/banners-and-slides.md) |
| Beside a sand lift the `lift` hint says "Step on the plate", and there is no plate; riding a sand lift learns `lift` | `checkHints` | fixed (38b): its own hint and learned move, `sandlift` | [lifts](elements/lifts.md) |
| Once a sand lift's slab has left, its top mouth's play plane shuts (`f.gT` 0) with no slab drawn there | sand lift update | fixed (38b): the plane stands only while the slab is within the top storey | [lifts](elements/lifts.md) |
| Roof blocks hang again after a respawn | respawn | not a fault: a respawn rebuilds the floor and every trap resets; the comment now says so (38b) | [roof blocks](elements/roof-blocks.md) |
| The stakes, the saw's blade and the pendulum are not carved out of the lamp shadow either | `glMask` | confirmed and fixed with the slabs (38a) | [spikes](elements/spikes.md), [saws](elements/saws.md), [pendulum](elements/pendulum.md) |
| Torchlight's shafts test only the first four blocker quads in view | `beamBlockers` | fixed (38a): `GLC_BK` 8, those in a beam's haze first; lift mouth slabs block too, both modes | [slicer jaws](elements/slicer-jaws.md) |
| No test covers a saw turned into spikes under a low ceiling | end of `buildLevel` | `sawceil.py` (38c): 4 of 519 saws on floors 1-48 x 3 seeds; the bot plays each | [saws](elements/saws.md) |
| `estPath` has no `saw` entry | `estPath` | no change: no timed stretch holds a saw or darts (38b, floors 1-48 x 3 seeds and P4 forced) | [saws](elements/saws.md) |
| The fork's grating takes no beam footprint | grating draw | fixed (38a): `fpMarkGrate` marks its bars | [gates](elements/gates.md) |
| The recruit's HUD hearts and rank name are light blue (`#8fa3d8`) under the rule "no guard in blue or white" | `TIERS[0]` | fixed (38b): rose `#e894a4` | [guards and snakes](elements/guards-and-snakes.md) |

Left as they are (found while fixing): the hanging roof block's shadow is not scanned (it sits inside the wall's carved face); about
1 px of unshadowed wall beside a stake or a rope inside his shadow (the carve is widened for the quarter-size mask); `JAWP` makes a
`Path2D` per jaw a frame (round 37b); a save whose sand-lift ride learned `lift` keeps it, so the plate lift's hint stays away for it.

### CLAUDE.md against the code

All corrected in CLAUDE.md before v83 (and `dev/FIGURE_SPEC.md`'s body table); kept here as the record.

| CLAUDE.md said (v82) | The code (CLAUDE.md now says so) |
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
| jaws with `EGP.traps` off are each style's v61 steel or iron | the metal is; the drawing (`JAWG`, spine, bevel, verdigris) is round 37b's in both |
| the re-skinned traps built in at round 4 | the code's comment says round 3 |
| Egyptian looks re-skin the traps | only the stakes and the jaws (`METAL_EG` holds the jaws alone); saws and the pendulum stay steel or iron |

### Stale comments in the code

All corrected in v83 (round 38c), `drawBar` included (the pull is the ropes' own swing `f.ps`, which `barPos` and so `swingPlace` use).
They were: Torchlight's header (falls back to Classic over ~22 ms: since v63 only `GLP.rs`); the shafts' march "jittered" (same steps every pixel);
caustics "round the Cistern's arches" (`LFX.caus` is nun and foggara); `krng` "the puzzles' stream" (it draws turn kits; `zrng` is the
puzzles'); timed side gates latched "two in five" (`%100<62`); `CYC` keeps the paternoster out of turns with a timed gate (any gate slot);
the dark drawn in Classic's emissive pass (after `hazePass`); the fire vent "lit through the whole window" from phase .70 (it hurts from .75, `on=ph>=0.75`; .70 is the bot's `danger` window); `doorHead`'s "pointed" kind (a flat lintel); every rank its own weapon
(soldier and veteran both the axe); `drawBar`'s pull "drawn only" (`swingPlace` uses it).

### Checks that the suite did not run

v82's `suite.py` ran none of `doorscan.py`, `stairscan.py`, `openscan.py`, `tilescan.py`, `beamwall.py`, `lampscan.py`, `slabscan.py`,
`wellscan.py`, `figscan.py`, `sandshaft.py`, `swingfeel.py`, and there was no standard tool for "layouts identical on floors 1-48 x 3
seeds". v83 (round 38c):

| Check | v83 |
|---|---|
| `lampscan.py`, `slabscan.py`, `sandshaft.py`, `wellscan.py` (9-75 s each), `r38b_tests.py`, `sawceil.py` | every tier |
| `figscan.py` | every tier where `hk_v69_release.html` is (kept locally, not in git) |
| `shadowscan.py`, `doorscan.py`, `openscan.py`, `tilescan.py` | release tier, split by floors (Torchlight jobs) |
| `stairscan.py` (about 3 min a floor here), `beamwall.py`, `swingfeel.py` | by hand |
| `layoutcmp.py` (round 38a; holds 38b's `layoutcmp_play.py`) | by hand: a generator round differs on purpose |
| `guardscan.py` | in the suite, and now in CLAUDE.md's table |

## Keeping them current

A round that changes an element updates that element's file in the same commit (its layer, rules, passes and relations) and its rows in
[layers.md](layers.md), and adds its History line; CLAUDE.md keeps the round's entry as before. A new element gets a file on the template above and a row in both tables here.
