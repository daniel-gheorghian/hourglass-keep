# egyptround22d.py: round 22d's section of egypt_themes.html (built in): the prince rebuilt to the 1989 Prince of Persia kid's proportions.
# Numbers from egypt_themes/r22d.json (egyptr22d.py; the kid and our figure measured by r22dmeasure.py); the gameplay check is figscan.py.
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


ROWS = [('heads', 'Height in heads (crown to chin)', '%.2f'), ('h_chin', 'Chin over the sole / height', '%.3f'),
        ('chin_acr_head', 'Chin to the shoulder\'s top (deltoid) / head', '%.2f'), ('chin_acr_H', 'Chin to the shoulder\'s top / height', '%.3f'),
        ('neck_front_H', 'Chin to the pit of the neck / height', '%.3f'), ('h_shoulder_line', 'Shoulder line at the back (C7) / height', '%.3f'),
        ('h_acromion', 'Shoulder\'s top / height', '%.3f'), ('h_shoulder_joint', 'Shoulder joint / height', '%.3f'), ('h_elbow', 'Elbow / height', '%.3f'),
        ('h_wrist', 'Wrist / height', '%.3f'), ('h_fingertip', 'Fingertips / height', '%.3f'), ('arm_H', 'Shoulder joint to fingertips / height', '%.3f'),
        ('h_crotch', 'Crotch (the legs\' split, read along a straight leg) / height', '%.3f'), ('h_knee', 'Knee / height', '%.3f'),
        ('head_depth_head', 'Head depth / head height', '%.2f'), ('neck_depth_H', 'Neck depth under the chin / height', '%.3f'),
        ('chest_H', 'Depth at the chest, arm in (0.25-0.36 of height down) / height', '%.3f'), ('belly_H', 'Depth at the waist (0.40-0.55) / height', '%.3f'),
        ('hips_H', 'Depth at the hips (0.60-0.68) / height', '%.3f'), ('knees_H', 'Depth at the knees (0.72-0.80) / height', '%.3f'),
        ('foot_H', 'Foot length / height', '%.3f')]

TESTS = ('figscan.py against v69: ok, 80 poses (no contact hand moved more than 0.35 px; no crown higher; feet and hip unmoved on the ground; the '
         'swing\'s hands on the bar and hip as v69\'s; the drink\'s hand to mouth kept). Differences, all look only: the head\'s centre about 1.1 px '
         '(2.5 crawling), the mouth about 2 px (the drink\'s hand follows it, 1.95 px), the silhouette\'s front up to 1.5 px in (slimmer chest, '
         'shorter foot), the crown up to 1.6 px lower. Against 22c the hands overhead (fall, wall run) are up to 1.9 px higher: back at v69\'s. '
         'lowceil ALL OK; lifttest 0 failures; swingtest ok (floors 6 to 9); stairscan ALL OK (floors 1 to 48); run2 floors 3 to 6, two seeds, '
         '8/8 passed, no damage; run2 fight floors 6 and 7, 2/2 passed, no damage; rendersmoke 7 to 9 both modes, no errors (0.55 ms a frame; '
         '22c 0.52).')


