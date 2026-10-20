# egyptround10.py: round 10's section of egypt_themes.html (built in): the prince and the robbers drawn as one body, their build
# carried by the silhouette and broad planes so that it reads at the phone's resolution; after the 1989 prince and v62's. Pictures
# from egyptr10.py (1x crops of the game's canvas, 3x sheets, a run and a fight at 1x).
import html
E = html.escape


def links(src):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(l)) for l, u in src) + '</ul>'


def fig(img, f, cap, w=None):
    return '<figure%s>%s<figcaption>%s</figcaption></figure>' % (' style="width:%dpx"' % w if w else '', img(f, cap), E(cap))


def sections(D, REL, img):
    row = lambda pre, w: '<div style="display:flex;gap:10px;flex-wrap:wrap;align-items:flex-start">' + ''.join(fig(img, f, c, w) for f, c in pre) + '</div>'
    o = ['<section class="card" id="prince10"><h2>The prince and the robbers, round 10 (built in): a body that reads at the phone\'s size</h2>'
         '<p>Owner: "Again the prince: the athletic/muscular constitution needs to read at the screen resolution. Also he need to look more organic: study the original prince."</p>'
         '<h3>What was studied</h3><ul>'
         '<li><b>The 1989 prince.</b> Jordan Mechner filmed his brother David, then about 15 or 16, running, jumping, climbing and hanging in loose white clothes, and traced the frames one by one (rotoscoping). '
         'His journal of 29 April 1986 says the key is not to clean the frames up too much. What that gives a figure only some 40 pixels tall is weight, not detail. The outline does all the work: limbs taper and curve, the trunk compresses in a landing and stretches in a hang, '
         'and the shoulders and hips shift with each step. There are hardly any inner lines; the prince is one white shape, and the shape is the anatomy.</li>'
         '<li><b>v62\'s figure</b>, the one the owner liked, reads for the same reason. Its baggy trousers and vest are big, simple shapes with a clear outline, the torso is one solid mass, and its few tones are broad. '
         'Rounds 8 and 9 put the build into thin shade lines (the chest\'s edge, the belly, the deltoid). At the phone\'s size those lines are under a pixel and vanish, and each limb was a separate capsule with its own outline, so the joins showed as seams.</li></ul>'
         '<h3>What changed (the drawing only: skeleton, poses, hit boxes and timing are the same)</h3><ul>'
         '<li><b>The silhouette carries the build.</b> A deltoid rounds the top of each arm. The upper arm swells at the biceps and narrows to the elbow, and the forearm swells below the elbow and tapers to the wrist. The thigh is fuller in front where it shows under the kilt\'s hem, and the calf swells behind, below the knee. '
         'The torso is one outline round a curved spine: the back and ribcage are deep and taper into a narrow waist (the V, seen from the side), with no chest jutting forward. The prince stays a lean youth, and the robbers keep a heavier, grown men\'s build.</li>'
         '<li><b>Broad planes instead of lines.</b> The torso has a shaded plane on the side away from the light, wide at the ribs and narrowing into the waist, and a lit plane over the chest and shoulder toward it. Both are big enough to survive at 1x, and their edges repeat the V. The fine chest, belly and deltoid lines are gone; the oiled sheen stays.</li>'
         '<li><b>One body, not capsules.</b> Each group lays its outline first and then its fills: a limb with its hand or foot, the torso with the neck. So the shoulder, neck, wrist and ankle joins have no seams, and elbows and knees were never split. '
         'The front arm\'s dark outline lies under the torso, so it shows only against the background. Over the body the arm keeps a soft contour in its own shade, and none at the shoulder, where it melts into the deltoid.</li>'
         '<li><b>The body moves with the pose.</b> The spine bends: with the hips flexed (a tuck, a crouch, a landing) the back rounds; with the arms up (a hang, a climb) it arches, the lats stretch and the chest lifts. '
         'The shoulders move forward and back with the arms\' swing, so a run turns the chest. The contours of the chest and back therefore differ between run, jump, hang and fight.</li>'
         '<li><b>Hands and feet.</b> An open hand is an oval laid along the forearm, a fist is rounder round the weapon, and the foot has a heel, an arch and a narrowing toe. All are joined without seams.</li></ul>'
         '<p>Cost: a few more fills per figure (the outlines are laid once per group), with no new pass, texture or shader. The figures\' masks follow the new outline as before.</p>' +
         links([('Ubisoft: Prince of Persia 35th anniversary, a look back at the original game (David Mechner filmed in white clothes, the parking lot and the high school)', 'https://news.ubisoft.com/en-us/article/6yLrRf7b0U1MBYxmlxE225/prince-of-persia-35th-anniversary-a-look-back-at-the-original-game'),
                ('Jordan Mechner: the 1985 process (videotape of David, frames rotoscoped one at a time), on his site', 'https://jordanmechner.com/'),
                ('Boing Boing (2014): how Prince of Persia\'s famous jump animation was made, with the original footage', 'https://boingboing.net/2014/10/30/how-prince-of-persias-famous.html'),
                ('Game Anim: the journal entry of 29 April 1986 ("the key is not to clean up the frames too much")', 'https://www.gameanim.com/?p=5826'),
                ('Animation Obsessive: How the Little Guy Moved', 'https://animationobsessive.substack.com/p/how-the-little-guy-moved'),
                ('J. Mechner, The Making of Prince of Persia: Journals 1985-1993 (Stripe Press, 2020)', 'https://www.thevideogamelibrary.org/book/the-making-of-prince-of-persia-journals-1985-1993')]) +
         '<p class="meta">The 1989 frames are not copied here. Follow the Boing Boing and Ubisoft links for the footage and the game\'s frames.</p>'
         '<h3>In the game at the phone\'s resolution (crops of the 1704 px canvas, shown at the phone\'s size; click for 1:1): round 9, round 10 (round 20a: v62\'s two crops retired)</h3>' +
         row([('r10_1x_r9_torch.png', 'Round 9, Torchlight'), ('r10_1x_r10_torch.png', 'Round 10')], 150) +
         row([('r10_1x_r9_classic.png', 'Round 9, Classic'), ('r10_1x_r10_classic.png', 'Round 10')], 150) +
         '<h3>A fight at the phone\'s resolution: round 9, round 10 (round 20a: round 9\'s Classic crop retired)</h3>' +
         row([('r10_1x_fight_r9_torch.png', 'Round 9, Torchlight'), ('r10_1x_fight_r10_torch.png', 'Round 10, Torchlight'), ('r10_1x_fight_r10_classic.png', 'Round 10, Classic')], 210) +
         '<h3>Running and fighting, round 10, at the phone\'s resolution</h3>' +
         row([('r10_run.gif', 'Running (Torchlight)'), ('r10_fight.gif', 'A fight with a robber (Torchlight, the bot playing)')], 210) +
         '<h3>At 3x: v62\'s figure, the prince, the robbers (recruit, soldier, captain); round 9 above, round 10 below</h3>' +
         '<div class="g2">%s%s</div></section>' % (fig(img, 'r10_sheet3x_r9.png', 'Round 9'), fig(img, 'r10_sheet3x_r10.png', 'Round 10'))]
    return o
