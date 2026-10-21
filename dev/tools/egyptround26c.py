# egyptround26c.py: round 26c's section of egypt_themes.html: the running jump's stride drawn for the distance the jump is for (owner: "when
# jumping the stride is too large. It works for large gaps but for smaller gaps looks silly. I'd adjust the stride with the actual distance he
# jumps"). Pictures and numbers from egyptr26c.py (r26c_stride.png, r26c_jumps.gif, r26c.json).
import html
E = html.escape


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def links(L):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(t)) for t, u in L) + '</ul>'


SOURCES = [
    ('Novacheck, The biomechanics of running, Gait & Posture 7 (1998): the hip\'s range and the stride grow with speed; in a run\'s flight the '
     'thighs are 60-75 degrees apart', 'https://doi.org/10.1016/S0966-6362(97)00038-6'),
    ('Mesquita, Morin, Dewolf (UCLouvain): the hip\'s sagittal range follows the stride\'s frequency and length',
     'https://research.dial.uclouvain.be/bitstreams/de8a379d-810c-4968-b100-8eb3f86768b8/download'),
    ('Kalichova, the grand jete\'s take-off and flight (3D kinematics of dance students): a split is a timed, large leap\'s shape', 'https://www.muni.cz/en/research/publications/978400'),
    ('Kinematics of rhythmic gymnastics leaps (J. Human Sport and Exercise 2009): flight time follows the push and the last stride\'s length, the split '
     'what is done in it', 'https://rua.ua.es/dspace/handle/10045/8968'),
    ('Clavet, Motion Matching and The Road to Next-Gen Animation (GDC 2016, For Honor): the pose picked from captured motion by where the body is going',
     'https://gdcvault.com/play/1023280/Motion-Matching-and-The-Road'),
    ('Unreal Engine: blend spaces (clips blended by a parameter such as speed or distance) and distance matching (a clip advanced by the distance '
     'travelled, not time)', 'https://dev.epicgames.com/documentation/unreal-engine/blend-spaces-in-unreal-engine'),
    ('Unreal Engine: distance matching', 'https://dev.epicgames.com/documentation/ko-kr/unreal-engine/distance-matching-in-unreal-engine'),
    ('Desilets on Prince of Persia: The Sands of Time (Engadget, Devs Play): a platformer\'s animation is the transitions between short and long moves',
     'https://www.engadget.com/2015-12-23-prince-of-persia-patrick-desilets-devs-play.html'),
    ('The CMU Graphics Lab Motion Capture Database: 49_04 (run, leap) and 09_01 (run); the data used in this project was obtained from '
     'mocap.cs.cmu.edu, created with funding from NSF EIA-0196217', 'http://mocap.cs.cmu.edu/'),
]

FOUND = ('Measured in play first (the bot on floors 1 to 27, two seeds, 2,500 jumps; the table in the picture). The arcs are fixed: every '
         'running jump on a level floor flies 97.6 px in 0.53 s (183 px/s, three tiles), whether it crosses three tiles of pit, two, one, or a '
         'saw; a low leap 74.2 px in 0.35 s; a standing jump 59.4 px in 0.45 s. What changes the distance actually flown is where the jump ends: '
         'a grab at a ledge a storey up (33.8 px), a swing bar (42.7), a landing a storey down (137.8 for a low leap). v72 drew every running jump '
         'with one held frame, 49_04 f176, the top of a dancer\'s leap: thighs 124 degrees apart, the feet 40 px apart on a 51 px figure, for a '
         'one-tile pit as for three. The standing jumps keep the feet together (4 degrees, 0.8 px): there is no stride to scale.')
