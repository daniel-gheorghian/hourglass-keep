# egyptround26f.py: round 26f's section of egypt_themes.html: the exit into the light and the entry out of the dark door (owner: "the
# climb animation: the prince climbs the wall, he should instead disappear on the stairs ... Maybe we should research and propose some other
# way to exit and maybe enter the level"; chosen from five mock-ups: exit D, entry E1). Pictures from egyptr26f.py.
import html
E = html.escape


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def links(L):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(t)) for t, u in L) + '</ul>'


SOURCES = [
    ('SDLPoP seqtbl.c: the kid\'s own climb-the-stairs sequence at the level door', 'https://github.com/NagyD/SDLPoP/blob/master/src/seqtbl.c'),
    ('SDLPoP seg006.c, clip_char: while he climbs the exit stairs the kid is clipped at the level door\'s bottom edge (leveldoor_ybottom + 1) '
     'and its right edge, so his head and shoulders go behind the wall first', 'https://github.com/NagyD/SDLPoP/blob/master/src/seg006.c'),
    ('SDLPoP seg003.c: the level\'s start and the kid\'s first moments', 'https://github.com/NagyD/SDLPoP/blob/master/src/seg003.c'),
    ('SDLPoP seg007.c, start_level_door and animate_leveldoor: the entrance door slams shut behind the kid, speeding up 5, 17 and 99 px a '
     'frame, with a slide and a thud', 'https://github.com/NagyD/SDLPoP/blob/master/src/seg007.c'),
    ('Spelunky: the exit door ends the level at once with a short transition card, the next level opens from its entrance door',
     'https://en.wikipedia.org/wiki/Spelunky'),
    ('The false door of Ni-ankh-Snefru (North Carolina Museum of Art): the door through which the ka comes and goes between the tomb and '
     'the world beyond', 'https://learn.ncartmuseum.org/artwork/false-door-of-ni-ankh-snefru-called-fefi'),
    ('Book of the Dead, in Egyptian the Book of Coming Forth by Day', 'https://en.wikipedia.org/wiki/Book_of_the_Dead'),
    ('Ancient Egyptian conception of the soul: the ka and the ba', 'https://en.wikipedia.org/wiki/Ancient_Egyptian_conception_of_the_soul'),
    ('Valley of the Kings, KV7 (Ramesses II): the tomb\'s plan, stairways and sloping corridors running down from the entrance',
     'https://madainproject.com/tomb_kv7_(tomb_of_ramesses_ii)'),
]

