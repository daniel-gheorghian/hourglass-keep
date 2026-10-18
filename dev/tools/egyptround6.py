# egyptround6.py: the sixth round's sections of egypt_themes.html: the Green Hall's and Meroë's softer tints (before and after), and
# the prince in Egyptian dress (the research, the three variants, the one built in, how he reads on every floor, and what else of
# his still looks medieval). egyptpage.py puts them after the second round's; the pictures come from egyptprince.py and egyptshot.py.
import html, json, os
E = html.escape


def links(src):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(l)) for l, u in src) + '</ul>'


SRC = [('Sidelock of youth: the mark of children, and of the 18th Dynasty\'s princes', 'https://en.wikipedia.org/wiki/Sidelock_of_youth'),
       ('Hilary Wilson on the sidelock of youth (a plait, its end twisted)', 'https://the-past.com/feature/hilary-wilson-on-the-sidelock-of-youth'),
       ('MFA Boston: block statue of Prince Mentuherkhepeshef, Ramesses II\'s son, recarved with the sidelock', 'https://collections.mfa.org/objects/131438/block-statue-of-prince-mentuherkhepeshef'),
       ('Crown prince Ramesses: Ramesses II\'s sons in procession', 'https://the-past.com/feature/crown-prince-ramesses-pharaoh-in-waiting'),
       ('Shendyt, the kilt of linen', 'https://en.wikipedia.org/wiki/Shendyt'),
       ('Khat, the headcloth (the nemes is the king\'s)', 'https://en.wikipedia.org/wiki/Khat_(apparel)'),
       ('Brooklyn Museum: broad collar, "wesekh, the broad one"', 'https://brooklynmuseum.org/objects/3453'),
       ('The Met: faience broad collar, Amarna', 'https://www.metmuseum.org/art/collection/search/549199'),
       ('Ancient Egyptian art: men shown red-brown, its conventions', 'https://en.wikipedia.org/wiki/Art_of_ancient_Egypt'),
       ('Khopesh (two in Tutankhamun\'s tomb)', 'https://en.wikipedia.org/wiki/Khopesh'),
       ('Egypt Museum: the khopesh of Tutankhamun', 'https://egypt-museum.com/khopesh-sword-of-tutankhamun/'),
       ('The Met: kneeling Kushite king (cap crown, bandeau, ram\'s-head amulets)', 'https://www.metmuseum.org/art/collection/search/545027'),
       ('The Met: ram\'s-head amulet, worn on a cord by the Kushite kings', 'https://www.metmuseum.org/art/collection/search/547771')]
VAR = {'A': ('A: New Kingdom prince (built in)', 'A shaven head with the sidelock of youth, the plaited lock that marked the 18th Dynasty\'s princes and Ramesses II\'s sons; a pleated linen kilt with a red belt; bare chest under a broad collar of faience beads; gold armlets and bracelets; sandals; kohl; the red-brown of Egyptian painting\'s men; the bronze khopesh. It says "prince" at a glance without a crown: the uraeus is the king\'s, so he has none.'),
       'B': ('B: the khat headcloth', 'The same dress under the khat, the plain linen headcloth gathered in a bag at the nape, worn by kings and the court in daily life (the striped nemes is the king\'s alone). Reads clearly at phone size, but a white head is less Egyptian-young than the sidelock and close to the guards\' helmets in shape.'),
       'C': ('C: a Kushite (Napatan) youth', 'Darker skin; a close cap with a gold band, after the Kushite kings\' cap crown (without its uraei); a gold ear stud; a ram\'s-head amulet on a cord, as the Kushite kings wore it; a yellow belt. For the Kush half of the game; it could be the prince of the Meroë, Napata and Kerma floors if the owner wants him to change with the land.')}


