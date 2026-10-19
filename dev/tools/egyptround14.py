# egyptround14.py: round 14's section of egypt_themes.html (built in): two perspective notes from the owner's phone, the portcullis's top and
# its modelling by the light, and the order across a lift's mouth. Pictures: r14_gate.png from egyptr14.py; r14_lift.png from liftshot.py
# (round 13 and round 14 builds, lift3u on floor 3, seed 70182, at 3x).
import html
E = html.escape


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def sections(D, REL, img):
    return ['<section class="card" id="r14"><h2>Round 14 (built in): the portcullis\'s top and light, the lift\'s mouth</h2>'
            '<p>Owner: "at the top it looks like the slab is behind the wall right at the top right corner. Also the slab has thickness, and the light coming from the left should really fall and produce light and shadow that clearly will show the edge of the slab, now that edge is barely visible. '
            'The second photo: the slab doesn\'t extend from edge to edge of the coridor. The tile should shift left by the thickness of the slab. The tile of the lift should move freely in the shaft, then the slab right next to the edge of the lift tile the next to the tickness of the slab is the outer tile".</p>'
            '<h3>The portcullis</h3><ul>'
            '<li><b>The top-right corner.</b> In the game\'s projection a block shows its right side face, drawn 16 px right and 8 px up for the corridor\'s depth. Where the block of ceiling over the gate ends at the tile\'s right edge, with no wall beside it above the corridor, that dithered side face stood over the slab\'s back corner. '
            'The slab was also cut off level with the ceiling\'s front edge, so its top-right corner seemed to pass behind the wall. The dark hatched patch in the photo was that side face. Now the slab runs up to its slot along its own slant there, in front of that face, with the slot\'s dark mouth over its top (a second draw clipped to a rectangle).</li>'
            '<li><b>Its thickness, modelled by the light.</b> The key light (the nearest lamp, or the scene\'s light, and its side) now shades it. The face toward the light is lit and the face turned from it is in shade. A crisp bright arris runs between them, the edge that shows the thickness. Its shadow falls on the floor along its foot and down the back wall on the far side. '
            'It works the same in both modes: no new pass, no texture written per frame, nothing jittered.</li></ul>' +
            fig(img, 'r14_gate.png', 'A Nun portcullis whose ceiling block ends beside it, part open and closed: round 13 and round 14, Torchlight and Classic (2x of the 1:1 canvas)') +
            '<h3>The lift\'s mouth</h3><p>Across the corridor, in order: the lift\'s platform moving freely in its shaft; the stone slab, its inner face on the shaft\'s edge, as thick as it is; then the landing tile beyond it. '
            'Before, the slab stood inside the shaft\'s column over the platform\'s edge, and the landing\'s call plate ran under it. Now the slab stands wholly outside the shaft. The call plate on that tile is drawn shorter by the slab\'s thickness on that side, and the slab\'s foot is drawn again over it, so the three sit side by side. '
            'Both mouths are fixed, whichever side of the shaft they open on. The walkable floor, the gate\'s plane for play (<code>liftGx</code>) and the bot\'s lift actions are unchanged; only the drawing moved. The paternoster has no mouth slabs.</p>' +
            '<p class="meta">(The round 14 picture of the mouths is retired: round 16c\'s <a href="#r16c">r16c_lift.png</a> shows them before and after that round\'s fix.)</p>' +
            '<h3>For v63: Tools, and lighting by hand only</h3><p>Owner: "put some buttons under a menu that runs the benchmark and the profiler"; "disable the automatic disabling of the torchlight. Leave only manual control". '
            'The pause menu has a <b>Tools…</b> screen with Benchmark, Benchmark (classic), Benchmark (auto scale) and Profiler. Each reloads the game with its setting, as typing <code>?bench</code> or <code>?prof</code> would, and the save is kept as it is. The bench\'s table and the profiler each have a button back to the game. '
            'Torchlight is no longer switched off by the game when frames are slow: it only draws its scene smaller (to half size at most). Only the Graphics menu switches it off; a phone without WebGL2, or whose context is lost, still gets Classic so the screen is not black.</p></section>']
