# What the WebGL port taught us (for the next themes)

Practical notes for adding to Torchlight on the WebGL path (v62): the Egyptian themes' lamps, sand streams, the portcullis, roof
blocks, theme effects (LFX), new masks. The history (research, stages, every measurement) is in [WEBGL_PLAN.md](WEBGL_PLAN.md).

## The architecture in brief

- **One drawing code, two contexts.** The game's drawing functions are unchanged. In Classic they draw on the 2D canvas. In
  Torchlight they draw on `G2D`, a recording look-alike of Canvas2D (`GLS.F` for the scene). Paths are flattened in screen
  pixels. Fills are fans, earcut, or stencil-then-cover for self-crossing and even-odd shapes. Strokes carry joins, caps and
  dashes. Gradients are evaluated per pixel, and composite modes are blend functions.
  - `Path2D` is `HKPath`, which records its commands.
  - Gradients and patterns remember how they were made (prototype hooks), so the same objects work on both contexts.
- **Batching.** Everything goes into one vertex buffer and one index buffer per frame. A new batch starts only when the
  texture, sampler, blend, clip level or clip rectangle changes. Each fill or stroke gets its own depth, so a pixel is painted
  once per call.
- **Targets, in order (`g2Replay`):**
  1. The backdrop (low resolution).
  2. The silhouettes (192 px slots).
  3. The masks: effect mask, beam occluders and metal, drawn straight into their places in **one** multisampled atlas of
     fixed size. `GLA.G` holds the layout; `glAtlas` lays it out.
  4. The scene.
- **MSAA and the resolve.** Each target is 4x MSAA and is resolved once (`blitFramebuffer`) into its texture. Depth and stencil
  are invalidated *before* the blit, while the pass is still open, so they are never stored. Colour is invalidated after.
- **Light map and relief.** The light map (quarter size), relief (half size), atmosphere, bloom and composite are the same
  shader passes as v60.
  - The relief reads each room texture's mip level 1 (`GLS.smpL1`), so rooms need no copies of their own.
  - Lights come from `gatherLights` as before.
- **What is pipelined.** On this path `glPrep` and `glSubmit` run in the same frame: there is no frame of delay, and
  `GLP.pipe` only affects the v60 path. Only images that come from 2D canvases are pipelined: rooms are uploaded in strips two
  frames after they are built.
- **Fallback.** `?wgl=0` (also `?bench=2d`, or the ?prof step '2D scene (v60)') draws the scene in 2D and copies it one frame
  late, as up to v60. The v60 path is also used when WebGL2 is missing.

## Adding a drawn element, effect or mask

Draw it with ordinary Canvas2D calls in the shared drawing code. It then works in Classic, in the facade and on the v60
fallback. Prefer the following, for the reasons we found:

- **Gradients.**
  - Safari mixes *radial* gradients premultiplied and linear ones not; Chrome mixes neither premultiplied. The facade asks the
    browser once (`g2GradPM`), so a white-to-transparent radial looks the same on both paths. Do not hand-tune colours on one
    browser.
  - A gradient that fades every frame, with stops whose alpha changes, used to need a new ramp row each frame. Now the stops
    are stored over their largest alpha (`g._am`), and the fill's alpha carries that factor. This is exact. Fading by
    `globalAlpha` or by the stops' alpha is equally cheap.
  - Stops that change *colour* every frame still make a new row each frame; quantise the colour if it animates.
- **No CPU writes into a texture the GPU may be reading.** On the iPhone's shared memory, such a write makes Safari wait for the
  GPU. Per-frame data goes in the ring textures (`GLS.gpR`, `GLS.rampR`: three in turn, rows copied on the GPU before a write).
  For a new per-frame table, use a ring too, or vertex attributes or uniforms.
- **Clips.** An axis-aligned rectangle clip is free: a scissor box plus each pixel's covered share in the shader, antialiased
  like the canvas's clip. Any other clip shape is a stencil clip: three stencil passes over its box at 4 samples. That was 40% of
  the scene's GPU time before rectangles stopped using the stencil. Clip to rectangles where you can, and keep shaped clips
  small.
