# egyptround27b.py: round 27b's section of egypt_themes.html: the view through the openings, each layer at the depth it shows (owner: "The
# background moves too fast: do some research into the equations that govern how much a backgrounds like ours should move ... We should keep
# the illusion of distance between that background and our walls and windows. If it is cheap we can add multiple backgrounds that scroll at
# different speeds and so simulate closeness and farness"). Pictures and numbers from egyptr27b.py (r27b_parallax.png, r27b_parallax.gif, r27b.json).
import html
E = html.escape


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def links(L):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(t)) for t, u in L) + '</ul>'


SOURCES = [
    ('Rogers and Graham, Motion parallax as an independent cue for depth perception, Perception 8 (1979): relative motion alone gives a reliable, '
     'unambiguous impression of relative depth', 'https://journals.sagepub.com/doi/10.1068/p080125'),
    ('Keren, Scroll Back: The Theory and Practice of Cameras in Side-Scrollers (GDC 2015, Independent Games Summit; the written version): camera '
     'windows, smoothing and parallax layers', 'https://www.gamedeveloper.com/design/scroll-back-the-theory-and-practice-of-cameras-in-side-scrollers'),
    ('Godot, ParallaxLayer.motion_scale (per-axis factor; 0 stops an axis) and Parallax2D.scroll_scale', 'https://docs.godotengine.org/en/4.2/classes/class_parallaxlayer.html'),
    ('Unity forum: a perspective camera with layers at their Z, against hand-set factors on an orthographic one', 'https://discussions.unity.com/t/new-to-unity-help-creating-a-parallax-background/804098'),
    ('Pyramid of Djoser: 62.5 m; its enclosure wall 10.5 m', 'https://en.wikipedia.org/wiki/Pyramid_of_Djoser'),
    ('Al-Qurn: the peak over the Theban necropolis, about 420 m above sea level (the plain about 75 m)', 'https://en.wikipedia.org/wiki/Al-Qurn'),
    ('Luxor Temple: the first pylon 24 m high', 'https://en.wikipedia.org/wiki/Luxor_Temple'),
    ('Western Deffufa: about 18-20 m', 'https://en.wikipedia.org/wiki/Western_Deffufa'),
    ('Jebel Barkal: 98 m', 'https://en.wikipedia.org/wiki/Jebel_Barkal'),
    ('Nubian pyramids (Meroe: 6-30 m)', 'https://en.wikipedia.org/wiki/Nubian_pyramids'),
    ('List of Egyptian pyramids (Hawara: 58 m when built)', 'https://en.wikipedia.org/wiki/List_of_Egyptian_pyramids'),
    ('Obelisk of Aksum (24.6 m) and King Ezana\'s Stele (about 21 m)', 'https://en.wikipedia.org/wiki/Obelisk_of_Axum'),
    ('Date palm, Phoenix dactylifera: 15-25 m', 'https://en.wikipedia.org/wiki/Date_palm'),
    ('Aerial perspective (the far layers take the sky\'s colour)', 'https://en.wikipedia.org/wiki/Aerial_perspective'),
]

FOUND = ('Measured first (egyptr27b.py). The view is drawn in layers (BGART), each scrolled at a factor f of the camera\'s pan. Each layer\'s factor '
         'can be checked against the drawing\'s own scale: the prince\'s 1.75 m is 51.5 px, so s = 29.4 px a metre on the play plane, and a thing '
         'H m high seen at depth Z is drawn h = s f H px when f = Z0/Z. Measured on the layers\' canvases, the factors were 3 to 10 times too large '
         'for what they show. El-Qurn (345 m over the plain, drawn 54 px) moved at 0.05, which makes it a 37 m hill 107 m behind the window. The '
         'step pyramid at 0.1 made a 21 m pyramid, Barkal at 0.05 a 60 m hill, Shali\'s town at 0.16 a 9 m block. The palms, acacias and trees '
         'at 0.3-0.32 read as 5-9 m shrubs 13 m off, and the mounds of a foggara as 3 m heaps 26 m off. So every window showed a small painted '
         'diorama a few metres behind the glass, sliding by fast: at the run\'s 100 px/s the far land moved 4-5 px/s and the palms 30-32 px/s on the '
         'screen. The sky and stars moved too (f 0.015). Up and down (round 25e) the view moves with the keep at 0.8 of its speed (0.2 (1 - f) of slide), '
         'which round 25e set so that a descent never swims the view through a window (it was 3.3 px a frame, now under 1). It stays: the camera moves '
         'up or down only 17% of the time (55 px/s median), across nearly all of it (61 px/s median, 98 p90, 437 at a turn).')
EQ = ('The equation (a pinhole seen from above): a camera Z0 from the play plane pans by x. A point of the play plane moves x on the screen; a point Z '
      'away moves x Z0/Z (screen x\' = Z0 X / Z). So a layer\'s factor is f = Z0/Z, and it slides past the windows by 1 - f. A thing H m high at Z is '
      'drawn h = s f H, so f = h/(s H): the factor follows from how big a thing is drawn and how big it is, with no lens to choose. Z0 matters only to '
      'name the depths: a 60 degree vertical view of the 6.5 m frame puts the camera 5.65 m off, so f 0.25 is 17 m behind the walls, 0.13 is 38 m, '
      '0.035 is 156 m, 0.005 is 1.1 km. Vertically the same equation holds for an eye that travels round 25e\'s BG_VK (0.2) of the camera\'s height.')
