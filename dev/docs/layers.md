# Layers

Which layer every part of every element belongs to, what may cover what, and what each light pass may touch. Round 39 (owner:
"We need a layering rule ... background, back wall, corridor, front wall ... take each of the game elements and assign them to one
layer ... check that we draw correctly the game elements").

## Example

Floor 9, a saw running to the end of its run beside a wall block. The blade turns at mid-depth in the corridor; the wall's front face
stands on the front plane, nearer than the blade and drawn `HX` (8 px) left of its own cell. So where the blade reaches past the
cell's right edge less 8 px, the face must hide it. The room picture already holds that face and every live thing is drawn after the
room picture, so the face hides the blade only if the blade's drawing is cut there.

```
 screen x ->      cell c (saw)                    cell c+1 (wall)
                  X                    X+TW-HX  X+TW
 front plane      .....................|=========|====== wall's front face (L3), drawn from X+TW-HX
 mid-depth             (  blade  )-->  |         |
                                    ^ blade past X+TW-HX: behind the face, must be cut
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
| lamp shadow (Torchlight, effect mask r) | L1, L2's floor tops | an L2 thing that stands, L3 | `glMask` carves faces, floors, figures, `JAWP`, `SHC` (`shadowscan.py`) |
| relief | the stone of the room picture: L1, L3 | any live L2 thing over it | `glRel*` rubbings (`tilescan.py`, `liftscan.py`) |
| sky beams | L2's air (haze), L2's floor tops and flat things (footprint), L1's opening (rim, pane) | L3, L1 round the opening, sand | tile texture, `sandSegs`, `beamBlockers`, `fpGate` (`beamwall.py`) |
| figures' fill light | L1, L2, L3 | L0 | the scene's alpha (round 25c) |
| floor looks (sheen, embers) | L2's floor tops as the scene still shows them | anything drawn over them | alpha marks (round 31) |
| L4 | everything | | drawn last, not cut |

- R4 every part of every element has a row below; a new element adds its rows, and `layerscan.py` must print `layerscan: ok`.

Approved exceptions: the prince's hands on a ledge while the wall hides the rest of him (round 19, `figClip` mode 2); the swing bar's
timber end grain, 3 px proud of the lintel's face (round 18b); the lift mouth gratings, drawn after the shaft on the mouth's own
boundary; the sky clock's room glow, which is light (round 37c).
