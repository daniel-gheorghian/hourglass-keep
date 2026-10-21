# egyptround23b.py: round 23b's section of egypt_themes.html: the prince's muscle bulk multiplier (a choice for the owner; the game draws 1.0).
# Numbers from r23bulk.json (r23poses.py); pictures from egyptr23b.py.
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


ANS = [('biceps, flexed', 1.049, 1.101, 1.144), ('forearm, flexed', 1.028, 1.066, 1.106), ('chest depth', 1.023, 1.068, 1.114),
       ('deltoid soft tissue (bideltoid less biacromial)', 1.05, 1.13, 1.17), ('thigh at the gluteal fold', 1.023, 1.067, 1.105),
       ('lower thigh (above the knee)', 1.030, 1.063, 1.088), ('calf', 1.035, 1.069, 1.090), ('neck', 1.033, 1.061, 1.087),
       ('buttock depth', 1.031, 1.052, 1.098), ('waist depth', 1.034, 1.036, 1.063), ('wrist (bone)', 1.021, 1.034, 1.055)]
NAMES = {'arm': 'upper arm (biceps)', 'fore': 'forearm', 'delt': 'deltoid (profile)', 'armLo': 'above the elbow (brachialis, triceps)', 'thigh': 'thigh',
         'thighM': 'mid-thigh', 'lthigh': 'above the knee (vastus medialis)', 'calf': 'calf (gastrocnemius, laid behind the shank)', 'soleus': 'lower calf (soleus)',
         'neck': 'neck', 'neckB': 'neck at its base', 'trap': 'trapezius slope', 'chest': 'chest depth (pectorals in front, lats behind)',
         'lowch': 'lower ribs (lats)', 'seat': 'seat depth (glutes, behind)', 'waist': 'waist depth (held: no fat)'}
TESTS = ('Round 23\'s look is unchanged at 1.0: the drawing of eight poses, prince and robber, is pixel for pixel round 23\'s (R23D is the same table). '
         'At 1.0: figscan ok, lowceil ALL OK, swingtest ok (floors 6 to 9), rendersmoke floors 7 to 9 both modes no errors (0.55 ms a frame). '
         'At the bulkiest level (window.__MUS=1.28 before load): figscan ok (held hands, crown, soles and reach as before: only the drawing\'s widths '
         'change), lowceil ALL OK.')


