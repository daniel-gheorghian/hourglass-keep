# egyptround27a.py: round 27a's section of egypt_themes.html: the running jump's height (owner: "The running jump of the prince: the stride is
# better now, but I think the height is wrong: he moves up too much"). Pictures and numbers from egyptr27a.py (r27a_jump.png, r27a_jump.gif,
# r27a.json).
import html
E = html.escape


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def links(L):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(t)) for t, u in L) + '</ul>'


SOURCES = [
    ('SDLPoP (the reverse-engineered Prince of Persia 1989), seqtbl.c, the runjump sequence: frames 40-44 move the kid dy -3, -9, -2, +11, +3 '
     '(14 px up at the top, on a 63 px storey)', 'https://github.com/NagyD/SDLPoP/blob/master/src/seqtbl.c'),
    ('Linthorne, Guzman, Bridgett, Optimum take-off angle in the long jump, J. Sports Sciences 23 (2005): take-off angles about 21-23 degrees',
     'https://bura.brunel.ac.uk/handle/2438/544'),
    ('The optimum takeoff angle in the long jump (ISBS proceedings): elite take-off velocity about 8.8 m/s along and 3.4 m/s up for men (3.1 for '
     'women), so the centre of mass rises about 0.5-0.6 m over an 8 m jump', 'https://ojs.ub.uni-konstanz.de/cpa/article/view/653'),
    ('Hay, Citius, altius, longius: a review of jumping for distance, J. Biomechanics 26 Suppl. 1 (1993): flight, take-off height and angle',
     'https://doi.org/10.1016/0021-9290(93)90082-P'),
    ('Novacheck, The biomechanics of running, Gait & Posture 7 (1998): the centre of mass rises only a few centimetres in a running stride\'s '
     'flight', 'https://doi.org/10.1016/S0966-6362(97)00038-6'),
    ('The CMU Graphics Lab Motion Capture Database: 09_01 (run) and 49_04 (run, leap), the flight\'s poses since round 26c; the data used in this '
     'project was obtained from mocap.cs.cmu.edu, created with funding from NSF EIA-0196217', 'http://mocap.cs.cmu.edu/'),
]

FOUND = ('Measured in play first (the bot on floors 1 to 27, 1,220 jumps; the table in the picture). Every running jump leaves the floor at 190 '
         'px/s under the game\'s gravity (700 px/s2) and rises 25.8 px (the hit box 24.2 at a frame), and the figure was drawn on that arc: '
         'the hip at the hit box\'s feet plus a fixed 26 px. So over every running jump, a one-tile pit or three, his hip and crown rose 25 px, '
         'half his height (51.5 px), and with round 26c\'s leap the lowest foot came 27 px (one tile) to 37 px (three tiles) off the floor. On a '
         '1.75 m man 25.8 px is 0.88 m: more than an elite long jumper\'s centre of mass rises over 8 m (about 0.5-0.6 m); the same 0.54 s of '
         'flight under real gravity rises 0.36 m, 10.6 px; Prince of Persia\'s kid rises 14 px of a 63 px storey (14.2 of ours). The game\'s '
         'gravity is 2.4 times real (falls are quick), so the arc that carries him three tiles in 0.54 s is twice as high as a real one. Both '
         'parts were there: mostly the arc itself (the box, 24-26 px), and the pose only by tucking the feet up (the leap\'s split), which is '
         'right for a leap. The low leap (a ceiling at his height) already rose only 10.6 px; the standing jump 16.8.')
