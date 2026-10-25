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
| [doors](elements/doors.md) | posts, lintel, frame, reveal; the opening, the leaf and the stairs beyond | L1 | live, right after the lamps | placed clear of a nearer face (`doorX`); he is cut at the opening (`doorClip`) |
| [lamps and light](elements/lamps-and-light.md) | bracket, shelf, socket on the wall | L1 | live, first | clipped at a ceiling over the cell |
| | a free lamp's stand | L2b | live, first | placement (`lampClear`) |
| | flame, tongues, embers | air at d ~1 | live, first | clipped at a ceiling over the cell |
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
| | flames (back row d .7, front row d .3), sparks | L2x, air | `drawEmissive`, after the figures | placement (floor on both sides, open above) |
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
| [swing bar](elements/swing-bar.md) | timber, pole | L2x along the depth | live, before the figures | clipped at the lintel's edge; the end grain 3 px proud (approved) |
| | ropes (d .1 and .9) | L2m | live | the same |
| [banners and slides](elements/banners-and-slides.md) | rod, runner, fringe | L2b, in front of the back wall (owner: it may cover windows and wall art) | live, before the figures | the faces and the landing's slab in the next column |
| [lifts](elements/lifts.md) | shaft's back plane, channel, counterweight | L1, L2b | `drawLift` half 0 | `liftOccl`, `liftOcclSide` |
| | rig, ropes, platform, paternoster slabs, sand, sand slab, the rider | L2 | half 0, the rider with the figures | `liftOccl`, `liftNearCut` |
| | mouth slabs | L2x | far half in half 0, near half in half 1 (after the figures) | `liftMouthCut` for the plate beside |
| | the foot's pit | L2f | room picture (`liftPitDraw`) | n/a |
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
