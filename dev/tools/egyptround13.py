# egyptround13.py: round 13's section of egypt_themes.html (built in): the owner's notes after playing round 12 on the phone: Egyptian
# lifts, the prince's head, the prince against a fallen block, faster sand and falls, the sand that kept running. Pictures from
# egyptr13.py (and egyptr12.py's GIFs, re-taken).
import html
E = html.escape


def links(src):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(l)) for l, u in src) + '</ul>'


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def sections(D, REL, img):
    return ['<section class="card" id="r13"><h2>Round 13 (built in): lifts, the head, the block underfoot, faster sand</h2>'
            '<p>Owner, after playing round 12 ("Great"): "need to egyptianise the lifts: rope instead of chain, stone slabs instead of grates, wooden wheels / first photo: what is that on the prince head, in the red circle? / second photo: the feet and the slab in the red circle / '
            'the sand animation: need to be faster and also the slab falling animation. when it runs for a tile in the coridor floor, after the tile falls, the sand still trickles in two columns, that doesn\'t make sense".</p>'
            '<h3>The lifts</h3><ul>'
            '<li><b>Ropes, not chains.</b> Two-strand twisted rope of papyrus or palm fibre, its lay drawn as two staggered rows of short strokes. The paternoster\'s rope loop carries its lay as it runs. The Red Sea harbours\' ropes were papyrus, and a Theban tomb (TT 261) shows rope-makers twisting two strands.</li>'
            '<li><b>Wooden wheels.</b> The counterweight lift\'s pulley is a solid disc of planks joined by a batten, with a groove for the rope and an axle peg. Pulleys are first claimed for 12th-Dynasty Egypt, for wells, and the MFA holds a small Middle Kingdom wooden disc catalogued as a possible pulley wheel. '
            'The paternoster\'s gears are wooden wheels with peg teeth, as on the saqiya, the ox-driven geared water wheel of Ptolemaic Egypt. That puts them late in the period, and this is the device the game needs.</li>'
            '<li><b>Stone, not grates or bronze.</b> The platforms and the paternoster\'s slabs are slabs of the theme\'s stone with round 12\'s texture, their tops level with the ledges, and the ropes are knotted through holes under their lips. The counterweight is a block of the theme\'s stone. The mouths are closed by plain stone slabs running in grooves, like the portcullis, in place of the iron gratings. '
            'The sheave hangs from a timber. With no metal left, the Torchlight metal shader no longer touches the lifts.</li>'
            '<li>Everything the lifts rely on is unchanged: their geometry, the walls\' occlusion (<code>liftOccl</code>, <code>liftOcclSide</code>), wear (<code>liftWear</code>) and gameplay. Classic draws them the same way.</li></ul>' +
            fig(img, 'r13_lifts.png', 'Counterweight lift and paternoster, round 12 and round 13, both modes (1:1)') +
            '<h3>The head (first photo)</h3><p>The circled shape was round 9\'s close-cropped hair cap. Its outline ran past the skull at the back and ended in a point below it: a hook at the nape, and a bump where it stood up off the crown. It was not an ear, the oiled-skin sheen or round 10\'s outline. '
            'The cap now follows the skull\'s own curve, a hair outside it, from a hairline over the brow round the crown and the back of the head. It ends inside the head\'s outline at the nape, its lower edge passing behind the ear. The result is a round, close-cropped skull with a natural nape. Checked standing, running, jumping, hanging, in guard, crouching and falling, facing both ways, in both modes.</p>' +
            fig(img, 'r13_head.png', 'The head, round 12 and round 13 (2x of the 1:1 canvas; at the right, Torchlight at 4x)') +
            '<h3>The feet and the fallen block (second photo)</h3><p>The fallen block spans the corridor\'s whole depth, and he walks its middle. So the half of the block nearer than him (depth 0 to 0.5) is in front of him. Before, the whole block was drawn behind him, and his feet lay over its front face. '
            'Now that near half is drawn again after the figures, so his toes stop at the block\'s face at his own depth, hidden by its near corner as they would be. The block sits flat on the floor\'s top face, its front foot on the floor\'s front edge, with a soft shadow round its foot. '
            'The little squares at its base, which read as feet, were rubble drawn on its front edge. Rubble now lies as round-edged chips on the floor beside the block, and the portcullis\'s rubble likewise. Its faces still follow the floor\'s projection: front, right side, top. Gameplay is unchanged.</p>' +
            fig(img, 'r13_block.png', 'Standing against a fallen block, round 12 and round 13, both modes (2x of the 1:1 canvas)') +
            '<h3>Faster sand, heavier falls</h3><p>The same shape at about half the length. A roof block\'s rise from trickle to full flow takes 0.15 s instead of 0.3 s, a sand floor\'s 0.25 s instead of 0.5 s; the billows last about 0.5 s instead of 0.9 to 1.2 s, and the settling 1.1 s instead of 2.2 s. '
            'The blocks and a sand floor\'s slabs fall under a heavier pull (1400 px/s², against the prince\'s 700), so the drop reads heavy and quick. '
            '<b>The warning:</b> a waiting block still trickles all the time, and its 0.3 s shift and a sand floor\'s 0.5 s are unchanged. From the moment a block starts to shift to the moment it reaches a standing prince\'s head is now about 0.6 s (about 0.3 s of fall), against 0.72 s before. '
            'A running prince sets it off 22 px before it and is 38 px past it when it reaches head height, so the bot\'s runs are unaffected (run2 below, 0 damage). The route\'s times (<code>estPath</code>) do not depend on the fall.</p>'
            '<h3>The sand that kept running</h3><p>The owner saw the sand-filled shaft under a slab. When the slab gave way, its two streams followed the falling slab down for as long as it fell, never dropping below 15% of full, from sand that had already gone. '
            'Now sand runs only from a source that is still there. For a sand floor, the sand lay on the slab; once the slab drops, what is left runs out of the hole in a short last dribble, gone in about 0.3 s and at most 40 px long. Then only the billow and the settling dust remain. '
            'A waiting roof block\'s joints trickle while it hangs. As it falls, its slot pours only until it lands. After that the slot is empty and nothing runs. The plugs carry sand on their top edge, which runs off for as long as they move. Checked in all three.</p>'
            '<p>The pour and sand-floor GIFs in round 12\'s section above show the new timing.</p>' +
            links([('Wadi al-Jarf: the Red Sea papyrus ropes (Borojevic and Mountain)', 'https://en.wikipedia.org/wiki/Wadi_al-Jarf'),
                   ('Innsbruck spindle typology: rope making in Egypt (the Dra Abu el-Naga tomb 261 scene)', 'https://www.uibk.ac.at/en/archaeologien/arbeitsgemeinschaften/abt/spindeltypologie/rope-making-egypt/'),
                   ('Pulley: the earliest evidence, 12th-Dynasty Egypt', 'https://en.wikipedia.org/wiki/Pulley'),
                   ('MFA Boston: a Middle Kingdom wooden disc from Sheikh Farag, "winder(?) or pulley wheel"', 'https://www.mfa.org/collections/object/disc-141220'),
                   ('Saqiyah: the geared water wheel, Ptolemaic Egypt (the Faiyum, 3rd century BC)', 'https://en.wikipedia.org/wiki/Saqiyah'),
                   ('Britannica: the shaduf, lever and counterweight, Egypt', 'https://www.britannica.com/technology/lever')]) + '</section>']
