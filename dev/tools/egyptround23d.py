# egyptround23d.py: round 23d's section of egypt_themes.html: the neck 1 px longer than round 23c (owner: "Too short, one pixel longer").
# Numbers from r23body.json (r23poses.py); picture from egyptr23d.py.
import html, json, os
E = html.escape
HERE = os.path.dirname(os.path.abspath(__file__))


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def table(head, rows):
    return ('<table><tr>' + ''.join('<th>%s</th>' % E(h) for h in head) + '</tr>' +
            ''.join('<tr>' + ''.join('<td>%s</td>' % E(str(c)) for c in r) + '</tr>' for r in rows) + '</table>')


TESTS = ('figscan ok against v69 (held hands, crowns, soles, the swing\'s bar, the drink\'s hand at the mouth; standing height 53.00 to 51.50 px); '
         'lowceil ALL OK; swingtest ok (floors 6 to 9); rendersmoke floors 7 to 9 in both modes: no errors.')


def sections(D, REL, img):
    J = json.load(open(os.path.join(HERE, 'r23body.json')))
    B, W = J['body'], J['widths']
    rows = [('shoulder joint to chin', '%.2f px' % W['jc'], '%.2f px' % (W['jc'] - 2.0), '%.2f px' % W['jcH']),
            ('LEN.nk (skel: the head\'s centre nk + hd from the joint)', '%.3f' % (B['nk'] + 1.0), '%.3f' % (B['nk'] - 1.0), '%.3f' % B['nk']),
            ('the nape point NJ.km, along the neck\'s axis from the joint', '4.61', '4.61', '4.11'),
            ('C7, along the same axis', '3.46', '3.46', '3.46'),
            ('standing height, sole to crown', '52.5 px', '50.5 px', '51.5 px')]
    return ['<section class="card" id="r23d"><h2>Round 23d: the neck one pixel longer</h2>'
            '<p>Owner, after round 23c: "Too short, one pixel longer". r23poses.py\'s <b>NECK_CUT is 1.0</b> (round 23c: 2.0): the span from the '
            'shoulder joint to the chin is ANSUR\'s 4.0 px less 1, so LEN.nk is 3.518 and the head sits 1 px higher than in round 23c, 1 px lower than '
            'round 23b, in every pose. As in round 23c everything under the chin is unchanged (the pit of the neck, C7, the trapezius slope, every '
            'width, bone, pose, grip, hit box and timer; MUS stays 1.28), and the face, hair, fillet, robbers\' head cloths, the neck\'s top and the '
            'drinking hand follow the head.</p>'
            '<h3>The back of the neck</h3><p>Round 23c left the nape point (NJ.km) where it was, 2.6 px over the chin, inside the skull, so the '
            'skull\'s back met the trapezius just above C7. With the chin 1 px higher a little of the neck\'s back shows again under the skull, so '
            'the nape now comes down half the cut (KM_DROP 0.5 px: 4.61 to 4.11 along the neck\'s axis), halfway between its round 23c place and '
            'round 23b\'s place relative to the chin (0.6 px over the chin, which would now be 3.61). Taken all the way it would sit 0.15 px over C7 '
            '(3.46) and the back edge would fold; at 4.11 the line runs from the skull down the back of the neck into the trapezius slope with no '
            'gap, overlap or hump in any pose checked (standing, hanging, reaching, running, crouching, crawling, drinking, en garde, the robber). '
            'The difference is under a pixel at 1x: a few pixels at 10x along the nape.</p>'
            '<h3>What changed</h3>' + table(('Measure', 'Round 23b', 'Round 23c', 'Round 23d (game)'), rows) +
            fig(img, 'r23d_neck.png', 'Round 23b (ANSUR\'s neck) | round 23c (2 px shorter) | round 23d (1 px shorter), all at MUS 1.28: standing at 10x '
                'with the chin (red; the other rounds\' chins dashed) and the shoulder joint (blue); stand, hang, reach, run, crouch, crawl, drink, en '
                'garde and a robber at 4x; standing at 1x and 3x beside a robber; in the game at the phone\'s resolution, Torchlight and Classic, '
                'standing and running') +
            '<h3>Tests</h3><p>' + E(TESTS) + '</p></section>']
