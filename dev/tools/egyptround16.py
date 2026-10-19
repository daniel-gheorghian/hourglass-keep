# egyptround16.py: round 16a's section of egypt_themes.html (built in): the fallen roof block as a low obstacle stepped over, the cracked
# slab's two kinds (crumbling over a corridor, dragged down by a draining sand well), and the sand lift. Pictures from egyptr16.py.
import html
E = html.escape


def links(src):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(l)) for l, u in src) + '</ul>'


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def sections(D, REL, img):
    return ['<section class="card" id="r16"><h2>Round 16 (16a, built in): the fallen block, the slab\'s two kinds, the sand lift</h2>'
            '<p>Owner: "falling slab and the roof block: I\'d keep them separate; but, the roof block after settling on the ground needs to behave as a low obstacle: now the prince has to do a wide jump to clear them. '
            'The falling slab should have two variants: If there is a corridor underneath it should just crumple and fall with some sand effect as a billow of dust, otherwise do a realistic sand draining animation: like there is a well filled with sand that drains and breaks and drags the slab. '
            'The animation needs to be faster than today with a realistic sand draining. Sand lift: just the draining kind. Animation like the above. I see it as an alternate to the drape ripping."</p>'
            '<h3>The fallen roof block: a step, not a jump</h3><ul>'
            '<li><b>Research.</b> The block lies 10 px high, about 35 cm at the prince\'s scale (he is some 50 px tall): knee height. Prince of Persia has no such obstacle (its fallen floor tiles leave rubble that is walked over). The grid games that do have low steps treat them by height: Tomb Raider\'s levels are built in quarter-block "clicks": a one-click step is a stair taken in stride (Lara hops up it as she goes), while a block takes a climb. A knee-high stone is a one-click step.</li>'
            '<li><b>Now.</b> It no longer stops him: walking or running, he steps up onto it and down off it with no key. While his feet are over its top (its middle 22 px, at his depth) he is drawn standing on it, eased up and down over its edges in about 36 ms; his position, falls and hit boxes stay at floor level. Guards still keep to their side of it. '
            'The bot\'s way back over the two blocks in a side passage is a run instead of a running jump (the timers sized on that way are a little shorter, the bot runs it faster still). The "slide off the top" push is gone.</li></ul>' +
            fig(img, 'r16_block.gif', 'Running over a fallen block, Torchlight and Classic (1:1, real time)') +
            '<h3>The cracked slab: two kinds, chosen by what lies under it</h3><ul>'
            '<li><b>Which.</b> A slab over a shaft walled in on both sides down to its floor (a pit) sits on a well of sand. A slab with anything open beside the space under it (a corridor, a landing, a room) has only air under it. The play is the same for both: it holds 0.5 s, then drops under the heavy pull and hurts whoever is under it; nothing in the bot or the timers changed.</li>'
            '<li><b>The well.</b> The late tombs\' shafts were filled with sand and emptied to lower what stood on it: the Serapeum\'s sarcophagi were set down by filling their chambers with sand and taking it away, Hawara\'s burial chamber was closed with a roof slab lowered on sand, and the Abusir shaft tombs guard their burials with the "pseudo-hydraulic" behaviour of sand. '
            'Sand draining from a well runs like grain from a flat-bottomed silo: through an outlet in its floor at a rate set by the outlet and the grain, not by how much sand stands above it (Beverloo\'s law), so its level falls at one steady speed from the first moment (150 px/s: a storey in 0.43 s). '
            'With a flat floor it drains in funnel flow: the sand over the outlet moves, the surface opens into a cone-shaped crater, its slope a little steeper than the angle of repose. '
            'Drawn: the sand cut by the front plane, in courses, darker deeper in the shaft; its top a rim round the crater, the far slope lit, grains running down it to the throat; the outlet in the foot of the back wall. The slab rests on the well\'s rims; as the crater opens under it, its cracked middle loses support and sags (up to 8 degrees), then breaks along its crack and the two halves fold down into the emptied shaft. '
            'The sand is gone before they land (a 2-storey well in 0.85 s): nothing trickles after. The only sand that falls from the slab is what lay in its seams, running into the crater and gone as it breaks.</li>'
            '<li><b>The corridor.</b> Only grit sifts from its cracks while it holds (short, faint). Then it parts in four pieces that separate and turn a little as they fall, with a billow of dust tumbling out of the hole (0.45 s) and, where it lands, a cloud that hugs the floor and rolls out both ways, its head the biggest, slowing and thinning (0.7 s): the shape of a gravity current. '
            'The dust is soft volume: overlapping lobes of one radial gradient, no squares.</li>'
            '<li><b>Faster.</b> Before: a 0.5 s rise of the pour, the fall, a 0.55 s billow and 1.1 s of settling dust at the hole, about 1.6 s after the slab let go. Now the drain is at full rate at once, the dust lasts 0.45 s at the hole and 0.7 s where it lands, about 1.1 s in all.</li></ul>' +
            '<div class="g2">%s%s</div>' % (fig(img, 'r16_drain.gif', 'Over a sand well: the drain, the crater, the sag, the break (1:1, real time)'), fig(img, 'r16_crumble.gif', 'Over a corridor: grit, the crumble, the billow, the landing cloud (1:1, real time)')) +
            '<h3>The sand lift</h3><ul>'
            '<li><b>Where.</b> It is the banner slide\'s alternative: the same shaft (3 or 4 storeys, down only), the same width and landing. A turn drawn with a banner is built as a sand lift about a third of the time (from a hash of its place, using none of the generator\'s random streams), so every floor\'s layout, length and traps are exactly as before (<code>metrics40.py</code>: no floor changed). Not in a fork\'s short way (the long way may pass its foot) and not where the turn\'s gate must stand at the slide\'s foot.</li>'
            '<li><b>How.</b> A slab of the theme\'s stone sits flush with the landing on a shaft full of sand. He steps onto it; after a 0.25 s settle (a puff as it first gives) the sand drains from the shaft\'s foot and the slab sinks with him at one steady 140 px/s, the banner slide\'s own pace (1.6 s for 3 storeys, 2.1 s for 4), to the floor at the bottom, where it stays. No key is held; he cannot step off on the way. '
            'Grains left on the shaft\'s sides run down the gap after it and stop when it stops. Only the draining kind is built; there is no other.</li></ul>' +
            fig(img, 'r16_lift.gif', 'The sand lift, Torchlight and Classic (1:1, real time)') +
            '<h3>At 2x, and in three more themes</h3>' + fig(img, 'r16_2x.png', 'Key frames at 2x: on the block, stepping off; the well draining, the halves folding; the corridor\'s crumble and billow; the lift setting off, halfway') +
            fig(img, 'r16_themes.png', 'The Halls of the West, Meroë and Aksum, Torchlight 1:1: block, well, corridor, lift') +
            links([('Serapeum of Saqqara: the sarcophagi lowered by filling the chambers with sand and removing it', 'https://en.wikipedia.org/wiki/Serapeum_of_Saqqara'),
                   ('History Hit, Hawara: the burial chamber closed by a roof block lowered with sand', 'https://www.historyhit.com/locations/hawara-pyramid/'),
                   ('Hawara (Petrie\'s chamber and its roof slabs)', 'https://en.wikipedia.org/wiki/Hawara'),
                   ('Czech Institute of Egyptology: the Late Period shaft tombs of Abusir (protection by the pseudo-hydraulic properties of sand)', 'https://cegu.ff.cuni.cz/en/research/projects/field-projects/abusir/list-of-structures-in-abusir/abusir-west-late-period-shaft-tombs/'),
                   ('Granular discharge rate: Beverloo\'s law, the flow independent of the filling height (arXiv 1307.2812)', 'https://arxiv.org/pdf/1307.2812'),
                   ('Pressure independence of granular flow through an aperture (arXiv 1005.2884)', 'https://ar5iv.arxiv.org/html/1005.2884'),
                   ('Surface depression during the discharge of grains from a silo: funnel flow, the conical crater and its angles (arXiv 1703.10605)', 'https://ar5iv.arxiv.org/html/1703.10605'),
                   ('Inside the head and tail of a turbulent gravity current (J. Fluid Mech.)', 'https://www.cambridge.org/core/services/aop-cambridge-core/content/view/16F7947417B387D3DACE6EFF53C04766/S0022112015007041a_hi.pdf/inside-the-head-and-tail-of-a-turbulent-gravity-current.pdf'),
                   ('Dusty currents from building collapses (Doronzo et al.)', 'https://ricerca.uniba.it/handle/11586/167450'),
                   ('Tomb Raider\'s grid: four clicks to a block', 'https://tombraiderwiki.org/index.php/Block')]) + '</section>']
