# egyptround9.py: round 9's section of egypt_themes.html (built in): the prince with a gold sash, a lean young build and natural cropped
# hair; round 8 and round 9 side by side, the chest before and after, the hair options in the game. Pictures from egyptr9.py.
import html
E = html.escape


def links(src):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(l)) for l, u in src) + '</ul>'


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def sections(D, REL, img):
    o = ['<section class="card" id="prince9"><h2>The prince, round 9 (built in; his build redrawn in round 10 and his belt in round 11, above; the hair stays)</h2><p>Owner: "For the prince: I\'d make the sash golden and the chest not that pronounced, study a bit profiles of muscular/athletic youth. Also not fond of the headband and the hair."</p><ul>'
         '<li><b>Gold sash:</b> a gold-yellow girdle, like gilded linen, with a bright upper edge that takes the lamp\'s tint; it is drawn, not added light, so it never blooms. Its tie ends hang at the front as before.</li>'
         '<li><b>A lean young build:</b> the broad shoulders and narrow waist stay, but his torso is slimmer and the chest flatter, with one soft line under it and a faint shoulder line, no belly or rib shading; his arms and calves are leaner. '
         'The robbers keep the heavier build of grown men, which also tells them apart at a glance. What it is based on: the young male figures of Egyptian art, slim and long-limbed with broad shoulders and a narrow waist (Tutankhamun\'s ka statues; the youths of New Kingdom tomb paintings such as Nebamun\'s), '
         'and the lean, flat-chested build of an athletic late-teen in profile. I worked from the Egyptian figures; I did not study photographs of athletes for this round.</li>'
         '<li><b>Hair:</b> the fillet and round 8\'s options (wig, side lock, long hair) are dropped. Three natural cuts were tried on the figure in the game, in both modes: <b>close-cropped, following the skull, with a soft highlight (built in)</b>; short tight curls with a little volume; an ear-length bob. '
         'The crop is built in because it reads cleanly at phone size from every pose, as the short natural hair of working men and youths in tomb paintings (wigs were the elite\'s, for occasions), and it keeps his head the simple shape of the original prince; the curls are a close second, but their bumps read as noise at game size.</li></ul>' +
         links([('JSTOR Daily: hair, gender and status in ancient Egypt (after Gay Robins: non-elite men with their natural hair, elite men\'s wigs)', 'https://daily.jstor.org/hair-gender-and-social-status-in-ancient-egypt'), ('British Museum: wigs and hairstyles in ancient Egypt', 'https://www.britishmuseum.org/blog/wigs-and-hairstyles-ancient-egypt'),
                ('Egyptian Museum, Cairo: the ka statue of Tutankhamun', 'https://egyptianmuseumcairo.eg/artefacts/statue-of-the-ka-of-tutankhamun'), ('The tomb of Nebamun (British Museum paintings)', 'https://en.wikipedia.org/wiki/Tomb_of_Nebamun'),
                ('Artistic canons of body proportions: the Egyptian grid', 'https://en.wikipedia.org/wiki/Artistic_canons_of_body_proportions')]) +
         '<div class="g2">%s%s</div>' % (fig(img, 'r9_prince_before.png', 'Round 8: the prince and a robber (soldier)'), fig(img, 'r9_prince_after.png', 'Round 9: gold sash, lean build, cropped hair; the robber unchanged')) +
         '<h3>Hair, on the figure and in the game (Torchlight above, Classic below)</h3>' + fig(img, 'r9_hair_sheet.png', 'Close-cropped (built in), short curls, ear-length bob') +
         '<div class="g4" style="margin-top:8px">' + ''.join(fig(img, 'r9_hair_%s_%s.jpg' % (h, m), '%s, %s' % (nm, m)) for m in ('torch', 'classic') for h, nm in (('crop', 'cropped (built in)'), ('curls', 'curls'), ('bob', 'bob'))) + '</div>' +
         '<figure style="max-width:420px;margin-top:8px">%s<figcaption>Running, Torchlight</figcaption></figure></section>' % img('r9_prince_run.gif', 'run')]
    o.append('<section class="card" id="flasks9"><h2>The flasks, as an Egyptian would have made them (built in, round 9)</h2><p>Owner: "Those painted glass jars look more Amerindian than Egyptian. Let\'s make an exercise in imagination: if you would that the original potions how would they have looked if an Egyptian would have made it."</p>'
             '<p>The core-formed jars, with their combed zigzags and feather trails, are gone. The flasks are v62\'s again, with the same round bulb, neck, sizes, red, gold and blue liquid, bubbles, tilt when drunk and pickup boxes. They are imagined as a craftsman of Tutankhamun\'s workshops would have made them: clear glass with a pale turquoise tint, so the liquid glows through as in the original, and one or two touches each, with no painted pattern.</p><ul>'
             '<li><b>Small (heal):</b> a thin gold rim at the mouth and a stopper that is a round knob of turquoise-blue faience, in place of the cork. Faience was the Egyptians\' everyday "shining" substitute for turquoise, coloured with copper.</li>'
             '<li><b>Large (heal):</b> v62\'s gold rim. The stopper is a closed lotus bud in blue faience with gold sepals, and a tiny gold cartouche tag hangs on a cord at the neck, the way jars in the tomb were labelled and sealed. The lotus and papyrus are the two plants of Tutankhamun\'s great calcite vases (the union of the Two Lands).</li>'
             '<li><b>Extra life:</b> gold leaf over the shoulder of the bulb, above the liquid, and a gold stopper shaped as a papyrus umbel. The papyrus is the other plant of those vases; the gold marks it as the rarest potion.</li>'
             '<li><b>Poison:</b> dark glass, like obsidian, that dims the blue glow but still shows it, and a polished black stone stopper. It has no gold.</li></ul>'
             '<p>The glass tint stays light because Tutankhamun\'s glass, like his blue and turquoise headrests, is coloured through. A strong blue would have hidden the liquid, which was round 7\'s trouble. The gold is drawn colour, not added light, so it does not bloom. Cost: a few more small fills per flask on screen, with no new pass and no texture.</p>' +
             links([('Global Egyptian Museum: Tutankhamun\'s calcite vase (JE 62114), with the plants of the union of the Two Lands', 'https://www.globalegyptianmuseum.org/detail.aspx?id=15098'),
                    ('C. Hallmann (Peeters, 2019): the ornamental calcite vessels of Tutankhamun, made for scented unguents', 'https://www.torrossa.com/en/resources/an/5262242'),
                    ('Corning Museum of Glass: Dr Brill\'s research on the glass from Tutankhamun\'s tomb (the blue and turquoise headrests, the few vessels)', 'https://blog.cmog.org/2012/glass-king-tut-dr-brills-research-ancient-egyptian-glass-tutankhamuns-tomb'),
                    ('The Met: Egyptian faience, technology and production (a turquoise substitute, coloured with copper, "shining")', 'https://www.metmuseum.org/en/essays/egyptian-faience-technology-and-production'),
                    ('Egyptian blue', 'https://en.wikipedia.org/wiki/Egyptian_blue'),
                    ('The Met: gold in ancient Egypt (wire, twisted and braided, soldered on)', 'https://www.metmuseum.org/essays/gold-in-ancient-egypt')]) +
             '<h3>v62 (top), round 8\'s jars (middle), round 9 (bottom): small, large, extra life, poison</h3><div class="g2">%s%s</div><div class="g2" style="margin-top:8px">%s%s</div></section>' % (
                 fig(img, 'r9_flasks_compare.png', 'v62, round 8, round 9'), fig(img, 'r9_flasks_drink.gif', 'Being drunk: the level, the tilt, the bubbles'),
                 fig(img, 'r9_flask_game_torch.jpg', 'On the floor, Torchlight'), fig(img, 'r9_flask_game_classic.jpg', 'Classic')))
    return o
