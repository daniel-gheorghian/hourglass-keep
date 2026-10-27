# Layers

Which layer every part of every element belongs to, what may cover what, and what each light pass may touch. Round 39 (owner:
"We need a layering rule ... background, back wall, corridor, front wall ... take each of the game elements and assign them to one
layer ... check that we draw correctly the game elements").

## Example

Floor 4, seed 1: a banner hangs in the shaft in column 85, with a wall block in column 86 on its right. The cloth hangs in the corridor
in front of the back wall, so it may cover the back wall's art and its windows (owner). The wall block's front face stands on the
front plane, nearer than the cloth, drawn `HX` (8 px) left of its own cell, from X+24. The cloth runs to X+31, so its last 7 px lay over
that face on both storeys until round 39. The room picture already holds the face and the cloth is drawn after it, so only a cut
puts the stone back in front.

```
 screen x ->   X (col 85)               X+24  X+32 (col 86)
 back wall     ##########################|#####   L1: the cloth may cover it
 cloth         |X+1 ..................X+31|        L2: hangs in front of the back wall
 front plane                             |=======  L3: column 86's front face, from X+24: hides the cloth's last 7 px
```

## The layers

```
 far                                                                                         near
 L0 backdrop  | L1 back wall  | L2 corridor, depth d from 1 (back) to 0 (front)            | L3 front plane | L4 overlay
 the sky and  | the plane at  | L2b against the back wall (d ~ 1)                           | d = 0          | not in the world
 the far land,| d = 1: stone, | L2x across the depth (d 1..0): its far half, then           | wall blocks'   | the dark's rip,
 seen only    | its art, its  | L2m mid-depth (d ~ .5): the figures and what they meet,     | front faces,   | HUD, hit and
 through the  | openings,     | L2x's near half                                             | low ceilings'  | rewind looks,
 openings     | what is fixed | L2f flat on the floor's top face (the floor itself)         | faces, floor   | grade, vignette,
              | on it         | air: beam haze, mist, motes, smoke, particles               | slabs' lips    | the card
```

| Layer | Holds | Drawn in |
|---|---|---|
| L0 backdrop | sky, sun, moon, stars, clouds, `BGART` layers | `drawBackdrop`, only inside the openings' boxes, under `G2D.na` |
| L1 back wall | the back plane (`backCell`, decor), arch recesses and frames, window frames and panes, breaches' edges, scars, hangings, AO on it; lamps and their stands, doorways with their stairs and leaves, a lift shaft's back plane, channel and counterweight, a kick shaft's light and grips | room picture stage 0; live things fixed on it first in `drawDynamic` |
| L2 corridor | the floor's top faces, the side faces of wall blocks (the corridor's ends), every figure, trap, item and lift part between the back wall and the front plane, the air | room picture stage 1 (side faces) and 2 (top faces); live in `drawDynamic` and the air passes after it |
| L3 front plane | wall blocks' front faces (`wallCell` at `X-HX`), cornices, low ceilings' faces (the top `LOW_H` px, `X-HX`), floor slabs' lips (`FHH` 5 px under the top face's front edge, `X-HX`) | room picture stages 1 and 2 |
| L4 overlay | the dark's rip, the HUD, the hit and rewind looks, grade, vignette, the card between floors | after the scene (`glStorm`/`drawDark2D`, `hudLayer`, the composite) |

## Rules

- R1 order. A part may cover only parts of farther layers, or farther parts of its own layer. The room picture holds L1 and L3
  together and every live thing is drawn after it, so L3 in front of a live L1 or L2 part is never given by draw order: it is a cut,
  the nearer faces clipped out of the live drawing (`wallPress` and `figClip`, `CUT_AT_WALL`, `liftOccl`/`liftNearCut`, `cpCut`,
  `nearCut`, the debris clip). Inside `drawDynamic` the things fixed on L1 come first, then L2's far halves, its mid-depth, its near
  halves (`planeClip`).
- R2 openings. L1 covers L0 everywhere but its openings, and L1's art never runs over an opening (`doorscan.py`, `openscan.py`).
- R3 passes act per layer.

