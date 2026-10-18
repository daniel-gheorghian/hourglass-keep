# egyptround8.py: round 8's sections of egypt_themes.html (built into the game): the sky clock (Nut's arch, the timekeeper since round 8)
# with its two other concepts, and the rebalanced glass jars. Pictures from egyptr8.py.
import html
E = html.escape


def links(src):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(l)) for l, u in src) + '</ul>'


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def sections(D, REL, img):
    o = []
    o.append('<section class="card" id="skyclock"><h2>The sky clock (built in, round 8)</h2><p>Owner\'s rules: "Do these changes in the code and document. Do this by default from now on unless stated otherwise." and "As for the hourglass, anything that looks like a water glass or a hourglass is rejected by default." '
             'So the barque clock of round 7 (a bowl over a basin) is gone, and the timekeeper is no vessel at all.</p>'
             '<p><b>A, the sky clock (built in): Nut.</b> The sky goddess arches over the earth on her hands and feet, as on the ceilings of Seti I\'s tomb and the Dendera temple; at dusk she swallows the sun, it travels through her body through the twelve hours of night, and she gives birth to it at dawn (the Book of Nut). '
             'Here the sun disc rides her arch from her mouth toward her feet: the gold of her body ahead of the sun, and the twelve hour stars ahead of it, are the time left; behind it the stars are out. It reads at a glance as an amount running out (a gold arch shortening, a big red-gold disc moving along it), and it is the story of Dawnward: the night running toward dawn. '
             'The disc is twice the size of round 7\'s barque (a 3.8 px disc at HUD size, ringed in black), the weak spot fixed. In the rewind the sun runs back toward her mouth, white and cool, and the stars relight. '
             'It is the checkpoint (lit when reached: the sun runs back to her mouth, then the night runs out over 8 s and round again), the HUD\'s three hours, the gates\' timers and the rewind\'s picture.</p>'
             '<p><b>Its light:</b> a halo round the disc, the gold ahead of it shining, a sheen along her body toward the nearest lamp: added light in the shared 2D code (both modes). At the checkpoint, in the WebGL scene, the sun also carries its own light through the light map (a light that travels along the arch), so the stone round it is lit where the sun is. No new pass; the HUD redraws only when its picture changes.</p>'
             '<p><b>B, the twelve gates.</b> The sun\'s barque sails a band of hour gates (the Book of Gates), each closing behind it. Clear as a progress bar; at HUD size only six gates fit. '
             '<b>C, the diagonal star clock.</b> Decan stars lighting in turn across a grid, as on Middle Kingdom coffin lids. Distinctive, but the count of stars is slow to read at a glance.</p>' +
             links([('Nut (goddess): her arched body, swallowing and bearing the sun', 'https://en.wikipedia.org/wiki/Nut_(goddess)'), ('Book of Nut (the sun\'s night journey through her body)', 'https://en.wikipedia.org/wiki/Book_of_Nut'),
                    ('Dendera zodiac and the temple\'s ceilings (Nut over the hours)', 'https://en.wikipedia.org/wiki/Dendera_zodiac'), ('KV17, Seti I: the astronomical ceiling', 'https://thebanmappingproject.com/tombs/kv-17-sety-i'),
                    ('Book of Gates (the twelve hour gates)', 'https://en.wikipedia.org/wiki/Book_of_Gates'), ('Diagonal star tables on coffin lids', 'https://en.wikipedia.org/wiki/Decan')]))
    for k, nm in (('A', 'A, the sky clock (built in)'), ('B', 'B, the twelve gates'), ('C', 'C, the diagonal star clock')):
        o.append('<h3>%s</h3><div class="g4">%s%s%s<div style="display:flex;gap:8px;align-items:center">%s%s</div></div>' % (E(nm), fig(img, 'r8_clock_%s_10.png' % k, 'full'), fig(img, 'r8_clock_%s_5.png' % k, 'half'), fig(img, 'r8_clock_%s_1.png' % k, 'nearly out'),
                                                                                                             fig(img, 'r8_clock_%s_hud.png' % k, 'HUD size (x3)'), fig(img, 'r8_clock_%s_gate.png' % k, 'gate clock (x3)')))
    o.append('<div class="g4" style="margin-top:8px">%s%s%s%s</div><div class="g4" style="margin-top:8px">%s%s%s%s</div></section>' % (
        fig(img, 'r8_clock_run.gif', 'Running out, then the rewind'), fig(img, 'r8_clock_game_torch.jpg', 'Checkpoint, Torchlight'), fig(img, 'r8_clock_game_classic.jpg', 'Checkpoint, Classic'), fig(img, 'r8_hud.png', 'The HUD: hearts and two hours left'),
        fig(img, 'r8_gate_torch.jpg', 'A gate\'s clock, Torchlight'), fig(img, 'r8_gate_classic.jpg', 'Classic'), fig(img, 'r8_rewind_torch.jpg', 'The rewind, Torchlight'), fig(img, 'r8_rewind_classic.jpg', 'The rewind, Classic')))
    o.append('<section class="card" id="jars8"><h2>The jars, rebalanced (built in, round 8)</h2><p>Round 7\'s weak spot: the liquid hid the glass. Now the jar is drawn in its own blue core-formed glass first, the liquid is a glow seen through it, lower (at most 70% of the body) and added as light, with a soft glow of its colour, and the yellow and white trails are drawn over it, thicker. The bubbles, the level and tilt when drunk, the glow and the pickup box are as before.</p>'
             '<div class="g4">%s%s%s%s</div></section>' % (fig(img, 'r8_jars.png', 'Small, large, extra life, poison'), fig(img, 'r8_jars_drink.gif', 'Being drunk'), fig(img, 'r8_jar_game_torch.jpg', 'On the floor, Torchlight'), fig(img, 'r8_jar_game_classic.jpg', 'Classic')))
    o.append('<section class="card" id="prince8"><h2>The prince, round 8 (built in)</h2><p>Owner: "bare chest, only a loin cloth, darker skin; open to ideas about the hair", then "use the pleated Egyptian design as best it can be represented", '
             '"give the hint of muscular/athletic men on all characters" and "some sheen on the skin".</p><ul>'
             '<li><b>Dress:</b> bare-chested in a short pleated shendyt of white linen, its front panel\'s fine pleats fanning from the belt with soft shade bands between (drawn on the skeleton, so they follow him and do not crawl), tied with the orange sash, its ends hanging at the front. The robbers keep plain, unpleated, greyer undyed kilts and coloured head cloths, so he stands apart at a glance.</li>'
             '<li><b>Skin:</b> a warm deep brown. Checked on the darkest floors (the Green Hall, Nun, Hawara, Meroë) in both modes: the lamp-lit edge the figures already get, the white kilt and the fillet keep him readable.</li>'
             '<li><b>Hair (built in):</b> his own short black hair with its swept tail, under a plain linen fillet. Shown for choice: a short rounded wig (as the workmen in tomb paintings), close-cropped with a single side lock, long hair tied back.</li>'
             '<li><b>Athletic, for all characters:</b> broader shoulders over a narrower waist, rounded upper arms and fuller calves in the outline, and a few soft shade lines on the bare chests (the chest\'s lower edge, the belly, the serratus) and at the deltoid. The outline change is in the figures\' mask too (his and the robbers\', <code>PAL_GSIL</code>); hit boxes, poses and timing are untouched. Skeletons unchanged.</li>'
             '<li><b>Oiled skin:</b> soft highlights on the shoulders, chest, upper arms and calves on the side toward the key light (the lamp the figure lighting already uses), stronger near a flame. Not added light, so it never blooms, and it stays under the figure light\'s cap.</li></ul>' +
             links([('Shendyt (the pleated kilt)', 'https://en.wikipedia.org/wiki/Shendyt'), ('Clothing in ancient Egypt', 'https://en.wikipedia.org/wiki/Clothing_in_ancient_Egypt'),
                    ('Artistic canons of body proportions: the Egyptian grid', 'https://en.wikipedia.org/wiki/Artistic_canons_of_body_proportions'), ('G. Robins, Proportion and Style in Ancient Egyptian Art (1994)', 'https://sactx.aspendiscovery.org/Record/69932'),
                    ('Deir el-Medina strikes: "no clothing, no ointment" among the workmen\'s complaints', 'https://en.wikipedia.org/wiki/Deir_el-Medina_strikes'), ('Museo Egizio: the Turin Strike Papyrus', 'https://collezionepapiri.museoegizio.it/en-GB/section/Papyrus-Collection/History-and-content/Highlights-Turin-Strike-Papyrus/'),
                    ('Sidelock of youth (the side-lock option)', 'https://en.wikipedia.org/wiki/Sidelock_of_youth')]) +
             fig(img, 'r8_prince_compare.png', 'v62 (top), round 7 (middle), round 8 (bottom): stand, jump, hang, guard, lunge, fallen') +
             '<div class="g2" style="margin-top:8px">%s%s</div>' % (fig(img, 'r8_prince_hair.png', 'Hair: own hair with a linen fillet (built in), a rounded wig, a side lock, long and tied back'), fig(img, 'r8_prince_run.gif', 'Running, Torchlight')) +
             '<h3>Athletic and oiled: before and after</h3><div class="g2">%s%s</div>' % (fig(img, 'r8_muscle_before.png', 'Before: the prince and the robbers (recruit, soldier, captain)'), fig(img, 'r8_muscle_after.png', 'After: broad shoulders, narrow waist, muscle shading, the sheen')) +
             '<h3>On the darkest floors</h3><div class="g4">' + ''.join(fig(img, 'r8_prince_on_%s_%s.jpg' % (lk, m), '%s, %s' % (nm, m)) for lk, nm in (('osiris', 'Green Hall'), ('nun', 'Nun'), ('hawara', 'Hawara'), ('meroe', 'Meroë')) for m in ('torch', 'classic')) + '</div></section>')
    return o
