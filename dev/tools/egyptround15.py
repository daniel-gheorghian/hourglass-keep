# egyptround15.py: round 15's section of egypt_themes.html (built in): sky beams that lit walls round corners, wall art embossed over the
# doors, and the prince climbing the exit stairs. Pictures from beamwall.py (r15_beams.png) and egyptr15.py (r15_door.png, r15_exit.gif).
import html
E = html.escape


def links(src):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(l)) for l, u in src) + '</ul>'


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def sections(D, REL, img):
    return ['<section class="card" id="r15"><h2>Round 15 (built in): beams round corners, art over doors, climbing the exit stairs</h2>'
            '<h3>Sky beams lighting walls they cannot reach</h3><p>Owner: "The light beams are producing light around corners. It happens on multiple levels. So I suspect it is an issue of how light beams detect walls."</p><ul>'
            '<li><b>The cause.</b> In this view a wall block\'s front face stands at the front of the room, in front of its whole depth, and is drawn 8 px (HX) left of its cell. '
            'Torchlight\'s shaft shader marched from each pixel toward the opening and stopped at walls <i>between</i> the pixel and the opening, but never asked whether the pixel itself lay on a wall\'s front face. So the haze, the floor patch and the opening\'s rim were added over the bricks of any wall the beam\'s path crossed. '
            'The stair steps came from that light being shown only "against the dark" of the light map, at a quarter of the resolution. Classic cut wall cells out of its beam sprites, but at the cell\'s own place, 8 px right of the face it draws, so a strip of every face was lit and a strip of open air beside it was dark. '
            'The soft "bounce" light where a beam lands was placed even when a wall block stood between the opening and its landing.</li>'
            '<li><b>The fix.</b> Nothing from a beam reaches a pixel on a wall block\'s front face: the shader takes the face\'s coverage at four columns across its quarter-size pixel, so the face\'s edge is a one-pixel soft ramp, not a step. Classic cuts the faces where they are drawn. '
            'A beam\'s bounce light is left out when a wall stands on the line from the opening to where it lands. The windows\' own soft glow round their frames (a fill light like a lamp\'s) is unchanged.</li>'
            '<li><b>How it should fall.</b> The sky is behind the back wall: light through an opening travels down, sideways and toward the viewer, so it can light the air of the room, the floor\'s top face and figures in it, but never a front face (those face the viewer, away from the opening) or anything behind a block. That is the v58 rule, now kept everywhere.</li>'
            '<li><b>Cost</b> (floor 4 on this Mac, <code>?bench&amp;floors=4</code>): 59.2 fps, 16.9 ms mean before and after.</li></ul>' +
            fig(img, 'r15_beams.png', 'Beams that cross a wall block on their way down: round 14 and round 15, Torchlight and Classic (1:1)') +
            '<h3>Wall art over the doors</h3><p>Owner: "Wall decoration over door. Check all levels for this issue."</p>'
            '<p>The doors are drawn live over the room\'s picture, and opaque, but Torchlight\'s relief (the light raking across the stonework) is taken from the room\'s picture, which has the back wall\'s courses, friezes and hangings under the doorway. So they were embossed over the door and the lit stair. '
            'Under each doorway and its frame the back wall is now one flat tone (the door covers it). <code>doorscan.py</code> frames the exit door, open and lit, and the entry door on every floor from 1 to 48 (all twelve themes) in both modes and compares the opening with the same frame drawn without the back wall\'s art: '
            'before, 47 of 192 door views in Torchlight had art showing over the opening (none in Classic); after, 0 in both.</p>' +
            fig(img, 'r15_door.png', 'Exit doors on floors 5, 9 and 11: round 14 and round 15, Torchlight') +
            '<h3>Climbing the exit stairs</h3><p>Owner: "the prince should be animated correctly when climbing the stairs. Now it is marching in place."</p>'
            '<p>Before, he walked on the spot at the floor\'s level, fading out. In Prince of Persia the kid climbs the exit stairs with an animation of its own and is lost into the doorway. Now he walks to the doorway\'s middle and climbs its stairs: one footfall per tread, half a stride each, his body rising a tread (6.2 px up and the stair\'s own depth step) as each foot lands. '
            'He moves up and back with the treads drawn in the doorway, is cut by the door\'s posts on either side and by the ceiling\'s front edge as he rises, and fades over the last treads. The climb takes about 1.6 s instead of 1.0 s; nothing else in play changes.</p>' +
            fig(img, 'r15_exit.gif', 'The exit, round 14 above and round 15 below (Torchlight, 2x of the 1:1 canvas)') +
            links([('SDLPoP (the original game\'s animation tables, seqtbl.c: the kid\'s climb up the level door\'s stairs)', 'https://github.com/NagyD/SDLPoP/blob/master/src/seqtbl.c')]) + '</section>']
