# Rendering

How a frame of Dawnward is drawn in both modes, in what order, what cuts what, and every Torchlight pass: what it reads, what it
writes, its switch, how an element joins it or stays out of it, and what Classic does instead. Element docs link here by the anchors
in the index below. The architecture's history is in `dev/WEBGL_PLAN.md`; working practice for the WebGL path is in
`dev/WEBGL_LESSONS.md`. Which layer every part of every element belongs to, and what may cover what, is [layers.md](layers.md); the cuts
that keep that order are below. This file states the code as of v84 (round 39, the layering rule).

## Index of passes

| Anchor | Pass | GLFX switch | Classic |
|---|---|---|---|
| [#g2d-and-the-replay](#g2d-and-the-replay) | G2D facade, `g2Replay`, targets, atlas | `wgl` | the real 2D context |
| [#light-map](#light-map) | `gatherLights` and the light map | none (Graphics' Lighting) | `lightPass` |
| [#key-light](#key-light) | `keyLight` | none | same |
| [#lamp-shadows](#lamp-shadows) | effect mask r, `glShadow`, carving in `glMask` (`SHC`, `shcCarve`) | `shadow` | none |
| [#heat](#heat) | effect mask g | `heat` | none |
| [#the-darks-veil](#the-darks-veil) | effect mask b | `storm` | `drawDark2D`'s shade |
| [#silhouettes](#silhouettes) | `glSilhouette`, `silPal` | none | same canvases (`d2`) |
| [#relief](#relief) | `glRelief`, the `glRel*` rubbings | `relief` | none |
| [#metal](#metal) | unit MS, `drawMetalMask` | `metal`, `metalGlint` | painted highlights (`METAL_PAINT_HI`) |
| [#sky-beams](#sky-beams) | unit RY, S pass, `beamBlockers`, `fpGate` | `shafts`, `fpgate` | `ryBeams2D` |
| [#atmosphere](#atmosphere) | S3-C M pass: mist, theme looks; caustics | `mist`, `lookfx`, `caustics` | `atmoPass`, `classicLookFx`, `lampGlints` |
| [#floor-looks](#floor-looks) | `floorFx`: sheen, embers; alpha marks | `sheen`; embers under `lookfx` | `classicEmbers` |
| [#bloom-grade-vignette](#bloom-grade-vignette) | bright pass, blur, composite | `grade` | `bloomPass`, grade strip, vignette gradients |
| [#ao](#ao) | corner shading baked in the room picture | `ao` | same (both modes) |
| [#distance-blur](#distance-blur) | backdrop layers softened at bake | `bgblur` | same (both modes) |
| [#the-dark](#the-dark) | `glStorm` | `storm2` | `stormLayer2D` |
| [#hit-and-rewind-looks](#hit-and-rewind-looks) | S3-A: rewind, hit, last life, dissolve | `rewind`, `hit`, `low` | `rewind2D`, `lowEdge2D` |
| [#checklist](#checklist) | what a new live element must do | | |

`GLFX` is a code-only table of switches (every key `true` by default; `?prof` turns them off one at a time). `GLFX.low` is the
last-life pulse, not low ceilings.

## Two modes

| | Classic | Torchlight |
|---|---|---|
| Setting | `S.set.lightMode='classic'` | `S.set.lightMode='torch'`, the default since v42 |
| Who switches | only the player: Graphics, button `gShader` ("Lighting: Classic") | same; `shaderOn()` also needs Graphics' Lighting (`GFX().light`) and a working `glInit()` |
| Scene drawn by | the visible 2D canvas `gx` | WebGL2 through `G2D` (`GLS.F`), then shader passes; `?wgl=0`, `?bench=2d` or no WebGL2: the v60 path (scene drawn in 2D into `GLP.sceneC`, copied with `glScene`) |
| Lights | a ¼-size 2D light canvas multiplied over the scene | a ¼-size light map in a shader, with flicker per kind |
| HUD | drawn on the same canvas after the scene | drawn on the 2D canvas above the GL canvas, only when `hudKey` changes |

- Fallback: a lost context (`webglcontextlost`) or a frame that throws in `glPrep`/`glSubmit` calls `glKill`, which sets the save to
  Classic (otherwise the screen would be black). No WebGL at all: `glInit` fails, `shaderOn()` is false and the frame is drawn as
  Classic. Slow frames never switch modes (v63, owner).
- Render scale: `GLP.rs` (1, 0.75, 0.5) scales only the scene target. Two 2 s windows in a row averaging over 38 ms step down
  (`glTime`); three windows under `UP_MS` (17.2 ms) step back up; a step up that turns slow within `UP_BACK` (10 s) doubles the windows
  needed (up to `UP_MAX` 30), reset each floor. Not stepped up in Battery saver or under `?prof`. `glauto.py` checks this.
- Battery saver (`S.set.saver`): every other frame drawn, devicePixelRatio 1, the game still stepped at 60 Hz; both modes.
- dpr is capped at 2. Classic's lamp glows are drawn at full strength; Torchlight halves every lamp's drawn glow (`GLOWK` 0.5)
  because the light map adds the light.

## The frame

`render()` runs the same drawing code on whichever context the mode gives it. Everything up to `glPrep` is shared.

```
render()                                  ctx = GLS.F (Torchlight) | GLP.sceneG (v60 path) | gx (Classic)
 |- fill the void #07060c                 G2D.na=1: the void and the backdrop leave the scene's alpha at 0
 |- drawBackdrop                          only the openings' boxes; composed at BGQ 0.42 in its own target (GLS.bg / bgC)
 |- room pictures in view                 drawImage(roomCanvas(rx,ry)); from here na=0 (alpha 1: not sky)
 |- gatherLights -> frameLights           this frame's lights (keyLight and every pass read them)
 |- drawDynamic                           everything live, see "Draw order"
 |- na=1; ambientLit                      ambient motes, trickles, petals, smoke, bats (none on a face: onFace, airCut, faceGap)
 |- Torchlight: lightPass(gradeOnly)      the grade strip multiplied; ryBeams2D only if !GLFX.shafts
 |  Classic:    lightPass + bloomPass     light canvas multiplied; lights' bloom sprites; ryBeams2D
 |- atmoPass, ambientGlow, drawEmissive   mist sprites (cropped to their floor), moths, glints; vent fire, FX particles (none on a face)
 |- hazePass                              the theme's haze strip at the top of the view
 |- drawDark2D                            in a chase, unless glStorm draws the dark (stormGL)
 |- Classic only: vignette, lowEdge2D
 |- Torchlight: glPrep                    glMask, glMetal, glcPre, glAtlas, then glSubmit -> glFrame
 '- hudLayer                              flashes, rewind2D streaks, HUD, text, ?fps (2D canvas)

glFrame (Torchlight)
 1 g2Replay        targets in order of pri: bg 0 -> sil, diss 1 -> mask, occ, metal (one atlas) 2 -> scene 9
 2 light map       1/4: clear to ambient, <= GLMAXL 64 lights as quads
 3 glRelief        1/2: rooms' mip level 1 against the light map's slope; rubbings
 4 glAtmo          1/4: S (shafts, caustics) and M (mist, theme looks), each only when on screen
 5 bright pass     1/4: (scene x light x 1.5 - 0.7) x 1.6, metal glints, beam footprint and rim
 6 blur            1/4: horizontal taps (the vertical taps are in the composite)
 7 composite       full size, see "Bloom, grade, vignette"
 8 glStorm         full size, only over the dark's rectangle, only in a chase
```

Room pictures (`drawRoomStatic`) are cached (`roomCache`, 18 rooms) and built in the background over three light frames, one stage
each (back plane, wall faces, floors: `startRoomJob`/`stepRoomJob`); a room needed now is finished at once. A changed cell
(`invalidateCell`: a tile fell, rubble landed, a block moved) marks the rooms that draw it dirty; they are redrawn on a frame with time
to spare while the live drawing covers the change. In Torchlight each room picture becomes a texture once (`g2Tex`, with mipmaps for
the relief); one built in the background goes up in strips of 80 rows, one strip a frame, two frames after it was drawn
(`g2Warm`/`g2Stage`, a staging canvas per strip). A canvas redrawn every frame must be marked `_glv=1`, or WebGL keeps its first picture.

The Crossing (`mode==='cross'`) hands the frame to `crossRender`/`crossGL` before the rooms: no room pictures, relief or floor passes
(see [the-crossing](elements/the-crossing.md)).

## The view

Oblique depth: the back of every block is drawn `DX` 16 px right and `DY` 8 px up from its front; `HX`, `HY` are half of them. Tiles are
`TW` 32 by `TH` 64 px, a room is `RW` 10 by `RH` 3 tiles (`ROOM_W` 320 by `ROOM_H` 192). Figures walk at mid-depth on the walking line
`SURF(r)=(r+1)*TH-4`. `onFloor(x,d,ys)` places a point at depth `d` (0 the front edge, 1 the back edge) on the floor at `ys`.

```
 a wall block at cell c (X=c*TW), row r (Y=r*TH)

        (X-HX+DX, Y-DY) +------------------------+ (X-HX+TW+DX, Y-DY)
                       /        top face        /|
        (X-HX, Y)     +------------------------+ |
                      |                        | |  right side face (sideFace):
                      |       front face       | |  X+TW-HX to X+TW-HX+DX
                      |       (wallCell)       | |
                      |                        | + (X+TW-HX+DX, Y+TH-DY)
                      |                        |/
        (X-HX, Y+TH)  +------------------------+ (X+TW-HX, Y+TH)

 the back wall behind an open cell (backCell) fills the cell's own rectangle X..X+TW, Y..Y+TH

 a floor cell (ys=SURF(r), fx=X-HX)

        (fx+DX, ys-HY) +------------------------+ (fx+TW+DX, ys-HY)    back edge, d=1
                      /  top face; figures walk /
                     /   on ys at d=0.5        /
        (fx, ys+HY)  +------------------------+ (fx+TW, ys+HY)         front edge, d=0
                     |   lip, FHH 5 px         |
                     +------------------------+
```

- The front plane is the plane of the front faces (depth 0). A wall's front face, a low ceiling's face (`lowCeil`, the top `LOW_H`
  px of its cell) and a floor's lip are all drawn `HX` left of their cell, so anything at mid-depth in the cell to their left can be
  overlapped by them. A wall on the left hides a mid-depth point left of its cell's right edge (its front face and the near half of its
  side face). Every rule about faces (shadow carving, beam cuts, `cpX`, `startDoorX`, `wallPress`, `nearCut`, `onFace`) uses that offset.
- A thing lying on the floor runs along the depth diagonal (`DX`, `-DY`); a reflection stands vertical (round 31).

## Draw order

Inside a room picture, by stage (each loop also draws the cells one outside the room, so faces that overhang a room's edge leave no
seam; the canvas clips at the room's edge):

```
stage 0 back plane   backCell + decor per cell (clipped to the cell; no decor on walls, low ceilings, openings)
                     arch recesses -> breaches -> arch frames -> windows
                     drawWallScars, drawHangings (EGP.noover leaves them out)
                     a hurtdrop's shaft: its back wall darkened, source-atop over its two cells (openings stay open; round 39)
                     doorway cut-outs: flat th.wall under each door and frame, the start door's at startDoorX (EGP.nocut leaves them)
                     aoBack (GLFX.ao)
                     ctBack: the courts' cut, colonnade, posts, parapet, light well (round 45)
stage 1 wall faces   side faces (behind the front plane) -> front faces: wallCell at X-HX, cornice, lowCeil
                     ctOver: the ceiling's face over a court (round 45)
stage 2 floors       slab(...,mark) per floor cell, except live tiles (loose s<2, plate, xplate, lplate, closer, grate)
                     and lift pits (liftPitDraw)
                     on the rlBegin scratch canvas: spike holes, rubble, a hurtdrop's hanging stones, chips and heap, breach
                     rubble, fallen lamps and cloth -> rlEnd (laid on cut by the walls' and low ceilings' faces, marked RL_A 251);
                     a hurtdrop's lip bites on the room itself
                     aoFloor
```

Between rooms: `render()` draws the room pictures row by row, left to right. They do not overlap, so nothing in one room picture
covers another. Every live thing is drawn after all room pictures, so the stone in a room picture never hides a live thing by itself:
the room picture holds the back wall (L1) and the front plane (L3) together, and stone in front of anything live is a clip (see "Cuts";
the layering rule's R1, [layers.md](layers.md)). Inside `drawDynamic` the things fixed on the back wall come first, then the corridor's
far halves, its mid-depth, its near halves.

Live, in `drawDynamic`:

```
lamps (drawLight: lampCeil) -> start door (startDoorX), exit door -> sky clocks (not one on a resting sand lift)
-> lifts (back half) -> a sky clock on a sand lift's resting slab (cpOnLift) -> L.dyn features by type (banners in nearCut,
   the three far stakes, a gate's far half in nearCut beside a lip)
-> movable blocks -> darts, spent darts -> hidden flasks' stars, secret cues, jet hints -> flasks
-> sand wells (once per group) -> dust clouds (airCut) -> debris (debrisCut, roofFallClip) -> snakes -> guards -> the prince
-> trails and rings (Graphics' Effects) -> near halves of gates, jaws, a fallen roof block; the front stake (drawNeedles)
-> lifts (front half: right mouths' near half, left mouths' front face, liftMouthL)
-> sandDraw (the crumbling guard's heap in deadCut, grains behind stone skipped) -> drawEmissive (only when Lighting is off)
```

## Cuts

Every cut keeps the nearer stone in front of a live part (the layering rule's R1, [layers.md](layers.md)); round 39 added the shared
helpers (`nearCut`, `onFace`, `airCut`, `faceGap`) and the rows marked 39.

| Cut | What it removes | Used by |
|---|---|---|
| `wallPress` + `figClip(...,wc)` | a figure reaching past a face beside it. On the right (the next column's front face): pushed left up to `HX`+12 px. On the left (39: the column before's front face and its side face's near half hide a mid-depth point left of that cell's right edge; `figReach`'s `left`): pushed right up to `HX`+4. Between two where it does not fit (a kick shaft, 24 px at mid-depth): drawn in the middle. Eased in `P.rdx`; the rest clipped at each face over its rows (`wallRows`, which takes a moving block's drawn face, not its cells; 39) | prince, guards |
| `figClip` modes 1 and 2 | behind a wall's face while jumping up to, hanging from or climbing a ledge on its near side: only the hands above the ledge show (round 19) | prince (`P.hideMode`, `P.hideLg`); `glMask` applies the same clip, so the hidden part casts no shadow |
| `figClip` modes 3 and 4 (39) | at a ledge with no wall below on his side (3: the slab on his right; 4: on his left), hanging, jumping up, climbing or climbing down: the slab's lip and the near half of its top face (and of its end) cut him, so below its mid line only the hands' grip shows (owner: "Cut the arms at the lip, keep only the hands") | prince; `glMask` too |
| `deadCut` (39) | a figure lying dead, a guard crumbling, its sand heap: not pressed (its reach does not know it lies flat), it keeps its last press (`P.rdx`, `g.rdx`) and is cut by every wall's or low ceiling's face within 28 px, from the face's left edge to its cell's right edge; a falling grain behind stone is skipped (`midHid`) | prince, guards, `sandDraw` |
| `dropCeil` (39) | a guard dropping in, above the ceiling's lower edge (a wall's foot; under the storey above's floor slab its lip's foot), in the drawing and in his silhouette | guards, `glSilhouette` |
| `CUT_AT_WALL` | a floor feature's top that would run behind a wall face on its right (plate, xplate, lplate, closer, loose, spikes); the front stake in the near-halves loop takes the same rectangle (39) | `drawDynamic` |
| `planeClip` | a gate's or jaw's far half (drawn before figures) and near half (after; `JAW_OV` overlap) | gates, jaws, their metal mask |
| `nearCut(ctx,c0,c1,r0,r1,fl)` (39) | the front plane in a block of cells as one even-odd clip: walls' front faces and low ceilings' faces (`HX` left of their cells); with `fl` also the floor slabs' top faces and lips (a slab ends at a wall's face on its right, as the room picture trims it; the strip under a slab's lip is that slab's) | a banner's next column, a gate's far half beside a lip, the hanging roof block's trickles, `roofFallClip`, `debrisCut`, `airCut` |
| `debrisCut` (39) | what falls through a hole (a plank, a corridor's cracked slab with its chunks and billow, the rock and slab with `EGP.traps` off): the next column's faces and floor slabs on every row it passes, the column before's faces and lip on the hole's row | the debris loop |
| the well's clip in the debris loop | a well's slab falling into its shaft, inside the group's columns (`g.xa`, `g.n` tiles), behind the walls' faces | [cracked-slabs-and-sand-wells](elements/cracked-slabs-and-sand-wells.md) |
| `roofFallClip` (39) | the falling roof block, its sand and billow outside the slot's hole and above the ceiling's edge, and the next column's front plane (`nearCut`) | `egRoofFall` |
| `liftOccl`, `liftNearCut`, `liftMouthCut` | lift parts and the rider behind the faces in front of the shaft; what stands nearer in the column right of it; a left mouth slab's front face is drawn after the figures instead (`liftMouthL`, 39) | [lifts](elements/lifts.md) |
| `doorClip` (`doorHead`) | the prince at the opening's head and jambs on the exit's stairs and coming out of the entry (at `startDoorX`, 39) | [doors](elements/doors.md) |
| `cpCut` | the sky clock by the faces beside it on its row | [checkpoint](elements/checkpoint.md) |
| `lampCeil` (39) | a lamp's tongues, embers, smoke and drawn glow above the ceiling over its column and the next: one rectangle where they match, else an even-odd path of the stone in front only | `drawLight` |
| `drawShut`'s clip (39) | his pulled-back shadow outside the back wall as it shows (cell by cell: under a wall's foot, a slab's lip, a low ceiling's face, short of the next face); its smear off anything but the floors' top faces | [the dark](elements/the-dark.md) |
| `rlEnd`'s face clip (39) | the floor's scratch layer (rubble, specks, breach rubble, fallen things, a hurtdrop's heap) on the walls' and low ceilings' faces | room picture stage 2 |
| `onFace(x,y)` (39) | a point of air on a wall's or low ceiling's face or a slab's lip: not drawn | motes, gusts, petals, bats, ash, moths, flies, sparks, wisps' trails, the torches' motes, FX particles, the sword's rings, `lampGlints`, the granite crystals |
| `airCut(ctx,x,y,w,h,fl)` (39) | a soft sprite of air: a rectangle (a scissor in Torchlight, so the stencil stays small), then `nearCut` in its cells | smoke puffs, wisps' glows, the landing dust cloud (`DUSTC`) |
| `faceGap(x,r,y0,y1)`, `FGX` (39) | the corridor's run between the nearest faces on a row: a trickle or drip on a face is not drawn, its pool or splash cut at the faces beside it | `ambientLit` trickles, `drawDrips` |
| the mist's source rectangle (39) | the floor mist past its floor's front edge and the faces ending its run on that row (the sprite cropped, no clip) | `atmoPass` |
| single clips (39) | a banner at a wall's face in the next column (a rectangle), a hidden flask's stars at a wall's face, a dart in flight on its mouth's side only, the kick shaft's jet stream inside the right wall's face (`wx1` `X+TW-HX`) | their elements |
| placement | `cpX` and `startDoorX` (39) move a drawing along the back wall off a nearer face; `lampClear`, the saw's slot, the pendulum's hall and the snakes keep away from faces | checkpoint, doors, lamps, saws, pendulum, snakes |

Light is cut the same way: no beam, haze or footprint on a front face, a low ceiling's face or sand ([#sky-beams](#sky-beams)); no lamp
shadow on a face ([#lamp-shadows](#lamp-shadows)); a mid-depth light (the sky clock's glow) is not cut, being room light, nor are the lamps'
and the exit's glow sprites (a lamp's drawn glow is cut at the ceiling over it, `lampCeil`).

Left as they are (round 39; round 42b drew the swing bar's near pole and rope after him and the vent's back row before him): a figure's shadow, beam cut, fill cut, relief ellipse and trails use its play x, not the pressed x; the hint streams and the
descending secret cue brush a face's end by a few px; in Classic a lamp's light band lies on the foot of a face. `layerscan.py` checks the
rest (below).

## Torchlight's passes

### G2D and the replay

| | |
|---|---|
| Reads | every Canvas2D call the shared drawing code makes on `GLS.F` (the scene) and on the mask facades |
| Writes | targets `bg` (the backdrop), `sil` (silhouettes, 768x576, twelve 192 px slots), `diss` (dissolving guards), the atlas (`mask`, `occ`, `metal` laid out by `glAtlas`, held in `GLA.G`), `scene` |
| Switch | `GLFX.wgl` (false, `?wgl=0`: the v60 path) |
| Join | draw with ordinary Canvas2D calls in the shared code; it then works in Classic, here and on the v60 path |
| Classic | the same functions on the real context |

`G2D` records paths flattened in screen pixels, fans, earcut, stencil-then-cover for self-crossing and even-odd fills, strokes with
joins, caps and dashes, gradients evaluated per pixel (stops in a ramp texture), composite modes, one vertex buffer a frame, 4x MSAA;
`Path2D` inside the game is `HKPath`. `g2Replay` uploads images first, then draws each target and resolves it once
(`blitFramebuffer`, depth and stencil invalidated first). Rectangle clips are a scissor plus coverage in the shader; other clips are
stencil passes (costly: keep them small). `glPrep` and `glSubmit` run in the same frame on this path (`GLP.pipe` only delays the v60
path).

Two facade flags carry meaning for later passes:
- `na` (no alpha): blends that leave the target's alpha as it is. On while the void, the backdrop and the full-view grade, glows and
  haze are drawn; off for rooms and `drawDynamic`. So the scene's alpha is "how much of this pixel is not the backdrop" (round 25c),
  which the composite reads for the fill light, the shadows and the floor marks.
- `ke` (keep alpha on erasers): destination-out and similar keep the alpha on the main scene; `fpMark` turns it off for its own eraser.

### Light map

| | |
|---|---|
| Reads | `frameLights` from `gatherLights(x0,x1,y0,y1)`: `{x,y,r,col,a,kind,bloom}` in world px |
| Writes | the ¼-size map: rgb the light, alpha the figures' fill share |
| Switch | none in GLFX (Graphics' Lighting) |
| Join | push an entry in `gatherLights` with a fitting `kind` |
| Classic | `lightPass`: ambient `lookOf(style).amb`, each light's sprite (`lightSprite`) added, the grade strip multiplied, all multiplied over the scene |

Ambient: `lookOf(style).amb` times `glAmbK(style,lk)`, which is `GLAMBT[style]` (palace 0.62, forge 0.6, dungeon 0.78, tile 0.8, crypt
0.9) raised so the brightest channel is at least `AMB_MIN` 0.45 of full. Each light is a quad with the classic sprite's falloff (1 to
0.62 at 0.28 of r, 0.2 at 0.62, 0 at the edge) and a flicker by kind (`GLFLICK`: torch 0.6, fire 1, door 0.5, item 0.35; times 0.3 in
"Softer flashes"). Classic has no per-kind flicker; both modes flicker a lamp's radius (`flK`).

| kind | Sources | `keyLight` | Shadow (`GLSTRONG`, r >= 84) | Metal lamps (`MSLK`) | Relief rubbing |
|---|---|---|---|---|---|
| `torch` | each unbroken lamp: r 150 x flicker (`r0` 150) and a low one 22 px under it, r 70 (`a0` 0.45) | yes | yes | yes | flame ellipse (r >= 100) |
| `win` | each window in the sky beam's colour, r 84; forge and crypt windows lit from within, r 92 | yes | yes | yes | no |
| `sky` | each opening's glow; the spill under an own-light window; Torchlight's bounce where a beam lands (dropped if `solidFront` stands between) | no | no | no | no |
| `fill` | prince r 84 a 0.42, guards r 56 a 0.22, snakes r 34 a 0.25 | no | no | no | snakes (r < 50) |
| `item` | flasks, the lit sky clock (r 150) or unlit (r 38), a running gate timer's glint | yes | no | yes | ellipse |
| `door` | the exit door while open, r 120, swelling during the exit (`exitSwell`) | yes | yes | yes | no |
| `fire` | a vent while it burns, r 110 | yes | yes | yes | ellipse |
| `trap` | faint glints so the dark never hides a trap (spikes, plates, saws, lifts, darts, bars, pendulum, roof blocks, falling sand), the sun on the lit clock's arch | no | no | no | ellipse |

Fill light (round 25c): the fill's share goes in the map's alpha; the composite and the bright pass subtract `FILL_C x fa x 1.5` where
the scene's alpha says the backdrop shows, so a figure's halo never lands on the sky. Classic: `fillCut` draws the fills apart and cuts
them where the room pictures are clear, except over the figures' silhouettes. The lamps, the fill, the ambient floor, the bounce, the door
light and the dark's drain are detailed in [lamps-and-light](elements/lamps-and-light.md).

### Key light

`keyLight(x,y)` returns which side the lamps light a point from (`sx` -1..1, `dir` its sign), how much a lamp rather than the default
carries it (`m`), a strength `k` and a colour. Every lamp in reach pulls by a smooth falloff over its steady radius, with a weak pull
from the left; never the nearest lamp, never a flickering radius (round 20b). Both modes. Read by the HD figures' rim (`drawActor`), the
granite portcullis' faces (`egSlab`, `uL`), the jaws, snakes, the sky clock and `stoneGlints` (`graniteGlints` reads it too, but nothing
calls `graniteGlints`). Details:
[lamps-and-light](elements/lamps-and-light.md#the-key-light).

### Effect mask

One ¼-size target (`glMask`, the light map's size), part of the atlas: r shadows, g heat, b the dark's veil. The composite reads it
blurred over five taps.

#### Lamp shadows

| | |
|---|---|
| Reads | the prince (not dead, dying, exiting, deep in the entry, or fallen off the level) and live guards in view; lights of a `GLSTRONG` kind with r >= 84 |
| Writes | effect mask r |
| Switch | `GLFX.shadow` |
| Join | anything drawn live in front of the back wall records its outline as drawn this frame in `SHC` (`shcBeg`, `shcRect`/`shcLine`/`shcEll`/`shcBox`, `shcEnd`), or a figure's shadow is painted across its face |
| Classic | none (the contact shadow ellipse under a standing figure, `drawActor`, is drawn in both modes) |

`glShadow` draws each figure's silhouette for its two nearest strong lights within 1.5 r (the second at 0.7), pushed away from the lamp
(`ox` clamp(0.6 dx ± 8, ±44), widened by `1.15+|ox|/50`), alpha up to 0.85. Then `glMask` carves in multiply: the figures themselves,
each wall block as drawn (front face `HX` left, top, right side; round 19: carving at the cell left a prince-shaped stripe on a lit face),
each floor's top and lip, a low ceiling's front face and its side face at a tunnel's right end (round 20a), the slicer's jaws by
their outline this frame (`JAWP`, inside the plane's visible part; round 37b), and after the jaws `shcCarve`: every outline in `SHC`
(round 38a). Before the carving, the prince's silhouette is clipped by `figClip` in every hide mode (1-4, round 39), so what a ledge's
wall or slab hides of him casts no shadow, and a guard dropping in is drawn into his silhouette only below the ceiling (`dropCeil`).
Composite: `sh` (times the scene's alpha: never on the sky) takes `0.85 sh` of the light and `0.4 sh` of the colour.

`SHC` holds typed arrays filled again each frame (`SHC_E` 128 entries, `SHC_PN` 4096 points since round 42b; nothing allocated): each entry is rings of
points in world px (a NaN x ends a ring) with the drawing's own rectangle clip and a kind (`SHC_K`). `render` sets `SHC.on` (Torchlight
with `GLFX.shadow`) around `drawDynamic`, so the drawings record only then. Thin things are recorded 1.2 px wider than drawn (the mask is
¼ size and read blurred). `SHC.off` skips `shcCarve` (v82's look, for counts before).

| Carved by `SHC` (kind) | Not carved |
|---|---|
| a portcullis or a lift's or sand lift's mouth slab that is down (`slab`; `egSlab`, recorded whole: two half clips meeting at X+16 left a line), the stakes (`stakes`, all four in the far pass), a saw's blade within its slot's clip (`saw`), the pendulum's blade and arm (`pend`), a falling roof block from the slot's hole down (round 39) or a lying one (`roof`), the sky clock and its pedestal (`clock`; the wall inside the arch keeps the shadow), flasks (`flask`), a lift's platform and paternoster slabs (`liftslab`), the platform's ropes, its sling legs and the paternoster's upright ropes (`rope`), the sand lift's slab (`sandslab`); round 42b: the swing bar's log, ropes and pole (`bar`), a counterweight lift's hoist beam, brace, hanger and sheave (`rig`), the paternoster's level runs and wheels (`loop`), lamp flames and free lamps' stands (`lamp`, `shcFlame`, `shcStand`), the sand of wells and sand lifts (`sand`, from `sandSegs`), falling slabs and planks (`debris`), the vent's flame (`vent`), darts in flight (`dart`) | the hanging roof block (inside the wall's carved face), the counterweight (in the back wall), banners and the wall lamps' bodies (flat on the back wall: the shadow falls on them as on the wall, round 42b's choice), doors, a let-go flask; the iron gate (`EGP.traps` off) |

`shadowscan.py [file] [lo hi] [seeds] [kinds=] [per=K]` stands the prince beside each kind with a torch behind him and draws Torchlight
with the shadow on and off: the thing's pixels (1.7 px in from its outline) must not change; it must print `shadowscan: ok` (floors 1-48
seed 1: 266 of 300 things before round 38a, 0 after; round 42b's kinds 361 of 397 before, 0 after: bar 39/40, rig 24/24, loop 10/14, lamp
83/96, sand 91/91, debris 80/92, vent 12/16, dart 22/24). A thing counts when more than 4 of its pixels are darker with the shadow on by more
than 24 (round 42b: darker only; the GPU's multisampled fine detail varied a few levels either way between renders).

#### Heat

Effect mask g: a green sprite over each vent while it burns (and a moment after) and over each lamp flame (r >= 100) at
`lfx().heat`, else forge 0.5, tile 0, others 0.25; times 0.3 in "Softer flashes". The composite reads the scene a little off in rising
ripples. Switch `GLFX.heat`. Classic: none.

#### The dark's veil

Effect mask b: the veil in front of the dark during a chase (`GLFX.storm`; with `storm2` only a soft strip, `glStorm` draws the rip).
The composite bends the scene toward the rip (a lens, the veil cubed) and greys and darkens the air before it (`u_sd` in the composite;
the shafts' shader uses the same name for the sand). Classic: `drawDark2D`. See [the-dark](elements/the-dark.md).

### Silhouettes

`glSilhouette(e,d2)` draws a figure once a frame, flat red (`mono '#ff0000'`), at twice the world's scale, in its own palette (`silPal`:
`PAL_HERO`, `guardPal(e)`, `PAL_SKEL`) with its sword when drawn. WebGL: a 192 px slot of target `sil` (twelve; a thirteenth figure gets
`null`). `d2` or the v60 path: a 2D canvas from `SIL.pool`. Cached per figure per frame (`SIL.m`, `SIL.m2`, cleared by `glPrep`).

Read by: `glShadow`, the beams' figure mask (`glcOcc`), the metal carve, Classic's `fillCut` and `ryBeams2D`. A guard dropping in is drawn
into it only below the ceiling's lower edge (`dropCeil`, round 39), as he is drawn. A palette key that
`drawFigureHD` reads must exist in every palette that reaches it: from round 7 to 27b the robbers' `khat` was missing from the old
silhouette palette, `figDraw` threw, and every guard cast no shadow and was drawn under the beams (round 27c).

### Relief

| | |
|---|---|
| Reads | the room pictures in view (their textures' mip level 1, `GLS.smpL1`); the light map |
| Writes | a ½-size factor around 0.5 (`GLREL.fb`), used by the composite as `l *= 1 + (f - 0.5) x 2 x GLREL_K (0.6)`, not over metal |
| Switch | `GLFX.relief`; the pass is skipped when no `torch`, `win`, `door` or `fire` light is in view, and in the Crossing |
| Join | anything drawn live over the room picture that hides the back wall needs a rubbing |
| Classic | none |

The height is the room picture's brightness (Sobel, edges only): lamp light rakes across joints, cracks and broken edges. Because it
reads the room picture, whatever is drawn live over the back wall would carry the wall's pattern embossed on it. So after the rooms'
quads `glRelief` lays rubbing quads that set the factor back to neutral (`GLRS.ex`), up to `GLREL_Q` 160 quads a frame:

| Rubbing | Over | Round |
|---|---|---|
| `glRelEx` (soft ellipse) | the prince, guards, lamp flames, `item`/`trap`/`fire` lights, small fills, debris; a moving iron gate with `EGP.traps` off | S3 unit B |
| `glRelSlab` | a granite portcullis whenever down, lift mouth slabs, a sand lift's foot mouths; from the ceiling's edge (it started `DY` above it and flattened 8 px of the lintel's face), the top piece above the edge too, short of a floor's lip beside the lintel | 16c, 26e, 39 |
| `glRelLifts` | paternoster slabs and wheels, the counterweight platform, its weight and wheel | 26a |
| `glRelBox` | a sand lift's sand (and its slab at rest in the foot's pit) | 21b, 37a |
| `glRelWell` | each sand well's body, cell by cell from its surface down | 21b |
| `glRelFloors` (`glRelQ`, `glRelLive`) | every run of live floor tiles (cracked slab, plate, xplate, lplate, closer, grate): exactly the top face and lip; pushed blocks (front, top, side) | 35c |
| `glRelJaws` | each jaw's plate to half way down its teeth | 37b |
| `glRelRoof` (called from `glRelFloors`) | a lying roof block (`stone` with `s` >= 2): its front, top and right side as `stoneBox` draws them; `EGP.traps` only | 38a |
| `glRelRoofFall` (called from `glRelFloors`) | a falling roof block (`L.debris` rock) only where `roofFallClip` lets it be drawn: each face cut by row to below the ceiling's edge or inside the slot's hole and short of the next column's face (`rcpCut`, Sutherland-Hodgman), laid as a fan of quads; `EGP.traps` only | 39 |
| `glRelBanners` (after `glRelJaws`) | each banner tile in view as `drawBannerTile` draws it (rod, runner, fringe), short of the next column's front plane where the cloth is cut, the gap of a cut runner left open (the wall shows through it) | 39 |

The room picture also flattens the back wall's art under each doorway (`drawRoomStatic`'s doorway cut-outs, round 15) so the doors drawn
live are not embossed. Left as they are (round 39): lamp bodies, free lamp stands and the sky clock are rubbed only by their lights'
ellipses (`glRelEx`: a flask and most of the clock are covered). Checks: `tilescan.py`, `openscan.py`, `doorscan.py`, `liftscan.py`.

### Metal

| | |
|---|---|
| Reads | the metal mask (½ size, `drawMetalMask`): b coverage, r which metal (`MKID` / 8), g the grain; the four strongest `MSLK` lights near the view's middle |
| Writes | light added in the composite and the bright pass, only inside the metal's box (`msPasses`, scissored) |
| Switch | `GLFX.metal`, `GLFX.metalGlint`; strength preset `GLMETAL_K` (`satin`) |
| Join | draw the part again in `drawMetalMask` with `msCol(msKind(role), grain)` and `msBox`, using the drawing's own geometry |
| Classic | the sprites' painted highlights (`METAL_PAINT_HI` is true unless the metal shader runs) |

In the mask: non-Egyptian gates (`EGP.traps` off), jaws (by `JAWP`), saws (a spinning-disc grain, up to four), the pendulum, gratings,
the v61 iron lifts, and the figures' swords and helmets (`msFig`); figures in front are carved by their silhouettes. Not metal: the
granite portcullis, the Egyptian lifts (rope, wood, stone), the swing bar (wood and rope, round 18b). `metalOf(role)` takes `METAL_EG`
(jaws bronze) over the style's table; `metalPal(role)` gives the painted colours from the same choice. The shader: a pillow normal from
the mask's edge, Blinn-Phong, Kajiya-Kay along a bar's grain or round a saw's centre, a lit edge, a rim, Filament's F0 per metal; glints
on fixed world cells so they do not crawl. Needs 8 texture units and 48 uniform vectors, else it is left out with one console note and
the frame is drawn by the program without metal code (`HK_NOMS`); `metaltest.py` checks both.

### Sky beams

| | |
|---|---|
| Reads | `skyBeam()` (the floor's one light from `SKYB` by time of day: dusk `a` -48, night 21, dawn 48; strength, colour, length, `q` depth per px fallen); `ryOps()` (windows, runs of open arches, open breaches) with their profiles (`ryProfile`, made once per floor); the tile texture (`glcTiles`: r wall, `LOW_R` 40 a low ceiling, g floor, b near water, a open arch); the figures' mask (`glcOcc`, ¼); `beamBlockers` (`u_bk`); the sand's outline (`sandSegs`, `u_sd`, `u_sf`) |
| Writes | the S pass (¼): rgb light on things, alpha the haze's share |
| Switch | `GLFX.shafts` (off: Torchlight draws Classic's `ryBeams2D` at 1.9 x `RY_2D`); `GLFX.fpgate` |
| Join | see below |
| Classic | `ryBeams2D`: sprites from the same profiles (`rySprite`: haze, rim, pane, footprint), `ryMotes2D` |

Up to `GLCMAX` 16 beams (nearest the view's middle). A pixel is in a beam by an exact test of the opening's shape swept along the light;
inside it a 12-step march (the same steps for every pixel, no jitter) finds walls, low ceilings, the floor slab, figures and blockers
between it and the opening. The light lands on the floor's top face in the opening's shape (the footprint), lights the opening's rim and
a window's pane, and the air glows against the dark only (haze, with motes). Forge and crypt windows are lit from within: a glow at
the pane, no shaft. Figures in a beam get only a weak capped light on the side toward it (`RY_FIG` 0.2, `RY_FIGC` 0.14) and never bloom
from it; the footprint and rim bloom a little (`RY_BLOOM` 0.5), the haze never. A figure's shadow down the haze is soft (round 28b:
the mask at ¼, three taps across the light).

How an element relates to the beams:
- Stands in front of the room's whole depth (a wall's or low ceiling's front face, sand): no beam light, haze, rim or footprint on it.
  Faces come from the tile texture; sand from `sandSegs` (at most `SDMAX` 24 segments; round 35b).
- Stands across the corridor's depth (a slicer's blades; with `EGP.traps` a granite portcullis, a lift's or sand lift's mouth slab that
  is down, the slabs by `blkSlab` through one shared gate state `BLKG`, round 38a): a quad in `beamBlockers` (up to `BLKMAX` 12), read by
  both modes, so the beam behind it is shaded and only the near half of the haze lies over it (round 20a). The shafts' shader tests up to
  `GLC_BK` 8 exactly (`u_bk[16]`; four before round 38a); when more than eight stand in the beams' box, those in a beam's haze go first
  (`glcBlk`, `GLCBL`, by `ryBlkLit`, Classic's test). `blkC` skips a blocker whose box the pixel's disc misses (same result, less work).
- Lies flat on the floor and is drawn live (plates, cracked slabs, planks, closers, a vent's grate): `fpMark` keeps the footprint on it
  (alpha 254, `FPM_A`); the fork's grating marks only its bars (`fpMarkGrate`: one path 2.4 px wide; the dark between them stays 255,
  round 38a). Anything else drawn live on the floor's face is alpha 255 and gets no footprint (`fpGate`, round 35b).

Classic: the beam sprites are cut by the walls' and low ceilings' faces (`ryLow`), the sand (`rySandCut`), what stands on the floor
(`ryStand`, `ryStandCut`: a saw's slot and blade, raised stakes, a lying roof block, flasks, and since round 39 a sky clock's pedestal
and a free lamp's floor stand; their own contact shadows stay lit floor) and blockers in a beam's haze (`ryHull`, drawn `RY_SH` 5 times
so the shadow fades and widens toward the floor); figures cut the haze to `RY_FIG2D`. Classic draws no figure shadow in the haze. Checks: `beamshot.py`, `beamwall.py`.

### Atmosphere

The M pass (¼, `glcM`; unit S3-C): what lies in the air or on the floor's skin; the composite veils the scene by its alpha and adds its
colour. Skipped when nothing of it is on screen and in the Crossing.

| Effect | Where | Switch |
|---|---|---|
| floor mist (height fog, lit by the light map) | crypt and dungeon styles, themes with dust, night except in the forge | `GLFX.mist` |
| caustics (in the S pass) | round the open arches near water where the look has `caus` (Waters of Nun, Foggaras of Garama) | `GLFX.caustics` |
| theme looks (`LFX`): salt, glaze, faience walls, granite, incense, arch dust | per theme, in the lamps' light only (the light map less the ambient) | `GLFX.lookfx` |

Round 45 (owner: "blotchy"): the arch dust (in open arches, and so in the courts) was value noise read through a narrow ramp, axis-aligned square patches at the pass's quarter size; it now takes lower, rotated frequencies and a wide ramp (`smoothstep(.18,.95)`, 0.3 of the old 0.42) and reads as haze. The courts' own L0 (`ctBg`) is drawn in `drawBackdrop` under `G2D.na`, so the composite treats it as backdrop (no fill light, no lamp shadow).

Rule (round 27d): no travelling bands in a look effect. The Blue Chambers' glaze was a sine of x and y that slid as slanted bars over
windows and beams; it is now soft noise patches that swell in place, times the scene's alpha (never on the sky). Sharp single glints stay
in 2D at full resolution (`lampGlints`, `stoneGlints`, and Aksum's granite crystals in `classicLookFx`, both modes; `graniteGlints` is
defined but never called). A glint or crystal on a wall's or low ceiling's face or a slab's lip is not drawn (`onFace`; round 39: they
tested the cell, so a face's left `HX` px kept them). Classic: `atmoPass` (mist sprites on floors, cropped through the sprite's source
rectangle to the floor's front edge and the faces ending its run, round 39; motes near lamps, none on a face), `classicLookFx` (embers,
incense), the haze strip (`hazePass`, both modes).

### Floor looks

`floorFx` in the composite (`GLSL_FL`, round 31): the wet flagstones' sheen (dungeon and crypt styles unless the look is `dry`: Nun, Garama, Osiris, Aksum; `GLFX.sheen`) and the Forges'
embers in the flagstones' joints (`lfx().embers`, under `GLFX.lookfx`; joints from `FLOOR_FT`, one texel a tile, as `slab()` draws them). They lie only on the
floor's own top face as the scene still shows it, read from the scene's alpha:

| Scene alpha | Meaning | Set by | `floorFx` | Footprint (`fpGate`) |
|---|---|---|---|---|
| 254 | the floor's own top face | the room picture: `slab(...,mark)` | yes (on a plain floor tile) | yes |
| 254 on an `FT_FLAT` tile (128 in `FLOOR_FT`) | a flat thing drawn live (plate, cracked slab, plank, closer, vent grate; the fork's grating on its bars only) | `fpMark`; `fpMarkGrate` | no | yes |
| 251 (`RL_A`) | what the room picture lays on the face: rubble, fallen stones and lamps, spike holes, a broken end | `rlBegin`/`rlEnd` | no | yes |
| 255 | anything drawn live over the face: a figure, saw blade and slot, stakes, a flask, a lamp stand, a block | any opaque live drawing | no | no |

Between the marks the gates fade: `floorFx` is full from 252 to 254 and fades out toward 251 and toward 255; the footprint is full up to
254.5 and fades out toward 255. So a soft shadow drawn over the face (which raises 254 a little toward 255) keeps most of both.

The sheen is a reflection: its streak stands vertical under the light, mirrored about the wall's foot, brightest at the front edge; the
embers keep v76's mean strength (owner). A new floor look goes in `floorFx`, never back in the mist pass. The `?wgl=0` path has no
marks and keeps the old overdraw. Classic: `classicEmbers` in the same joints, off feature tiles, cut where a figure stands.

### Bloom, grade, vignette

The composite, per pixel, in this order:

```
heat ripple (mask g) -> lens at the dark's edge (mask b) -> hkWarp (rewind ripples)
-> scene (hkScene: hit smear) x light x 1.5, less the fill over the sky, x relief, x (1 - 0.85 shadow), colour x (1 - 0.4 shadow)
-> msApply (metal) -> shafts and caustics (light x fpGate, plus haze against the dark) -> mist and looks -> floorFx
-> + bloom x 0.6 -> the dark's grey air -> hkGrade (rewind, last life) -> theme grade (saturation, shadow and light tints)
-> roll-off over 0.85 -> vignette
```

- Bloom: the bright pass keeps `(scene x light x 1.5 - 0.7) x 1.6`, metal highlights and glints, and the beams' footprint and rim;
  blurred at ¼ (horizontal taps in the blur pass, vertical in the composite). Classic: `bloomPass` adds each light's `bloom` sprite.
- Grade: the style's or theme's `GLGRADE`/`th.gr` times the hour's `TODG` (`gradeOf`, memoised); switch `GLFX.grade` and Graphics'
  Colour grade. Both modes also multiply the grade strip (top tint, 0.55 neutral, bottom tint: `lk.top`, `lk.bot`).
- Vignette: in the composite; Classic draws `vignette` (or `vignette2` with the grade on) after the scene.

### AO

Corner shading baked into the room picture from the tile map (`aoBack`: the wall's foot, under ceilings and ledges, beside walls;
`aoFloor`: a floor running into a wall, not on live tiles or lift pits), drawn source-atop so an opening is left alone. `GLFX.ao`; both
modes.

### Distance blur

Each backdrop layer is softened once when it is baked (`bgSoften`, a small image pyramid), more for farther layers (`bgBlurR(f)` on the
log of its depth factor); stars are left sharp. `GLFX.bgblur`; both modes. See [openings-and-backdrop](elements/openings-and-backdrop.md).

### The dark

`glStorm` (`GLFX.storm2`) draws the rip after the composite, at full resolution, only over the dark's rectangle, with the composite's
vignette, from the same table (`dkTable`) and art (`dkArt`) as Classic's `stormLayer2D` (drawn in `drawDark2D` after the haze). Nothing
lights it. See [the-dark](elements/the-dark.md).

### Hit and rewind looks

S3-A, strengths from `hkFxUpdate` each frame (`HK`):

| Look | Torchlight | Classic | Switch |
|---|---|---|---|
| rewind (`HK.rw`) | ripples toward the prince (`hkWarp`), a cool sepia and the edges drawn in (`hkGrade`) | `rewind2D`: saturation, multiply, edge gradient, rings | `GLFX.rewind` |
| hit (`HK.hit`, 0.4 s per hurt) | the scene read along the line from him with red and blue split (`hkScene`) | none (the figure's `flash` in both modes) | `GLFX.hit` |
| last life (`HK.low`) | a dark red pulse at the edges | `lowEdge2D` | `GLFX.low` |
| sand dissolve (`DISS`) | the guard drawn into a `diss` slot, threshold and edge on the GPU | 2D | `DISS.on` |

Both modes draw the sand streaks flowing back to him and the words in `hudLayer`. "Softer flashes" (`S.set.calm`) sets `HK.dist` 0.25.

## Checklist

A new element drawn live over the room picture must:

| Must | Why | Round that taught it |
|---|---|---|
| be drawn with ordinary Canvas2D calls in the shared code and checked in Classic, Torchlight and `?wgl=0` | one drawing code, three paths | v61 (WGL) |
| be rubbed out of the relief if it hides the back wall (`glRelFloors`/`glRelLive` for a tile type, `glRelBox`/`glRelQ` for a box or quad, `glRelSlab` for a slab), only where it is drawn | the relief reads the room picture, so the wall's art is embossed on anything drawn over it | 16c slabs, 21b sand, 26a lifts, 35c tiles, 37b jaws, 38a roof blocks, 39 banners, the falling block |
| have every palette key it reads in every palette that reaches it (`silPal`, `guardPal`, `PAL_HERO`, `PAL_SKEL`) | a missing key throws inside `figDraw`; the silhouette goes null and its shadow, beam cut, metal carve and fill cut with it | 27c |
| record its outline in `SHC` as drawn (`shcBeg` ... `shcEnd`, thin parts 1.2 px wider) if it stands in front of the back wall, so `glMask` carves it out of the lamp shadow; check with `shadowscan.py` | otherwise a figure's shadow is painted across its face | 19 walls, 20a low ceilings, 37b jaws, 38a the rest |
| add a quad to `beamBlockers` if it stands across the corridor's depth | otherwise a beam passes through it and its haze lies over it | 20a, 38a lift mouth slabs |
| call `fpMark` if it lies flat on the floor's face (or mark only its solid parts, as `fpMarkGrate`) | otherwise its opaque pixels refuse the beam's footprint (255) | 35b, 38a grating |
| keep off the sky: draw under `G2D.na` only full-view effects that are not things; never read the scene's alpha with a new dst-alpha blend on the main scene | the composite reads that alpha for the fill, shadows and floor marks | 25c |
| be marked `_glv=1` if it is a canvas redrawn every frame (better: draw it through the facade) | otherwise WebGL keeps its first upload; a marked canvas costs a readback every frame | v61 |
| allocate nothing per frame (cached sprites, gradients kept over their largest alpha, typed arrays) | GC pauses and ramp rows on the phone | v61 (WEBGL_LESSONS) |
| use rectangle clips where it can and no pass of its own (a new mask goes in the atlas) | stencil clips and passes cost more than their pixels on a tile GPU | v61 rounds 3-4 |
| take no jitter per low-resolution pixel and no travelling bands | staircases and crawling bars | v61b march, 27d glaze |
| light through `gatherLights`, not paint light into the scene; key looks on `keyLight`'s `sx`, never on one lamp or a flickering radius | both modes read the same lights; flicker flipped the slab's lit face | 20b |
| have its parts' rows in [layers.md](layers.md) and be cut by the stone nearer than its layer: `nearCut` (walls' and low ceilings' faces `HX` left of their cells; with `fl` the floor slabs) for a part, `onFace` for a particle, `airCut` for a soft sprite, `wallPress`/`figClip` for a figure, `liftOccl`/`liftNearCut` in a shaft; a part nearer than the figures is drawn after them (the near-halves loop); check with `layerscan.py` (`layerscan: ok`) | live drawing comes after every room picture, which holds the back wall and the front plane together, so the stone in front is never given by draw order | 19, 26a, 37c, 39 |
| be a pure function of the clock and its tiles where it animates (hashes, no generator stream) | rewind-safe, layouts unchanged | 21b, 26d |

Checks for rendering: `rendersmoke.py` (both modes, every floor), `glauto.py`, `metaltest.py`, `tilescan.py`, `openscan.py`,
`doorscan.py`, `liftscan.py`, `beamshot.py`, `beamwall.py`, `cpscan.py`, `shadowscan.py`, `stormfair.py`;
`layerscan.py [file] [lo hi] [seeds] [torch|classic|both] [kinds=] [phases=K]` (round 39, by hand, not yet in `suite.py`: views covering
every instance of each kind, each drawn whole and with that kind left out by `LAYER_DBG.hide`; the front plane's pixels must not change;
must print `layerscan: ok`);
pixel comparisons `wgl_cmp.py`, `wgl_maskcmp.py`, `wgl_parity.py`, `wgl_relcmp.py`; cost `wgl_calls.py`, `wgl_gputime.py`, `?prof`, `?bench`.