FIX = [
    'Each layer gets the factor its size and subject give (the table in the picture): far land 0.004-0.012 (el-Qurn 0.005, 1.1 km; the ambas 0.004; '
    'the escarpment 0.006; the hills 0.012), monuments 0.021-0.11 (the cliffs 0.021, Barkal 0.031, the step pyramid 0.034, Meroe\'s pyramids 0.036, '
    'Shali 0.035, the pylons 0.07, the obelisks 0.075, the Deffufa and the stelae 0.11), walls, huts and mounds 0.02-0.13, palms and trees 0.12-0.155 '
    '(31-41 m off). Clouds 0.002 (they keep their drift); the sky, stars, moon and sun at infinity (0). Within each look the order far to near is kept.',
    'More depth, from the same kinds of art: a near band in ten of the twelve looks, the nearest anything in the view stands (f 0.25, 17 m): fallen '
    'blocks, boulders, column drums and broken piers (Saqqara, Aksum, Hawara), halfa scrub and stones (the Fezzan, Kerma, Siwa), or papyrus and reeds '
    'on a bank (Thebes, the Osiris look, Napata); things 1-4 m high, 7-30 px. And a far ridge in the air\'s colour (aerial perspective: mixed half into '
    'the sky\'s horizon stop at every time of day) at 0.002 where the farthest land was near: Meroe, the Osiris look, Kerma, Napata, Hawara. The '
    'interiors (the Cistern\'s hall, the Forge\'s ropes) keep their hall\'s depths; their ropes come in to the near limit, 0.25.',
    'Seams: every outline now repeats in whole periods over the strip (hills, dunes, el-Qurn, cliffs, the ridge), the escarpment\'s and the ambas\' '
    'walks close on their first height, a foggara\'s rows of mounds swell instead of slanting (a 32 px step at the repeat), the columns and niches step '
    'in whole steps, and the strip\'s copies join on whole pixels of the target (a faint line ran down the view at every join).',
    'Distance blur on the log of the depth, so each layer keeps the sharpness it had for its place in the set. Look only, both modes, every GLP.rs, the '
    '?wgl=0 path: the composition, the openings, round 25e\'s anchors and its vertical rule unchanged; nothing a frame is allocated.',
]
RESULT = ('Before > after on the screen at the run\'s 100 px/s: the far land 4-5 > 0.4-1.2 px/s, monuments 4-16 > 2-11, palms and trees 30-32 > 12-15.5, '
          'the new near band 25; the sky 1.5 > 0. Cost: one more copy of a cached canvas (two in five looks) into the low-resolution backdrop target, no '
          'new pass; a frame with the largest opening of floors 5, 9, 25 and 45 on the screen (median, this Mac, headless, the two builds in turn): Classic '
          '3.95 > 4.20 ms, Torchlight 2.0 > 2.0 ms.')
RESEARCH = ('Games do the same two ways. With a perspective camera the layers are placed at their depth and the factor comes out of the projection '
            '(Rayman Origins and Legends\' UbiArt planes, Ori, Hollow Knight\'s layers at their Z with atmospheric colour); with an orthographic '
            'camera each layer is given a factor by hand (Godot\'s motion_scale, Unity\'s scripts, the Mega Drive and SNES scrolling per layer and, '
            'in Sonic, per line, which bends the ground plane toward the horizon). Hand-set factors drift from what the art shows unless they are '
            'checked against it, which is what happened here. Separate factors across and up are common (Godot\'s per-axis motion_scale; Keren on '
            'camera windows that hold the vertical still). Perception: motion parallax alone gives a clear sense of which surface is nearer and by '
            'how much (Rogers and Graham 1979), and far things read as far when they barely move, take the sky\'s colour and lose contrast.')
TESTS = ('From a copy of dev/: egyptr25e: the computed view through each opening moves at most 0.65 px a frame in descents (p95 0.47) and 0.48 in '
         'ascents, as in round 25e. rendersmoke floors 7 to 9, both modes: no errors (0.65 ms/frame). beamwall: no errors, before and after alike. openscan: '
         'windows 0 of 96, gates 0 of 89, lift mouths 0 of 422 in both modes. run2 floors 3 to 6, one seed: 4 of 4 passed, 0 runs with damage (0.04 ms/frame).')


def sections(D, REL, img):
    return ['<section class="card" id="r27b"><h2>Round 27b: the view at the depth it shows</h2>'
            '<p>Owner: "The background moves too fast: do some research into the equations that govern how much a backgrounds like ours should move. '
            'The background is tied to the camera, but the rate at which the camera moves isn\'t equal to that of the background. We should keep the '
            'illusion of distance between that background and our walls and windows. If it is cheap we can add multiple backgrounds that scroll at '
            'different speeds and so simulate closeness and farness."</p>'
            '<h3>What was found</h3><p>' + E(FOUND) + '</p>'
            '<h3>The equation</h3><p>' + E(EQ) + '</p>'
            '<h3>The fix</h3><ul>' + ''.join('<li>%s</li>' % E(t) for t in FIX) + '</ul><p>' + E(RESULT) + '</p>'
            '<h3>Research</h3><p>' + E(RESEARCH) + '</p>' + links(SOURCES) +
            fig(img, 'r27b_parallax.png', 'The depth equation and every layer\'s factor against its depth; the table of the twelve looks (what each layer shows, '
                'its drawn and real height, the factor before and what it implied, the factor after and its depth); screen speeds; a pan past the largest '
                'opening, before | after, Torchlight and Classic') +
            fig(img, 'r27b_parallax.gif', 'In game, Torchlight, the bot running past the openings of floor 5: before | after') +
            '<h3>Tests</h3><p>' + E(TESTS) + '</p>'
            '<p class="meta">Retired to keep the page at 505 pictures: round 8\'s concept clock B (the twelve gates, not built), its last two pictures, '
            'r8_clock_B_10.png and r8_clock_B_1.png.</p></section>']
