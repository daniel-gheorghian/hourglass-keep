# egyptround26a.py: round 26a's section of egypt_themes.html: the lifts drawn clean (owner, five phone screenshots of v72: "windows or walls
# or wall trims are drawn over the lift mechanisms", "at the top the lift slab is drawn in front of the wall", "when at the bottom the slab
# digs into the tile floor", "part of the door slab doesn't respect the shadow"). Pictures from egyptr26a.py, numbers from liftscan.py.
import html
E = html.escape


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def links(L):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(t)) for t, u in L) + '</ul>'


SOURCES = [
    ('Paternoster lifts: open cars on a continuous chain that pass over the top and under the bottom floor out of sight, through the head room '
     'and the pit; at each floor the car\'s floor passes the landing\'s', 'https://en.wikipedia.org/wiki/Paternoster_lift'),
    ('Elevators: the hoistway is an enclosed shaft (openings only for the landing doors); the car rests level with the landing, over a pit',
     'https://en.wikipedia.org/wiki/Elevator'),
    ('SDLPoP (Prince of Persia 1989 reimplemented): draw_tile_fore draws the near parts of tiles (a wall\'s front, a floor\'s lip) after what '
     'moves behind them; nothing in a tile\'s depth shows over the tile in front of it', 'https://github.com/NagyD/SDLPoP'),
    ('Bump and emboss: a relief taken from a picture\'s brightness raises whatever that picture holds, so anything drawn over it must be kept out '
     'of the height map', 'https://en.wikipedia.org/wiki/Bump_mapping'),
]

NUMBERS = ('Measured with the extended liftscan.py (floors 3 to 30, two seeds, both modes: 976 cases, each lift kind at the top, halfway and the '
           'bottom, the paternoster at five clock times). Before: 251 arch cells and 28 breaches in lift shafts\' back walls; the lift drawn over the '
           'landing beside its shaft in 227 cases, a slab over the foot floor\'s lip in 29, a bright mouth-slab wedge in 63 (in Torchlight 40 against '
           '25 for the shade just under the ceiling\'s edge on floor 8), the relief on the lift\'s stone in 161: 368 failing cases. After: 0 of each.')
TESTS = ('liftscan floors 3 to 30, two seeds, both modes: ALL OK, 976 cases (near 0, foot 0, wedge 0, relief 0; 0 arches and 0 breaches in 3,169 '
         'shaft cells; walls, low ceilings and gratings 0 as before). lifttest: FAILURES 0. slabscan: ok (2,452 slabs). openscan floors 1 to 48, both '
         'modes: 0 of 96 windows, 89 gates and 422 lift mouths. beamwall: no errors. rendersmoke floors 7 to 9, both modes: no errors (0.77 ms/frame, '
         'with another scan running). run2 floors 3 to 6, one seed: 4 of 4 passed, 0 runs with damage (0.04 ms/frame). lampscan: ok. Floors 1 to 48 '
         '(seed 701) against v72: the tiles, route, bot actions, windows, items and lamps identical. Looked at in both modes with GLP.rs 1 and 0.5.')


