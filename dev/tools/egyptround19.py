# egyptround19.py: round 19's section of egypt_themes.html (built in): four owner bugs. Lamps jammed against steps, the prince seen
# through the wall he hangs behind, the sand lift's slab out of perspective, the hump on his back with his arms up. Pictures from egyptr19.py.
import html, json, os
E = html.escape


def links(src):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(l)) for l, u in src) + '</ul>'


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def vid(REL, f, cap):
    return ('<figure><video src="%s/%s" controls loop muted playsinline autoplay preload="metadata" style="width:100%%;border-radius:6px"></video>'
            '<figcaption>%s (<a href="%s/%s">%s</a>)</figcaption></figure>' % (REL, f, E(cap), REL, f, f))


SCAN_BEFORE = {'lamps': 9584, 'bad': 2165, 'ledge': 1332, 'clock': 428, 'wall': 316, 'door': 75, 'gate': 69, 'lift shaft': 21, 'banner': 6, 'pendulum': 6, 'lift plate': 5, 'lift': 1}
SCAN_AFTER = {'lamps': 9621, 'bad': 0}


def sections(D, REL, img):
    J = json.load(open(os.path.join(D, 'r19.json'))) if os.path.exists(os.path.join(D, 'r19.json')) else {}
    hang = ', '.join('%s (floor %d)' % (h[2], h[0]) for h in J.get('hangs', []))
    kinds = ', '.join('%s %d' % (k, v) for k, v in SCAN_BEFORE.items() if k not in ('lamps', 'bad'))
    return ['<section class="card" id="r19"><h2>Round 19 (built in): lamps, the hidden prince, the sand lift\'s slab, his back</h2>'
            '<p>Four bugs from the owner\'s phone. Look and decoration only: the generator\'s floors, the moves, timings, hit boxes and the bot are unchanged.</p>'
            # ---- 1
            '<h3>1. Lamps against a step</h3>'
            '<p>Owner: "sometimes lamps or torches are placed just like that, I would avoid them" (a lamp at the foot of a step, half over the step\'s face). '
            '<b>Cause</b>: the generator puts a lamp on the floor tile where a stretch ends, which is often the tile in front of a step up. A wall\'s front face stands HX (8 px) left of its cell, '
            'so a lamp centred in the tile beside it (its bracket 6 px right of centre in the palace style) overlapped the face by several pixels and was drawn over it. Nothing checked the cells beside a lamp. '
            '<b>Fix</b> (<code>lampClear</code>, <code>lampsClear</code> in <code>settleLights</code>): a lamp burns only where both cells beside it are plain floor (no wall face or step, no ledge, '
            'no gate, banner, swing bar, pendulum, lift or lift plate), no lift shaft is beside it and no water clock or door is near. One that is not is moved along its row to the nearest such tile within six '
            '(never nearer than three to another lamp); the lamps that replace the ones fallen with the wall follow the same rule (and look six tiles each way, not four). It reads no generator stream, so the floors are as they were. '
            'In Prince of Persia a torch is a tile of its own (SDLPoP <code>tiles_19_torch</code>: a floor tile with the torch on its back wall), so it never shares a tile with a wall\'s face.</p>'
            '<p><b>lampscan.py</b>, floors 1 to 48, seeds 1 to 3 (144 floors): before, <b>%d of %d</b> burning lamps were jammed (%s; a lamp can count under more than one); after, <b>%d of %d</b>. '
            'The lamps a floor: %.1f before, %.1f after (97 of them, 0.7 a floor, found no tile within six and went out; the wider search for replacements made up for them).</p>' % (
                SCAN_BEFORE['bad'], SCAN_BEFORE['lamps'], E(kinds), SCAN_AFTER['bad'], SCAN_AFTER['lamps'], SCAN_BEFORE['lamps'] / 144, SCAN_AFTER['lamps'] / 144) +
            fig(img, 'r19_lamps.png', 'Lamps the old placement set against a step (two themes), Torchlight and Classic, before and after: 1:1 (above), 2x (below)') +
            # ---- 2
            '<h3>2. The prince seen through the wall</h3>'
            '<p>Owner: "the prince is visible when hanging by a ledge. I really don\'t know how to solve this. Research how the original pop did this exact movement: was the prince visible when hanging like that?"</p>'
            '<p><b>What Prince of Persia did</b>: the Kid is <b>hidden</b> behind the wall, all but his hands. In SDLPoP (the reverse-engineered DOS source) every wall tile\'s front piece goes into the '
            '<i>foretable</i>, drawn after the characters (<code>draw_tile_fore</code>, <code>case tiles_20_wall: add_foretable(...)</code>), and <code>clip_char()</code> cuts the Kid\'s sprite: its top at the floor '
            'above when the tile at his top-left is a wall or floor, and its right edge at a wall tile\'s left edge when he hangs or climbs facing left (<code>actions_2_hang_climb</code>, <code>actions_6_hang_straight</code>). '
            'The Apple II source draws block fronts on the foreground layer after the characters (<code>FRAMEADV.S</code>: <code>drawfrnt</code> through <code>addfore</code>, with a mask so only the wall\'s pixels cover him), '
            'and <code>CTRL.S</code> switches a Kid hanging against a block to <i>hangstraight</i>. Nothing is drawn through the wall: no ghost, no outline. Played, he climbs into view head first as he rises over the ledge.</p>'
            '<p><b>The real cause</b> here was not the figure: Dawnward already hid him behind the face (<code>figClip</code>, <code>hideMode</code>). Two things showed through. (1) In Torchlight a lamp casts a figure\'s shadow on the back wall '
            '(<code>glShadow</code>, his silhouette at an offset away from the lamp); the shadow mask then carves out the nearer stone, but it carved each wall at its cell, not at its front face, which is HX to the left. '
            'The face\'s left 8 px kept the shadow: with a lamp at the foot of the step it was a dark prince-shaped stripe down the lit face (the owner\'s picture). '
            '(2) While he jumped up, climbed or had just caught the ledge, a 0.4 ghost of him was drawn through the wall (in both modes). '
            '<b>Fix</b>: the shadow carve follows the stone as drawn (a wall\'s front face, top and right side; a floor\'s lip and top), what the wall hides of him casts no shadow either, and the ghost is gone: '
            'as in PoP1 only his hands show above the ledge until he comes up over it.</p>' +
            vid(REL, 'r19_hang.mp4', 'Jumping up, hanging, climbing up (4 s), then hanging and dropping off (4 s), %s; Torchlight, before (left) and after (right); a lamp set at the foot of the step as in the owner\'s picture' % hang) +
            fig(img, 'r19_hang.png', 'Jumping up, hanging, hanging still, climbing, dropping; %s; Torchlight and Classic, before and after, 1:1; the hang at 2x' % hang) +
            # ---- 3
            '<h3>3. The sand lift\'s slab</h3>'
            '<p>Owner: the slab "doesn\'t respect perspective". <b>Perspective</b>: the view is a cabinet-style oblique projection: front faces true, depth drawn up and to the right (DX 16, DY 8), '
            'a wall\'s or floor\'s front face HX left of its cell; a floor tile is a lip on the front plane and a top running back along the depth diagonal, and the next tile\'s top starts on that same diagonal. '
            '<b>Cause</b>: the slab was drawn as a free box (<code>stoneBox</code> with a right side face and a black outline all round, half a pixel short of each edge): at the top and the bottom of the shaft its side face '
            'and outline lay over the next floor tile\'s top and lip, so it read as a box set on the floor, not a tile of it; the shaft\'s back wall (its right groove) was drawn over that tile too. '
            '<b>Fix</b> (<code>sandSlab</code>): a floor tile of the theme\'s stone, its lip over the whole cell from X-HX like the floor\'s, its top running back like theirs, the floor\'s lip shadow and arris, '
            'no side face, ink only on its left edge and the lip\'s foot (where it meets the open shaft); once it leaves a landing, the next column\'s nearer stone (a wall\'s face, a floor\'s lip and top) cuts it; '
            'the shaft\'s back wall is seen through the hole only. The order across the corridor stays round 16c\'s: the platform in its shaft, the slab, then the floor tile. '
            '<b>Texture</b>: the theme\'s own stone (<code>THEME_STONE</code>, the same sheet the portcullis and roof block use), worn by the wall\'s wear level. <b>Not pixelated</b>: drawn with paths and the stone sheet at 4 px per pixel, checked at 2x below. '
            '<code>liftscan.py</code> and <code>lifttest.py</code> pass.</p>' +
            fig(img, 'r19_sand.png', 'The sand lift in three drawing styles: at the top, just leaving it, riding, at the bottom; Torchlight and Classic, before and after, 1:1; the top and bottom at 2x (below)') +
            # ---- 4
            '<h3>4. The hump</h3>'
            '<p>Owner: "the prince has a hump in that pose" (hanging from the swing). <b>Anatomy</b>: raising the arm overhead turns the shoulder blade up about 60 degrees and slides it out round the ribs '
            '(the scapulohumeral rhythm); the latissimus and teres major stretch from the waist into the back of the upper arm, so the back\'s contour runs in one long line from the waist up into the arm, '
            'and the top of the shoulder sinks between the raised arm and the neck. <b>Cause</b>: <code>torsoG</code> widened the back near the shoulders by 0.9 px with the arms up (meant as the lats stretching), '
            'and the raised arm rose from the middle of the shoulder, so the torso\'s back corner stood out behind the arm as a round bump. '
            '<b>Fix</b>: with the arms up the back near the shoulders is drawn up to 1.3 px narrower, easing in from three quarters of the way up, and the raised arm rises from the back of the shoulder (0.8 px), '
            'so the back line flows into the arm. Checked on every pose with the arms raised: hang, reach (the jump up), pull, fall, slide and the swing both ways; the climb blends these.</p>' +
            '<p class="meta">(Round 22b: the arms-up poses sheet retired to keep the page\'s size; round 22b\'s every-pose sheet and the swing in the game show them now.)</p>' +
            links([('SDLPoP seg008.c: draw_tile_fore (wall fronts into the foretable)', 'https://github.com/NagyD/SDLPoP/blob/master/src/seg008.c'),
                   ('SDLPoP seg006.c: clip_char (the Kid cut at walls while hanging and climbing)', 'https://github.com/NagyD/SDLPoP/blob/master/src/seg006.c'),
                   ('Prince of Persia Apple II source: FRAMEADV.S (drawfrnt, addfore)', 'https://github.com/jmechner/Prince-of-Persia-Apple-II/blob/master/01%20POP%20Source/Source/FRAMEADV.S'),
                   ('Prince of Persia Apple II source: CTRL.S (hanging, hangstraight)', 'https://github.com/jmechner/Prince-of-Persia-Apple-II/blob/master/01%20POP%20Source/Source/CTRL.S'),
                   ('Oblique projection (cabinet and cavalier)', 'https://en.wikipedia.org/wiki/Oblique_projection'),
                   ('Scapulohumeral rhythm: about 60 degrees of upward rotation at full elevation', 'https://yinyoga.com/the-scapulohumeral-rhythm/'),
                   ('Proko: the shoulder muscles (teres major stretched with the arm raised)', 'https://www.proko.com/course-lesson/inventing-the-shoulder-muscles'),
                   ('Cubebrush forum: the scapula slides round the ribs as the arm rises', 'https://forums.cubebrush.co/t/t3-anatomy-question/10760')]) + '</section>']