| Pass | May touch | Never | How it is kept |
|---|---|---|---|
| lamp shadow (Torchlight, effect mask r) | L1 only (the lamps hang on the back wall; floor tops are carved too) | L2, L3 | `glMask` carves faces, floors and lips, figures, `JAWP`, `SHC` (`shadowscan.py`) |
| relief | the stone of the room picture: L1, L3 | any live L2 thing over it | `glRel*` rubbings (`tilescan.py`, `liftscan.py`) |
| sky beams | L2's air (haze), L2's floor tops and flat things (footprint), L1's opening (rim, pane) | L3, L1 round the opening, sand | tile texture, `sandSegs`, `beamBlockers`, `fpGate` (`beamwall.py`) |
| figures' fill light | L1, L2, L3 | L0 | the scene's alpha (round 25c) |
| floor looks (sheen, embers) | L2's floor tops as the scene still shows them | anything drawn over them | alpha marks (round 31) |
| L4 | everything | | drawn last, not cut |

- R4 every part of every element has a row below; a new element adds its rows, and `layerscan.py` must print `layerscan: ok`.

Approved exceptions: the prince's hands on a ledge while the wall hides the rest of him (round 19, `figClip` mode 2); the swing bar's
timber end grain, 3 px proud of the lintel's face (round 18b); the lift mouth gratings, drawn after the shaft on the mouth's own
boundary; the sky clock's room glow, which is light (round 37c).

## Every element

Depth `d` runs from 1 at the back wall to 0 at the front plane; mid-depth (0.5) is where the figures walk. "Cut" names what keeps the
nearer stone in front of a live part (R1). Where a pass is left out of a row, the element's own file has it.

