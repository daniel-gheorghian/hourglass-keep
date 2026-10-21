# egyptround25d.py: round 25d's section of egypt_themes.html: a lintel over the lift's slab (owner, with a photo of floor 7 on the phone:
# "lift slab with no ceiling above it"). Pictures from egyptr25d.py; the check is slabscan.py.
import html
E = html.escape


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def links(L):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(t)) for t, u in L) + '</ul>'


SOURCES = [
    ('Portcullis: a grille or slab lowered in grooves from a chamber in the gatehouse above the passage', 'https://en.wikipedia.org/wiki/Portcullis'),
    ('Great Pyramid of Giza, the antechamber: three granite portcullis slabs let down in grooves cut in its granite walls, housed above the passage', 'https://en.wikipedia.org/wiki/Great_Pyramid_of_Giza'),
    ('Lintel: the beam over an opening that carries the wall above it (post and lintel, the game\'s rule for doors and windows)', 'https://en.wikipedia.org/wiki/Lintel'),
    ('SDLPoP (Prince of Persia 1989 reimplemented): the gate is a tile of its own whose bars are drawn down from the top of its cell; in the original levels the cell above a gate is a floor or a wall block', 'https://github.com/NagyD/SDLPoP'),
]

TESTS = ('slabscan.py (new; floors 1 to 48, 3 seeds: 2,452 slabs: 1,496 portcullises, 478 top and 478 bottom lift mouths): 0 without stone '
         'above (477 before, every one a top mouth). The floors otherwise unchanged: over the same 144 floors 955 cells differ (the lintels), 156 '
         'windows that were cut in them are gone, no other window, lamp, guard, item or bot action differs. metrics40.py against round 25c: every floor\'s route, traps and spacing identical. lifttest FAILURES 0; liftscan floors 3 to 30, 2 seeds, both modes: ALL OK (900 cases); openscan: 0 lift mouths, gates or windows with wall art over the opening (422 lift mouths, both modes); beamwall: no errors; primtest FAILURES 0; lowceil ALL OK; rendersmoke floors 7 to 9, both modes: no errors (0.73 ms/frame); run2 floors 3 to 6: 4 of 4 passed, 0 runs with damage (0.04 ms/frame).')


def sections(D, REL, img):
    return ['<section class="card" id="r25d"><h2>Round 25d: a lintel over the lift\'s slab</h2>'
            '<p>Owner, with a photo of floor 7 on the phone (the prince at the top of a lift, a tall stone slab beside him ending in front of the '
            'dusk sky): "lift slab with no ceiling above it".</p>'
            '<h3>The cause</h3>'
            '<p>A counterweight lift shuts each mouth with a stone slab (a grating with the Egyptian traps off) that slides up into the stone over '
            'it while the platform is at that landing. The lift is built with a wall over both mouths, but near the end of the layout the '
            'open-hall pass gives everything the prince moves through a row of headroom: it cut the cell over the top mouth and the one over '
            'the shaft out of the wall. Gates and blades were spared (they keep their lintel); the lift\'s slab was not, so on every lift the top '
            'slab, shut while the platform was below, stood in the hall with nothing above it, against the back wall, a window or the sky. '
            'The tiles show it: of 2,452 slabs on floors 1 to 48 (3 seeds), 477 had open air above, all of them top mouths; every portcullis and '
            'every bottom mouth had stone.</p>'
            '<h3>The fix</h3><ul>'
            '<li>The open-hall pass keeps the lintel over a counterweight lift\'s top mouth and its shaft\'s top, as it does over a gate: the mouth '
            'is now a doorway in the wall, as the bottom one always was, and the slab slides up into stone. The pass still draws its random number '
            'for those cells, so every other window and the rest of the floor are as they were; only the windows that had been cut in those two '
            'cells are gone. Route, traps, guards, items, timers and the bot\'s actions are unchanged.</li>'
            '<li>The sheave\'s hoist beam lies in the lintel and the wheel turns in a slot in its underside (its upper half behind the lintel\'s '
            'face), so the prince standing on the platform at the top does not have it at his head.</li>'
            '<li>As at every bottom mouth, the stone over the top mouth is a ceiling to him: a jump from the platform or the call plate there is a '
            'low leap, as under any ceiling at his height.</li></ul>'
            '<h3>Research</h3><p>A slab that rises has to go into something: a portcullis hangs in a chamber over the gate passage, and the granite '
            'slabs of Khufu\'s antechamber ran in grooves into the granite above. In Prince of Persia (1989) a gate is drawn down from the top of '
            'its cell and the cell above it is always a floor or a wall block, so it never stands free. The game\'s own rule already held for its '
            'portcullises ("gates and blades keep their lintel"); now it holds for the lifts too.</p>' + links(SOURCES) +
            fig(img, 'r25d_slab.png', 'Round 25c (before) | 25d (after), Torchlight and Classic, the platform at the bottom and the top mouth shut; '
                'under each, 2x round the slab\'s top. Floor 7 (the owner\'s case), floors 10, 26 and 41 (other themes, both sides)') +
            '<h3>Tests</h3><p>' + E(TESTS) + '</p>'
            '<p class="meta">Retired to keep the page at 505 pictures: round 7\'s r7_hud.png (the round 7 HUD, superseded by round 8\'s).</p></section>']
