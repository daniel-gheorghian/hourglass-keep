# egyptround21a.py: round 21a's section of egypt_themes.html (built in): the prince's back when he stands straight, and how the lifts'
# slabs hang on their ropes. Pictures from egyptr21a.py.
import html
E = html.escape


def links(src):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(l)) for l, u in src) + '</ul>'


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def sections(D, REL, img):
    return ['<section class="card" id="r21a"><h2>Round 21a (built in): no hump when he stands, rope holes in the lifts\' slabs</h2>'
            '<p>Two bugs from the owner\'s phone. Look only: the generator, floors, moves, hit boxes, timings and the bot are unchanged.</p>'
            # ---- 1
            '<h3>1. "The prince has a hump when standing straight"</h3>'
            '<p><b>Cause</b>: the torso (<code>torsoG</code>\'s outline round the spine) ended at the shoulders in a flat top: from the neck\'s back edge the '
            'outline ran straight back to the full depth of the upper back (5 px behind the spine) and turned down round a corner. The neck rose out of that shelf '
            'as a thin tube, so seen from the side the back of the neck and the upper back met at a right angle, and the corner read as a rounded lump behind '
            'the shoulders, most of all when the light comes from his back (the lit plane runs over it). Round 19 thinned the back near the shoulders only when '
            'the arms are raised; standing, walking, running and fighting kept the shelf. Not the arm: the back arm\'s deltoid lies inside the torso.</p>'
            '<p><b>Fix</b>: seen from the side, a standing man\'s back runs from the base of the skull down the back of the neck and on down the trapezius in one '
            'long, nearly straight slope to the shoulder blades, then the upper back\'s gentle convexity (thoracic kyphosis) and the hollow of the lumbar curve; '
            'the plumb line of good posture passes through the ear and the shoulder joint, so the back of the head, the shoulder blades and the seat line up. '
            'The neck meets the chest lower in front (at the jugular notch) than it meets the back behind. So the torso\'s top now runs up into the neck\'s base '
            'along the neck\'s own axis, behind (the nape, 2.6 px up the neck) and in front, and the back\'s depth is taken in over the top quarter of the trunk '
            '(<code>TRAP</code>: 0.15 to 1.2 px from the shoulder blades up), so the line from the nape to the shoulder blades is one slope. As the arms rise '
            'both fade out (round 19\'s arched back is unchanged); the shoulders\' sheen no longer runs past the slope. Egyptian reliefs draw the same back line in '
            'profile (the shoulders turned to the front, the back one smooth line from the nape), and the 1989 prince, traced from film of David Mechner, has the '
            'same sloping neck and flat upper back. Checked in every pose at 4x and 10x, and in the game at GLP.rs 1 and 0.5 in both modes: stand, the run cycle, '
            'step, turn, crouch, the jumps, hang, pull, climb, the fight stances, hurt, drink, death, and the robbers (who share the torso).</p>' +
            fig(img, 'r21a_prince.png', 'Standing in the game (Torchlight at rs 1 and 0.5, Classic, facing both ways), the upper body at 10x lit from his back and front and '
                'as a silhouette, and every pose at 4x: before (v68) and after') +
            # ---- 2
            '<h3>2. "Lift rope ends look off ... holes in the slab with the rope threaded through them"</h3>'
            '<p><b>Which lifts</b>: the counterweight lift\'s platform (the owner\'s picture) and the paternoster\'s slabs hang on ropes; the sand lift has no rope. '
            '<b>Cause</b>: on the counterweight lift each rope stopped at the middle of the slab\'s top and a second piece of rope was drawn lying across the top from '
            'there to the front lip, ending in a round dark blob on the lip (meant as a knot under it). On the slab\'s top it read as two loose sticks. The '
            'paternoster\'s slabs were tied to their rope by a blob under the lip that the slab hid, so they seemed to float beside it. The ropes were round 13\'s '
            'two dashed rows, not the laid rope of the swing.</p>'
            '<p><b>How stones were hung</b>: Egyptian masons moved blocks with ropes and levers round lifting bosses left on the stone; Bronze Age stone anchors '
            '(the Egyptian anchors of Wadi Gawasis on the Red Sea, those of Byblos, the single-hole anchors of the Uluburun wreck) and stone weights were hung by a '
            'rope through a hole drilled through the stone near the top, its end knotted or spliced back; early Greek builders cut U-shaped rope channels and holes '
            'into blocks to sling them (Corinth, Isthmia) before the lewis. A flat slab hung level is slung by a bridle: two legs from the hoisting rope to two points '
            'apart, so it cannot tip.</p>'
            '<p><b>Fix</b> (<code>liftSling</code>, <code>ropeHole</code>, <code>ropeSeize</code>): each of the platform\'s two ropes ends in an eye seized with a few '
            'turns of cord 8 px above the slab (<code>LS_J</code>); from it a sling runs down through a hole drilled through the slab near its front edge, under the slab '
            'and up through a second hole near its back edge. Seen in this view the legs part along the depth diagonal (the front one down to the left, the back one '
            'up to the right), and each hole is a circle on the top face drawn in the view\'s own oblique (<code>DX/TW</code>, <code>-DY/TW</code>: a flat, slanted lens) '
            'with its worn lip, the rope going into its far side so its near side shows dark. The counterweight is hung the anchors\' way: a hole through the stone '
            'below its top, the rope\'s seized eye above it and its sling going in. A paternoster slab sits on its rope where the rope runs through a hole in its '
            'middle, held by a seized stopper above it (and one below, unseen); while the rope runs upright, its part from the hole up over the slab\'s back half is '
            'drawn again in front of the top. All the lifts\' ropes are now the swing\'s laid rope (<code>barRope</code>) in the theme\'s fibre and ply '
            '(<code>ropeOf</code>, <code>BARM</code>), and their lay travels with the rope as it runs over the sheave or round the wheels (<code>barRope</code>\'s new '
            '<code>ph</code>). Drawn inside <code>liftOccl</code> as before; the same calls in both modes.</p>' +
            fig(img, 'r21a_lift.png', 'The counterweight lift, floor 3: the platform mid-shaft and docked with him on it, in the game (Torchlight rs 1 and 0.5, Classic), and Classic at 6x: before and after') +
            fig(img, 'r21a_paternoster.png', 'The paternoster, floor 8, at two moments, in the game and at 6x: before and after') +
            '<p><b>Tests</b>: <code>liftscan.py</code> floors 3 to 12, two seeds, both modes (276 cases, 0 bad), <code>lifttest.py</code> (every check as in v68; its paternoster '
            '"slabs solid" case fails the same way on the v68 release), <code>rendersmoke.py</code> 7 to 9 both modes (no errors), <code>run2.py</code> 8 to 10, two seeds (all '
            'passed, no damage). Retired from the page to stay at 505 files: round 10\'s Classic crop and Classic fight crop at the phone\'s size, and its round 9 sheet at 3x.</p>' +
            links([('Spinal posture: the plumb line through the ear, the cervical bodies and the shoulder joint', 'https://en.wikipedia.org/wiki/Spinal_posture'),
                   ('Postural assessment: earlobe, acromion, greater trochanter in one line', 'https://pabau.com/templates/postural-assessment/'),
                   ('Trapezius muscle', 'https://en.wikipedia.org/wiki/Trapezius_muscle'),
                   ('Kyphosis (the thoracic curve)', 'https://en.wikipedia.org/wiki/Kyphosis'),
                   ('Art of ancient Egypt: the composite view of the human figure', 'https://en.wikipedia.org/wiki/Art_of_ancient_Egypt'),
                   ('Boing Boing (2014): the original Prince of Persia rotoscope footage', 'https://boingboing.net/2014/10/30/how-prince-of-persias-famous.html'),
                   ('Lifting boss (handling bosses left for ropes and levers)', 'https://en.wikipedia.org/wiki/Lifting_boss'),
                   ('Zazzaro et al.: the stone anchors of Mersa/Wadi Gawasis (upper rope hole and groove)', 'https://unora.unior.it/retrieve/dfd1bedc-b3b3-d55a-e053-3705fe0af723/A01_Zazzaro_SD.pdf'),
                   ('Ancient Egyptian anchors: new results from Wadi Gawasis', 'https://journals.ekb.eg/article_56700.html'),
                   ('Noureddine 2016: stone anchors off Byblos', 'https://www.ancientportsantiques.com/wp-content/uploads/Documents/ETUDESarchivees/Navires/Anchors/AnchorsByblos-Noureddine2016.pdf'),
                   ('Frost 1963: stone anchors (perforated anchors and weights)', 'https://ancientportsantiques.com/wp-content/uploads/Documents/ETUDESarchivees/Navires/Anchors/Anchors-Frost1963.pdf'),
                   ('Coulton 1974: Lifting in Early Greek Architecture (JHS 94; U-shaped rope cuttings)', 'https://resolve.cambridge.org/core/journals/journal-of-hellenic-studies/article/abs/lifting-in-early-greek-architecture/83AECC23A4CFF572B9B01B204832F222'),
                   ('Pierattini 2019 (via Cambridge Core blog): the grooved blocks of Corinth and Isthmia were slung for lifting', 'https://www.cambridge.org/core/blog/?p=31049'),
                   ('Oblique projection', 'https://en.wikipedia.org/wiki/Oblique_projection')]) + '</section>']
