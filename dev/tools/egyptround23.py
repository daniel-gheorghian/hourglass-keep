# egyptround23.py: round 23's section of egypt_themes.html (built in): the prince rebuilt from motion capture.
# Numbers from r23body.json and r23measure.json (r23poses.py, egyptr23.py body); pictures from egyptr23.py.
import html, json, os
E = html.escape
HERE = os.path.dirname(os.path.abspath(__file__))


def links(src):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(l)) for l, u in src) + '</ul>'


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def table(head, rows):
    return ('<table><tr>' + ''.join('<th>%s</th>' % E(h) for h in head) + '</tr>' +
            ''.join('<tr>' + ''.join('<td>%s</td>' % E(str(c)) for c in r) + '</tr>' for r in rows) + '</table>')


TESTS = ('figscan.py against v69: ok (held hands within 0.35 px, 0.75 for the lunges; on the lip while pulling up and on the floor while '
         'pressing up; the crawl\'s palms on the floor; no crown above v69\'s standing crown in any pose, nor above v69\'s own in the crawl, the low '
         'leaps and the slide; soles on the floor where v69\'s were; the swing\'s hands on the bar; the drink\'s hand at the mouth). Differences, all '
         'look only: the joints themselves (the legs are longer: the hip joint 25.2 px over the floor, v69 24; the trunk upright as the clips stand, '
         'so the run\'s head is up to 6 px higher than v69\'s stooped run, still under v69\'s standing crown), the run\'s flight (the hip lifted by the '
         'clip\'s clearance, up to 2.6 px). lowceil ALL OK (the open jumps carry exactly as far; the drawn peak 1 to 2 px lower); lifttest 0 failures; '
         'swingtest ok (floors 6 to 9); stairscan ALL OK; primtest 0 failures; run2 floors 3 to 6, two seeds, 8/8 passed, no damage; run2 fight '
         'floors 6, 7 and 12, 3/3 passed, no damage; rendersmoke floors 7 to 9, both modes, no errors.')


