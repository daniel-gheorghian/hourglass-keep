# egyptround26e.py: round 26e's section of egypt_themes.html: every sand lift works within a shaft (owner: "sand lifts must always work
# within a shaft otherwise they don't make sense"). Picture from egyptr26e.py (r26e_sandshaft.png); counts from sandshaft.py.
import html
E = html.escape


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def links(L):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(t)) for t, u in L) + '</ul>'


SOURCES = [
    ('Janssen effect: a column of grains in a bin carries much of its weight on the walls by friction; without walls it slumps to its angle '
     'of repose', 'https://en.wikipedia.org/wiki/Janssen_effect'),
    ('Angle of repose: dry sand stands no steeper than about 30 to 35 degrees; a free-standing column of sand is impossible',
     'https://en.wikipedia.org/wiki/Angle_of_repose'),
    ('Udjahorresnet and his shaft tomb at Abusir (Late Period): the great shaft filled with sand, the sarcophagus lowered as the sand was '
     'taken out at its foot through side galleries (Bares, Abusir IV, 1999)', 'https://en.wikipedia.org/wiki/Udjahorresnet'),
    ('Landreau et al., On the possible use of hydraulic force to assist with building the step pyramid of Saqqara (PLOS ONE, 2024): sand-filled '
     'shafts emptied at the bottom to lower a load, as in Late Period shaft tombs', 'https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0306690'),
    ('SDLPoP, the Prince of Persia source port: a lift or gate stands in a mouth under a lintel (draw_tile_fore)', 'https://github.com/NagyD/SDLPoP'),
]

FOUND = ('Scanned on the tiles first (sandshaft.py, floors 1 to 48, three seeds, 322 sand lifts): not one stood in a shaft. A sand lift is '
         'the banner slide\'s shaft filled with sand under a slab; its sand reaches from under the top landing down to the foot\'s floor. '
         'The storey over the foot was open on the exit side in every one (the open-hall pass gives every floor a row of headroom and so '
         'opened the cell over the foot\'s floor beside the shaft) and on the far side in 173; the foot storey itself was open on the exit '
         'side in all (that is where he walks out) and on the far side in 171, where a corridor runs on past the foot; 6 were open higher up, '
         'and 13 had a drop beside the shaft. So the sand stood as a free pillar a tile wide in a hall two storeys high, often with the sky '
         'behind it through the hall\'s arches. The storeys higher up were walled (the banner\'s shaft is cut into solid wall).')
FIX = [
    'The walls are kept: the open-hall pass leaves the cells either side of a sand lift\'s shaft, from its top row to its foot, as wall, the '
    'way round 25d kept the counterweight lift\'s lintel: its random number for a window there is drawn all the same, so nothing else on '
    'the floor moves. The foot storey\'s exit is now a mouth under a lintel, as the counterweight lift\'s bottom mouth always was.',
    'The foot is shut by granite mouth slabs, the counterweight lift\'s own (egSlab): on the exit side always, and on the far side where a '
    'corridor runs on there. They hold the sand in and rise over the ride\'s last 28 px, a function of the slab\'s height alone (rewind-safe), '
    'so they are up as it lands. Play: the exit was already held shut while the slab was away (f.gB, an invisible grating); the far mouth now '
    'holds the same way, so nobody walks into a cell full of sand from behind. Torchlight\'s relief is rubbed off them as off the other mouths.',
    'Where the shaft cannot be one: a later run, passage or fill opened a side above the foot, or left a drop beside the foot (16 of the 322) '
    'the move is built as what it otherwise is, the banner slide: the same tiles, the bot\'s action a slide, which estPath times exactly as it '
    'timed the sand lift. No generator stream is drawn either way.',
]
CHOICE = ('Why this way: (a) on its own, choosing only enclosed places, would have removed every sand lift, since the exit storey and the '
          'hall pass\'s headroom are part of every one; (b), walling the cells, is what the counterweight lift going down has always done, and '
          'done through the hall pass\'s keep list it moves no random stream; (c), a drawn casing, would have put stone where the tiles say air. '
          'So (b) for the sides, the counterweight lift\'s mouth slabs for the foot, and (a) as the fallback for the few with a drop or a corridor '
          'cutting in.')
LAYOUT = ('Layouts against round 26d (floors 1 to 48, three seeds): routes, bot actions (but the 16 slides), items, lamps and features '
          'identical; 464 tiles stay wall (all beside sand shafts) and 59 hall windows that were in them are gone; on the 16 floors with a '
          'slide the shaft\'s top cell is open, as a banner\'s.')
TESTS = ('sandshaft.py floors 1 to 48, three seeds: before, 322 of 322 not in a shaft; after, 306 sand lifts, 0 not in a shaft, 463 foot mouth '
         'slabs (157 lifts with two): sandshaft: ok. lifttest: FAILURES 0 (sand3 1.63 s, sand4 2.08 s). liftscan floors 3 to 30, two seeds, both '
         'modes: ALL OK (976 cases; near, foot, wedge, relief 0; 0 arches and breaches in shafts). metrics40 against v72: every column identical on '
         'floors 1 to 27. featurescan: identical to round 26d. run2 floors 1 to 27: 27 of 27 passed, 0 runs with damage (0.07 ms/frame at most). '
         'featbot with the banner family and the lift family forced (floors 4, 9, 13, 18): 4 of 4 each, 0 damage. The bot on six floors chosen '
         'for two mouth slabs or a slide in place of a sand lift: all passed, 0 damage. rendersmoke floors 7 to 9, both modes: no errors '
         '(0.82 ms/frame).')


def sections(D, REL, img):
    return ['<section class="card" id="r26e"><h2>Round 26e: every sand lift in a shaft</h2>'
            '<p>Owner: "sand lifts must always work within a shaft otherwise they don\'t make sense."</p>'
            '<h3>What was found</h3><p>' + E(FOUND) + '</p>'
            '<h3>The fix</h3><ul>' + ''.join('<li>%s</li>' % E(t) for t in FIX) + '</ul><p>' + E(CHOICE) + '</p><p>' + E(LAYOUT) + '</p>'
            '<h3>Research</h3><p>Sand only stands as a column when walls hold it: a granular column in a bin carries much of its weight on the '
            'walls by friction (Janssen), and loose sand without walls slumps to its angle of repose. The Late Period shaft tombs at Saqqara and '
            'Abusir used exactly this: the shaft was filled with sand, the sarcophagus set on it, and the sand taken out at the foot through '
            'side galleries so the load sank down the shaft; the shaft\'s walls are what make it work. Prince of Persia stands its lifts and '
            'gates in mouths under lintels, and this game\'s counterweight lift does too.</p>' + links(SOURCES) +
            fig(img, 'r26e_sandshaft.png', 'Before | after, Torchlight and Classic: three storeys with a corridor past the foot (two mouth slabs), '
                'three storeys with a wall past the foot (one), four storeys near the end of the ride (the slabs rising), and one with a drop '
                'beside the foot, now the banner slide; the scan\'s counts under them') +
            '<h3>Tests</h3><p>' + E(TESTS) + '</p>'
            '<p class="meta">Retired to keep the page at 505 pictures: round 8\'s HUD-size picture of the star clock concept not built, '
            'r8_clock_C_hud.png.</p></section>']