def sections(D, REL, img):
    J = json.load(open(os.path.join(HERE, 'egypt_themes', 'r22d.json')))
    K, M = J['kid'], J['measure']
    rows = [(name, f % K[k] if k in K else '-') + tuple(f % M[v][k] for v in ('v69', '22c', 'after')) for k, name, f in ROWS]
    a = M['after']
    return ['<section class="card" id="r22d"><h2>Round 22d (built in): the proportions of the 1989 kid</h2>'
            '<p>Owner, after round 22c: "That is still slightly off. I like best the proportions in the original PoP sprite you downloaded. Replicate '
            'the proportions from there in our prince." <b>The rule from now on: the prince\'s proportions follow the 1989 Prince of Persia kid (DOS).</b> '
            'The ANSUR II measures of rounds 22b and 22c stay as background (dev/FIGURE_SPEC.md).</p>'
            '<h3>How the kid was measured</h3><ul>'
            '<li>Frames: the DOS kid\'s sprite sheet from the PrinceJS project (assets/gfx/kid.png and kid.json, kept in dev/tools/ref), frame numbers '
            'as Mechner\'s frame list names them in SDLPoP (src/types.h: frame_15_stand, frame_7..14_run, frame_121..132_stepping, frame_109_crouch, '
            'frame_87..99_hanging, frame_135..149_climbing, frame_150_parry, frame_158_stand_with_sword, frame_191..205_drink). Shown here only as a '
            'measured reference.</li>'
            '<li>Aspect: DOS 320x200 on a 4:3 screen makes a pixel 1.2 times taller than wide. Every horizontal measure was <b>divided by 1.2</b> to put it '
            'in rows; vertical measures are as they are. The pictures draw each pixel 1.2 times as tall as it is wide.</li>'
            '<li>Standing (frame 15) he is 41 rows from the crown to the sole; the head is 7 rows (the same bitmap in every upright frame), so 5.86 heads. '
            'Heights are read from frame 15 (chin, shoulder, fingertips, foot), the bent arm of run frame 10 (elbow), the straight back legs of frames 12 '
            'and 152 and the fight stance 158 (crotch and knee: his baggy trousers hide the crotch standing); widths are the silhouettes of the upright '
            'frames 15, 121 and 132 averaged row by row. The waist is not drawn on the kid (one white shirt and trousers); the guards\' sash (guard frame 29: '
            'rows 16-17 of 40) gives 0.59 of the height.</li>'
            '<li>Our figure is measured the same way (r22dmeasure.py): the standing figure drawn at 10x, its silhouette\'s widths at the same fractions '
            'of its height, the landmarks from the drawing and the skeleton.</li></ul>'
            '<h3>How he reads</h3><p>Rotoscoped from a real young man: a small head on a long, slim body; the chin sits almost on the shoulders with one row of '
            'throat showing; the shirt\'s shoulder line runs level with the chin behind the neck and the deltoid starts one row lower, so the shoulders '
            'slope down and back from the jaw; the back of the head, the back and the seat stand on one straight vertical line; the trunk is about as deep '
            'as the head and barely tapers; the arms hang long, the fingertips at the crotch\'s level; the feet are small.</p>' +
            table(('Measure', 'PoP 1989 kid', 'v69', 'Round 22c', 'After (22d)'), rows) +
            '<h3>What changed</h3><ul>'
            '<li><b>Skeleton</b> (<code>LEN</code>): the head\'s radius 4.4 to 3.52 (the head 9.0 px of 52.75, 5.86 heads as the kid); the trunk back to v69\'s '
            '15 (shoulder joint 0.76 of the height, the kid 0.77); the arm back to v69\'s 17.5, now 8.9 + 8.6 (elbow 0.59, fingertips 0.39: the kid 0.60 and '
            '0.39); the neck 4.66 to the head\'s centre, so the crown stays where it was (0.25 px lower standing). Legs and feet joints unchanged (gameplay).</li>'
            '<li><b>Held hands</b> (<code>hold</code>, <code>hb</code>, <code>mh</code>, <code>F69</code>) keep v69\'s places; with v69\'s trunk and arm length '
            'they reach every grip as v69 did. The crown never rises above v69\'s; no hit box reads the drawing.</li>'
            '<li><b>Neck and shoulders</b> (<code>NJ</code>): the pit of the neck and the deltoid\'s top %.1f px under the chin (the kid: one row, 1.3 px), C7 '
            'just under the chin, the neck %.1f px deep under the jaw (the kid 4.3); the neck\'s top scales with the head (<code>NJ.hn</code>).</li>'
            '<li><b>Outline</b>: the trunk slimmer (<code>BQ</code>, <code>Fo</code>, <code>Bo</code>: chest about 0.8 of 22c\'s, waist 0.9), arms '
            '(deltoid 5.2 to 4.4, forearm 2.8 to 2.4) and thighs (6.6 to 5.0 at the hip) thinner, the foot 0.78 as long. Round 19\'s raised arms, round '
            '20b\'s kilt seat and blade, 21a\'s and 22c\'s smooth back stay; the kilt\'s hem follows the thinner thighs.</li>'
            '<li><b>Robbers</b> share the skeleton (the same head, neck and trunk) with their own heavier build (their offsets and limbs about 0.9 of '
            'before): the PoP guards (guard.png) are rotoscoped men too, broader in the chest (0.20 of the height against the kid\'s 0.15).</li>'
            '<li><b>Not matched</b>: the knee (0.25 against the kid\'s 0.28: the legs are gameplay\'s and stay) and the crotch as read along a straight leg '
            '(%.2f against 0.44: our thighs are round tubes about the hip joint under the kilt, the kid\'s baggy trousers split low); the waist depth is the '
            'kid\'s shirt blousing.</li></ul>' % (a['chin_acr_H'] * a['height'], a['neck_depth_H'] * a['height'], a['h_crotch']) +
            fig(img, 'r22d_compare.png', 'The 1989 kid (DOS frames, nearest neighbour, aspect-corrected) beside our prince at the same height: v69 | 22c | after, '
                'standing with the kid\'s landmarks as guide lines (crown, chin, shoulder, waist, hip, crotch, knee, sole), then running, stepping, crouching, '
                'hanging, climbing and en garde') +
            fig(img, 'r22d_poses.png', 'Every pose at 4x, 22c | after, lit from his back, and a robber standing and en garde') +
            fig(img, 'r22d_game.png', 'In the game, 22c | after: standing and running (Torchlight at GLP.rs 1 and 0.5, Classic), hanging and climbing, crawling, '
                'swinging, and in a fight') +
            '<h3>Tests</h3><p>' + E(TESTS) + '</p>'
            '<p class="meta">Retired to stay under 505 files: round 22c\'s variants, guide, poses and game sheets (superseded by this round\'s three).</p>' +
            links([('PrinceJS (oklemenz): the DOS sprites, assets/gfx/kid.png and kid.json, guard.png', 'https://github.com/oklemenz/PrinceJS/tree/master/assets/gfx'),
                   ('SDLPoP (NagyD): src/types.h, the frame list (frameids)', 'https://github.com/NagyD/SDLPoP/blob/master/src/types.h'),
                   ('SDLPoP: src/seqtbl.c, the animation sequences that use the frames', 'https://github.com/NagyD/SDLPoP/blob/master/src/seqtbl.c')]) +
            '</section>']