def sections(D, REL, img):
    J = json.load(open(os.path.join(HERE, 'r23body.json')))
    M = json.load(open(os.path.join(HERE, 'r23measure.json')))
    B, W, I, A = J['body'], J['widths'], J['info'], J['ansur']
    src = J['src']
    prop = [('Standing height, sole to crown', '%.1f px' % M['height'], 'v69 53.0; never higher'),
            ('Heads tall (chin to crown %.1f px)' % M['head'], '%.2f' % M['heads'], 'the decision below'),
            ('Scale below the chin', '%.2f cm a px' % I['cm_per_px'], 'ANSUR stature %.0f mm, head 228 mm' % A['stature']),
            ('Hip joint over the floor', '%.1f px (%.2f of the height)' % (-M['hip'], -M['hip'] / M['height']), 'ANSUR trochanter %.0f mm' % A['trochanterionheight']),
            ('Thigh, shank to the floor', '%.1f, %.1f px' % (B['th'], B['sh']), 'CMU femur %.1f cm, tibia %.1f cm; ANSUR ankle' % (I['mocap_cm']['lfemur'], I['mocap_cm']['ltibia'])),
            ('Hip joint to shoulder joint', '%.1f px' % B['to'], 'CMU rest pose %.1f cm' % I['trunk_cm']),
            ('Shoulder joint to chin', '%.1f px' % W['jc'], 'ANSUR acromion %.0f mm, the joint 40 mm under it' % A['acromialheight']),
            ('Upper arm, forearm to the palm', '%.1f, %.1f px' % (B['ua'], B['fa']), 'CMU humerus %.1f cm, radius %.1f cm, 0.4 of the hand' % (I['mocap_cm']['lhumerus'], I['mocap_cm']['lradius'])),
            ('Chest, waist, seat depth', '%.1f, %.1f, %.1f px' % (W['chest'], W['waist'], W['seat']), 'ANSUR depths'),
            ('Neck depth (at its base)', '%.1f (%.1f) px' % (W['neck'], W['neckB']), 'ANSUR neck circumference / pi'),
            ('C7, pit of the neck under the chin', '%.2f, %.2f px' % (W['c7'], W['pit']), 'ANSUR cervicale, suprasternale'),
            ('Thigh, calf, upper arm across', '%.1f, %.1f, %.1f px' % (W['thigh'], W['calf'], W['arm']), 'ANSUR girths / pi (all 422)'),
            ('Foot', '%.1f px' % W['foot'], 'ANSUR foot length')]
    order = ['stand', 'run', 'walk', 'skid', 'turn', 'step', 'crouch', 'land', 'jumpS', 'jumpR', 'jumpLow', 'jumpLowS', 'reach', 'hang', 'pull', 'press',
             'kneelUp', 'kneel', 'slide', 'fall', 'kickPush', 'kickTuck', 'kickReach', 'swing', 'garde', 'windup', 'lunge', 'parry', 'lowStrike', 'hurt',
             'dead', 'crawl', 'drink']
    mv = [(k, src[k]['clip'], str(src[k]['frame']), src[k]['why'] + ('; ' + '; '.join(src[k]['fix']) if src[k].get('fix') else '')) for k in order if k in src]
    return ['<section class="card" id="r23"><h2>Round 23 (built in): the prince rebuilt from motion capture</h2>'
            '<p>Owner, after round 22d: "Start from those clips and build the athletic teen prince body and scrap the current skeleton and proportions so that '
            'we don\'t get swayed in the wrong direction." <b>The rule from now on: the body and every pose come from measured motion capture</b> (the CMU '
            'database) and ANSUR II; nothing was fitted to the earlier figures. Rounds 22b to 22d (the ANSUR fit and the 1989 kid) are superseded; '
            'dev/FIGURE_SPEC.md has the tables.</p>'
            '<h3>Sources</h3><ul>'
            '<li><b>CMU Graphics Lab Motion Capture Database</b>: per subject a skeleton (.asf: bone lengths, axes, degrees of freedom), per trial the joint '
            'angles at 120 frames a second (.amc), and a video. "The data used in this project was obtained from mocap.cs.cmu.edu. The database was created '
            'with funding from NSF EIA-0196217." The FAQ allows copying, changing and passing on the data.</li>'
            '<li><b>ANSUR II</b> (US Army anthropometric survey, 2012): men aged 17 to 20; the lean ones (BMI under 23, n=124) for the trunk\'s lengths '
            'and depths, all 422 for the limbs\' girths and the chest: an athlete\'s muscle on a lean frame.</li></ul>'
            '<h3>Method</h3><ul>'
            '<li><b>mocap.py</b> parses the ASF and AMC files (units: length 0.45, so metres = value / 0.45 x 0.0254; each bone\'s rotation is '
            'C M C<sup>-1</sup> with M the product Rz Ry Rx of its angles, as the database\'s own viewer does), runs the forward kinematics and projects '
            'every joint onto the plane of the body\'s own facing (the pelvis\'s forward over the frames used). Contact sheets of every clip were drawn '
            'to pick the frames. Video frames (ffmpeg, frame / 4 at 30 fps) of 09_01, 43_02, 02_07, 14_07, 01_03 and 01_09 confirmed what the chosen '
            'frames show: 43_02\'s bar is low, so he swings piked; 02_07\'s sword is a stick held in both hands; 01_09 f1745 hangs with the knees up; '
            '01_03 f1765, used for the hang\'s shape, still has his feet on the ground. They are filmed from the front or at an angle, so they were not '
            'used to check the side view frame by frame.</li>'
            '<li><b>The body</b>: lengths below the chin from four CMU subjects\' mean bones (09, 13, 14, 16: the run and jump clips), scaled so the hip '
            'joint stands at ANSUR\'s trochanter height in the body\'s scale; the shoulder-to-chin span, the neck and every depth and girth from ANSUR. '
            'The drawing keeps the game\'s style (outlined, shaded, the shendyt, the cropped hair), only sized by these numbers.</li>'
            '<li><b>The head (decision)</b>: a real 17 to 20 year old is 7.7 heads tall (ANSUR stature, head 0.13 of it: Drillis and Contini); Loomis '
            '(1943) draws a man at 7.5. Side-view games of this figure height enlarge the head so the face reads: the rotoscoped 1989 Prince of Persia kid '
            'is 5.86 heads (measured from his DOS frames in round 22d), Another World and Flashback about 6.5 to 7 (round 22b\'s survey), stylised '
            'platformers 2 to 3. Ours is 52 px at 1x, two to three device pixels a game pixel on the phone, and the eye, brow, nose and jaw need about 8 px '
            'of head: <b>6.5 heads</b> (6.57 as drawn), between the real 7.7 and the kid\'s 5.86; everything below the chin is real size.</li>'
            '<li><b>The poses</b>: each is the game\'s own angles (lean and head from straight up, the limbs from straight down, knees and elbows as the bend '
            'from the bone above) measured from one clip frame (or a short average), the near side the subject\'s right (his left, the lead leg, in the '
            'fight). The run and the walk are 16 keys over one measured cycle, the near foot down at phase 0 and the far one at 0.5, the hip set over '
            'the lowest foot by the clip\'s own clearance (so a planted foot is on the floor and the flight is the clip\'s). The swing is the clip\'s body '
            'in the frame of the line from the hip to the hands, in 12 bins of the swing\'s phase. r23poses.py writes all of it into one generated block '
            'of the source (R23B, R23D, MCP, MCK).</li>'
            '<li><b>Gameplay is not the clips\'</b>: every timer, the run\'s phase (a cycle per 44 px, footfalls at 0 and 0.5), the climb\'s 0.72 s and '
            'its positions, the drink\'s beats, the swing\'s physics, hit boxes and the bot are unchanged; air, the hip\'s height in the air, the blade\'s '
            'angle and the held hands are v69\'s (read from v69 by r23grips.py). Where the new arm could not reach v69\'s grip the trunk was turned '
            'toward it (listed in the table); the low leaps were pitched forward until the head stays under v69\'s.</li></ul>'
            '<h3>The body</h3>' + table(('Measure', 'Value', 'Source'), prop) +
            fig(img, 'r23_body.png', 'The new prince at 10x beside the CMU subject the standing pose comes from (79_38 f30, side view), in game at 1x and 3x, '
                'a robber at 4x, and the proportions') +
            '<h3>The clip and frame of each move</h3>' + table(('Move', 'Clip', 'Frame', 'What it is'), mv) +
            '<p>Derived where no clip fits: the turn (a turn is not in the side view: the settle after a sudden stop), hurt (no clip of a blow: the stop\'s '
            'brace), the wall-kick poses (from the leap and the broad jump), the low leaps (pitched forward), the climb onto a ledge (no clip pulls up onto '
            'one: the hang, then 81_14 played backwards), the drink\'s pick-up (a crouch). The crawl is weak (111_03, a pregnant woman): only its limb '
            'timing. Kept procedural: the wall run and the kick-shaft plant (two-bone IK on the new legs).</p>' +
            fig(img, 'r23_moves.png', 'Each move: the clip as measured (side view, red the near limbs) | the new prince | v69, at 4x') +
            fig(img, 'r23_game.png', 'In the game, v69 | after: standing and running (Torchlight at GLP.rs 1 and 0.5, Classic), hanging, pulling up and '
                'climbing, crawling, swinging, and in a fight') +
            '<div class="g2">' + fig(img, 'r23_run_swing.gif', 'Running, then swinging on the bar: v69 | after, in game (Classic)') +
            fig(img, 'r23_climb.gif', 'Jumping up to grab a ledge, hanging and climbing onto it: v69 | after') + '</div>'
            '<h3>Tests</h3><p>' + E(TESTS) + '</p>'
            '<p class="meta">Retired to stay at 505 files: round 22d\'s three sheets (r22d_compare, r22d_poses, r22d_game) and round 22b\'s games schematic '
            '(r22b_games), superseded by this round\'s.</p>' +
            links([('CMU Graphics Lab Motion Capture Database', 'http://mocap.cs.cmu.edu/'),
                   ('CMU mocap FAQ (use of the data)', 'http://mocap.cs.cmu.edu/faqs.php'),
                   ('ANSUR II (calmcode.io dataset page)', 'https://calmcode.io/datasets/ansur'),
                   ('ASF/AMC file format (CMU)', 'http://research.cs.wisc.edu/graphics/Courses/cs-838-1999/Jeff/ASF-AMC.html')]) +
            '</section>']
