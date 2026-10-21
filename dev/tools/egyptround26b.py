# egyptround26b.py: round 26b's section of egypt_themes.html: no hump behind the shoulder with the arms up (owner, a phone shot of the
# prince hanging from a ledge in Torchlight, the upper back circled: "The last photo shows the prince with a hump of sorts. I don't know if it
# is because the lights or an error in the measurements. In my opinion I'd reduce with 1px the back"). Picture and numbers from egyptr26b.py.
import html
E = html.escape


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def links(L):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(t)) for t, u in L) + '</ul>'


SOURCES = [
    ('Scapulohumeral rhythm: raising the arm overhead turns the scapula upward about 60 degrees, its lower angle swinging out under the arm; '
     'seen from the side the upper back flattens under the raised arms', 'https://en.wikipedia.org/wiki/Scapulohumeral_rhythm'),
    ('Inverse kinematics: a two-bone limb solved to reach a target, the elbow\'s side chosen by its bend', 'https://en.wikipedia.org/wiki/Inverse_kinematics'),
    ('The CMU Graphics Lab Motion Capture Database (the hang\'s clip 01_03: holding a bar overhead; the data used in this project was obtained from '
     'mocap.cs.cmu.edu, created with funding from NSF EIA-0196217)', 'http://mocap.cs.cmu.edu/'),
]

CAUSE = ('Geometry, not the light. The silhouette (the figure in one flat colour, no light at all) has the same bump as the lit picture, and with '
         'both arms left out the trunk alone has it too: the outline, not a shading band, a rim or the relief. The light only makes it read: a lamp '
         'behind him lights the back\'s plane, which follows the outline. Why the outline: since round 23 a held hand (the hang, the jump up, the '
         'climb\'s start, the slide, the sword, the drink) is put on its grip by the skeleton\'s two-bone solve, so the upper arm is drawn where that '
         'solve puts it, not at the clip\'s angle. The trunk\'s arms-up shaping (round 19: the scapulae turned up, the neck between the arms, the lats; '
         'and the raised arm rising from the back of the shoulder) still read the clip\'s angles. The hang\'s clip (01_03, holding a bar overhead) '
         'gives 1.81 and 1.98 rad from straight down; the arms are drawn at 2.69 and 2.83, overhead. So the trunk was shaped for arms half down '
         '(ra 0.13 of 1): the standing back, full at the trapezius and 4.6 to 4.9 px behind the spine\'s line from U .62 to .96, stood behind '
         'arms that rise past the head. v69\'s hang had its arms at 2.72 and 2.78 and was shaped right; round 23 lost it. On the silhouette at 10x '
         'the upper back stood 3.3 px behind the neck\'s back and 2.2 px behind the waist (standing: 2.1 and 2.9, the blades on the skull-to-seat '
         'line of round 22). The same in the climb\'s start (ra 0.14) and the slide (0.18). The jump up\'s reach had its arms up in the clip (ra 1) '
         'but there round 22\'s arms-up back (the lats out 0.35 px) made the upper back 5.1 px deep, the fullest of any pose.')
FIX = [
    'The trunk and the shoulder read the arm as drawn: for a held hand the upper arm\'s angle is taken from the solved elbow (armDrawn), for the '
    'arms-up shaping (ra), the trunk\'s twist and the shoulder\'s root (armG). The hang, the climb\'s start and the slide are now shaped as '
    'arms up (ra 1.00), as v69\'s were; the pull (ra 0.28 to 0, its arms are drawn forward over the ledge), the windup (0.31 to 0.09) and the '
    'drink\'s last keys (up to 0.32, the elbow raised to the mouth) follow their drawn arms too.',
    'The owner\'s pixel: the arms-up back (Bo, r23poses.py BO_CUT) is 1 px shallower at its fullest (U .62 and .76), 0.55 at .88 and 0.2 at .96, '
    'nothing at the waist and the shoulder\'s top, so it runs from the trunk\'s top down to the lats as one slope with no notch: at MUS 1.65 '
    '5.07, 5.19, 4.96, 4.51 to 4.07, 4.19, 4.41, 4.31 (drawn with round 19\'s turn-up: 4.13, 4.14, 3.48, 2.99 behind the spine). The cut grows '
    'with the muscle: a share (m-1)/(MUS-1) at the lower levels (none at 1.0, where the back is only 2.5 px deep), 1 px at 1.85.',
    'Arms down (BQ) is unchanged: there the shoulder blades stand on the line from the skull to the seat (0.6 px behind it standing), the '
    'consistency round 22 set; taking the pixel off there too would put them in front of it. The robbers keep v70\'s table (R23DR) and round 22\'s '
    'arms-up back. Joints, skeleton, poses, grips, hit boxes and timings unchanged.',
]
RESULT = ('After, on the silhouette at 10x: the hang\'s upper back 2.6 px behind the neck\'s back (3.3 before) and 1.4 px behind the waist (2.2); '
          'the jump up\'s 0.9 px nearer the spine; stand and run identical to the pixel.')
TESTS = ('figscan: ok (held hands, crowns, soles, the bar, the mouth). lowceil: ALL OK. swingtest: FAILURES 0. rendersmoke floors 7 to 9, both '
         'modes: no errors (0.57 ms/frame). run2 floors 3 to 6, one seed: 4 of 4 passed, 0 runs with damage (0.03 ms/frame).')


def sections(D, REL, img):
    return ['<section class="card" id="r26b"><h2>Round 26b: no hump behind the shoulder</h2>'
            '<p>Owner, with a phone shot of the prince hanging from a ledge in Torchlight, the upper back behind the shoulder circled: "The last photo '
            'shows the prince with a hump of sorts. I don\'t know if it is because the lights or an error in the measurements. In my opinion I\'d '
            'reduce with 1px the back."</p>'
            '<h3>The cause</h3><p>' + E(CAUSE) + '</p>'
            '<h3>The fix</h3><ul>' + ''.join('<li>%s</li>' % E(t) for t in FIX) + '</ul><p>' + E(RESULT) + '</p>'
            '<h3>Research</h3><p>With the arms overhead the scapulae turn upward and swing out under the arms (scapulohumeral rhythm), so in '
            'profile the upper back flattens and the trapezius\'s slope is taken up by the raised arms; it never stands out behind the neck. Round 19 '
            'drew this; its test was the pose\'s own arm angles, which a solved (inverse kinematics) arm no longer matches.</p>' + links(SOURCES) +
            fig(img, 'r26b_back.png', 'Before (v72) | after. At 10x the hang, the jump up\'s reach and the climb\'s start, lit from behind as in the '
                'owner\'s shot and as a silhouette, the back\'s contour from the head to the hip in red (before\'s in blue on after); at 4x seven poses; '
                'the numbers; in game at the phone\'s resolution (floor 5): jumping up, hanging, climbing, Torchlight and Classic, 1:1 and 3x') +
            '<h3>Tests</h3><p>' + E(TESTS) + '</p>'
            '<p class="meta">Retired to keep the page at 505 pictures: round 7\'s fight against the soldier, r7_fight_1.gif (the prince and the '
            'robbers were rebuilt from motion capture in round 23).</p></section>']
