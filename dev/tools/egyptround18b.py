# egyptround18b.py: round 18b's section of egypt_themes.html (built in): the swing rigged in rope and timber, and every chain in the
# game turned to rope. Pictures from egyptr18b.py; the floors used in egypt_themes/r18b.json.
import html, json, os
E = html.escape


def links(src):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(l)) for l, u in src) + '</ul>'


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def sections(D, REL, img):
    J = json.load(open(os.path.join(D, 'r18b.json')))
    rigs = ', '.join('%s %d' % (lk, n) for lk, n, sd in J.get('rigs', []))
    return ['<section class="card" id="r18b"><h2>Round 18b (built in): the swing on ropes, and no chains</h2>'
            '<p>Owner: "about the swing jump: replace the chains with rope, and make the whole thing Egyptian looking; also check we are not using chains anywhere else"</p>'
            '<h3>The swing</h3><ul>'
            '<li><b>Ropes</b>, not link chains: two taut laid ropes, drawn straight (a hanging load keeps a rope straight), each about 2.5 px wide in a dark outline. '
            'The lay shows as the diagonal grooves between strands, running down to the right as on an S-plied rope (Z-spun yarns plied S, the usual make of Egyptian grass cordage: 94% of the plied grass cordage at Berenike), '
            'and the crown of each strand is lit on its left, the lamps\' side, with the right edge in shade. The lay is counted from the top of the rope, so it stays on the rope as the rope swings. '
            'Palm-fibre ropes are drawn with three strands, closer set (the three-strand palm-fibre rope from Deir el-Bahri); halfa and papyrus with two.</li>'
            '<li><b>The fibre and the timber follow the theme</b>: papyrus rope by the water (Nun, Osiris, Hawara: the papyrus ropes of the Red Sea harbour at Mersa Gawasis); halfa grass in the Theban and Saqqara halls and at Aksum (the halfa rope found hanging in Seti I\'s tomb shaft); palm fibre in Kush and the Sahara oases. '
            'The pole and the log: imported cedar in the royal halls (west, blue, osiris), sycomore fig at Nun, acacia (the hard native timber) at Hawara and in Kush, tamarisk in the Sahara, juniper at Aksum. Rope wears with the stonework: darker and greyer, more loose fibres, a longer fray.</li>'
            '<li><b>The anchor, in perspective</b>: a round timber set across under the ceiling, front to back, its end grain standing 3 px proud of the lintel\'s face (the logs over which the ropes ran in the Great Pyramid\'s antechamber, set in grooves in its walls; the roof poles of mud-brick houses; Aksum\'s beam ends). '
            'The view looks down on the rooms, so no ceiling\'s underside is seen: the log shows only its end and the near part of its underside, receding up and to the right under the lintel\'s edge, and the far rope comes out from behind the lintel. The near rope is wound three turns round the log. '
            'Before, the chains\' ceiling plates were drawn 4 px too low: the near plate floated under the lintel and the far one sat on its face.</li>'
            '<li><b>The pole</b>: wood, its end grain to us at the near end, a little grain along it; each rope lashed three turns round its end with a frayed tail; the grip bound in rawhide, dark and shiny where hands have held it (rawhide and cord bindings on Egyptian handles and chariots). No metal: the pole and the ropes are no longer in Torchlight\'s metal mask.</li>'
            '<li><b>The cue</b>: when the swing will carry him, a glint now runs up the near rope\'s fibres to the log (it ran along a metal pole), the grip keeps its warm glow, and the sound is the ropes taking the strain, a run of short fibrous creaks (ropecreak) under the chime; the creak at each turn is two short groans of rope on wood instead of a metal squeal. '
            'Round 18a\'s jet stream on the throw is unchanged. Physics, hit boxes and the bot are unchanged (swingtest: all floors ok).</li></ul>'
            '<h3>Every chain in the game, and what it became</h3><ul>'
            '<li><b>The swing bar</b>: two link chains and metal ceiling plates; <b>two laid ropes on a timber log</b> (above).</li>'
            '<li><b>The pendulum blade</b>: dark chain links on the arm by its pivot; <b>the arm lashed to its pivot with four turns of rope</b>.</li>'
            '<li><b>Siwa\'s hanging lamp</b> (a lamp in an opening): three chains from the lintel; <b>one palm-fibre cord from a peg, knotted, and three short cords to the lamp</b> (a lamp in a cord sling).</li>'
            '<li><b>A fallen lamp\'s scar</b>: in an opening (every style), a broken chain hanging from the lintel; in the tile style, a thin chain from the ceiling: <b>a cut cord with a frayed end</b>.</li>'
            '<li><b>The fallen lantern</b> (tile style): a chain of links trailing on the floor; <b>its cord trailing off, frayed</b>.</li>'
            '<li><b>The backdrops</b> of the Waters of Nun and the Furnaces of Meroë: iron chains with rings hanging in front of the view; <b>ropes</b>, some ending in a knot and a frayed tail, some carrying a water jar in a rope sling (Nun) or a basket (Meroë).</li>'
            '<li><b>The tower flag\'s card</b>: "Counterweights and chains, everywhere." now reads "Counterweights and <b>ropes</b>, everywhere."</li>'
            '<li><b>Already rope</b>: the counterweight lift and the paternoster (round 13: rope, wooden wheels, stone slabs).</li>'
            '<li><b>Kept, not seen in play</b>: the iron chains of the lifts and the chained lanterns of the palace and tile lamps are still in the code behind the debugging switches EGP.traps and EGP.lamps (off, they draw the v61 looks for comparison); with the switches on, as shipped, none is drawn. '
            'Not chains: the Meroë lamp hangs on its own bronze hook from a bracket (Boston MFA 24.959); the gates\' and lifts\' gratings are stone slabs; the guards wear no mail; there are no shackles, chandeliers or chains in the HUD or the menus. The word "chain" survives only in code names (the paternoster is <code>t:\'chain\'</code>, the hidden passage\'s "crumbling chain" of floor tiles).</li></ul>'
            '<h3>Pictures</h3>' +
            '<p class="meta">The still sheet of the swing is retired (the film above shows it): its figure had the hump on the back that round 19 took out (r19_pose.png).</p>' +
            fig(img, 'r18b_swing.gif', 'Pumping and the throw, 18a (left) and 18b (right), Torchlight, 0.1 s a frame: the ropes swing with the bar from the log') +
            fig(img, 'r18b_rigs.png', 'The rig in the twelve themes\' fibres and timbers, Torchlight, 1:1 (floors: %s)' % rigs) +
            fig(img, 'r18b_chains.png', 'The other chains, before and after, Torchlight and Classic, 2x: the pendulum\'s pivot, a fallen lamp\'s scar in an opening, the fallen lantern (tile style), Siwa\'s hanging lamp') +
            fig(img, 'r18b_bgropes.png', 'The backdrops\' hanging chains, before and after: the Waters of Nun (with jars) and the Furnaces of Meroë (with baskets)') +
            links([('Mersa/Wadi Gawasis: the rope cave of the Middle Kingdom harbour (Boston University)', 'https://www.bu.edu/articles/2009/archaeologist-kathryn-bard%e2%80%99s-amazing-egyptian-digs/'),
                   ('Coils of ancient Egyptian rope found in a cave (Discovery News)', 'https://www.timesifters.org/coils-of-ancient-egyptian-rope-found-in-cave-by-rossella-lorenzi-discovery-news/'),
                   ('Veldmeijer and Zazzaro, The rope cave at Mersa Gawasis: a preliminary report (UCA)', 'https://repositorio.uca.edu.ar/handle/123456789/11940'),
                   ('Veldmeijer, Cordage from Berenike, 2001 season (zS2 the usual make of halfa cordage)', 'https://repositorio.uca.edu.ar/bitstream/123456789/11836/1/cordage-from-2001-season.pdf'),
                   ('British Museum EA43222: a rope of halfa grass, one end knotted', 'https://www.britishmuseum.org/collection/object/Y_EA43222'),
                   ('World History Encyclopedia: halfa grass rope from the tomb of Seti I', 'https://www.worldhistory.org/image/8361/halfa-grass-rope-from-the-tomb-of-seti-i/'),
                   ('Electrum Magazine: three-strand palm-fibre rope from Deir el-Bahri (ROM), Egyptian cordage', 'https://www.electrummagazine.com/?p=4746'),
                   ('Louvre: palm-fibre basket from Deir el-Medina, "brun clair"', 'https://collections.louvre.fr/en/ark:/53355/cl010023658'),
                   ('Wikipedia: Woodworking in Egypt (acacia, sycomore, tamarisk; cedar from Lebanon; mortise and tenon, lashing)', 'https://en.wikipedia.org/wiki/Woodworking'),
                   ('Abd Elhamid, ancient Egyptian woods (IntechOpen)', 'https://www.intechopen.com/online-first/1201517'),
                   ('Perring 1839: the four rope grooves in the Great Pyramid\'s antechamber', 'https://digi.ub.uni-heidelberg.de/diglit/perring1839bd1/0004'),
                   ('Kassel University: a full-scale replica of the antechamber\'s closing mechanism (ropes over logs)', 'https://kobra.uni-kassel.de/bitstreams/554b494a-ebf1-4a8b-948a-e192160d2a2f/download'),
                   ('EXARC: Reinventing the Egyptian pulley (no pulley known before the Middle Kingdom; ropes ran over fixed timbers)', 'https://exarc.net/sites/default/files/2025-11/Reinventing%20the%20Egyptian%20Pulley%20_%20The%20EXARC%20Journal.pdf')]) + '</section>']