def sections(D, REL, img):
    return ['<section class="card" id="r26a"><h2>Round 26a: the lifts drawn clean</h2>'
            '<p>Owner, on v72, with five screenshots: "windows or walls or wall trims are drawn over the lift mechanisms" (twice, a paternoster); '
            '"at the top the lift slab is drawn in front of the wall"; "when at the bottom the slab digs into the tile floor"; "part of the door '
            'slab doesn\'t respect the shadow".</p>'
            '<h3>The causes</h3><ul>'
            '<li><b>Windows and trims over the lift.</b> The back wall\'s arches (a recess framed by two posts and a lintel, or one time in four an '
            'opening to the sky) are a hash of the cell: any open cell over a floor that is not walled on both sides. A paternoster\'s shaft is two '
            'columns of such cells over its foot, so most paternosters (158 of 182 on floors 3 to 48, three seeds; and 293 of 380 sand lifts) had an '
            'arch two storeys high right behind the slabs\' bottom run, 57 of them open to the sky. In Torchlight the relief, which is read from '
            'the room\'s picture, embossed the arch\'s posts, the opening\'s edges and the courses of the shaft\'s back on every slab, the platform, '
            'the counterweight and the wheels that passed (only the mouth slabs and the sand were rubbed out of it), so the slabs seemed to pass '
            'behind the posts; and the opening\'s sky light and beam lay over them. A breach (a hole knocked through the back wall) could open there '
            'too (8 shafts).</li>'
            '<li><b>The slab in front of the wall at the top.</b> Lift parts are cut by the walls\' front faces round the shaft (liftOccl), but that '
            'cut leaves a wall\'s top 9 px open (a floor\'s lip lies there) and never cut floor tiles. A slab level with a landing on the shaft\'s '
            'right drew its right side face, 16 px of it, over that landing\'s floor top and lip and the wall\'s top under it, where it abuts the '
            'landing and can never be seen. The shaft\'s back wall shade did the same, 8 px into the landing\'s lip, and so did a counterweight lift\'s '
            'platform docked beside a right landing.</li>'
            '<li><b>The slab sunk into the floor.</b> A paternoster\'s bottom run lies level with the shaft\'s foot floor (it must: he steps on and '
            'off there), so the slab sat in the floor tile itself and its lip and dark underside were drawn over the floor\'s lip and its border: it '
            'looked sunk into the tile.</li>'
            '<li><b>The mouth slab out of the shadow.</b> A shut slab on the shaft\'s left edge rises past the ceiling\'s front edge along its own '
            'slant beside the shaft (round 14\'s top piece, drawn so its corner does not seem to pass behind the wall). The ceiling\'s shade '
            '(ceilShade, 0.92 at the edge) is laid only under the edge, so that piece, deeper in the ceiling\'s shadow, stood in full light: a '
            'bright wedge over a dark band (both modes).</li></ul>'
            '<p>' + E(NUMBERS) + '</p>'
            '<h3>The fix (look only)</h3><ul>'
            '<li>No arch, recess, opening or breach in a lift shaft\'s back wall (liftCell: every cell of a shaft from its top row to its foot; a breach '
            'not in the cells beside one either, as its ragged hole runs into them). The arches are a hash and the breaches their own hash: no generator '
            'stream is touched; tiles, route, windows, items, lamps and the bot\'s actions are identical on every floor (only one hanging moved into a '
            'place an arch had kept it from, and 35 of 2,178 breaches on floors 3 to 30 went).</li>'
            '<li>Torchlight\'s relief is rubbed back over the lift\'s stone and wood in view: each paternoster slab, the platform, the counterweight, '
            'the wheels (glRelLifts, as a mouth slab\'s box).</li>'
            '<li>What stands nearer than the shaft beside it is cut out of the whole lift drawing (liftNearCut): in the column right of the shaft, '
            'the walls\' whole front faces and each floor tile\'s top and lip, whose left edge is the shaft\'s edge along the depth. The sand lift\'s '
            'slab has had this since round 19.</li>'
            '<li>A paternoster\'s bottom run is a pit across the foot: the foot floor\'s lip stands in front of a slab there, which shows only its top, '
            'flush with the floor; it rises out of the pit behind the lip. The rest heights, timing, boarding and hit boxes are unchanged.</li>'
            '<li>The mouth slab\'s piece above the ceiling\'s edge is shaded as deep as the ceiling\'s shade begins (0.9), in both modes.</li></ul>'
            '<h3>Research</h3><p>A real paternoster\'s cars pass over the top and under the bottom floor out of sight, and every lift\'s car rests over a '
            'pit with its floor level with the landing\'s: the slab at the foot is now seen that way, its top flush in the floor and its edge behind '
            'the floor\'s. A hoistway is an enclosed shaft, opening only to its landings, so no window or arch belongs in its back wall. Prince of '
            'Persia draws the near parts of tiles (a wall\'s front, a floor\'s lip) after anything in the depth behind them (SDLPoP\'s draw_tile_fore): '
            'the right landing\'s floor now does that to the slabs. An emboss taken from the background\'s picture raises everything that picture '
            'holds, so the moving stone has to be kept out of it, as the mouth slabs (round 16c) and the sand (round 21b) already were.</p>' + links(SOURCES) +
            fig(img, 'r26a_lifts.png', 'The five faults, the owner\'s kind of case each: Torchlight before | after, Classic before | after, at the phone\'s '
                'resolution, and under each a 2x crop of the red box. (1) slabs before an open arch at a paternoster\'s foot; (2) an arch recess\'s posts '
                'and the courses embossed on a slab; (3) a slab at the top of the column beside the right landing; (4) a slab on the bottom run; (5) a '
                'shut left mouth slab where it rises past the ceiling\'s edge') +
            '<h3>Tests</h3><p>' + E(TESTS) + '</p>'
            '<p class="meta">Retired to keep the page at 505 pictures: round 7\'s fight against the captain, r7_fight_3.gif (the prince and the robbers '
            'were rebuilt from motion capture in round 23).</p></section>']
