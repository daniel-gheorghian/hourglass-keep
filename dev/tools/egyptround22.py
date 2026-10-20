# egyptround22.py: round 22's section of egypt_themes.html (built in): the prince's back in profile, after research on the backs of lean
# athletic youths seen from the side. Pictures from egyptr22.py.
import html
E = html.escape


def links(src):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(l)) for l, u in src) + '</ul>'


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def sections(D, REL, img):
    return ['<section class="card" id="r22"><h2>Round 22 (built in): the back in profile</h2>'
            '<p>Owner, after round 21a: "It still looks off. Perform research on backs viewed from profile of athletic youths." Look only: the skeleton, poses, '
            'hit boxes, timings, generator and bot are unchanged.</p>'
            '<h3>What a lean young athlete\'s back looks like from the side</h3><ul>'
            '<li><b>One wall line.</b> Standing well, the back of the head, the shoulder blades and the seat all touch a wall, with a flat hand\'s gap at the small of '
            'the back (Mayo Clinic\'s wall test); a head that cannot reach the wall is the clinical sign of a rounded upper back (occiput-to-wall distance above 0 cm). '
            'The plumb line falls through the ear, the shoulder joint and the hip joint.</li>'
            '<li><b>The neck leans forward and its back is flat.</b> Bridgman: "From the sloping platform of the shoulders the neck rises, a cylindrical column, curving '
            'slightly forward"; "the strength of the neck is therefore at the back, which is somewhat flat and overhung by the base of the skull". Proko: the trapezius '
            'makes the back wall of the neck, the throat is the front half of its depth. The plane where the neck meets the trunk is tilted: from the seventh cervical '
            'vertebra behind (C7) down to the pit of the neck in front, which lies at the level of T2. In young adults standing, the line from C7 to the ear rises at '
            'about 50 degrees (craniovertebral angle, Titcomb et al. 2024): the ear is well forward of the neck\'s base, and C7 sits a few centimetres in front of the wall line.</li>'
            '<li><b>The upper back is one long, gentle convexity, broken by the almost vertical shoulder blade</b> (Bridgman), its apex at T6 to T7 (normal thoracic '
            'kyphosis 20 to 40 degrees): below the nape the trapezius runs down and back in a long, nearly straight slope to the top of the shoulder blades, then the '
            'line is nearly vertical over them, a slight bulge of the latissimus below, the "sharp anterior curve of the waist" opposite the navel, and "the shorter '
            'curve of the buttocks".</li>'
            '<li><b>The shoulder sits on the side of the ribcage, not behind it</b>: the deltoid\'s mass is centred about the plumb line, inside the trunk\'s depth, and '
            'in a relaxed profile it never shows behind the back line. Its top is well below the chin.</li>'
            '<li><b>Youths in art.</b> Archaic kouroi are broad from the front but slim in profile, with a slender neck, a distinct hollow at the waist and full, '
            'rounded buttocks; Egyptian reliefs draw the back as one smooth line from the nape; the 1989 prince, rotoscoped from film of David Mechner, has a visible '
            'neck and low, relaxed shoulders.</li></ul>'
            '<h3>The proportions, at the figure\'s scale</h3>'
            '<p>The head is about 10 px deep and 11.5 px tall, so one px is about 2 cm of a young man. Adult means (approximate, as in the ANSUR II survey): the chin is '
            'about 23 cm under the crown, C7 about 2 to 3 cm under the chin, the shoulder\'s top about 8 cm under it. So at this scale: the back of the skull, the '
            'shoulder blades and the seat on one vertical line; C7 about 2 px in front of it and a little under the chin; the trapezius slope from C7 to the shoulder '
            'blades about 20 to 30 degrees from the vertical, steepening into their nearly vertical line; the deepest point of the back at the shoulder blades, about '
            'u 0.7 of the trunk; a lumbar hollow of about 1.5 px; the neck at its base about half the head\'s depth (a lean youth\'s neck is about 11 to 12 cm deep). '
            'The figure\'s neck is short by design (the big head of the style); the shoulder joint is where the skeleton puts it.</p>'
            '<h3>What was wrong</h3>'
            '<p>Measured against those guides (<code>r22_guide.png</code>), v69\'s back was right at the wall line but wrong at the top. Round 21a had put the nape point '
            '(the torso\'s top at the back of the neck) 2.6 px up the neck, higher than the chin, and taken the back\'s depth in to 1.6 px at the shoulder joint\'s level '
            '(<code>TRAP</code>): the outline ran up behind the neck, dipped into a notch at the shoulders and swelled out again to the shoulder blades, so the top of the '
            'back read as a round mound right behind the jaw. The back arm\'s deltoid (radius 2.6 px round its root) stuck out of that notch by about half a pixel '
            'plus its outline, a second bump, most of all lit from his back. The neck was a thin tube (4 px at its base, 0.4 of the head\'s depth), so the mound looked '
            'bigger beside it, and both arms\' roots sat so high that the shoulders\' tops were level with the chin, a shrug.</p>'
            '<h3>What changed</h3><ul>'
            '<li>The back\'s offsets from the spine (<code>BQ</code>, standing; the arms-up offsets of round 19 are kept and blended in as the arms rise) now follow the '
            'guides: 4.6 px at the seat, 3.2 in the hollow of the waist, 4.5 at the shoulder blades (u 0.76), 4.25, 3.65 and 3.1 above, so from the shoulder blades up '
            'the line steepens into one trapezius slope; <code>TRAP</code> is gone.</li>'
            '<li>The nape point (C7) is 1.3 px up the neck and 2.6 px behind its axis: just under the chin, on the neck\'s back edge, with no notch under it.</li>'
            '<li>The neck is wider and set back: 5 px at its base and 3.7 at the head, its back edge 0.5 and 0.3 px further back and its front where it was, so the back of '
            'the neck runs straight from under the skull into the slope. Both fade to round 19\'s neck as the arms rise.</li>'
            '<li>The arms\' roots are 0.8 px lower while the arm hangs or swings (fading out from 1 to 2 rad, so raised arms are as before), so the shoulder caps sit '
            'below the chin and the back arm\'s deltoid stays inside the back; the shoulders\' sheen follows them down (it had shown as a grey fleck under the chin).</li>'
            '<li>The robbers share all of it (their offsets 0.4 to 0.6 px deeper).</li></ul>' +
            fig(img, 'r22_guide.png', 'Standing at 10x, before (v69) and after: lit from his back, from his front, and the silhouette with the guides (blue the wall line, '
                'orange the plumb line through the ear, shoulder joint and hip, purple C7 and the lumbar hand gap; the back\'s edge measured row by row, before red, after '
                'green). Below: the silhouettes in motion laid over each other (red only before, green only after)') +
            fig(img, 'r22_poses.png', 'Every pose at 4x, lit from his back: before (v69) above, after below, and a robber') +
            fig(img, 'r22_game.png', 'In the game: Torchlight at GLP.rs 1 and 0.5 and Classic, facing both ways on floors 7 and 14, before and after; then the '
                'Torchlight crops at 3x') +
            '<p><b>Tests</b>: <code>run2.py</code> 5 to 6, two seeds (all passed, no damage), <code>rendersmoke.py</code> 7 to 8 both modes (no errors). Retired from the page to '
            'stay at 505 files: round 10\'s fight clip and its 3x sheet, and round 9\'s running clip.</p>' +
            links([('Mayo Clinic: posture, the wall test (head, shoulder blades and buttocks on the wall, a hand behind the lower back)', 'https://newsnetwork.mayoclinic.org/discussion/mayo-clinic-q-and-a-proper-posture-and-body-alignment/'),
                   ('HealthDay: the wall test for good posture', 'https://www.healthday.com/health-news/bone-and-joint/health-tip-the-wall-test-for-good-posture-751126'),
                   ('St Emlyn\'s spine examination sheet: wall-to-tragus distance, a head that cannot touch the wall', 'https://www.stemlynsblog.org/wp-content/uploads/2022/01/MSK-Spine-StEmlyns.pdf'),
                   ('Postural assessment: the plumb line through earlobe, acromion, greater trochanter, knee and ankle', 'https://pabau.com/templates/postural-assessment/'),
                   ('G. B. Bridgman, Constructive Anatomy (1920): the neck, the trapezius, the torso in profile', 'https://archive.org/details/constructiveanat00brid'),
                   ('Proko: how to draw neck muscles (the trapezius the back wall of the neck)', 'https://www.proko.com/how-to-draw-neck-muscles-anatomy-and-motion/'),
                   ('Life Drawing Academy: the seventh vertebra, the tilted plane from it to the pit of the neck', 'https://lifedrawing.academy/drawing-lessons/how-to-draw-female-from-life'),
                   ('Vertebral levels: the jugular notch at T2 (Loyola gross anatomy)', 'https://www.meddean.luc.edu/lumen/meded/grossanatomy/2010/VertebralLevels.pdf'),
                   ('Titcomb et al. 2024: craniovertebral angle standing in young adults (50 degrees)', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC11042887/'),
                   ('POSNA: postural kyphosis (normal 20 to 40 degrees, apex T6-T7)', 'https://posna.org/physician-education/study-guide/postural-kyphosis'),
                   ('ANSUR II anthropometric survey (Penn State OpenLab)', 'https://www.openlab.psu.edu/ansur2/'),
                   ('The Anavyssos and Volomandra kouroi: slim in profile, swayback waist, slender neck', 'https://www2.iath.virginia.edu/Barbarians/Sites/Hirschlanden/Hirschlanden_volo.html'),
                   ('Art of ancient Egypt: the composite view of the figure', 'https://en.wikipedia.org/wiki/Art_of_ancient_Egypt'),
                   ('Boing Boing (2014): the original Prince of Persia rotoscope footage', 'https://boingboing.net/2014/10/30/how-prince-of-persias-famous.html')]) + '</section>']
