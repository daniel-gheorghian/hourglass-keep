# egyptround25f.py: round 25f's section of egypt_themes.html: every move audited for stiffness (owner: "I ment a stiff prince in the broader
# sense: check all his movements for stiffness and make adjustments based on research"). Pictures from egyptr25f.py.
import html
E = html.escape


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def table(head, rows):
    return ('<table><tr>' + ''.join('<th>%s</th>' % E(h) for h in head) + '</tr>' +
            ''.join('<tr>' + ''.join('<td>%s</td>' % E(str(c)) for c in r) + '</tr>' for r in rows) + '</table>')


def links(L):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(t)) for t, u in L) + '</ul>'


SOURCES = [
    ('Twelve basic principles of animation (Thomas and Johnston, The Illusion of Life, 1981): anticipation; follow-through and overlapping '
     'action ("parts of the body move at different rates"; drag); slow in and out; arcs; secondary action; the moving hold', 'https://en.wikipedia.org/wiki/Twelve_basic_principles_of_animation'),
    ('Jonathan Cooper, Game Anim (excerpt): the principles in games: body parts that start and stop together show the keys; follow-through '
     '(recovery after a jump, cloth and hair) carries the weight, as a long anticipation costs responsiveness; not everything needs slow in and out',
     'https://gamedeveloper.com/production/the-12-principles-of-animation-in-video-games'),
    ('David Rosen, An Indie Approach to Procedural Animation (GDC 2014, Overgrowth): very few keys, procedural layers between them',
     'https://gamedeveloper.com/design/video-an-indie-approach-to-procedural-animation'),
    ('Travis McIntosh, Animation and Player Control in Uncharted (GDC 2010): partial and additive animations, layering',
     'https://gdcvault.com/play/1012300/Animation-and-Player-Control-in'),
    ('Thomas Vasseur, Dead Cells: a 3D pipeline for 2D animation: figures about 50 px tall, pose to pose, impact carried by effects',
     'https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i-'),
    ('Ori and the Will of the Wisps (Rock Paper Shotgun): squash and stretch for punch; ears and tail follow through from the body\'s momentum',
     'https://www.orithegame.com/rockpapershotgun-how-animation-powers-ori-and-the-will-of-the-wisps/'),
    ('Prince of Persia (1989): rotoscoped from video of David Mechner running and jumping', 'https://en.wikipedia.org/wiki/Prince_of_Persia_(1989_video_game)'),
    ('Ubisoft, Prince of Persia 35th anniversary: "an endearing awkwardness to the way that he moved"',
     'https://news.ubisoft.com/en-us/article/6yLrRf7b0U1MBYxmlxE225/prince-of-persia-35th-anniversary-a-look-back-at-the-original-game'),
    ('Allen Chou, precise control over numeric springing (frequency and damping for secondary motion)', 'https://allenchou.net/2015/04/game-math-precise-control-over-numeric-springing/'),
    ('Daniel Holden, spring roll call (critically damped springs; inertialization: decay the offset at a transition)', 'https://theorangeduck.com/page/spring-roll-call'),
    ('DeVita and Skelly 1992, landing stiffness and joint kinetics (MSSE 24:108): soft landings 117 deg of knee flexion against 77 stiff; the hip and '
     'knee take the energy (abstract)', 'https://pubmed.ncbi.nlm.nih.gov/1548984/'),
    ('Landing from 22 and 44 cm (Sports Med Open 2016): peak knee flexion 45 to 88 deg by technique; the knee\'s load peaks ~0.07 s after contact',
     'https://pmc.ncbi.nlm.nih.gov/articles/PMC5243232/'),
    ('Hodges et al. 2002, postural activity with breathing (Exp Brain Res 144:293): ~0.5 deg trunk and leg movement with each breath in quiet stance (abstract)',
     'https://doi.org/10.1007/s00221-002-1040-x'),
    ('Yamamoto et al. 2015: quiet standing sway, median frequency 0.32-0.33 Hz', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC4393163/'),
    ('American Lung Association: 12 to 20 breaths a minute at rest', 'https://www.lung.org/blog/respiratory-rate-vital-signs'),
    ('Pendulum (mechanics): a uniform rod hung from its end swings with T = 2 pi sqrt(2 l / 3 g)', 'https://en.wikipedia.org/wiki/Pendulum_(mechanics)'),
    ('Scapular motion in pull-ups (11 men, Vicon): 10 to 22 deg of retraction, ~10 deg of upward rotation', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC4916995/'),
    ('CMU Graphics Lab Motion Capture Database (16_05 broad jump, 16_08 sudden stop, 13_11 forward jump, 79_38 standing, 111_03 crawling)', 'http://mocap.cs.cmu.edu')]

# the audit: move, what the side view drops against the clip (a), where it is rigid between keys (b), what should trail (c), the fix
AUDIT = [
    ['stand, idle', '79_38 f30: the actor stands nearly still (under 0.3 deg in 90 frames): no idle to measure', 'breathing on one sine: chest, arms and head together', 'arms, head', 'breathing in overlap (arms 0.5 rad, head 0.3 rad behind the chest; the spine bends with it) and a slow weight shift (0.05-0.08 Hz), the head kept steady'],
    ['turn', 'no clip turns on the spot in profile', 'facing flips; PS.turn eased at one rate; nothing trails', 'arms, hair, kilt', 'turnSettle: the arms trail from the old side and swing through (1.4 Hz, half-life 0.12 s), forearms drag, the knees dip once in 0.32 s; the cloth and hair swing across'],
    ['step, edge walk', '139_29', 'a sine blend stand-step', 'arms', 'overlap only'],
    ['skid, stop', '16_08: braking for 0.3 s, forearms swing on 0.5 s more', 'one frame (f114) held, then up in 0.1 s', 'forearms, rear leg', 'the stop settle from 16_08: 0.9 s, elbows +38 / -40 deg of follow-through, the rear thigh coming forward'],
    ['crouch (Down)', 'the crawl\'s keys', 'a clip cycle', '-', 'unchanged'],
    ['land (soft)', '16_05: deepest 0.13 s after touchdown, standing by 0.5 s', 'PS.land held 0.08-0.2 s, then up in 0.1 s; a whole-figure squash 0.87', 'head, trunk, knees', 'the land settle from 16_05 by the landing\'s speed (0.3 to 1); the legs reach for the floor at touchdown, the head nods; the squash 0.96'],
    ['land (hurt)', '-', 'the crouch 0.6 s, squash 0.80, then up in 0.1 s', 'trunk', 'the squash 0.92; standing up continues the land settle from its deepest frame'],
    ['jumpPrep (the crouch before a standing jump)', '16_05 f110: elbows bent by the sides', 'arms do not swing back before swinging forward', 'arms', 'its own pose, jumpCrouch, 13_11 f196: both arms back (-43 / -46 deg), knees 74 deg; jumpUp, bonk, landHurt and the climb\'s end keep the crouch'],
    ['jumpS, jumpLowS, jumpR, jumpLow', 'the clips\' flight frames', 'the pose eased at one rate', 'legs, arms, head', 'overlap: in the air the legs trail the body too'],
    ['kick shaft (push, tuck, reach, plant), wall run', 'derived; two-bone IK on the wall', 'blends of IK poses', '-', 'unchanged (feet on the wall: no lag)'],
    ['reach, jumpUp', '14_07', 'crouch then reach, one rate', 'legs', 'overlap, the legs trail'],
    ['hang', '01_03: a frozen shape', 'one pose for as long as he hangs', 'the whole body, legs', 'a pendulum swing about the hands (T 1.6 s with the game\'s gravity, settles in ~2 swings), the legs trailing; its size by how he came to hang'],
    ['pull, press, kneelUp, kneel (climb)', '01_09, 81_14', 'keys eased (slow in and out already)', '-', 'unchanged; the hang\'s swing fades over its first 0.18 s'],
    ['slide', '01_09', 'a procedural shudder', '-', 'unchanged'],
    ['fall', '90_16 f356', 'one frame for the whole fall', 'arms, legs', 'the limbs move a little against each other after 0.15 s'],
    ['dead', '90_16 f600', 'the collapse eased at one rate', 'arms, head', 'overlap: the arms and head settle after the trunk'],
    ['garde, windup, lunge, parry, lowStrike, hurt', '02_07, 02_08, 16_08', 'every part switching at once (rates 30-55)', 'the free arm, head', 'overlap: the free arm and the head trail; the sword hand stays on its grip at the full rate'],
    ['swing', '43_02 by phase', 'physics', '-', 'unchanged'],
    ['drink', '79_38, 81_14', '11 keys eased', '-', 'unchanged'],
    ['crawl', '111_03; 25b turned the head up', 'the face 20 deg under the horizontal', '-', 'the neck line 0.64 rad, the skull -0.52 at the atlas: the face 7 deg under the horizontal, looking along the tunnel'],
    ['run start', '09_01', 'the full stride from the first frame', 'trunk', 'he leans into the start, +0.12 rad fading as he reaches speed'],
    ['run, walk, exit stairs', '09_01, 16_15 (round 25a: spine, shoulders, foot roll)', 'a clip cycle', 'kilt (25a)', 'unchanged'],
    ['the kilt outside the run', '-', 'the hem fixed to the thighs', 'kilt', 'a stiff spring (22 rad/s, damping 0.55) lets the hem trail the thighs'],
]

VALUES = [
    ['followPose', 'upper arms 0.7, forearms 0.55, head 0.75 of the state\'s rate; in the air legs 0.75 (thighs), 0.7 (knees)', 'held poses and short transitions only (LAGM); the clip cycles as before'],
    ['MCK.set_land', '16_05 f187-270 (peak f203), keys every 1/30 s', 'arms follow the blend (round 25b dropped 16_05\'s arm action)'],
    ['MCK.set_stop', '16_08 f112-222 (peak f114)', 'strength |vx|/RUN, 0.35 to 1'],
    ['land strength', '(impact speed - 60) / 240, 0.3 to 1', 'standing jump 0.41, running 0.54, one storey 1'],
    ['turnSettle', 'arms -0.32 / -0.28 rad x e^(-t/0.18) cos(9t); forearms +0.25 / +0.2; knees +0.2, hips +0.1 over 0.32 s', '0.7 s from the flip'],
    ['hang', 'HG_A jumpUp 0.045, from the air 0.075, climbDown 0.1 rad; HG_W 3.9 rad/s; HG_TAU 0.75 s; legs HG_LAG 0.09 s', 'about the hands: the grips do not move'],
    ['breathing', '0.37 Hz; lean 0.02, spine 0.015, arms 0.035 / 0.03 (0.5 rad late), head 0.018 (0.3 rad late); weight shift 0.012 rad', 'stand, garde, drink'],
    ['crawl', 'CRAWL_NECK 0.64 (25b 0.80), CRAWL_HP -0.52 (25b -0.45)', 'the face 7 deg under the horizontal (25b 20)'],
    ['squash', 'land 0.96 (0.87), landHurt 0.92 (0.80), take-off kick 1.3 (2.6)', 'the knees carry the landing now'],
]

TESTS = ('figscan ok against v69 (the crawl\'s crown 3.4 to 4.5 px under v69\'s crawl crown); lowceil ALL OK; primtest FAILURES 0; swingtest ok '
         '(6-9); lifttest FAILURES 0; stairscan ALL OK; run2 floors 3 to 6, two seeds: 8 of 8, 0 runs with damage (0.04 ms/frame); run2 floors 6 to 7 '
         'fighting: 2 of 2 (0.06 ms/frame); rendersmoke floors 7 to 9, both modes: no errors (0.62 ms/frame).')


def sections(D, REL, img):
    return ['<section class="card" id="r25f"><h2>Round 25f: no stiff moves</h2>'
            '<p>Owner: "I ment a stiff prince in the broader sense: check all his movements for stiffness and make adjustments based on research." '
            '(Round 25a had loosened the run.)</p>'
            '<h3>What made him stiff</h3><ul>'
            '<li><b>Lockstep.</b> The game eased every part of him toward the next pose at one rate. The arms, forearms and head arrived with the '
            'trunk, which shows the keys (Cooper: body parts that start and stop together).</li>'
            '<li><b>Held frames.</b> A landing was one crouch frame held, then a snap to standing in 0.1 s. A stop was one braking frame. A hang was one '
            'frame for as long as he hung, and a fall one frame for the whole fall.</li>'
            '<li><b>Nothing trailed.</b> No overlap or settle followed a turn, a stop or a landing. The only exceptions were the cloth\'s wind and '
            'the run\'s kilt from round 25a.</li></ul>'
            '<h3>Research</h3><ul>'
            '<li><b>The principles.</b> Follow-through and overlapping action mean parts move at different rates and drag behind what moves them. '
            'Slow in and out, the moving hold and the settle complete them. In games, a long anticipation costs responsiveness, so the weight goes into the '
            'follow-through and recovery instead (Cooper). <b>Here no timer changed: everything added comes after the event.</b></li>'
            '<li><b>Practice.</b> Additive layers over a base (Naughty Dog), procedural motion between few keys (Overgrowth), and springs for '
            'secondary motion (Chou, Holden). Dead Cells draws its ~50 px figures from 3D, pose to pose. Prince of Persia 1989 kept the '
            'rotoscoped body\'s real weight.</li>'
            '<li><b>Biomechanics.</b> A soft landing takes the load in the knees and hips; the knee\'s load peaks ~0.07 s after contact. CMU 16_05 is '
            'deepest at 0.13 s and standing again by 0.5 s. Quiet standing moves the trunk ~0.5 deg with each breath, at 12-20 breaths a minute, and '
            'sways at ~0.3 Hz. A body hanging from its hands is a pendulum.</li></ul>' + links(SOURCES) +
            '<h3>The audit</h3>' +
            table(['move', '(a) the clip, and what the side view drops', '(b) rigid between keys', '(c) should trail', 'round 25f'], AUDIT) +
            '<h3>What changed (look only)</h3><ul>'
            '<li><b>Overlap</b> (followPose): each part eases at its own rate toward held poses and short transitions. The clip cycles (run, walk, '
            'crawl, climb, drink, swing) are followed as before. Held hands are put on their grips at the full rate.</li>'
            '<li><b>Measured settles</b> (r23poses.py SETTLE): keyed by the time since touchdown or the braking step. Each key holds g, how far the pose '
            'is from standing toward the clip\'s peak (read from the hip\'s height), and each angle\'s residual against that blend: what a plain blend '
            'misses. The game draws stand + (peak - stand) g s + residual s. The settle runs through land or stop and on into stand; anything else ends it.</li>'
            '<li><b>The turn, the hang and the fall</b> are pure functions of the time since the event. <b>The kilt</b> trails the thighs on a '
            'look-only spring. <b>The crawl</b> looks along the tunnel. <b>The standing jump</b> crouches with both arms back.</li>'
            '<li>Unchanged: every timer, transition, launch speed, hit box and grip; feet on the floor; crowns within figscan\'s limits; wall hiding '
            'and lift occlusion.</li></ul>' +
            table(['what', 'values', 'note'], VALUES) +
            fig(img, 'r25f_moves.png', 'At 4x, round 25b (before) above round 25f (after), frames as the game makes them, the pose as drawn: idle, the turn, '
                'the stop, the standing jump, a fall of one storey, the jump up and hang, the crawl. Red: what moved by about a pixel or more') +
            fig(img, 'r25f_moves1.gif', 'In the game at the phone\'s resolution, round 25b | 25f, Torchlight and Classic: idle, turning, running and stopping, '
                'a standing jump and its landing, the crouch (15 frames a second)') +
            fig(img, 'r25f_moves2.gif', 'The same: jumping up to a ledge, the hang, the climb, a fight exchange, the crawl') +
            '<h3>Not done yet</h3><ul><li>Round 25a\'s extra joints are not yet measured for the landing, stop and jump keys: the two-part trunk (sb), the '
            'shoulder girdle (soF/soB) and the foot\'s roll (fpF/fpB) at heel strike and toe-off. The settles carry only the ten angles.</li>'
            '<li>No local clip turns on the spot, so the turn\'s trail is procedural. A turning clip (for example 36_02) would need a download.</li></ul>'
            '<h3>Tests</h3><p>' + E(TESTS) + '</p>'
            '<p class="meta">Retired to keep the page at 505 pictures: round 9\'s r9_hair_crop_classic.jpg, r9_hair_curls_classic.jpg and '
            'r9_hair_bob_classic.jpg (the Torchlight crops stay).</p></section>']