- **No new framebuffer pass per element.** On the phone a pass costs more than its pixels: ?prof showed about 1 ms per pass-like
  feature. A new mask goes into the atlas: add its region to `glAtlas`'s layout and its placement to `PL` in `g2Replay`. Do not
  give it a target of its own.
- **Fixed sizes.** Do not re-create renderbuffers or textures when a size changes. The atlas used to be made again whenever the
  metal box changed (every ~30 frames on metal floors). Size targets for the largest case.
- **No staircases from a low-resolution pass (rules S1-S7, `docs/rendering.md`, "Low-resolution passes").** The S and M passes
  draw at a quarter of the canvas and are upsampled bilinearly, so any edge they draw narrower than their texel (4 device px on the
  phone, 8 with Battery saver) is a staircase that crawls as the view pans. The beams were fixed for it six times, one edge at a time:
  v61b's march began each pixel at a random offset (take the same steps for every pixel); round 20a's three hard taps across a low
  ceiling's end; round 28b's figure mask at an eighth; round 46a's profile read texel by texel with entries that jumped 19 px at each
  pier, a floor counted by `if(t>tm)break;`, and edges soft over 1.5 px under a march stepping 5-10 px. In such a pass: no branch,
  threshold, `step`, `break` or `NEAREST` read on a value that varies per pixel unless it is ramped over two texels (`8 u_cam.z`); every
  transition two texels wide at Battery saver; discrete samples overlap (soft width at least their spacing); data such as the beams'
  profiles prefiltered once on the CPU and read `LINEAR`; world positions in `highp`. `beamjag.py` measures it (in `suite.py`).
- **MSAA samples are never stored.** Keep the invalidate calls. Round 2 tried keeping the colour samples, which stored the 4x
  scene to memory every frame: heat, and it fixed nothing.
- **Uploads from 2D canvases.**
  - A whole room uploaded at once made Safari wait 12 ms or more.
  - Rooms built in the background go up in strips of 80 rows, one strip a frame, each from its own staging canvas, two frames
    after the strip was drawn.
  - A canvas redrawn every frame (marked `_glv=1`) costs a readback every frame; draw that content with the facade instead.
- **No big one-time bakes at the start of a floor.** The storm's Classic tiles took 50 to 150 ms in one frame at the start of
  floor 17. They are now generators run within a time budget (`stormReady(ch,bud)`), and are skipped when the shader draws the
  storm. Spread any new bake the same way, or do it on the GPU.
- **Matching Classic.** The masks and the relief read the same game state as Classic. Light new things through `gatherLights`
  and the light map, not by painting light into the scene.

## iPhone against the Mac

- **The Mac cannot show:**
  - shared-memory stalls (a discrete GPU uploads through a staging copy);
  - the tile GPU's costs: passes, stored MSAA, load and store of attachments;
  - mediump precision: mediump is real fp16 on the iPhone. The game's shaders are highp where it matters, so check that any new
    shader is too.

  In WebKit on the Mac, the new path ran at 60 fps while the phone sat 4 to 5 ms over the v60 path. Only the phone decides
  frame-time questions. The Mac is good for pictures, call counts, leaks and relative GPU time.
- **Low Power Mode** caps requestAnimationFrame at 30 fps on the iPhone. Turn it off before any phone round, or every number
  halves.
- **dpr is capped at 2** (`Math.min(2, devicePixelRatio)`). The phone's canvas is 1704x566 for 852x283 CSS px. Test at
  `VP=852x283x2`, not at dpr 3.
- **Battery saver** draws every other frame at dpr 1; the logic still runs at 60 Hz.
- **Heat** follows steady GPU load, not leaks. In 6 minutes of play the textures, framebuffers and heap stayed flat
  (`wgl_drift.py`).

## Testing workflow

