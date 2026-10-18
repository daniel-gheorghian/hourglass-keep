# egyptround9.py: round 9's section of egypt_themes.html (built in): the prince with a gold sash, a lean young build and natural cropped
# hair; round 8 and round 9 side by side, the chest before and after, the hair options in the game. Pictures from egyptr9.py.
import html
E = html.escape


def links(src):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(l)) for l, u in src) + '</ul>'


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def sections(D, REL, img):
    o = ['<section class="card" id="prince9"><h2>The prince, round 9 (built in)</h2><p>Owner: "For the prince: I\'d make the sash golden and the chest not that pronounced, study a bit profiles of muscular/athletic youth. Also not fond of the headband and the hair."</p><ul>'
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
    return o
