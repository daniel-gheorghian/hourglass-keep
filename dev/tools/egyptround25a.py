# egyptround25a.py: round 25a's section of egypt_themes.html: a supple run (owner: "The prince is somewhat stiff when running. Humans are
# somewhat flexible. Research a bit how games are handling that in their characters."). Numbers from egypt_themes/r25a.json (egyptr25a.py
# measure); pictures from egyptr25a.py.
import html, json, os
E = html.escape
HERE = os.path.dirname(os.path.abspath(__file__))


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def table(head, rows):
    return ('<table><tr>' + ''.join('<th>%s</th>' % E(h) for h in head) + '</tr>' +
            ''.join('<tr>' + ''.join('<td>%s</td>' % E(str(c)) for c in r) + '</tr>' for r in rows) + '</table>')


def links(L):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(t)) for t, u in L) + '</ul>'


SOURCES = [
    ('Animation Obsessive: how the little guy moved (Prince of Persia 1989: David Mechner filmed running and jumping, every third frame traced, '
     'stylised, played at about 15 fps)', 'https://animationobsessive.substack.com/p/how-the-little-guy-moved'),
    ('Game Anim: Mechner\'s 1986 journal on rotoscoping ("the key is not to clean up the frames too much")', 'https://www.gameanim.com/?p=5826'),
    ('Game Developer: Art Design Deep Dive: using a 3D pipeline for 2D animation in Dead Cells (Thomas Vasseur; characters about 50 px tall, '
     'key poses with interpolation in between)', 'https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i-'),
    ('GDC Vault: David Rosen, Animation Bootcamp: An Indie Approach to Procedural Animation (Overgrowth, GDC 2014: very few keyframes plus '
     'procedural layers)', 'https://www.gdcvault.com/play/1020583/Animation-Bootcamp-An-Indie-Approach'),
    ('GDC Vault: Simon Clavet, Motion Matching and The Road to Next-Gen Animation (For Honor, GDC 2016: whole poses picked from long capture, '
     'no rigid cycle)', 'https://www.gdcvault.com/play/1023280/Motion-Matching-and-The-Road'),
    ('Ori (Moon Studios): Thomas Mahler on why Ori is hand-animated, not captured', 'https://www.orithegame.com/gamesradar-moon-studios-thomas-mahler-on-the-art-science-and-magic-behind-ori-and-the-will-of-the-wisps'),
    ('Wikipedia: Another World (Chahi rotoscoped to plan the movement, polygons for the art)', 'https://en.wikipedia.org/wiki/Another_World_(video_game)'),
    ('Schache et al. 2002, three-dimensional angular kinematics of the lumbar spine and pelvis during running (Human Movement Science)',
     'https://findanexpert.unimelb.edu.au/scholarlywork/252200-three-dimensional-angular-kinematics-of-the-lumbar-spine-and-pelvis-during-running'),
    ('van Dieen et al. 2021, coordination of axial trunk rotations during gait (thorax and pelvis turn toward anti-phase as speed rises)', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC7877281'),
    ('Pozzo, Berthoz, Lefort 1990, head stabilization during various locomotor tasks in humans (Exp Brain Res)', 'https://pubmed.ncbi.nlm.nih.gov/2257917/'),
    ('Novacheck 1998, the biomechanics of running (Gait & Posture)', 'https://pubmed.ncbi.nlm.nih.gov/10200378/'),
    ('CMU Graphics Lab Motion Capture Database (clips 09_01-09_03, 16_35, 16_36, 16_15)', 'http://mocap.cs.cmu.edu')]

TESTS = ('figscan ok against v69 (crowns: the run\'s highest crown is unchanged, toe-off 1.8 px higher than v71 and still under v69\'s standing '
         'crown; against v71 only the run and walk differ); lowceil ALL OK; stairscan ALL OK (96 footfalls on the treads); run2 floors 3 to 6, two '
         'seeds: 8 of 8 passed, 0 runs with damage (0.03 ms/frame); rendersmoke floors 7 to 9 in both modes: no errors (0.56 ms/frame).')


def sections(D, REL, img):
    J = json.load(open(os.path.join(HERE, 'egypt_themes', 'r25a.json')))
    clips = ['09_01', '09_02', '09_03', '16_35', '16_36']
    rows = []
    for k, lab, use in J['rows']:
        rows.append([lab] + ['%.1f to %.1f' % (J[c]['stats'][k]['min'], J[c]['stats'][k]['max']) for c in clips] + [use])
    N = J['new']
    return ['<section class="card" id="r25a"><h2>Round 25a: a supple run</h2>'
            '<p>Owner: "The prince is somewhat stiff when running. Humans are somewhat flexible. Research a bit how games are handling that in their '
            'characters." Since round 23 the run is CMU clip 09_01, 16 keys a stride. The motion was real, but the side view kept only ten angles of it: '
            'the trunk as one straight line from the hips to the shoulders, both arms hung from one point that moved only with the arm\'s own swing, '
            'and feet drawn flat whatever the leg did. This round measures what the clip carries beyond those ten angles and draws the part that '
            'shows at 50 px.</p>'
            '<h3>Research: how games make a run read as flexible</h3><ul>'
            '<li><b>Rotoscoping (Prince of Persia 1989, Another World, Flashback).</b> Mechner traced his brother running on video, every third frame, '
            'and played it at about 15 fps. He wrote that the key was not to clean the frames up too much: the weight shifts and lean of a real body '
            'are what read as alive in a small sprite. Our run already comes from capture, so the stiffness here is what the projection threw '
            'away, not the motion itself.</li>'
            '<li><b>Capture or 3D, posed in 2D (Dead Cells, Ori).</b> Dead Cells animates a 3D skeleton and renders it at about 50 px, our size. '
            'The animators key poses and let the interpolation fill in the frames between, and the whole body moves in every frame. Moon Studios '
            'hand-animates Ori because raw capture looked "stilted and wooden" to them. Both point the same way: every segment needs its own '
            'timing, not one rigid block.</li>'
            '<li><b>Procedural layers (Overgrowth; Naughty Dog\'s additive layers; motion matching).</b> Rosen\'s GDC 2014 talk builds fluid '
            'motion from very few keyframes plus layers computed from the movement. Ubisoft\'s motion matching (Clavet, GDC 2016) picks whole '
            'captured poses rather than blending a few joints. For us, a layer must be a pure function of the run\'s phase: rewind-safe, no '
            'state.</li>'
            '<li><b>The animation principles for a run</b> (Williams, The Animator\'s Survival Kit; Thomas and Johnston, The Illusion of Life): '
            'overlapping action and follow-through (cloth and hair trail what moves them), arcs, contact and push-off (heel to toe), the shoulders '
            'counter-rotating against the hips, a spine that bends rather than a rigid trunk, a steady head.</li>'
            '<li><b>Biomechanics.</b> In running the thorax turns against the pelvis, more as speed rises (Schache 2002; van Dieen 2021). The trunk '
            'flexes and extends twice a stride. The head is held steadier than the chest (Pozzo 1990). The ankle plantarflexes through push-off and '
            'hangs plantarflexed under the folded leg in the swing (Novacheck 1998).</li></ul>' + links(SOURCES) +
            '<h3>Measured: what the clips carry (one stride each; px at the game\'s scale)</h3>' +
            table(['measure'] + clips + ['round 25a'], rows) +
            '<p>Before this round the game drew the trunk as one line (no bend between chest and pelvis). The shoulders moved only by the drawing\'s '
            '0.9 sin(upper arm), %.2f to %.2f px and never forward, where the clip has %.2f to %.2f. The feet stayed flat while the clip\'s foot runs from '
            'about 6 degrees toes-up at heel strike to 114 toes-down in the swing (09_01, from its foot-flat angle). The counter-rotation, 19 to 27 degrees peak to peak in all five clips, '
            'shows in profile as the near and far shoulder joints moving opposite ways. The hip joints\' own shift (0.3 px or less), the pelvis\'s '
            'drop (0.5 px, under the kilt) and the wrist (7 to 15 degrees, steady) are too small to show at 1x and are left out. The head is '
            'already the clip\'s, and steadier than the chest.</p>'
            % (J['v71']['shoulder'][0], J['v71']['shoulder'][1], N['soF'][0], N['soF'][1]) +
            '<h3>What changed</h3><ul>'
            '<li>r23poses.py (extras) adds five measured values to each run and walk key, so they come from the clip, not invented: <b>sb</b>, '
            'the chest\'s pitch over the pelvis\'s, %.0f to %.0f degrees (the chest nods forward as each foot takes the weight); <b>soF/soB</b>, '
            'each shoulder joint fore and aft, %.2f to %.2f px; <b>fpF/fpB</b>, the foot\'s pitch from flat, %.0f to %.0f degrees (flat is the '
            'clip\'s own foot-flat angle at mid-stance, -21 degrees); and <b>sm</b> = 1.</li>'
            '<li>The trunk bends: the spine\'s curve in drawFigureHD0 gets -LEN.to/2 tan(sb/2), so the tangents at the pelvis and the chest '
            'differ by sb. The chord (lean), the shoulder joint and the head stay as before.</li>'
            '<li>The shoulder girdle: each arm is drawn from its own shoulder joint, moved soF/soB along the trunk\'s normal with the elbow and '
            'hand. Where sm is 1, the drawing\'s own swing-driven shift fades out, so the clip\'s values are not counted twice.</li>'
            '<li>Foot roll: the foot turns by fp about the ankle joint, R23B.ah = 1.95 px up the shank (ANSUR\'s malleolus). The run\'s hip height '
            'comes from the turned foot\'s lowest point (footLow) plus the clip\'s clearance. The hip now rises onto the ball at toe-off, as in the '
            'clip, where v71\'s flat foot made it dip 1.8 px. At heel strike and mid-stance the sole is on the floor as before.</li>'
            '<li>Follow-through: the kilt\'s hem is laid on the thighs as they were 0.035 of a stride earlier, 0.8 of the way (KH_LAG, KH_K in '
            'runPoseHD). This is a pure function of the phase: no state, rewind-safe, and nothing allocated per frame.</li>'
            '<li>The walk (the exit) takes the same values from 16_15. On the stairs (part stride) the feet stay flat, so stairscan is unchanged. '
            'The push and pull of blocks use the run at 40 to 45%% with flat feet. Every other pose has 0 for all of these and is unchanged. '
            'Robbers never run and are unchanged. Timing, footfalls, hit boxes, wall hiding and lift occlusion are unchanged.</li></ul>'
            % (N['sb'][0] * 57.3, N['sb'][1] * 57.3, N['soF'][0], N['soF'][1], N['fpF'][1] * 57.3, N['fpF'][0] * 57.3) +
            fig(img, 'r25a_run.png', 'The 16 run keys at 4x: v71 | round 25a | the clip\'s stick figure at the same phases. Pelvis line (green), '
                'chest line (orange) and shoulder joints (near red, far blue) on keys 0, 4, 8, 12') +
            fig(img, 'r25a_run.gif', 'Running in the game at the phone\'s resolution, v71 | round 25a, Torchlight and Classic; every game frame at '
                '40 ms (0.4 times speed)') +
            '<h3>Tests</h3><p>' + E(TESTS) + '</p>'
            '<p class="meta">Retired to keep the page at 505 pictures: round 8\'s r8_prince_hair.png and r8_prince_run.gif.</p></section>']
