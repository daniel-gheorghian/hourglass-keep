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

### Stage 4. Measure, then trim (only what does not change the picture)
* Sprite atlas if `?prof` shows many batches; vertex format packing; render scale as a real scene scale.

### Stage 5 (optional). Rooms built off the 2D canvas
* Draw `drawRoomStatic` through the facade into the room texture (no room upload at all) or build rooms in a worker.

### What the owner should measure on the phone after each stage
`?bench` (Torchlight, full size), `?bench=saver`, `?bench=auto`, and `?prof` (rows: `scene` = the facade's replay,
`masks`, `lmap`, `relief`, `atmo`, `bloom`, `compose`, `storm`), plus how warm the phone gets after 10 minutes of play.
