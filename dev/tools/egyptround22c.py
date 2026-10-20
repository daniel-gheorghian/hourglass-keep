# egyptround22c.py: round 22c's section of egypt_themes.html (built in): the audit of round 22b's neck measures and the corrected neck.
# Numbers from egypt_themes/r22c.json (egyptr22c.py, landmarks by r22cmeasure.py); the gameplay check is figscan.py.
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


TESTS = ('figscan ok against v69 (the same differences as 22b: the skeleton is unchanged) and against round 22b with no difference over 0.25 px in any '
         'of the 80 poses (hands, feet, hip, crown, sole, reach, bar, mouth): look only; lowceil ALL OK; lifttest 0 failures; swingtest ok; stairscan ALL OK; '
         'run2 floors 3 to 6, two seeds, 8/8 passed, no damage; run2 fight floors 6 and 7 passed, no damage; rendersmoke 7 to 9 both modes, no errors '
         '(0.52 ms a frame, 22b 0.54).')


def sections(D, REL, img):
    J = json.load(open(os.path.join(HERE, 'egypt_themes', 'r22c.json')))
    M, A = J['measure'], J['ansur']
    V = ('v69', '22b', 'shorter', 'after', 'longer')
    f2 = lambda x: '%.2f' % x
    rows = [
        ('Chin to acromion top (px)', '2.54 (94 mm at 3.7 cm a px)') + tuple(f2(M[v]['chin_acr']) for v in V),
        ('  / acromion to hip', f2(A['R_neck_trunk'])) + tuple(f2(M[v]['R_neck_trunk']) for v in V),
        ('Chin to pit of the neck (px), as drawn', '2.5 (93 mm)') + tuple(f2(M[v]['chin_notch']) for v in V),
        ('  / pit of the neck to hip', f2(A['R_notch_trunk'])) + tuple(f2(M[v]['R_notch_trunk']) for v in V),
        ('C7 under the chin (px), as drawn', '0.4 (15 mm)') + tuple(f2(M[v]['c7_under_chin']) for v in V),
        ('  / pit of the neck to hip', f2(A['R_c7_trunk'])) + tuple(f2(M[v]['R_c7_trunk']) for v in V),
        ('Nape to C7 (px), back of the neck', '2.3 (about 86 mm, estimate)') + tuple('%.1f' % M[v]['neck_back'] for v in V),
        ('  / pit of the neck to hip', f2(A['R_back_trunk'])) + tuple(f2(M[v]['R_back_trunk']) for v in V),
        ('Neck depth / chest depth (silhouettes)', f2(A['R_neckD_chest'])) + tuple(f2(M[v]['R_neckD_chest']) for v in V),
        ('Neck depth / head height', f2(A['R_neckD_head'])) + tuple(f2(M[v]['R_neckD_head']) for v in V),
        ('Front neck length / neck depth', f2(A['R_len_width'])) + tuple(f2(M[v]['R_len_width']) for v in V),
        ('Acromion to hip / hip to sole (trunk/leg)', f2(A['R_trunk_leg'])) + tuple(f2(M[v]['R_trunk_leg']) for v in V),
        ('Shoulder joint over the hip (px)', '13.3 (acromion less ~40 mm)') + tuple('%.1f' % M[v]['joint'] for v in V),
        ('Height in heads (chin to crown)', '7.7') + tuple('%.2f' % M[v]['heads'] for v in V),
    ]
    b, a = M['22b'], M['after']
    return ['<section class="card" id="r22c"><h2>Round 22c (built in): the neck, measured again</h2>'
            '<p>Owner, after round 22b: "That\'s still off: the neck is too long. It\'s not in harmony with the rest of the body. Double check your '
            'measurements." The rule stays: the figure follows the researched proportions of an athletic youth of 16 to 20.</p>'
            '<h3>Definitions used from now on</h3><ul>'
            '<li><b>Neck length</b>: chin (menton, the head\'s lowest point) to the <b>acromion\'s top</b> (the visible top of the shoulder), in the '
            '<b>body\'s scale</b> (about 3.7 cm a px: the trochanter 900 mm is the hip, 24.3 px over the sole). Not to the shoulder joint.</li>'
            '<li><b>Shoulder joint</b>: the arm\'s pivot (the humeral head\'s centre, the skeleton\'s <code>sh</code>), about 40 mm (1.1 px) under the acromion\'s top.</li>'
            '<li><b>Pit of the neck</b> (suprasternale): where the neck\'s front meets the chest; in ANSUR II level with the acromion (1432 against 1431 mm).</li>'
            '<li><b>C7</b> (cervicale): where the neck\'s back meets the trunk, 15 mm under the chin. <b>Nape</b>: where the skull\'s back curve meets the neck.</li>'
            '<li>As drawn, the pit of the neck and C7 are the lowest rows where the neck\'s own fill shows along the silhouette\'s front and back edge '
            '(drawing the figure with and without it), so they measure the neck as it reads, not as it was meant.</li></ul>' +
            (('<h3>The audit of round 22b</h3><ol>'
            '<li><b>Landmark mix-up: confirmed, but it did not lengthen the front of the neck.</b> 22b took ANSUR\'s chin to acromion (1525 - 1431 = 94 mm, '
            '0.41 of a 228 mm head) and laid it from the chin to the shoulder <i>joint</i>: chin 4.23 px over the joint (13.0 + 4.9 + 4.4 - 1.15 x 4.4 = 17.23). '
            'The drawn deltoid\'s cap rises %.1f px over the joint (the arm\'s root 0.7 px under it, half its 5.2 px width over it), so the drawn chin to acromion '
            'was 17.23 - 14.90 = %.2f px, 0.22 of a head, not 0.41. The guide sheet labelled the joint "acromion".</li>'
            '<li><b>Scale: confirmed as a reasoning error, refuted as the cause.</b> In the head\'s scale (10.4 px for 228 mm, 2.2 cm a px) 94 mm is 4.3 px; in '
            'the body\'s 2.54 px. Because of error 1, the drawn front came out at %.2f px, within 0.2 px of the body\'s scale. The real excess was at the back '
            'and in the drawing: the neck\'s tube ran on 0.65 px under the shoulder joint (1.9 px under the acromion\'s top), and its back edge ran straight '
            'from the skull to the shoulder blades, so C7, as drawn, sat %.1f px under the chin (ANSUR: 15 mm, 0.4 px; ratio to the trunk %.2f against %.3f) '
            'and the back of the neck, nape to C7, was %.1f px (ratio %.2f against about %.2f): two to three times too long. That is the long neck the owner saw.</li>'
            '<li><b>The trunk: refuted.</b> Acromion to hip over hip to sole is %.3f in 22b against ANSUR\'s %.3f (531 / 900 mm); the shoulder joint 13.0 px over '
            'the hip against 13.3 (1431 - 40 - 900 = 491 mm). v69\'s 15 px trunk (%.3f) was the long one. The trunk stays at 13.</li>'
            '<li><b>Neck width: partly.</b> 22b\'s neck was not thin: %.2f of the chest\'s depth (ANSUR %.2f, the neck\'s circumference 381 mm over pi against '
            'a chest 236 mm deep) and %.2f of the head\'s height (%.2f). It read as a long, even column because its lit fill ran from the jaw to the shoulder '
            'joint with nothing to end it.</li>'
            '<li><b>Other games.</b> Round 22b\'s heads-tall and neck values for Abe and the boy of Limbo and Inside were its own estimates, drawn as schematics, not '
            'measured from stills. I could not measure them this round either: downloading images was refused in this session and the web tools here return '
            'text, not pictures. They are not used: the neck follows ANSUR II in the body\'s scale.</li></ol>') % (b['acr_joint'], b['chin_acr'], b['chin_acr'], b['c7_under_chin'], b['R_c7_trunk'], A['R_c7_trunk'], b['neck_back'], b['R_back_trunk'], A['R_back_trunk'], b['R_trunk_leg'], A['R_trunk_leg'], M['v69']['R_trunk_leg'], b['R_neckD_chest'], A['R_neckD_chest'], b['R_neckD_head'], A['R_neckD_head'])) +
            '<h3>ANSUR II</h3><p>The 422 men aged 17 to 20 of the public ANSUR II file (US Army, 2012; Penn State OpenLab), means as round 22b derived them: stature '
            '1753 mm, cervicale 1510, acromion 1431, suprasternale 1432, trochanter 900, neck circumference 381 (base 419), chest depth 236, head length 199, '
            'tragion to the top of the head 132; the chin about 1525 (stature less the head\'s height, about 228). The public file was not downloaded again this '
            'round (refused in this session); its column names and two 19-year-olds\' rows read through the web tool agree (suprasternale within 3 mm of acromion, '
            'cervicale 81 mm over acromion in both). The back of the neck, nape to C7, has no ANSUR landmark: about 86 mm, from the mastoid\'s level about 25 mm '
            'under tragion, an estimate.</p>' +
            table(('Measure', 'ANSUR II, body scale', 'v69', 'Round 22b', 'Shorter (-0.5)', 'After (recommended)', 'Longer (+0.5)'), rows) +
            (('<h3>What changed</h3><ul>'
            '<li>The skeleton is unchanged from 22b (trunk 13, neck 4.9, head 4.4: the crown, height, hands that hold, hit boxes as they were); the head stays the '
            'style\'s size but no longer sets the neck.</li>'
            '<li>The neck is drawn to end where the trunk begins (<code>NJ</code>, <code>NKP</code>): one shape cut along a line tilted from C7 (high, at the back, '
            '%.1f px under the chin) to the pit of the neck (low, in front, level with the acromion\'s top), instead of a tube running down to the shoulder joint. '
            'The trunk\'s outline rises up the back to C7 on the line from the shoulder blades (no shelf and no hump: the silhouette\'s back is one smooth, slightly '
            'concave line from the skull to the blades), and the nape curves in under the skull.</li>'
            '<li>The arm\'s root sits 0.9 px under the joint when the arm hangs (0.7 before; raised arms as before), so the deltoid\'s cap, the acromion\'s top, is '
            '%.2f px under the chin: ANSUR\'s 94 mm in the body\'s scale. The shoulder never rises beside the jaw.</li>'
            '<li>The neck, measured across 0.3 px under the chin (above C7), is %.2f of the chest\'s depth and %.2f of the head\'s height in silhouette (ANSUR 0.51 and 0.53; the drawn chest is as stylised as the head); its throat is set back under the jaw.</li>'
            '<li>Variants: the shorter and longer necks move the pit of the neck, C7 and the deltoid\'s cap 0.5 px up or down together. The shorter one (C7 almost '
            'at the chin, the shoulder 2.0 px under it) starts to crowd the jaw as v69 did; the longer one is 22b\'s front with a short back. The recommended one '
            'matches ANSUR\'s chin to acromion and C7.</li>'
            '<li>Robbers share the outline. Skeleton enemies are unchanged.</li></ul>') % (a['c7_under_chin'], a['chin_acr'], a['R_neckD_chest'], a['R_neckD_head'])) +
            '<p class="meta">Round 22d retired this round\'s four sheets (variants, guide, poses, game): superseded by round 22d\'s comparison with the 1989 kid.</p>'
            '<h3>Tests</h3><p>' + E(TESTS) + '</p>'
            '<p class="meta">Retired to stay at 505 files: round 22b\'s guide, every-pose and game sheets and its moves sheet (superseded by this round\'s four). '
            'Round 22b\'s games schematic stays.</p>' +
            links([('ANSUR II anthropometric survey: the public data (Penn State OpenLab)', 'https://www.openlab.psu.edu/ansur2/'),
                   ('Gordon et al. 2014: 2012 Anthropometric Survey of U.S. Army Personnel, methods and summary statistics (landmark definitions: acromion, cervicale, suprasternale)', 'https://hero.epa.gov/hero/index.cfm/reference/details/reference_id/8211558'),
                   ('D. A. Winter, Biomechanics and Motor Control of Human Movement (segment lengths as fractions of stature)', 'https://onlinelibrary.wiley.com/doi/book/10.1002/9780470549148')]) +
            '</section>']
