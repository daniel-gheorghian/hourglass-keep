# Torchlight in WebGL: research, plan and stages (branch `webgl`, from v60)

Owner's brief: the best performance and the least heat **with the least visual impact**; bake or simplify as few shader
effects as possible, preferably none. Battery saver (`S.set.saver`) stays exactly as it is (every other frame drawn, 30 fps,
devicePixelRatio 1, the game still stepped at 60 Hz with interpolated rendering) and must work in both modes.

Earlier study: `webgl_research.md` (v52; summarised in section 2). This plan re-checks it against v60 and adds a catalogue of
the techniques available (section 1), then chooses the stages from it (section 3).

**Baked or simplified effects: none.** Every effect (relief, sky beams with haze, motes and bloom, shadows, metal, flames,
sand, mist and sheen, heat shimmer, grade, the churning storm, figure light, bloom, rewind/hit/last-life) stays live and is
computed per frame exactly as now. The gains come from not copying 2D canvases into WebGL, not drawing things twice, and
not making the GPU move pixels it does not need to move.

---

## 1. Catalogue of techniques

Columns: what it saves (CPU = script time; SYNC = stalls where the script waits for the GPU/GPU process; ALU = shader
arithmetic; BW = memory traffic, which on a phone is the main source of heat); whether it changes the look; whether it
applies to Hourglass Keep; verdict.

### 1.1 Getting pixels into WebGL

| Technique | Saves | Look | Applies here | Verdict |
|---|---|---|---|---|
| **Stop drawing the scene in Canvas2D and copying it (`texImage2D(canvas)`) every frame**; draw it with WebGL instead | SYNC (the big one: Safari makes the script wait until the 2D canvas is rasterised, then reads the IOSurface back into the web process and uploads it again: WebKit bug 294602 comment; bug 231031 measured ~6 ms per full-texture upload on iOS 15 Metal), BW (a full-screen read back + upload each frame), CPU | none if the 2D drawing is reproduced faithfully (edge antialiasing differs at sub-pixel level) | yes: the scene copy is the largest cost measured on the phone (6.7 ms at full size in v52 `?prof`, script "work" 9 to 10 ms in v54 `?bench`) | **do it** (stage 2) |
| Upload static content once (rooms, sprites, backdrop layers) as textures, never per frame | SYNC, BW | none | yes: room images (one per build), sprite canvases (once) | **do it** (stage 2) |
| One upload per room for both uses (scene and relief): the relief reads the room texture's mip level 1 instead of its own half-size copy | SYNC (one copy less per room built), BW | none (mip 1 is the same 2x2 average as the 2D half-size copy) | yes | **do it** (stage 2) |
| Upload only in "light" frames and at least 2 frames after the canvas was drawn (its raster is done) | SYNC | none | already done for relief copies (v53); keep for room textures | do it |
| Texture compression (ASTC via `WEBGL_compressed_texture_astc`, iOS 12+; ETC2 in WebGL2) | BW, memory | **yes**: lossy blocks on pixel-art stone; and our content is generated at run time, so it would need a JS encoder each build | rooms are generated in the browser | **no** (changes the look, encode cost) |
| `createImageBitmap` / `OffscreenCanvas` + `transferToImageBitmap` in a worker | moves raster off the main thread | none | rooms could be built in a worker; Firefox measured its transfer to be dominated by a CPU readback (bug 1864882), Safari unmeasured | later, optional (stage 5) |
| PBO / double-buffered uploads | SYNC on readback, not on canvas uploads | none | WebKit bug 235002: PBO helps `readPixels` only; we do no readbacks in play | no |
| Avoid `readPixels`, `getError`, `finish`, `getParameter` in the frame (MDN WebGL best practices) | SYNC | none | `?prof` uses `finish` on purpose (labelled); `getImageData` once per dissolving guard | keep out of normal frames (already) |

### 1.2 Drawing efficiently (batching)