- **WebKit (Safari's engine) on the Mac.** Serve `dev/` with `python3 -m http.server 8765 --bind 127.0.0.1` and run a tool with
  `WK=1`. `wgl_env.py` blocks Google Fonts, whose stylesheet would hold the page. Without `WK=1` the tools use Chromium.
- **Pictures:**
  - `wgl_cmp.py base new out [quick]`: exact game states (frozen clock, seeded random), the WebGL canvas compared with another
    build.
  - `wgl_maskcmp.py`: the same for the mask atlas.
  - `wgl_parity.py`: single drawing calls through the facade against the real 2D context.
  - `wgl_classiccmp.py`: Classic against main.
  - `wgl_relcmp.py`: final frame, relief and light map at phone size, with diffs at 8x contrast. It found the blocky edge.
  - `wgl_shots.py`: live frames as PNGs.
- **Cost:**
  - `wgl_gputime.py [2d]`: GPU time per stage from timer queries (Chromium, this Mac's GPU; compare runs with runs).
  - `wgl_ops.py`: each scene draw's screen area (overdraw).
  - `wgl_gpustats.py`: targets, sizes and ops per frame.
  - `wgl_calls.py`: every WebGL call and upload per frame. Look for getError, readPixels, texImage2D, bufferData,
    renderbufferStorage.
  - `wgl_prof.py`: ?prof with the bot.
  - `wgl_bench.py` and `wgl_trace.py`: ?bench.
  - `wgl_alloc.py`: garbage per frame.
  - `wgl_floorprof.py` and `wgl_benchprof.py`: CPU profiles.
- **Long play:** `wgl_drift.py floor minutes` logs live GL objects, caches, heap and frame time every 30 s.
- **Debugging:**
  - `wgl_profwatch.py`: ?prof live, catching a stuck step.
  - `wgl_cliplog.py`: the clips of one frame.
  - `wgl_rampkeys.py`: gradient rows made new.
  - `wgl_striptest.py`: strip uploads against their canvases.
  - `wgl_layers.py`: the composited canvases.
- **`?prof`** cycles steps, each turning one thing off for a few seconds. The rows show work (script ms per frame) and frame (the
  interval), with their differences from "(none)". A negative difference is that feature's cost.
  - The steps are: metal, sky beams, flames, sand, relief, shadows, mist/sheen, heat, grade, sandstorm, upload (v60), scene .75,
    scene .5, no delay, 2D scene (v60), MSAA 2x, MSAA off.
  - "upload (v60)" and "no delay" only change the v60 path: on the new path their difference is noise. A single step's noise is
    about ±2 to 3 ms, so trust only large or repeated differences.
  - The stages row splits the work. Its GPU stages wait on the GPU (`gl.finish`) under ?prof only, so the frame there is longer
    than in play.
  - A step that throws shows "error: ..." and the steps go on.
- **`?bench`** (`=2d`, `=saver`, `=classic`, `=auto`, `=75`, `&floors=1,17`) has the bot play each floor live for 20 s. Its
  columns, per floor:

  | Column | Meaning |
  |---|---|
  | s | seconds played |
  | fps | frames per second |
  | mean, p95, max | frame interval in ms |
  | >20ms | share of frames over 20 ms |
  | w2s | worst 2-second window's mean frame |
  | work | script ms per frame |
  | rooms | rooms built |
  | relf | relief copies (v60 path) |
  | scale | GLP.rs |

  The Copy button takes the table.
- **A phone round:**
  1. Commit, then serve the worktree's `dev/` on the LAN.
  2. Make sure Low Power Mode is off and the phone is cool.
  3. Run `?bench` and `?bench=2d` and keep both tables.
  4. Run `?prof` on the floor in question: a photo of the table after a full cycle.
  5. Play the floor normally for the look, panning slowly past edges.
  6. Note heat after 5 minutes.
  7. Compare the new path and v60 on the same build, never across builds.

## Checklist for a new visual

1. Draw it with Canvas2D calls in the shared code, so it appears in Classic, on the WebGL path and on the `?wgl=0` fallback.
   Check all three.
2. Rectangle clips only, gradients faded by alpha, no per-frame canvas uploads, no new framebuffer pass (masks go in the atlas),
   fixed sizes, no per-pixel jitter in low-resolution passes, highp in shaders.
3. Compare with `wgl_cmp.py` (and `wgl_maskcmp.py` for a mask) against the last build, and with `wgl_parity.py` if it uses a new
   Canvas2D feature. Check the crops at contrast.
4. Count its calls with `wgl_calls.py`, and its GPU time with `wgl_gputime.py`.
5. On the phone, with Low Power Mode off: `?prof` (its step's difference) and `?bench` against `?bench=2d`.
6. Run `rendersmoke.py` on the floors it appears on, in both modes. Run `liftscan.py` if it is near lifts.