| Element | Part | Layer | Drawn | Cut by the nearer stone |
|---|---|---|---|---|
| [stonework](elements/stonework.md) | back plane, its art, arch recesses and frames, windows, breaches, scars, hangings, AO | L1 | room picture stage 0 | n/a (everything later covers it) |
| | side faces of wall blocks (the corridor's ends, d 0..1) | L2 | stage 1, before the front faces | n/a |
| | wall blocks' front faces, cornices, low ceilings' faces | L3 | stage 1 | n/a |
| | floor top faces | L2f | stage 2 (live tiles left out) | n/a |
| | floor lips | L3 | stage 2 | n/a |
| | rubble, breach rubble, fallen lamps and cloth, the hurtdrop's bites | L2f, laid on the floor | stage 2 scratch canvas (`rlEnd`) | `rlEnd`'s face clip |
| [openings and backdrop](elements/openings-and-backdrop.md) | sky, sun, moon, stars, far land | L0 | `drawBackdrop`, first, only inside the openings | n/a (R2) |
| | sky beams: rim and pane / haze / footprint | L1 / L2 air / L2f | S pass; Classic `ryBeams2D` | tile texture, `ryLow`, `sandSegs`, `beamBlockers` |
| [doors](elements/doors.md) | posts, lintel, frame, reveal; the opening, the leaf and the stairs beyond | L1 | live, right after the lamps | placed clear of a nearer face (`startDoorX`); he is cut at the opening (`doorClip`) |
| [lamps and light](elements/lamps-and-light.md) | bracket, shelf, socket on the wall | L1 | live, first | clipped at the ceiling's edge over its column and the next (`lampCeil`) |
| | a free lamp's stand | L2b | live, first | placement (`lampClear`) |
| | flame, tongues, embers | air at d ~1 | live, first | the same (`lampCeil`) |
| | glows and lights | light | glow sprites, light map | not cut (room light) |
| [checkpoint](elements/checkpoint.md) | pedestal, clock, halo, drops of light | L2m | live; after a lift it stands in | `cpX` places it, `cpCut` |
| | Classic's wide glow | light | | not cut (round 37c) |
| [spikes](elements/spikes.md) | tile and holes | L2f (lip L3) | room picture | n/a |
| | needles (d .26 to .78) | L2x | live; the nearer needles again after the figures | `CUT_AT_WALL` |
| [saws](elements/saws.md) | slot, blade | L2m | live, before the figures, clipped at the groove | placement (the slot keeps 18 px off any face) |
| [plates](elements/plates.md) | tile and plate (every kind, closers) | L2f (lip L3) | live | `CUT_AT_WALL`; `liftMouthCut` beside a lift's mouth |
| [cracked slabs and sand wells](elements/cracked-slabs-and-sand-wells.md) | slab or plank in place | L2f (lip L3) | live | `CUT_AT_WALL` |
| | a well's sand body and its cut face | L2x, d 0..1 | `drawWellGroup` | clipped to the pit |
| | falling slab, plank, chunks, billow, landing cloud | air | debris loop, `DUSTC` | the faces beside the fall, row by row |
| [hurtdrop](elements/hurtdrop.md) | the dark shaft | L1 (the shaft's back) | room picture | kept off nearer faces and openings |
| | landing heap | L2f | room picture | cut at the next wall's face |
| [fire vent](elements/fire-vent.md) | grate | L2f | live | placement |
| | flames (back row d .7, front row d .3), sparks | L2x, air | back row before the figures (round 42b), the rest in `drawEmissive` after them | placement (floor on both sides, open above) |
| [darts](elements/darts.md) | shooter's head | fixed on a riser's side face, juts into L2m | live | placement |
| | darts in flight, spent darts | L2m, L2f | live | cut at the mouth only |
| [roof blocks](elements/roof-blocks.md) | hanging block | L3 (flush with the ceiling's face) | live | its own face |
| | falling block, its pour and trickles | L2 box d 0..1, air | debris loop | the slot's hole and the faces beside it |
| | lying block | L2x, near half after the figures | live | placement (never beside a wall) |
| [movable blocks](elements/movable-blocks.md) | front face, top, side | L3, as a wall block | live, before the figures | figures pressed and cut at its drawn face |
| [gates](elements/gates.md) | slab (granite portcullis, iron gate, violet gate) | L2x, plane X+8..X+24 | far half before the figures, near half after (`planeClip`) | placement |
| | floor slot / timer dial and pair plaque on the lintel | L2f / L3 (fixed on the face) | live | n/a |
| | the fork's grating | L2f | live | placement |
| [slicer jaws](elements/slicer-jaws.md) | both jaws | L2x | far half before the figures, near half (`JAW_OV`) after | placement |
| [pendulum](elements/pendulum.md) | pivot, arm, blade | L2m | live, before the figures | placement (161 of 161 halls clear of faces) |
| [swing bar](elements/swing-bar.md) | timber, pole | L2x along the depth | live: the log and the pole from the grip back before the figures, the pole's near part and end grain after them (round 42b) | clipped at the lintel's edge; the end grain 3 px proud (approved) |
| | ropes (d .1 and .9) | L2m | the far rope before the figures, the near rope after them (round 42b) | the same |
| [banners and slides](elements/banners-and-slides.md) | rod, runner, fringe | L2b, in front of the back wall (owner: it may cover windows and wall art) | live, before the figures | the faces and the landing's slab in the next column |
| [lifts](elements/lifts.md) | shaft's back plane, channel, counterweight | L1, L2b | `drawLift` half 0 | `liftOccl`, `liftOcclSide` |
| | rig, ropes, platform, paternoster slabs, sand, sand slab, the rider | L2 | half 0, the rider with the figures | `liftOccl`, `liftNearCut` |
| | mouth slabs | L2x | far half in half 0, near half in half 1 (after the figures) | `liftMouthCut` for the plate beside |
| | the foot's pit | L2f | room picture (`liftPitDraw`) | n/a |
| | a sand lift's spike pit (round 41b): the spikes (a fixed spikes feature) hidden in the sand under the slab's top, standing through the slab at rest | L2f with the spikes (lip L3) | `drawNeedles` with `L.dyn`, after the lift's half 0 | clipped under the slab's top while it is above them |
| [kick shafts and jet streams](elements/kick-shafts-and-jet-streams.md) | light band, grips | light on L1, marks on the faces | live | the band stops at the face |
| | jet stream grains | air | live | clamped to the shaft, its right limit the face (`X+TW-HX`) |
| [flasks and secrets](elements/flasks-and-secrets.md) | flask, a hidden flask's stars | L2m | live | placement; the stars cut at the face |
| | the secret's cue | L2f, on the lip's top | live | n/a |
| [prince](elements/prince.md) | body in every state, blade | L2m | live, after every L2 far part | `wallPress` (faces on either side, a moving block's drawn face) and `figClip`; figClip modes 1-2 behind a near ledge's wall (hands only, approved); hanging over open space, the ledge's lip and the near half of its top hide all but his hands (owner, round 39); `liftOccl` in a shaft; `doorClip`; dead: clipped without pressing |
| | contact shadow | L2f | with him | the same |
| [guards and snakes](elements/guards-and-snakes.md) | guards alive, dying, dissolving, dropping in | L2m | live | as the prince; a drop-in guard clipped at the ceiling's edge |
| | snakes | L2m at the floor | live | placement (no face within 34 px) |
| [the dark](elements/the-dark.md) | the rip, tatters, jackal, eyes, veil, dawn | L4 | `glStorm` / `drawDark2D`, last | never cut |
| | his shadow pulled back (`drawShut`) | L1 (on the back wall), L2f smear | before him | the faces in front |
| | the sanctum's arch outline | L2m | live | placement |
| [the Crossing](elements/the-crossing.md) | its own scene | by `crossZ`: 10-49 behind the path, 50 the doorway, 60 him, 70 and 60.5+f the foreground | `crossRender` | n/a |
| air (rendering) | motes, gusts, petals, smoke, bats, moths, ash, sparks, drips, FX particles, sword trails and rings | L2 air | `ambientLit`, `atmoPass`, `ambientGlow`, `drawEmissive` | a particle on a face is not drawn (`onFace`) |
| | floor mist | L2 air on the floor | `atmoPass` | clipped to its floor |
| | haze strip, grade, vignette, hit and rewind looks, HUD | L4 | last | never cut |

## Checks

| Check | What it holds | Pass |
|---|---|---|
| `layerscan.py [file] [lo hi] [seeds] [torch\|classic\|both] [kinds=] [phases=K]` | R1 for everything live at its rest: each kind drawn and left out (`LAYER_DBG.hide`, lamps' drawn glows off in both frames), the front plane's pixels must not change; at K clock phases where a kind moves; guards at their posts | `layerscan: ok` |
| `cpscan.py`, `liftscan.py`, `stairscan.py`, `doorscan.py`, `openscan.py`, `tilescan.py`, `shadowscan.py`, `beamwall.py` | R1 for the clock, lifts and the exit's climb; R2 for doors and openings; R3 for relief, shadows and beams | as in CLAUDE.md |

`layerscan.py` does not see what exists only in play (darts in flight, debris, dust, trails, the prince's states): round 39's pictures
cover those (dead, crouched, hanging, pushing, dropping in, falling slabs and planks).

## Round 39: what the audit found and what was done

Four audits (back wall and overlay; floor things; things across the depth; figures and air) split every element into parts, 230 in all,
and checked each against R1-R3 in code, with a census of floors 1-48 x 3 seeds and pictures. Counts are front-plane pixels the element
changed in a test frame (canvas px at phone scale, Classic), v83 -> v84.

| Fault (v83) | Seen on | v84 |
|---|---|---|
| a banner's runner over the next column's wall face or landing (7 px) | 1,503 of 2,379 banner tiles | cut there (10,648 -> 0); the relief rubbed off the cloth (`glRelBanners`) |
| the start door over the next wall's face (18 px) when the first run heads left | 38 of 96 floors | drawn clear of it (`startDoorX`); `L.start.x` unchanged |
| a sky clock on a sand lift's foot covered by the shaft and the slab after the ride | 33 of 96 floors | drawn after the lifts' back half (`cpOnLift`) |
| the left lift mouth slab drawn whole before the figures: he stood in front of its near face | 497 lifts, 237 sand-lift foot mouths | its front face drawn after the figures (`liftMouthL`) |
| the falling roof block and its trickles over the ceiling's face and the next wall | 411 of 411 blocks (first 0.15 s) | cut to the slot's hole and below (`roofFallClip`) |
| a falling cracked slab, plank, their chunks and billow over the walls beside the hole | 740 of 1,838 corridor slabs, 181 of 697 planks | cut row by row (`debrisCut`) |
| dead and dying figures never cut; a pressed guard snapped 20 px as it died | every death beside a wall | cut by the faces within reach, the last press kept (`deadCut`) |
| faces on the left never cut a figure (crouch 18 px in) | every left wall | pressed and cut on both sides (`wallPress`, `wallRows`) |
| pushing a block: cut at the tile's face, not the sliding block's | every push | the block's drawn face |
| drop-in guards drawn through the ceiling's stone | every reinforcement and ambush | clipped at the ceiling's edge (`dropCeil`) |
| hanging over open space: forearms and head over the ledge's lip | every such hang and climb | owner: "Cut the arms at the lip, keep only the hands" (`figClip` modes 3, 4) |
| his pulled-back shadow in a chase painted over the faces in front | every chase climb | clipped to where the back wall shows |
| lamp tongues, embers and glow over the slab above | 136 of 6,525 lamps | clipped at the ceiling's edge (`lampCeil`) |
| rubble and the hurtdrop's heap running onto a wall's face; the hurtdrop's dark over the next lip, a wall's face and openings | 199 of 2,450 breaches; 77 hurtdrops | `rlEnd` clips by the faces; the shaft's dark in stage 0 |
| air never cut: mist, motes, smoke, sparks, bats, petals, dust, glints | every frame | skipped on a face (`onFace`), soft sprites cut (`airCut`), mist cropped to its floor |
| the front stake drawn before him | every walk across live spikes | drawn again after the figures (`drawNeedles`) |
| darts clipped to an 81 px window: invisible after 80 px of a 131 px flight, still hitting | all 91 shooters | clipped on the mouth's side only |
| a hidden flask's stars over the wall face beside it | 23 of 48 | clipped at the face |
| the kick shaft's jet stream clamped 6 px into the right wall's face | all 236 shafts | limit at the face |
| Classic's beam footprint over the clock and lamp stands | | `ryStand` boxes |
| one gate's slot and far half over the lip beside its lintel | 1 of 1,438 | cut there |

Side effect: in a kick shaft the corridor at mid-depth is 24 px wide, narrower than his planted pose, so the walls cut him (v83 drew him
over the far wall; measured in round 42a, 60 px a planted frame). Round 42a draws him there as a climber in a chimney, seated against the
wall behind him with his soles on the other (`chimPose`, `chimClip`), so he fits between the faces: 98% fewer of his pixels past them, the
rest a few px of a sole or knee in motion, still cut. His silhouette's uses (lamp shadow, beams, fill) take his drawn x there (`chimSX`).

Round 42b (owner: "Fix the drawing overlaps you choose are most noticeable") took three off this list. The swing bar's near pole, end
grain and near rope are drawn after the figures (`drawBar(...,1)`), the far part and the grip before. The vent's back row of flames is
drawn before the figures, the sheet and front row after. And the standing things the lamp shadow did not carve are recorded in `SHC`: the
bar (`bar`), a counterweight lift's rig (`rig`), the paternoster's loop (`loop`), lamp flames and free lamps' stands (`lamp`), the sand of
wells and sand lifts (`sand`), falling slabs and planks (`debris`), the vent's flame (`vent`) and darts in flight (`dart`); `shadowscan.py`
floors 1-48 seed 1: 361 of 397 such things took his shadow before, 0 after. Banners and the wall lamps' bodies stay uncarved by choice:
they hang flat on the back wall, so the shadow on the wall falls on them as on the wall.

Left as they are: the slab's top piece above the ceiling's edge over the lintel's side face (round 14, the owner's look); banners and
the wall lamps' bodies taking the lamp shadow (flat on the back wall, above); additive glows over the sky raising Torchlight's
alpha a little; the relief on lamp bodies and the clock; the vent's merged sheet drawn whole in front of him (it rises from the whole grate); the beam cut lagging a pushed
block by up to 40 frames; hint streams and the descending cue's star brushing a face by a few px; the shadow, beam cut and fill cut at a
figure's play x, not its pressed x; glow sprites of lamps and the exit door, which are light (as the clock's room glow).