| Technique | Saves | Look | Applies | Verdict |
|---|---|---|---|---|
| Batch geometry into few draw calls; split only on texture / blend / clip changes (PixiJS v8 performance tips; Phaser 3.60 "mobile pipeline": one bound texture, no `bufferSubData` stalls) | CPU (fewer GL calls through Safari's IPC) | none | yes: a recording facade turns ~600 to 1 100 Canvas2D calls a frame into one vertex buffer and a few dozen draws | **do it** (stage 2) |
| Uber-shader: solid, gradient and image fills in one program, chosen per vertex | CPU (no program switches), batches | none | yes | do it |
| Texture atlas for small sprites (Pixi spritesheets; Defold single atlas cut draws from ~150 to ~40) | CPU (fewer batch breaks) | none | sprite canvases are many and small; first measure batch count | later (stage 4) if batches are many |
| Instancing (`drawArraysInstanced`) for particles | CPU, vertex BW | none | particles are few hundred quads; plain batching suffices | not needed |
| Vector shapes tessellated per frame on the CPU (Pixi Graphics, Phaser Graphics, NanoVG, Ruffle/lyon) with earcut for concave shapes | replaces the 2D raster | edge AA by 4x MSAA instead of analytic coverage | our figures change every frame; this is the only way to keep the drawing code and its look | **do it** (stage 2) |
| MSAA 4x render target + resolve (WebGL2 `renderbufferStorageMultisample` + `blitFramebuffer`); on Apple's tile GPUs the samples live in tile memory and the resolve is cheap | — (needed for AA) | AA at 4 levels instead of analytic | yes | do it; `invalidateFramebuffer` the multisample attachments after the resolve so they are never stored |
| "Draw once per call" with a per-call depth value (`NOTEQUAL`) so a stroke or fill never blends twice over itself | — | makes translucent strokes match Canvas exactly | yes | do it |
| Stencil clips (nested levels) and stencil-then-cover for self-intersecting / even-odd fills (NanoVG) | — | exact clip and fill rules | yes | do it |
| CanvasKit (Skia wasm) or PixiJS as the facade | — | — | studied in `webgl_research.md` §6: 7 MB wasm, raster-only Canvas emulation, or a retained scene graph | no |

### 1.3 Tile-based GPUs (Apple TBDR) and render passes

| Technique | Saves | Look | Applies | Verdict |
|---|---|---|---|---|
| Clear (or invalidate) every target at the start of its pass so the tile is not loaded from memory (Apple: load action Clear/DontCare; Unity/PowerVR: "clears at the start of the RenderPass are free"; Mozilla MobileGPUs) | BW | none | the bright pass, the blur, the mist pass and the composite draw full-screen without a clear: ANGLE then has to load the old contents | **do it** (stage 1) |
| `invalidateFramebuffer` on attachments not needed after the pass (depth/stencil, MSAA colour after resolve) | BW (no store) | none | yes for the new MSAA scene target | do it (stage 2) |
| Fewer render passes / fewer full-screen intermediate targets (Apple TBDR guide; Arm "Bandwidth-efficient rendering", Bjorge, SIGGRAPH 2015) | BW | none if merged exactly | already few: light map, bright, blur (all ¼), relief (½), atmo (¼), composite, storm (¼). Merging the blur into the composite would change the bloom (it is a separable 5+5 tap blur) | keep; no merges that change the result |
| Dual-filter (Kawase) bloom | BW | **yes**: a different blur shape | — | no (changes the look) |
| Keep intermediates small (light map, bloom, atmo at ¼; relief at ½) | BW, ALU | — | already so | keep |
| `preserveDrawingBuffer:false` (default; Khronos/WHATWG: lets tilers skip copying the last frame) | BW | none | already default | keep |
| Scissor full-screen passes to the area that needs them | ALU, BW | none | already: metal (box), beams (box), storm (box) | keep |
| Framebuffer fetch / programmable blending | BW | — | not exposed to WebGL | n/a |

### 1.4 Precision and formats

| Technique | Saves | Look | Applies | Verdict |
|---|---|---|---|---|
| `mediump` in fragment shaders (Apple GPUs have 16-bit registers; 32-bit values take two: realworldtech on Apple's GPU; Unity's guidance: half everywhere but positions and UVs) | ALU, registers, power | can band where precision matters (UVs on a 1704 px target, the storm's noise, metal glints' world cells) | most passes are `mediump` already; composite, atmo and storm use `highp` where measured to need it | keep as is (changing it risks banding) |
| 8-bit targets (RGBA8) instead of half float | BW (half the bytes) | — | all targets are RGBA8 already | keep |

### 1.5 Resolution and frame rate

| Technique | Saves | Look | Applies | Verdict |
|---|---|---|---|---|
| Lighting at reduced resolution, sprites at full (2D light maps) | ALU, BW | none (already our design) | light map, bloom, atmo ¼; relief ½ | keep |
| Dynamic resolution (`GLP.rs`) | ALU, BW | blur when on | today it shrinks the *copy*; with the scene drawn by GL it becomes a real render scale (fewer pixels drawn) | keep the ladder; it should now rarely trigger |
| Battery saver (owner's setting): every other frame, dpr 1 | everything | the owner's choice | exists | keep exactly; benchmark it (`?bench=saver`) |
| Frame-rate cap / lower default scale | everything | changes feel | the owner's 30 fps option is Battery saver | no new setting |
| Skip identical frames (pause, menus, card between floors) | everything while idle | none | the loop already draws only every 20th frame when not playing | keep |
| Temporal amortisation (update slow effects every other frame) | ALU | **can show** (stepping) | every effect here moves with the camera | no |
| 120 Hz ProMotion: Safari pages run near 60 Hz unless the user turns off "Prefer Page Rendering Updates near 60fps" (WebKit bug 294338); Low Power Mode caps rAF at 30 fps (WebKit bug 215745, intentional) | — | — | the game steps at 60 Hz with interpolation, so both are handled; `glTime` judges intervals | no change; note for measuring |

### 1.6 Context and JS

| Technique | Saves | Look | Applies | Verdict |
|---|---|---|---|---|
| Context options: `alpha:false`, `antialias:false` (we resolve our own MSAA), `depth:false`, `stencil:false` on the default framebuffer | BW | none | already so | keep |
| `powerPreference` (WebKit treats default as low-power; iPhones have one GPU) | — | — | no effect on iPhone | keep |
| `desynchronized` | latency | — | not in WebKit's WebGL attributes | n/a |
| No per-frame allocation in the hot path (GC pauses) | CPU spikes | none | the facade writes into preallocated typed arrays; `glFrame` stops splitting colour strings every frame | do it |
| Handle `webglcontextlost` (Pixi forum, WebKit 286297: uploads push iOS into context loss) | robustness | — | today → Classic; keep | keep |

### 1.7 WebGPU and native engines

| Item | Finding | Verdict |
|---|---|---|
| WebGPU on iOS | on by default in Safari 26 (iOS 26, 2025); the 2D canvas → texture copy fix (WebKit 320765@main, 2026-09-09) is in WebGPU's path and not yet in a shipped iOS | not now: older iOS would lose Torchlight; the rewrite in WebGL2 removes the copy on every iOS |
| Godot web export | WebGL 2 only (Compatibility renderer); warns that Safari has WebGL 2 problems; mobile budgets "tight" | we already target WebGL2 |
| Unity WebGL on iOS | slowness attributed to Safari's WebGL-to-Metal translation; advice: fewer draw calls and blended draws, atlases, compressed textures, memory under ~300 MB | batching yes; compression no |
| Defold HTML5 | release build (no GL error checks), atlases, avoid stencil clipping (breaks batches), High DPI off for slow devices | no `getError`; stencil only where Canvas clips |
| PixiJS v8 | batch, spritesheets, `antialias:false`, avoid many complex Graphics rebuilt per frame | we accept per-frame tessellation (figures move every frame) but keep it in typed arrays |
| Native mobile 2D games | sprite atlases, one render pass with lights at low resolution, no readbacks, MSAA resolved on tile | the same tools, applied above |

Sources: WebKit bugs [294602](https://bugs.webkit.org/show_bug.cgi?id=294602), [231031](https://bugs.webkit.org/show_bug.cgi?id=231031),
[235002](https://bugs.webkit.org/show_bug.cgi?id=235002), [215745](https://bugs.webkit.org/show_bug.cgi?id=215745),
[294338](https://www2.webkit.org/show_bug.cgi?id=294338), [216010](https://bugs.webkit.org/show_bug.cgi?id=216010);
Apple, [Tailor your apps for Apple GPUs and TBDR](https://developer.apple.com/documentation/metal/tailor-your-apps-for-apple-gpus-and-tile-based-deferred-rendering),
[Metal best practices: load and store actions](https://developer-mdn.apple.com/library/archive/documentation/3DDrawing/Conceptual/MTLBestPracticesGuide/LoadandStoreActions.html);
[MDN WebGL best practices](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_best_practices);
[Mozilla mobile GPUs](https://wiki.mozilla.org/Platform/GFX/MobileGPUs); Unity on [invalidate vs clear (PowerVR)](https://issuetracker-mig.prd.it.unity3d.com/issues/android-opengl-not-every-renderpass-calls-glinvalidateframebuffer-when-blit-type-is-set-to-never);
Khronos list on [preserveDrawingBuffer and tilers](https://www.khronos.org/webgl/public-mailing-list/public_webgl/1110/msg00011.php);
Arm, [Mali best practices](https://developer.arm.com/community/arm-community-blogs/b/mobile-graphics-and-gaming-blog/posts/arm-mali-best-practices) and
[heat is bandwidth](https://community.arm.com/support-forums/f/graphics-gaming-and-vr-forum/5781/optimize-for-thermal); dual-filter blur:
Bjorge, SIGGRAPH 2015 ([summary](https://code.videolan.org/videolan/vlc/-/merge_requests/7461)); [realworldtech on Apple's GPU](https://www.realworldtech.com/apple-custom-gpu/);
[Unity shader precision](https://docs.unity3d.com/2023.2/Documentation/Manual/SL-DataTypesAndPrecision.html); [Imagination: precision](https://docs.imgtec.com/performance-guides/graphics-recommendations/html/topics/demystifying-precision.html);
[caniuse ASTC](https://caniuse.com/wf-webgl-compressed-texture-astc); [MDN transferToImageBitmap](https://developer.mozilla.org/en-US/docs/Web/API/OffscreenCanvas/transferToImageBitmap), [Firefox 1864882](https://bugzilla.mozilla.org/show_bug.cgi?id=1864882);
[PixiJS v8 performance tips](https://pixijs.com/8.x/guides/concepts/performance-tips); [Phaser 3.60 mobile pipeline](https://unpkg.com/phaser@4.2.1/changelog/v3/3.60/MobilePerformance.md);
[Godot exporting for the web](https://docs.godotengine.org/en/4.x/tutorials/export/exporting_for_web.html); [Unity: WebGL slow in Safari](https://issuetracker.unity3d.com/issues/webgl-bad-performance-when-playing-in-safari);
[Defold HTML5 optimisation thread](https://forum.defold.com/t/how-to-optimize-game-for-html5/2993); [WebGPU in Safari 26](https://appdevelopermagazine.com/webgpu-in-ios-26/);
[WebKit WebGLContextAttributes](https://webkit.googlesource.com/WebKit/+/master/Source/WebCore/html/canvas/WebGLContextAttributes.idl).

---

## 2. Where the time goes today (v60)

A Torchlight frame: the whole scene (backdrop, room images, `drawDynamic`, ambient, grade strip, mist, glows, flames, storm
sprites, haze) is drawn in Canvas2D into `GLP.sceneC`; three masks (effect ¼, metal ½, figures in beams ⅛) are drawn in 2D
from per-figure silhouettes (`glSilhouette`, a 2D `figDraw`) and packed into one atlas canvas; one frame later (`glPrep` →
`glSubmit`) WebGL copies the scene (`glScene`: `texSubImage2D` of a 1704×786 canvas on this Mac's phone-sized bench) and the
atlas, then runs light map, relief (½, from half-size room copies uploaded once per room), atmo (¼), bright, blur, composite,
storm.

Phone (owner, v52 to v54 `?prof`/`?bench`): copy ~6.7 ms at full size, masks copy ~1.1 ms, beams 2.7, relief 2.4, shadows
2.0; script "work" 9.3 to 10.3 ms a frame against ~1.7 ms on the Mac. The difference is Safari's wait for the 2D canvases
and the read back + upload of each (WebKit 294602). The GPU passes themselves are cheap. Heat comes from that traffic
(about 5 to 6 MB read back and uploaded per frame, ~330 MB/s at 60 fps) on top of the passes.

Mac baseline (`bench.py torch`, main, AMD 5500M via ANGLE-Metal; frame times are vsync-bound, "work" is script time):
fps 59.0, mean 17.0 ms, work 1.6 ms, 153 rooms built, 89 relief copies in 120 s.

---

## 3. Stages

Each stage ships alone, keeps Classic unchanged, and is measured with `?bench` (phone) / `bench.py` (Mac), `?prof`, and a
pixel comparison of exact states against main (`GLP.pipe=false`; floors of every theme and time of day, beams, storm,
metal, fights, lifts, a rewind, darkness).

### Stage 1. Pass hygiene (small, no visible change)
* Clear each target at the start of its pass (bright, blur, mist, the default framebuffer before the composite): no tile
  loads on TBDR. Bit-exact: every pixel is overwritten anyway.
* No per-frame allocation in `glFrame` (ambient colour split, grade arrays, closures).
* `?bench=saver`: the bench with Battery saver on (30 fps, dpr 1), so the owner's setting is measured too.
* Phone: small BW saving (four full-screen-sized loads at ¼ and one at full size avoided); script unchanged. Verify:
  pixel-identical frames; rendersmoke/glauto.

### Stage 2. The scene drawn by WebGL (the big one)
* `G2D`, a recording Canvas2D facade on WebGL2: paths (lines, quadratic/cubic curves, arcs, ellipses, rects), flattened
  in device space at 0.25 px; fills by fan (convex), earcut (concave), stencil-then-cover (even-odd, holes); strokes
  with joins, caps and dashes; transforms; `save/restore`; clips as nested stencil levels; `globalAlpha`; composite modes
  (source-over, lighter, multiply, destination-out/in, source-atop); linear and radial gradients (stops in a ramp texture,
  geometry evaluated per pixel, colours interpolated unpremultiplied as Chrome and Safari do); patterns; `drawImage` of
  canvases (uploaded once, or every frame for the few that change: the dissolving guard). One vertex buffer per frame,
  one program, draws split only by texture, blend and clip. 4x MSAA, resolved once and the samples invalidated.
* `Path2D` is replaced by `HKPath` (a subclass that also records its commands), so the same paths work on both contexts.
  `CanvasGradient`/`CanvasPattern` record their arguments (prototype hooks), so gradients cached by the drawing code work
  on both contexts.
* Torchlight's `render()` draws into the facade instead of `GLP.sceneC`: the backdrop (its own small target, as
  `bgC` today), room images as textures (uploaded once per build, in a light frame two frames after it was built, as v53
  does for relief), the dynamic layer, ambient, glows, flames, storm sprites; the grade strip and the haze are image
  draws of their strips. The relief reads the room textures' mip level 1, so `glRelStage/glRelUpload` and their copies go.
* The masks stay 2D in this stage (their atlas copy and the one-frame pipeline remain), so the picture keeps the same
  timing; the facade's commands are replayed at the start of the next frame like today's copy.
* Classic does not change (same functions, real context). Without WebGL2 Torchlight uses today's path.
* Phone: the scene copy (6.7 ms at full size) and its wait go; relief copies go; JS tessellation adds ~1 to 2 ms (to be
  measured with `?prof`). Visual risk: AA of edges (MSAA 4x vs analytic), gradient banding, a missed Canvas feature;
  verified by pixel diffs per floor and per effect.

### Stage 3. Masks in WebGL, no frame of delay
* Silhouettes (one per figure, drawn by the facade in flat red into an atlas target), the effect mask, the metal mask
  and the beam occluders are drawn by the facade into their own targets; the existing atlas layout is kept on the GPU
  (`blitFramebuffer` of each mask into the atlas texture), so the shaders do not change.
* With no 2D canvas left to wait for, `glPrep`/`glSubmit` draw in the same frame: the one-frame delay of v52 goes.
* Phone: the masks copy (~1.1 ms) and the 2D silhouettes go. Risk: low (the same drawing code through the proven facade).

### Stage 4. Trim what still copies a canvas (done: the dissolve)
* The dissolving guard (S3-A) was the last canvas copied into WebGL every frame (its picture plus two noise masks built
  with putImageData). Now, from its second frame on, the guard is drawn by the facade into a slot of its own target and the
  noise threshold and the crumbling edge's sand are computed on the GPU from the same noise (uploaded once as a float
  texture) and the same 16-step ramp (`G2D._diss`, modes 5 and 6). The first frame still runs in 2D once, because the
  grains' starting points are read back from it (`getImageData`, as before).
* Not done (measure first): a sprite atlas (batches are 30 to 70 a frame), packing the vertex format further.

### Stage 5 (optional, not done). Rooms built without a 2D canvas
* Each room picture is still drawn in 2D and uploaded once (on a quiet frame two frames after it is built): about one a
  second while moving. Drawing `drawRoomStatic` through the facade straight into a texture would remove that copy, but a
  whole room is ~5 000 calls of JS tessellation in one frame (the 2D build is spread over three frames); it needs the build
  split across frames into a kept target. Worth doing only if `?prof` on the phone shows room uploads as spikes.

### What the owner should measure on the phone
On the preview build: `?bench` (Torchlight, full size, the new path), `?bench=2d` (the same build, the scene drawn in 2D
and copied: the v60 path), `?bench=saver` (Battery saver), `?bench=auto` (the game's own scaling and fall back), and
`?prof` (rows: `scene` = the facade's draw, `masks` = the atlas copy on the GPU, `lmap`, `relief`, `atmo`, `bloom`,
`compose`, `storm`; the step '2D scene (v60)' toggles the old path; a line gives vertices, draws, batches and uploads).
Compare the `work` column (script time a frame) and `mean`/`>20ms` of `?bench` against `?bench=2d`, and how warm the
phone gets after 10 minutes of play in each.

---

## 4. Results (branch `webgl`, measured on this Mac)

### Visual equivalence
Exact game states rendered in Torchlight by main and by the branch (`wgl_cmp.py`: the bot plays a floor to a tick or a
condition, the same clock and random numbers for every render, `GLP.pipe=false`, 14 renders, the WebGL canvas read back;
headless Chromium's SwiftShader, 1704×786). Differences in 0-255 over RGB; "flat" counts only pixels whose neighbourhood
in main is flat (a difference there is not antialiasing).

| Stage | States | Mean | Pixels off by >24 (worst state) | Same, away from edges | Notes |
|---|---|---|---|---|---|
| 1 | 27 | 0 | 0 | 0 | bit-identical (1 LSB of driver noise in one state) |
| 2 | 77 | 0.56 | 0.071 % | 0.0038 % | every difference on a shape's edge (4x MSAA against analytic AA) |
| 3 | 84 | 0.56 | 0.075 % | 0.0032 % | mask atlas itself (`wgl_maskcmp.py`): mean 0.03, 0.35 % at edges |
| 4 | 34 + 17 | 0.55 / 0.61 | 0.081 % | 0.0009 % | the second set: fights, dissolves (also mid-dissolve at 30, 55, 80 %) |

Per function against the real Canvas2D (`wgl_parity.py`: rects, circles, concave, star, even-odd, self-crossing, strokes
with every join and cap, dashes, linear and radial gradients, transforms, nested clips, composite modes, images, Path2D,
figures): mean 0.05 to 0.66, nothing off away from edges beyond 0.4 % (the 0.4 % is the 1.25 px figure outline's AA).
Classic against main (`wgl_classiccmp.py`, 34 states): identical (at most 1 LSB).

### Speed (bench.py, Chrome on this Mac's AMD GPU through ANGLE-Metal; Chrome copies 2D canvases cheaply, so the Mac
### cannot show the phone's gain: only the script cost added by the new path)
| Build | fps | mean ms | worst 2 s | work ms | relief copies |
|---|---|---|---|---|---|
| main (v60) | 59.0 | 17.0 | 19.8 | 1.6 | 89 |
| stage 2 | 59.2 | 16.9 | 20.0 | 2.1 | 0 |
| stage 4 (final) | 59.3 | 16.9 | 19.8 | 2.5 | 0 |
| final, `?bench=2d` (the v60 path in the same build) | 59.1 | 16.9 | 19.6 | 1.8 | 89 |
| Battery saver: stage 1 / final | 59.7 / 59.6 | 16.7 / 16.8 | 17.4 / 17.5 | 2.1 / 2.7 | 89 / 0 |

The new path costs about 0.9 ms more script on the Mac (tessellation: the stroker, earcut, ellipses). On the phone it
removes the scene copy (6.7 ms at full size in v52 `?prof`), the masks' copy (1.1 ms), the relief copies and the waits for
Safari's 2D raster, which made up most of the phone's 9.3 to 10.3 ms of script work in v54. Expected phone script work:
about 3 to 5 ms a frame at full size, and no frame of delay. To be confirmed on the phone with `?bench` against
`?bench=2d`.

---

## 5. After the first phone run (v61 merged)

Phone, ?bench (new path / v60 path in the same build / saver): fps 54.5 / 55.3 / 57.4, work 10.9 / 13.0 / 10.7 ms, >20 ms
frames 13 % / 10 % / 2 %. The new path ran cool, the v60 path warmed the phone. Owner: a stutter at the start of the green
level (floor 17) in every mode; the saver's lights flicker; a light edge waving on floors 1 and 5 (new path).

**WebKit on this Mac.** Playwright's WebKit (Safari's engine: its 2D canvas, its WebGL on ANGLE-Metal, its GPU process) runs
the game (`WK=1` with the wgl_* tools, the page served on 127.0.0.1:8765, Google Fonts blocked). It reproduces the copy cost:
the v60 path runs at 24 fps there (40 ms of script a frame), the new path at 60 fps (3.3 ms). It is the closest thing to the
phone on this machine.

| Finding | Cause | Change |
|---|---|---|
| Stutter at the start of floor 17 (every mode) | the storm's tiles for Classic (unit ST, v60) were baked at the floor's start, one whole tile a frame: 13 to 20 ms of script each on this Mac (50 to 150 ms on the phone) for ~15 frames; the crypt floor has a chase | Torchlight with the storm shader never used those tiles: no bake there. Classic (and Torchlight without it) bakes a few rows at a time within 2 ms a frame (`stormReady(ch,bud)`, the bakes are generators). Trace of floor 17's first 6 s (Chromium, Mac GPU): before 14 to 15 frames over 6 ms of work (10 to 20 ms), after none (Torchlight) / work at most 7.7 ms (Classic) |
| More >20 ms frames on the new path | each room picture built in the background was uploaded whole: in WebKit 12 to 18 ms of script for the read back, and the next frame 36 to 40 ms late; rooms come in threes as he moves | rooms are uploaded in strips of 80 rows (drawn into a small staging canvas, uploaded two frames later, one strip a frame): in WebKit each strip 4 to 7 ms, the next frame at most 21 to 24 ms; WebKit bench: worst frame (after the first) 37 to 72 ms -> 24 to 41 ms, >20 ms 3 % -> 2 % |
| GC pressure | the facade made 918 KB of garbage a frame (Chromium; the v60 path 310 KB): contour arrays, earcut nodes, closures | pooled contours (typed arrays), earcut node pool, no closures in fills and strokes: 610 KB a frame, the rest being V8 boxing doubles (JavaScriptCore NaN-boxes them, so on the phone it is close to the v60 path's) |
| Radial gradients looked different in Safari | Safari's 2D canvas mixes a radial gradient's colours premultiplied (CoreGraphics), Chrome and the facade unpremultiplied: e.g. a white-to-transparent radial is twice as bright halfway in Safari | the facade asks the browser's own 2D canvas once per kind (`g2GradPM`) and builds its ramps the same way: in WebKit the facade's radial now matches its 2D canvas (mean 0.6 against 15) |
| Saver: the lights flicker | measured in WebKit at the phone's size (568x189 CSS, dpr 3; saver: dpr 1, 30 fps): the same back-and-forth change rate on the new path and on the v60 path (0.57 % / 0.60 % of pixels a frame), twice normal Torchlight's. Not the lamps' own flicker (the same with 'Softer flashes'). It is moving lights at 30 fps on a light map of 142 x 48 texels | none (not a regression; changing it changes the saver's look) |
| Waving light edge (floors 1, 5) | not reproduced: still and scrolling cameras give the same frames on both paths in Chromium and WebKit, and live play (frames lined up by the camera) changes no more on the new path. Most likely the extra slow frames (a juddering camera on a bright diagonal edge) | the two fixes above; to be checked on the phone |
| MSAA | 2x against 4x in WebKit: twice the edge pixels off by >24 against the v60 path (0.091 % / 0.047 %) | kept 4x; `?prof` steps 'MSAA 2x' and 'MSAA off' measure its cost on the phone |
| `?prof` froze at 'sky beams off' | Classic's beam sprites (`ryBeams2D`, drawn on a 2D canvas) asked for a figure's silhouette and got a WebGL view: the native `drawImage` threw, every frame | `glSilhouette(e,true)` gives a 2D silhouette there; a ?prof frame that throws is logged on the table ('error: ...') and the steps go on. Every step checked in WebKit at the phone's size |
| Blocky light edge that shimmers (floor 10, owner: everywhere, most on light walls) | not reproduced on the Mac (Chromium, WebKit at 852x283 dpr 2, scene scale 1 and .5, floors 1 and 10): the final frame, the relief factor and the light map match the v60 path but for edge antialiasing (diffs x8, `wgl_relcmp.py`). Blocks of tile size with an older frame's picture are what a tile GPU leaves when a resolve is skipped: the scene's colour samples were dropped (`invalidateFramebuffer`) right after the resolve blit | only depth and stencil are dropped now (`&inv=1` restores the old way, for an A/B on the phone); each room strip has its own staging canvas. If it stays: the ?prof step that makes it go names the cause ('MSAA off': the resolve; 'relief': the relief) |
| Blocky light edge, found (round 3, floor 1 photo: the moonbeam's lower edge a staircase of squares that crawls as the view pans) | not precision (the shaft shader is highp, as in v60) and not the new path: the shaft's shadow march (12 steps toward the opening) began each quarter-size pixel at its own jittered offset, so along a shadow's edge neighbouring pixels stopped on different sides of the wall: squares of 4 canvas px (6 on the phone's display). The same squares are in v60 and v61 on the Mac (`wgl_relcmp.py`, crops x3) | every pixel marches the same steps (`n0=.5`); walls and figures are read between texels, so no bands show (beam states of floors 1, 5, 14, 22). The invalidate change is undone: colour samples are dropped after the resolve again (keeping them stored the 4x scene to memory every frame on the phone: heat, and no fix) |
| GPU time of the new path (round 3: frame 23.3 ms against v60's 17.4; the phone warm) | `wgl_gputime.py` (EXT_disjoint_timer_query_webgl2 in Chromium, this Mac's GPU) and `wgl_ops.py` (each scene op's screen area): the scene target took 3.0 to 3.3 ms, 40 % of it the stencil passes of rectangle clips (one rectangle: three stencil passes over its area at 4 samples), and its overdraw was 6 to 8 screens; 4x MSAA itself costs 0.35 to 0.45 ms once the clips are gone. ?prof's 'texImage2D' step does nothing on the new path (it switches the v60 path's upload): its -3.0 there is one step's noise | rectangle clips without the stencil: a scissor box plus each pixel's covered share in the fragment shader (antialiased as the canvas's clip; destination-in keeps the uncovered share); an opaque fill of the whole target before anything else becomes its clear colour. Scene 3.26 to 1.61 ms (floor 1), 2.97 to 2.04 (10), 3.26 to 2.26 (17); overdraw 7.7 to 3.9 screens (floor 1), 6.0 to 3.4 (10) |
