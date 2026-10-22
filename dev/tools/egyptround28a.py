# egyptround28a.py: round 28a's section of egypt_themes.html: the hump behind the shoulder with the arms down (owner, a phone shot of floor 11,
# the Blue Chambers, Torchlight, the prince standing, the upper back and the shoulder circled: "Prince hump in the first photo - I don't think
# the upper back sticks out as much in a muscular teen seen from the side"). Picture from egyptr28a.py (r28a_back.png).
import html
E = html.escape


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def links(L):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(t)) for t, u in L) + '</ul>'


SOURCES = [
    ('Mayo Clinic\'s wall test (via HealthDay): the back of the head, the shoulder blades and the buttocks against a wall, a flat hand behind the low back',
     'https://www.healthday.com/health-news/bone-and-joint/health-tip-the-wall-test-for-good-posture-751126.html'),
    ('Fon, Pitt and Thies, Thoracic kyphosis: range in normal subjects (AJR 1980): kyphosis grows with age', 'https://pubmed.ncbi.nlm.nih.gov/6768276/'),
    ('Normal range of thoracic kyphosis in male school children (Kermanshah, boys 13-18: 35.5 +- 7.8 degrees, about 20 to 51)', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC4045366/'),
    ('Lowell and Winters\' Pediatric Orthopaedics, ch. 19: normal kyphosis 19 to 45 degrees, T2 to T12', 'https://www.rchsd.org/documents/2020/12/chapter-19-lowell-and-winters-pediatric-orthopedics-7th-ed-11.pdf/'),
    ('Proko, How to Draw Deltoids: three heads from the clavicle, the acromion and the scapula\'s spine; not a ball ("bubblemen")',
     'https://proko.com/course-lesson/how-to-draw-deltoids-anatomy-for-artists/notes'),
    ('The standard posture is a myth: a scoping review (2024): Kendall\'s plumb line is an ideal, not a measured norm', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC11492508/'),
]

FOUND = ('Measured on silhouettes at 10x (egyptr28a.py), px at 1x. Standing at MUS 1.65 the arms-down back (R23D.BQ) stood 4.89, 4.82, 4.82 px behind '
         'the spine\'s line at U .76, .88, .96 and 4.47 at the shoulder joint, so the back was fullest only 0.7 px under the joint, 2.1 px behind the '
         'nape and 0.6 px behind the seat, a square shoulder of muscle under the head (at MUS 1.0 the same back is 2.7 to 2.8 px deep and flat: 0.6 px '
         'behind the nape). The cause was round 24\'s bulk: TRUNK_G and TRUNK_G2 laid 55 to 75% of the trunk\'s growth behind at every level up to the '
         'shoulder joint (the \'trap\' measure at U 1 alone added 2.1 px behind). The lit and shaded planes only follow the outline (the flat silhouette '
         'has the hump). Second, the deltoid\'s root (the arm\'s tube, 6.36 px wide at 1.65 against 3.24 at 1.0) grew round its centre at the shoulder '
         'joint, so its cap stood 4 px over the joint, 0.8 px over the chin: the shoulder rose beside the jaw, as in the owner\'s shot. Not the clip\'s '
         'thoracic pitch (the same at every level), not the spine curve sb (0 standing), not RD.mh\'s lines (they follow the arm).')
FIX = ['The back rounds over above the shoulder blades: BT_TOP (r23poses.py) keeps 90, 80, 67, 51 and 57% of the growth behind at U .62, .76, .88, '
       '.96 and 1 (the prince only), and TR_K 0.6 of the trapezius\' bulge on the slope from C7, so the back runs from the nape down the trapezius '
       'into the blades and lats in one slope: BQ at 1.65 4.51, 4.45, 4.15, 3.80, 3.54 (was 4.72, 4.89, 4.81, 4.81, 4.46). Standing: behind the '
       'nape 2.1 > 1.6 px, behind the seat 0.6 > 0.1 (the wall line), the bulge over the chord nape to waist 2.15 > 1.66 px, fullest 0.7 > 3.2 px '
       'under the joint; walking 3.1 > 2.4 (bulge), landing 3.2 > 2.5, running .5 3.0 > 2.5.',
       'The deltoid hangs from its bony origin: its root drops down the humerus by the half-width it gained over round 23 (RD.dd, 1.56 px at 1.65), '
       'times cos of the arm\'s angle (arms down only, none past the horizontal), so its cap stays at round 23\'s place under the chin and its rear '
       'edge stays inside the far side of the back. The muscle is as broad as before.',
       'Kept: the arms-up back (Bo is made from the full BQ, so the hang and the jump up are round 26b\'s to the pixel), the bulk (MUS 1.65; the seat, '
       'waist, chest, lats and every limb), joints, bones, poses, grips and hit boxes; the robbers (R23DR: v70\'s back, no drop). Look only.']
CHECKS = ('Perspective: a pure side view; the far arm is drawn first behind the trunk and shows past the back only where its deltoid passes the trunk\'s '
          'outline, which the dropped root no longer does; the near arm\'s cap lies over the trunk with no line at the shoulder. Shading: the lit plane '
          '(a lamp behind him, as in the owner\'s shot) and the shaded plane follow the new outline; RD.mh\'s deltoid V moves down with the root; no '
          'new line on the back. Non-pixelated: drawn at 1x, at DPR 3 and at 10x; in game at 844x390 and DPR 3, 1:1 and 3x crops, Torchlight and Classic.')
TESTS = ('From a copy of dev/: figscan ok; lowceil ALL OK; egyptr23.py moves: no errors; rendersmoke floors 9 to 11, both modes: no errors '
         '(0.57 ms/frame at most); run2 floors 3 to 6, one seed: 4 of 4, 0 runs with damage (0.04 ms/frame); run2 floors 6 and 7 fighting: 2 of 2, '
         '0 damage (0.06 ms/frame).')


def sections(D, REL, img):
    return ['<section class="card" id="r28a"><h2>Round 28a: no hump behind the shoulder, arms down</h2>'
            '<p>Owner (a phone shot of floor 11, the Blue Chambers, Torchlight, the prince standing, the upper back and the shoulder circled): '
            '"Prince hump in the first photo - I don\'t think the upper back sticks out as much in a muscular teen seen from the side".</p>'
            '<h3>What was found</h3><p>' + E(FOUND) + '</p>'
            '<h3>The fix</h3><ul>' + ''.join('<li>%s</li>' % E(t) for t in FIX) + '</ul>' +
            fig(img, 'r28a_back.png', 'The owner\'s scene (floor 11, Torchlight and Classic, DPR 3, before | after, 1:1 and 3x); the stand at 10x with the '
                'back\'s contour (red; before\'s in blue) and the numbers for every pose at MUS 1.65, 1.28, 1.0; the poses before | after at 1x and 3x; '
                'the research') +
            '<h3>Research</h3><p>' + E('In a good standing posture the back of the head, the shoulder blades and the buttocks touch one wall; '
                                       'the thoracic curve (normal 20 to 45 degrees in adolescents) has its apex in the mid-thorax, over the shoulder '
                                       'blades\' lower half, and the back rounds over from there into the trapezius\' slope to C7, the nape a few cm '
                                       'in front (5 cm is 1.5 px at the game\'s 29.4 px a metre). Muscle grows from fixed bony origins: a bigger '
                                       'trapezius thickens along its slope, a bigger deltoid swells down and out over the arm (Proko; Bridgman\'s and '
                                       'Loomis\'s profile: the back of the neck runs into the back in one line, the shoulder\'s cap under it). At about '
                                       '52 px the build reads in the outline\'s whole pixels (round 22, PoP1\'s rotoscoped kid).') + '</p>' + links(SOURCES) +
            '<h3>Checks</h3><p>' + E(CHECKS) + '</p>'
            '<h3>Tests</h3><p>' + E(TESTS) + '</p>'
            '<p class="meta">Retired to keep the page at 505 pictures: round 8\'s sky clock\'s gate clock at 3x, r8_clock_A_gate.png (a gate\'s clock in game '
            'stays there).</p></section>']