def sections(D, REL, img):
    J = json.load(open(os.path.join(HERE, 'r23bulk.json')))
    L = J['levels']
    fac = [(NAMES.get(k, k), '%.2f' % g) + tuple('x%.2f' % q['factors'][k] for q in L[1:]) for k, g in J['grow'].items()]
    lv = [('%g' % q['m'], q['basis']) for q in L]
    return ['<section class="card" id="r23b"><h2>Round 23b (a choice): how muscular the prince is</h2>'
            '<p>Owner: "Yeah needs to be bulkier. Add a bulk multiplier, but in the sense of more muscle. Give me three variants of him with the current '
            'size then more and more bulky". <b>One multiplier, MUS</b>: the upper arm\'s girth over round 23\'s (ANSUR II\'s median). Every other measure '
            'grows at its own researched rate per unit of the upper arm\'s; the joints (elbow, wrist, knee, ankle), the bones, the skeleton, every pose, the '
            'held hands, hit boxes and timing do not change. The waist barely grows, so the V from the lats and shoulders to the waist sharpens: muscle, not '
            'fat. <b>The game still draws 1.0</b> (round 23); the four levels are below for the owner to pick. Picking one is one line: MUS in '
            'r23poses.py, then run it.</p>'
            '<h3>The levels</h3>' + table(('MUS', 'Basis'), lv) +
            fig(img, 'r23b_bulk.png', 'The four levels: standing at 10x; at 1x, 2x and 3x beside a robber of the same level; run, reach, hang, en garde and '
                'crouch at 4x; the table of widths as drawn (px, cm, and the factor on round 23)') +
            fig(img, 'r23b_game.png', 'Each level in the game (rows: 1.0, 1.10, 1.18, 1.28): standing and running in Torchlight at GLP.rs 1 and 0.5 and in '
                'Classic, and in a fight beside a robber') +
            '<h3>Research</h3><ul>'
            '<li><b>ANSUR II</b> (US Army, 2012; our copy): men aged 17 to 20 whose waist is under the median share of their chest (the lean half, n=211), '
            'ranked by their limb and chest girths for stature; the 97th to the 50th percentile group: biceps x1.17, chest depth x1.16, thigh x1.15, '
            'buttock depth x1.14, forearm x1.12, calf x1.11, neck x1.08. A second cut (men 17 to 24, lean by waist over stature, n=679, by a research '
            'agent) agrees (table below) and shows the frame grows too (wrist +5.5%): half of that is taken off the limbs, since our joints stay. The '
            'waist rises in the data with the body fat of the heaviest; it is held here (x1.03 at most, the abdominal wall and obliques).</li>'
            '<li><b>Where muscle grows first</b>: 12 weeks of training thickened the upper body\'s muscles 12 to 21% against 7 to 9% in the thigh (Abe et '
            'al. 2000); sprinters carry larger hip extensors and glutes, most of all the lower gluteus maximus, and the back of the thigh, while the '
            'muscles acting only on the knee are similar: so the seat and the hamstrings deepen more than the knee.</li>'
            '<li><b>Ceilings</b>: drug-free athletes top out near a fat-free mass index of 25 (Kouri et al. 1995); McCallum\'s ratios on ANSUR\'s wrist give '
            'arm x1.21, chest x1.15, neck x1.09 and a waist of 0.96; Steve Reeves\'s, scaled to ANSUR at his height, arm x1.31, chest x1.29, neck x1.15, '
            'waist 0.85. The last level, 1.28, sits between them. Heath-Carter mesomorphy (0.858 humerus + 0.601 femur breadth + 0.188 corrected arm + '
            '0.161 corrected calf - 0.131 height + 4.5): elite gymnasts about 6.3 against about 4 for an untrained young man; each cm of arm adds 0.19.</li>'
            '<li><b>Drawing it at 52 px</b> (Proko on the deltoid and the calf; small-sprite practice; figure drawing\'s form shading): muscle shows in the '
            'silhouette and in one or two value breaks, not in drawn lines. The deltoid\'s cap tapers to a V into the arm at its insertion, a little above '
            'half way down the humerus; the gastrocnemius is one round bump high on the back of the shank with the shin straight in front; the lats swell '
            'the back line under the armpit, then cut in to the waist; the pectoral\'s lower edge is a short firm line; the trapezius steepens the slope '
            'from the neck. Fat is soft and low (belly, flanks) and fills the narrow points; muscle swells between joints, so the knees, wrists, ankles, '
            'elbows and waist stay narrow.</li></ul>'
            '<h3>How it is drawn</h3><ul>'
            '<li>The widths: each tube\'s six or seven points (deltoid, biceps, above the elbow, elbow, forearm, wrist; thigh, mid-thigh, above the knee, '
            'knee, calf, lower calf, ankle) grow by their own factor; joints none. The calf\'s growth is laid behind the shank (the shin\'s line stays). '
            'The trunk\'s nine levels from the hip to the shoulder grow by the measure at that level, laid in front or behind by where the muscle is '
            '(glutes 80 to 85% behind; the lats 70% behind at the lower ribs; the chest about half and half; the trapezius behind, and up the slope from C7).</li>'
            '<li>Two faint contours in the part\'s own shade, only above 1.0 and growing with the level (none in round 23\'s look): the deltoid\'s V into '
            'the upper arm and the pectoral\'s short lower border (fading as the arms rise). Smooth vector strokes in the figure\'s own drawing, so they '
            'read the same in Classic and Torchlight at any scale; nothing new a frame but two strokes.</li>'
            '<li>The robbers keep their own 1.15 times the prince\'s breadth on top of the level, so they stay broader at every level.</li>'
            '<li>Run time: the source carries all four tables (R23MUS, R23DV); window.__MUS set before load, or __HK.setMus(m), draws the nearest level '
            '(for pictures and tests); the game draws R23D.</li></ul>'
            '<h3>Growth rates and the factors at each level</h3>' + table(('Measure', 'Rate (per unit of the upper arm)') + tuple('MUS %g' % q['m'] for q in L[1:]), fac) +
            '<h3>ANSUR II, the lean young men by muscle (17 to 24, frame not taken out)</h3>' +
            table(('Measure', '70-80th', '85-95th', '95-100th percentile'), [(a, 'x%.3f' % b, 'x%.3f' % c, 'x%.3f' % d) for a, b, c, d in ANS]) +
            '<h3>Tests</h3><p>' + E(TESTS) + '</p>'
            '<p class="meta">Retired to stay at 505 files: round 8\'s athletic before/after pair (r8_muscle_before, r8_muscle_after), superseded by round 23 '
            'and this round.</p>' +
            links([('ANSUR II (calmcode.io dataset page)', 'https://calmcode.io/datasets/ansur'),
                   ('Heath-Carter somatotype method (formulae)', 'https://ebooks.inflibnet.ac.in/antp06/chapter/heath-carter-methods-of-somatotyping/'),
                   ('Somatotypes of athletes (Topend Sports)', 'https://www.topendsports.com/testing/somatotype.htm'),
                   ('Elite Italian male gymnasts\' somatotype', 'https://iris.unica.it/handle/11584/105089'),
                   ('Sprinters\' girths and somatotype (Croatia)', 'https://sponet.de/sponet/Record/4015190'),
                   ('Abe et al. 2000: time course of muscle thickness gains, upper vs lower body', 'https://dx.doi.org/10.1007/s004210050027'),
                   ('Sprinters\' muscle volumes by MRI', 'https://lida.sport-iat.de/dlv/Record/4050802'),
                   ('Gluteus and posterior thigh sizes in sprinters', 'https://www.naseinc.com/blog/gluteus-and-posterior-thigh-muscle-sizes-in-sprinters/'),
                   ('Kouri et al. 1995, FFMI of drug-free athletes (review, Helms)', 'https://www.alanaragon.com/wp-content/uploads/2016/08/Helms-Aug-2014-AARR.pdf'),
                   ('FFMI calculator and the natural limit', 'https://dqydj.com/ffmi-calculator/'),
                   ('Casey Butt\'s lean mass formula', 'https://weighttraining.nz/cb_calculator.php'),
                   ('McCallum\'s and Reeves\'s proportions', 'https://protealpes.com/en/outils/mensuration-musculation/'),
                   ('Proko: the deltoid', 'https://proko.com/@pepijn'),
                   ('Proko: drawing the calf', 'https://proko.com/course-lesson/how-to-draw-the-calf-anatomy-for-artists/notes'),
                   ('Proko: shading, light and form', 'https://www.proko.com/lesson/shading-light-and-form-basics'),
                   ('Small sprites: silhouette and value', 'https://www.wayline.io/learn/pixel-art/4'),
                   ('Prince of Persia (1989): rotoscoped from David Mechner', 'https://en.wikipedia.org/wiki/Prince_of_Persia_(1989_video_game)')]) +
            '</section>']