FIX = [
    'The stride is drawn for the distance the jump is for, found once at take-off from the tiles (jumpSpan): the arc to the first floor his feet '
    'meet (or a wall in the way), and, if a pit or trap is in front (no floor, spikes, a loose slab, a closer plate, a saw, a fire vent), its far '
    'lip plus a foot (12 px). D is the shorter; s = (D - 48) / (the level arc - 48), 0 to 1. One tile of pit gives s 0.01-0.10, two 0.69-0.72, '
    'three 0.96-1, a jump up to a ledge 0-0.37, a jump down a storey 1. 48 px (a tile and a half) is where a lengthened running step stops '
    'being enough.',
    'The flight is a sequence (9 keys, take-off to touch-down, by the arc\'s phase) in two measured sets, blended by s: S, a running stride\'s '
    'flight (09_01 f27-43, the run\'s own clip: the thighs 73 degrees apart at toe-off closing to 31 at heel strike, the arms swinging against '
    'the legs) and L, the leap (49_04 f160-213: 88 degrees at take-off, 121 at the top, 77 as the lead foot reaches down). The leap\'s arms are '
    'a dancer\'s, opened to the sides and end-on to the camera for most of the flight, so L keeps v72\'s arms (forward and up) and its straight '
    'trunk; the game\'s landing blend lowers them as before. The feet point in the leap (round 25a\'s foot pitch from the same frames). The low '
    'leaps take the same keys, each pitched forward by the low-leap rule.',
    'Look only: the arcs, take-off timing, hit box, grabs, the bot and every timer are unchanged (the measured distances and air times are '
    'identical before and after). The numbers sit on the prince (P.jS, P.jT), so a rewind restores them; no allocation a frame. The standing '
    'jumps are unchanged.',
]
RESULT = ('Widest as drawn over the flight, before > after (thigh split, feet apart): one tile 124 > 62-71 degrees, 40.0 > 25.6-27.3 px; two tiles '
          '124 > 99-102, 40.0 > 36.4-36.9; three tiles 124 > 115-116, 40.0 > 39.6; up to a ledge 124 > 66-83, 40.0 > 25.6-31.9; the low leap over one '
          'tile 101 > 62-73, 30.7 > 27.1-28.3. The low leap down a storey or across two tiles now opens wider than v72\'s (101 > 113-114 degrees): it '
          'is drawn as the full leap there, where v72 held the leap\'s take-off frame.')
TESTS = ('figscan: ok. lowceil: ALL OK. primtest: FAILURES 0. run2 floors 3 to 6, two seeds: 8 of 8 passed, 0 runs with damage (0.04 ms/frame); '
         'floors 6 to 7 fighting: 2 of 2 passed. rendersmoke floors 7 to 9, both modes: no errors (0.72 ms/frame).')


def sections(D, REL, img):
    return ['<section class="card" id="r26c"><h2>Round 26c: the stride for the distance</h2>'
            '<p>Owner: "when jumping the stride is too large. It works for large gaps but for smaller gaps looks silly. I\'d adjust the stride '
            'with the actual distance he jumps."</p>'
            '<h3>What was found</h3><p>' + E(FOUND) + '</p>'
            '<h3>The fix</h3><ul>' + ''.join('<li>%s</li>' % E(t) for t in FIX) + '</ul><p>' + E(RESULT) + '</p>'
            '<h3>Research</h3><p>In running the hip\'s range and the stride grow with speed and with the stride\'s length; a running stride\'s flight '
            'holds the thighs 60 to 75 degrees apart. A leap\'s split (the grand jete, a hurdle, a gymnast\'s leap) belongs to a long, high flight and '
            'is timed to its top; over a puddle or a narrow gap a runner only lengthens a step. Games pick or blend the pose by what the move has to '
            'do: blend spaces keyed by speed or distance, distance matching (the clip advanced by the distance covered), and motion matching '
            '(For Honor), which picks captured frames by where the body is going; the Sands of Time\'s director put a platformer\'s animation in '
            'its transitions between short and long moves. Here the game\'s own arc is fixed, so the blend is keyed by the distance the jump has '
            'to cover, from two captured flights.</p>' + links(SOURCES) +
            fig(img, 'r26c_stride.png', 'Every jump the bot makes (floors 1-27): distance flown, air time, D and s, the widest split and feet before > '
                'after; onion skins before | after of running jumps over one, two and three tiles of pit and the low leap over one tile') +
            fig(img, 'r26c_jumps.gif', 'In game (Torchlight), half speed, before | after: a running jump over one tile of pit, then over three') +
            '<h3>Tests</h3><p>' + E(TESTS) + '</p>'
            '<p class="meta">Retired to keep the page at 505 pictures: round 7\'s robbers, r7_robbers.png (rebuilt from motion capture in round 23), '
            'and round 7\'s pause panel, r7_pause.jpg (the menu has grown since).</p></section>']
