# egyptround23c.py: round 23c's section of egypt_themes.html: the owner's pick of the muscle level (1.28) and the neck 2 px shorter.
# Numbers from r23body.json (r23poses.py); picture from egyptr23c.py.
import html, json, os
E = html.escape
HERE = os.path.dirname(os.path.abspath(__file__))


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def table(head, rows):
    return ('<table><tr>' + ''.join('<th>%s</th>' % E(h) for h in head) + '</tr>' +
            ''.join('<tr>' + ''.join('<td>%s</td>' % E(str(c)) for c in r) + '</tr>' for r in rows) + '</table>')


TESTS = ('figscan ok against v69 (held hands, crowns, soles, the swing\'s bar, the drink\'s hand at the mouth); against round 23b at 1.28 the only '
         'differences are the head\'s centre and mouth (2.00 px in every pose), the crown and the head\'s top for figReach (up to 2 px lower), the '
         'drawing\'s reach where the head was the front- or backmost part (wallPress\'s look only), and the drinking hand, which follows the mouth '
         '2 px down: hips, shoulders, feet, every other hand and the blade are unchanged. Standing height 52.5 to 50.5 px. lowceil ALL OK; swingtest '
         'ok (floors 6 to 9); rendersmoke floors 7 to 9 in both modes: no errors.')


def sections(D, REL, img):
    J = json.load(open(os.path.join(HERE, 'r23body.json')))
    B, W = J['body'], J['widths']
    rows = [('MUS, the game\'s muscle level', '1.0 (round 23b drew round 23\'s body)', '1.28 (natural near-limit)'),
            ('shoulder joint to chin', '%.2f px' % W['jc'], '%.2f px' % (W['jc'] - 2.0)),
            ('LEN.nk (skel: the head\'s centre nk + hd from the joint)', '%.3f' % (B['nk'] + 1.0), '%.3f' % (B['nk'] - 1.0)),   # (r23body.json now holds round 23d's neck, 1 px cut)
            ('chin over the pit of the neck', '%.2f px' % W['pit'], '%.2f px' % (W['pit'] - 2.0)),
            ('standing height, sole to crown', '52.5 px', '50.5 px')]
    return ['<section class="card" id="r23c"><h2>Round 23c: MUS 1.28, the neck 2 px shorter</h2>'
            '<p>Owner: "1.28 is fine. Now make the neck 2px shorter and keep everything else as is". The game now draws round 23b\'s last level, '
            '<b>MUS 1.28</b>, with no override (MUS in r23poses.py; the other levels stay in the source for window.__MUS and __HK.setMus). The '
            '<b>neck is 2 px shorter</b>: r23poses.py\'s NECK_CUT takes 2 px off the span from the shoulder joint to the chin (ANSUR\'s 4.0 px, now '
            '2.0), so LEN.nk drops by 2 and the whole head sits 2 px lower on the same body in every pose. Everything under the chin is as it was: '
            'the pit of the neck, C7 and the trapezius slope (NJ\'s body points stay measured from the shoulder joint), every width, bone, pose, grip, '
            'hit box and timer. The low leaps keep their lean (it is measured with round 23\'s neck), so their heads are simply 2 px lower.</p>'
            '<h3>What changed</h3>' + table(('Measure', 'Round 23b (game)', 'Round 23c'), rows) +
            '<h3>What follows the head</h3><ul>'
            '<li>The face, hair, fillet and the robbers\' head cloths and caps: all are drawn about the head\'s centre.</li>'
            '<li>The drink: while he drinks, the flask hand is placed at the mouth (skel\'s mouth term, mh), so the flask comes down 2 px with it.</li>'
            '<li>The neck\'s own top (NJ.hn, NJ.tp) hangs from the head. The nape point (NJ.km) is left where it was: lowered with the chin it would '
            'fall under C7 and fold the neck\'s back edge; where it is, it lies inside the skull. With the head lower, the back of the skull now meets '
            'the trapezius slope just above C7: no gap, no step and no new hump in any pose checked (standing, hanging, reaching, running, crouching, '
            'crawling, drinking, en garde).</li>'
            '<li>Robbers share the skeleton: their necks are 2 px shorter too.</li></ul>' +
            '<p class="meta">Picture: round 23c\'s before/after sheet (r23c_neck.png) is retired; round 23d\'s sheet shows round 23b, round 23c and '
            'round 23d side by side (see <a href="#r23d">round 23d</a>), made by egyptr23c.py\'s successor egyptr23d.py.</p>' +
            '<h3>Tests</h3><p>' + E(TESTS) + '</p>'
            '<p class="meta">Retired to stay at 505 files: round 8\'s prince comparison (r8_prince_compare: v62, round 7 and round 8 side by side), '
            'superseded by rounds 23 to 23c.</p></section>']