FOUND = [
    'He was cut at the ceiling\'s front edge, not at the opening\'s head (the lintel, or the round vault, 6 px lower), so his chest and arms '
    'were drawn over the lintel as he rose: he read as climbing the wall.',
    'The opening (45 to 50 px) is shorter than he is (51.5 px), and he rises about 49 px over the treads: seen whole, steep treads read as a '
    'ladder.',
    'Facing left (about 57% of layouts arrive at the exit going left) nothing turned him: the stairs\' sideways step took his facing, so he '
    'drifted onto the left jamb. stairscan.py only tested facing right.',
    'He stayed lit and opaque until a third of the way up, then faded, every part through every other.',
    'Entry: nothing happened. The entrance was drawn shut from the first frame while the floor\'s title showed.',
]
EXIT = [
    'He walks to the doorway\'s middle facing the way he goes, and if he came facing left he turns to the stairs (0.16 s); the stairs recede '
    'to the right whichever way he came.',
    'He climbs the same treads, a footfall on each. From the first rise he is cut at the opening\'s head (the lintel\'s line, or the round '
    'vault\'s curve, the same path the doorway is drawn with) and at its jambs, as SDLPoP cuts the kid: his head and shoulders go behind the '
    'wall first and what shows is a figure going up stairs inside the doorway.',
    'On the stairs he warms and whitens into the stair light and dissolves: his own pixels are tinted toward the treads\' amber, then toward '
    'the pale gold at the top of the stairs, and the whole figure fades as one (drawn into a buffer first, so no limb shows through another). '
    'Nothing glows round him: no haze (round 25c) and no bloom on a figure (v59); the light is the doorway\'s.',
    'As he goes, the doorway\'s light swells briefly (Torchlight: the door\'s own light, larger and brighter; Classic: the additive glow '
    'on the doorway, drawn under him), with a soft swell of sound, his steps going on up the stairs out of sight for half a second as in PoP, '
    'then the card. About 1.7 s from Up at the door facing right, 1.9 s facing left.',
]
ENTRY = [
    'Only on a fresh floor (the next floor, a new run, Restart): never on a checkpoint, a respawn, a Continue or a rewind.',
    'The entrance starts open on darkness. He comes out of it from inside the doorway, cut by its opening while deep in it, a dark silhouette '
    'taking its own colours as he reaches the light (0.42 s), and walks on to his start.',
    'Control at 0.62 s. The leaf starts down at 0.42 s and falls in 0.24 s speeding up (PoP\'s 5, 17 and 99 px a frame, scaled to our door), '
    'with a stone slide, a thud, a small shake and a puff of dust at its foot; it all lies under the floor\'s title.',
    'The floor\'s clock starts with control and no rewind snapshot is taken during the entry, so a rewind never plays it again; the leaf is '
    'a function of the clock from the floor\'s start, so nothing has to be restored. No gate timer runs at a floor\'s start (they start on '
    'their plates and are sized from estPath), so the entry takes nothing from any of them. The bot waits, keys up, until control is given.',
]
TESTS = ('stairscan.py floors 1 to 48: the feet on treads 1 to 4, now facing right and facing left (768 measures), every foot on its tread (gap -0.98 to -0.73 px, on the tread between -1.76 and 0), no sliding foot over 0.73 px, facing left turned to the stairs every time; the cut, the whole exit played from Up both facings in Classic and Torchlight (192 exits, 19 frames each from the first rise): his furthest pixel outside the opening\'s head and jambs 0.06 px under a lintel, 0.40 px under the round vault (antialiasing; the same check with the cut turned off finds 24 px), every exit ending facing right; the entry on all 48 floors: control at 0.63 s at his start, the leaf down with its thud by 1 s, no rewind snapshot of it, and a rewind, a respawn and a checkpoint start never play it again; the bot from the entry on floors 3 and 8 passed with 0 damage: ALL OK. doorscan: 0 of 192 door views with wall art over the opening. openscan: 0 of 89 gates, 0 of 422 lift mouths. rendersmoke floors 7 to 9, both modes: no errors (0.63 ms/frame at most). run2 floors 1 to 27: 27 of 27 passed, 0 runs with damage (0.06 ms/frame). run2 floors 6 and 7 fighting: 2 of 2, 0 damage. respawnplates: 0 bad. rewindrooms: FAILURES 0. glauto: FAILURES 0.')


def sections(D, REL, img):
    return ['<section class="card" id="r26f"><h2>Round 26f: into the light, and out of the dark door</h2>'
            '<p>Owner: "the climb animation: the prince climbs the wall, he should instead disappear on the stairs ... Maybe we should research '
            'and propose some other way to exit and maybe enter the level." From five mock-ups (A, the minimal cut; B, into the dark; C, down '
            'into the next chamber; D, into the light; E1, out of the dark door) the owner chose D for the exit and E1 for the entry.</p>'
            '<h3>What was found</h3><ul>' + ''.join('<li>%s</li>' % E(t) for t in FOUND) + '</ul>'
            '<h3>The exit: into the light</h3><ul>' + ''.join('<li>%s</li>' % E(t) for t in EXIT) + '</ul>'
            '<h3>The entry: out of the dark door</h3><ul>' + ''.join('<li>%s</li>' % E(t) for t in ENTRY) + '</ul>'
            '<h3>Research</h3><p>Prince of Persia gives the kid a climb of his own at the level door and clips him to the doorway as he goes '
            '(clip_char: at the door\'s bottom edge and its right edge), so he disappears into the stairs rather than over the wall; each '
            'level starts with the entrance door slamming shut behind him, speeding up, with a thud. Spelunky ends a level at its exit door '
            'and starts the next from an entrance door, a short card between. In Egypt the door between this world and the next is the false '
            'door, through which the ka comes and goes; the Book of the Dead is in Egyptian the Book of Coming Forth by Day; the royal tombs '
            'run down from their entrances by stairways and sloping corridors: so he goes up the stairs into the light, and comes out of the '
            'dark of the tomb\'s door.</p>' + links(SOURCES) +
            fig(img, 'r26f_exit.png', 'The exit before (v72 to round 26e) | after, three themes (two lintels, a round vault), Torchlight and '
                'Classic, facing right and facing left; then the entry on four floors') +
            fig(img, 'r26f_exit.gif', 'In game: he walks to the exit, climbs into the light, a pause where the card shows, the next floor\'s entry; Torchlight '
                '(arriving facing left), then Classic') +
            '<h3>Tests</h3><p>' + E(TESTS) + '</p>'
            '<p class="meta">Retired to keep the page at 505 pictures: round 8\'s clock concepts not built, concept B\'s HUD-size picture '
            'r8_clock_B_hud.png and concept C\'s half-run picture r8_clock_C_5.png.</p></section>']