FIX = [
    'He is drawn on a lower arc of the same shape: the drawn rise is k times the real one (P.yo = (1 - k) times his rise over the take-off floor), '
    'so the take-off, the touch-down, every grab below the take-off level and everything after are exactly where the arc puts them (the offset '
    'is 0 there) and the drawn flight is a true parabola (its gravity k times the game\'s), with no step anywhere.',
    'k is set by the distance the jump is for, like the stride (round 26c\'s s): the drawn top is 8 px for a stretched stride over one tile '
    '(s 0) to 14 px for the full leap (s 1, three tiles; Prince of Persia\'s 14 px of a storey), over the arc\'s 25.8 px: k 0.31 to 0.54.',
    'What he clears or catches comes first. Spikes (needles up to 21 px) and saws (the blade 12 px up, where it is at each moment of the flight: '
    'the bot times the jump to it): k rises until the drawn feet stand as high over each needle and blade as on the full arc, or 1.5 px over its '
    'top. Drawn on the full arc (k 1): a jump whose arc meets a wall standing over the take-off floor (a ledge he may catch), lands higher up, or '
    'passes a swing bar in reach (the hands must reach what they catch), and the standing jumps.',
    'Look only: the arc, P.y, the hit box, grabs, the landing reach, timers, estPath and the bot are unchanged (every one of the 1,220 jumps flies '
    'the same distance and drop and ends the same way before and after). k is found once at take-off (jumpSpan, jhK) and kept on the prince '
    '(P.jK), so a rewind restores it; no allocation a frame. The physical arc was kept: lowering it would shorten every running jump (its reach '
    'is 2 vx vy / g) and change play.',
]
RESULT = ('Before > after (medians; the game\'s px): over one tile (pit or trap) the hip rises 25.3 > 12.3 (8.0-15.5, higher over spikes and '
          'saws), two tiles 24.9 > 12.1, three tiles 24.9 > 13.6, a jump that falls short and catches the far lip 25.3 > 14.1; the crown the same; the '
          'lowest foot 26.7 > 13.5, 33.4 > 20.8, 36.9 > 25.6 off the floor. Unchanged: jumps up to a ledge (24.9) and to a swing bar (24.5), the low leap '
          'down a storey, the standing jumps. The low leap over one tile 9.0 > 6.5 (crown 6.3 > 3.8).')
TESTS = ('From a copy of dev/: figscan: ok. lowceil: ALL OK. primtest: FAILURES 0. run2 floors 1 to 27, one seed: 27 of 27 passed, 0 runs with '
         'damage (0.05 ms/frame); floors 6 to 7 fighting: 2 of 2. featbot 2 - all 9: 40 of 40 passed, 0 damage. rendersmoke floors 7 to 9, both '
         'modes: no errors (0.66 ms/frame). stairscan: ALL OK.')


def sections(D, REL, img):
    return ['<section class="card" id="r27a"><h2>Round 27a: the running jump\'s height</h2>'
            '<p>Owner: "The running jump of the prince: the stride is better now, but I think the height is wrong: he moves up too much."</p>'
            '<h3>What was found</h3><p>' + E(FOUND) + '</p>'
            '<h3>The fix</h3><ul>' + ''.join('<li>%s</li>' % E(t) for t in FIX) + '</ul><p>' + E(RESULT) + '</p>'
            '<h3>Research</h3><p>Prince of Persia\'s running jump moves the kid up only 14 px over its three airborne frames (dy -3, -9, -2, then '
            '+11, +3), a fifth of a storey, while it carries him across two tiles of pit; the height is in the frames\' legs, not in the body. An '
            'elite long jumper leaves the board at about 21 degrees (3.4 m/s up, 8.8 m/s along) and his centre of mass rises about half a metre '
            'over eight; a runner\'s stride lifts it a few centimetres. A jump over a one-tile gap or across three tiles is far shorter, so the '
            'body rises less: at our scale (51.5 px for 1.75 m) half a metre is 15 px. Here the arc carries play (reach, timing, grabs), so only '
            'the drawing comes down, by the draw offset the climb and the bump already use (P.yo).</p>' + links(SOURCES) +
            fig(img, 'r27a_jump.png', 'Every jump the bot makes (floors 1-27): how high the box, the drawn hip, crown and lowest foot rise, before > after, '
                'and k; onion skins before | after with the paths of the box (the arc), the hip and the crown, over one, two and three tiles, a saw and '
                'the low leap; in game at the top of the arc, Torchlight and Classic, 1x and 3x') +
            fig(img, 'r27a_jump.gif', 'In game, half speed, before | after: one tile of pit (Torchlight), then three tiles (Classic)') +
            '<h3>Tests</h3><p>' + E(TESTS) + '</p>'
            '<p class="meta">Retired to keep the page at 505 pictures: round 8\'s concept clocks not built, concept B\'s half-run picture, '
            'r8_clock_B_5.png, and concept C\'s nearly-out picture, r8_clock_C_1.png.</p></section>']