def sections(D, REL, img):
    out = []
    pj = os.path.join(D, 'prince.json')
    pr = json.load(open(pj)) if os.path.exists(pj) else {'variants': [], 'themes': []}
    # ---- tints
    out.append('<section class="card" id="tints"><h2>Softer green and red</h2><p>Owner: "The green and red level are maybe too heavily tinted." The Green Hall of Osiris and the Forges of Meroë are now a third less saturated, the same hues: '
               'their stone palette, the lamps\' and windows\' light (kept at full brightness), the ambient light (never under <code>AMB_MIN</code>), the haze and mist, and the colour grade (a theme\'s own grade, <code>gr</code>, over its style\'s), in both modes; '
               'the incense is paler and the slag a little weaker. The Stelae of Aksum (the same crypt style) and Napata (the forge style) are unchanged. Before (the previous build, bdc4d84) and after:</p>')
    for t, nm in (('t04', 'The Green Hall of Osiris'), ('t03', 'The Forges of Meroë')):
        out.append('<h3>%s</h3><div class="g4">%s</div>' % (nm, ''.join('<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, lab), lab) for f, lab in (
            ('tint_before_%s_p0_torch_wide.jpg' % t, 'before, Torchlight'), ('%s_p0_torch_wide.jpg' % t, 'after, Torchlight'), ('tint_before_%s_p0_classic_wide.jpg' % t, 'before, Classic'), ('%s_p0_classic_wide.jpg' % t, 'after, Classic')))))
    out.append('</section>')
    # ---- the prince
    out.append('<section class="card" id="prince"><h2>Round 6: the prince in full Egyptian dress (superseded)</h2><p>Researched as the themes were: how a young royal or noble man of the New Kingdom, and of Kush in the Napatan age, was dressed and shown. '
               '<b>Round 6 (superseded in round 7 by the plain prince above).</b> Variant A was built in then. The same skeleton, poses, hit boxes and timings; gameplay and the bot are untouched (the drawing alone changes, <code>drawFigureHD</code> with <code>pal.egy</code>). '
               'The figures\' mask and the beams\' figure light work from his new outline. The guards\' silhouettes keep their own outline (<code>PAL_GSIL</code>). The khopesh is drawn along the sword\'s line and length, so the fight reads the same. '
               '<code>setHero(\'B\')</code> or <code>(\'C\')</code> shows the others.</p>' + links(SRC))
    for v in pr['variants']:
        t, d = VAR[v['v']]
        out.append('<h3>%s</h3><p>%s</p><figure>%s<figcaption>Poses drawn by the game at 3x: stand, jump, hang, climb, guard, lunge, fallen</figcaption></figure>' % (E(t), E(d), img(v['sheet'], 'poses')))
        shots = sorted(v['shots'].items())
        out.append('<div class="g4" style="margin-top:8px">' + ''.join('<figure>%s<figcaption>floor %d, %s</figcaption></figure>' % (img(k + '.jpg', k), n, 'Torchlight' if k.endswith('torch') else 'Classic') for k, n in shots) + '</div>')
        out.append('<figure style="margin-top:8px;max-width:420px">%s<figcaption>Running, Torchlight</figcaption></figure>' % img(v['gif'], 'run'))
    if pr['themes']:
        out.append('<h3>Variant A on every theme\'s floor (Torchlight, phone size)</h3><div class="g4">' + ''.join('<figure>%s<figcaption>%s</figcaption></figure>' % (img(t['img'], t['name']), E(t['name'])) for t in pr['themes']) + '</div>')
    out.append('''<h3>Round 6's proposals for the rest (done in round 7, see above)</h3><ul>
<li><b>The guards:</b> helmeted swordsmen with plumes, in the old palace colours, with straight steel blades. As tomb robbers they should match: bare-chested men in kilts or short tunics, head cloths, a few with
the leather caps of New Kingdom soldiers; khopesh, axe, club or spear; the captain in a soldier\'s leather corselet (the robbers of the <a href="https://en.wikipedia.org/wiki/Abbott_Papyrus">tomb-robbery papyri</a> were workmen and officials). The skeletons can stay.</li>
<li><b>The flasks:</b> glass bottles with corks read medieval. Egyptian ones: a small faience or pottery jar (a kohl pot for small, an alabastron for large, a gold-capped jar for the extra life), poison in a dark stone jar.</li>
<li><b>The HUD's lives:</b> the red triangles are neutral, but could be a small ankh or a heart (ib) in faience.</li>
<li><b>The title card and menus:</b> done (Dawnward, Rokkitt and Jost); the pause and title screens' plain panels could take a cavetto-cornice frame.</li>
<li><b>The old figure style</b> (Graphics: "New characters" off) still draws him with the old shapes in the new colours.</li></ul></section>''')
    return out, [('tints', 'Softer tints'), ('prince', 'The prince')]
