# egyptround2.py: the second round's sections of egypt_themes.html (the name, the font, the lamps, the traps), with the notes and
# the sources they rest on. egyptpage.py imports it and puts the sections before the themes; the pictures come from egyptprop.py.
import html, json, os
E = html.escape
W = lambda t: 'https://en.wikipedia.org/wiki/' + t
GRIF = 'https://tutankhamun.griffith.ox.ac.uk/index.php/object-records/'

LAMPS = {
 'nun': ('A torch of fat-soaked linen on a stick, in a bronze socket', 'Tutankhamun\'s tomb held torches of this kind, set in bronze cups held up by ankh-shaped stands (see the Halls). The tomb builders of Deir el-Medina drew yarn for wicks from the state stores, and their lamps and wicks were counted.',
   [('Griffith Institute, Tutankhamun archive: the ankh "candlesticks" holding a bronze torch-cup', 'https://archive.griffith.ox.ac.uk/index.php/tutankhamun-archive-ii-6-73'), ('UCL Digital Egypt: Deir el-Medina ostraca (supply of yarn for lamp wicks)', 'https://www.ucl.ac.uk/museums-static/digitalegypt/deirelmedine/ostraca.html'), ('E. Tuttle, Egyptian lighting (Herodotus 2.62: oil and salt; castor oil; animal fat)', 'https://mysite.du.edu/~etuttle/classics/egyplite.htm')]),
 'west': ('Tutankhamun\'s candlestick: an ankh with arms raised, holding a bronze cup with a linen torch, on a stepped base', 'Found in the antechamber; on the wall it stands on a ledge, in an opening it stands on the floor.',
   [('Griffith Institute object 41a: bronze and wood candlestick, Cairo JE 62355-6', GRIF + '41a'), ('Object 41d, JE 62353', GRIF + '41d'), ('Archive description: "an anthropomorphic ankh with arms raised to hold a bronze torch-cup"', 'https://archive.griffith.ox.ac.uk/index.php/tutankhamun-archive-ii-6-73')]),
 'blue': ('Tutankhamun\'s triple lamp: three lotus cups of calcite (an open flower and two buds) on one stem', 'In the tiled halls\' openings it stands on a pale stand instead of the old star lantern hanging on a chain. There are no star-shaped lamps in Egypt: the star belongs to the painted ceilings, and the first round put it there (and on the doors).',
   [('Griffith Institute object 174: calcite lamp with three floral cups, Cairo JE 62112', GRIF + '174'), ('Egypt Museum: the triple lamp, traces of oil in its cups', 'https://egypt-museum.com/tutankhamun-triple-lamp-with-lotus-shapes/')]),
 'meroe': ('The bronze hanging lamp from Meroë: a griffin-head hook, an acanthus leaf as a flame guard', 'From pyramid Meroë North 29, AD 140-155, with a Meroitic inscription; local work, or an import reworked. On the wall it hangs from an iron rod, in an opening from a lamp stand.',
   [('MFA Boston 24.959, hanging lamp, Meroë', 'https://www.mfa.org/collections/object/hanging-lamp-145854'), ('Georgia State thesis: the Meroë bronze lamps made locally', 'https://scholarworks.gsu.edu/art_design_theses/47'), ('Penn Museum: bronze lamp on a high stand, Karanog', 'https://penn.museum/collections/object/188782')]),
 'osiris': ('Tutankhamun\'s lit chalice: a lotus cup of translucent calcite; when it burns, a painting on the inner cup shows through the stone', 'The painting shows the king and queen; the queen offers palm branches (years without end). Drawn as a small dark figure inside the glowing cup.',
   [('Global Egyptian Museum: the double-chalice lamp, JE 62111', 'https://globalegyptianmuseum.org/record.aspx?id=15110')]),
 'foggara': ('A Roman mould-made pottery lamp on a ledge or a lamp stand', 'The Garamantes imported oil lamps (with wine, oil and tableware) through their trade with Rome; the lamp is the common Roman type.',
   [('D. Mattingly, the Garamantes and their trade (British Academy)', 'https://www.thebritishacademy.ac.uk/documents/596/21-mattingly.pdf'), ('Garamantes', W('Garamantes'))]),
 'deffufa': ('A black-topped red bowl as a saucer lamp, on a clay ring or a wooden stand', 'A stylisation, said honestly: no Kerma lamp is known to me; Kerma\'s best-known ware is its thin black-topped red pottery, so the lamp is made from it.',
   [('Kerma culture: its black-topped red ware', W('Kerma_culture'))]),
 'wells': ('The tomb workers\' light: a pottery bowl of fat with twisted linen wicks, on a peg in the plaster or a wooden stand', 'What lit the painters in the Valley\'s corridors: wicks of linen yarn in fat or oil, issued and counted.',
   [('UCL Digital Egypt: Deir el-Medina ostraca on lamps and wick yarn', 'https://www.ucl.ac.uk/museums-static/digitalegypt/deirelmedine/ostraca.html'), ('E. Tuttle, Egyptian lighting', 'https://mysite.du.edu/~etuttle/classics/egyplite.htm'), ('Science Museum: pottery lamp from an Egyptian tomb', 'https://collection.sciencemuseum.org.uk/objects/co8015139/pottery-shell-form-oil-lamp-from-egyptian-tomb-oil-lamp')]),
 'napata': ('A bronze fire bowl on a tripod, or on a wall bracket', 'After the high bronze lamp stands of the Kushite graves (Karanog); a bowl of fire suits the forge style\'s bigger flame.',
   [('Penn Museum: bronze lamp on a high stand, Karanog', 'https://penn.museum/collections/object/188782')]),
 'aksum': ('A bronze lamp with a hound chasing an ibex along its rim', 'The Aksumite lamp with a dog biting an ibex; a bronze lamp also came from Matara (Eritrea).',
   [('SFSU image archive: "Oil lamp with dog biting an ibex", Axumite', 'https://diva.sfsu.edu/browse/tags/axumite'), ('Matara, Eritrea (a bronze oil lamp among its finds)', 'https://en.wikipedia.org/wiki/Matara,_Eritrea')]),
 'hawara': ('A pottery saucer with the wick over its rim, on a mudbrick ledge or a tall pottery stand', 'The plain Egyptian saucer lamp had no spout: the wick lay over the rim. Pottery stands carried bowls in tombs and temples.',
   [('E. Tuttle, Egyptian lighting (saucer lamps, wicks over the rim)', 'https://mysite.du.edu/~etuttle/classics/egyplite.htm')]),
 'shali': ('A pottery lamp in a niche cut in the kershef; in an opening, a bronze lamp hanging on three chains', 'Siwa\'s Amun oracle flourished in Graeco-Roman times, when hanging bronze lamps were in use in Egypt.',
   [('Siwa Oasis', 'https://en.wikipedia.org/wiki/Siwa_Oasis'), ('MFA Boston: a hanging bronze lamp of the period', 'https://www.mfa.org/collections/object/hanging-lamp-145854')]),
}

TRAPS = [
 ('portcullis', 'Granite portcullis', 'real', 'gate (and the closer\'s gate)',
  'Old Kingdom pyramids closed their corridors with granite slabs lowered in grooves: three in the Great Pyramid\'s antechamber, dropped once the king was inside; three in succession in Unas\'s corridor. The game\'s gate becomes a slab of Aswan rose granite rising and falling in the same grooves, on the same timing.',
  [('Live Science: the portcullis "machine" in the Great Pyramid\'s antechamber', 'https://livescience.com/55347-primitive-machine-in-great-pyramid-protected-pharaoh.html'), ('Pyramid of Unas: three granite portcullises in the corridor', 'https://en.wikipedia.org/wiki/Pyramid_of_Unas')]),
 ('roofblock', 'Sliding roof block', 'real', 'falling stone',
  'At Hawara, Petrie found 20-ton roof blocks meant to slide down into the passages as trapdoors (left open, never slid), and a burial chamber sealed by a roof slab lowered on sand. The falling stone becomes a dressed limestone block with sand running from its seams; it drops on the same trigger.',
  [('Hawara (Petrie: sliding trapdoor roof blocks, blind passages)', 'https://en.wikipedia.org/wiki/Hawara'), ('Petrie, Kahun, Gurob and Hawara (1890), the chamber', 'https://digi.ub.uni-heidelberg.de/diglit/petrie1890/0016'), ('History Hit: the roof block lowered with sand', 'https://www.historyhit.com/locations/hawara-pyramid/')]),
 ('sandfloor', 'Sand-filled shaft under a slab', 'partly real', 'loose floor',
  'Late Period tombs at Abusir and Saqqara sank their burial chambers 20-30 m down shafts and filled the shafts with sand, which robbers had to dig out. A floor that drops into such a shaft is the game\'s part. The loose tile shows sand in its seams, and sand pours through it as it gives.',
  [('Czech Institute of Egyptology: Abusir tomb R3, a 23 m shaft, its sand fill dug out by thieves', 'https://cegu.ff.cuni.cz/en/research/projects/field-projects/abusir/the-saite-persian-cemetery/tomb-r3/'), ('The tomb of Iufaa, Abusir: robbers\' tunnels stopping above the chamber', 'https://cegu.ff.cuni.cz/en/research/projects/field-projects/abusir/the-saite-persian-cemetery/the-tomb-of-iufaa/'), ('Saqqara Saite tombs project', 'https://uni-tuebingen.de/en/241681')]),
 ('plug', 'Granite plugs sliding down the corridors', 'real (the plugs), game (the chase)', 'the sandstorm chase (the same front, speed, rows and kill line)',
  'The Great Pyramid\'s ascending passage is still blocked by granite plugs, generally held to have been slid down from the Grand Gallery after the burial (Piazzi Smyth argued they were built in). Robbers tunnelled round them. A plug is the size of its passage, so the chase is drawn as one plug in every corridor row the chase spans: a block a storey high at most (floor to ceiling) and two tiles long, filling the corridor\'s depth, its polished leading face at the storm\'s front, pushing sand ahead of it. Where there is no floor at the front (a shaft, the air over a drop) the line is marked by the pale dust it throws up, the height of the span, since the storm\'s rule kills there too. The storm\'s shader, veil and baked frames are off behind it.',
  [('The Grand Gallery and the plugs (academic paper)', 'https://www.academia.edu/36645718'), ('Howard Vyse (1840-42) on the passages', 'https://digi.ub.uni-heidelberg.de/diglit/howard_vyse1841bd2/0264/text_ocr')]),
 ('wellshaft', 'Well shaft', 'real (its purpose debated)', 'the damaging drop and the pits (no new look needed yet)',
  'New Kingdom royal tombs cut a deep well shaft across the corridor (Thutmose III\'s KV34 among the early ones; Seti I\'s KV17 the best known). It may have caught flood water, or served as a ritual shaft; the Theban Mapping Project leaves its purpose open. The game\'s damaging drop already reads as such a shaft; a plastered and painted rim is the obvious next step.',
  [('Theban Mapping Project, KV17: the well chamber', 'https://thebanmappingproject.com/tombs/kv-17-sety-i'), ('Minor tombs in the Valley of the Kings', 'https://en.wikipedia.org/wiki/Minor_tombs_in_the_Valley_of_the_Kings')]),
 ('snakes', 'Snakes, and the spells against them', 'real', 'the snakes (unchanged)',
  'The Pyramid Texts of Unas hold a run of spells against snakes (Utterances 226-243), on the burial chamber\'s west gable: the serpent is told to lie down and crawl away. The game\'s snakes are already right for Egypt; a carved spell on the wall above their tunnels could mark them.',
  [('Pyramid Texts Online: Unas, the snake spells', 'https://pyramidtextsonline.com/sarcwestgable.html'), ('Pyramid Texts Online: Utterance 293, antechamber', 'https://pyramidtextsonline.com/anteeast.html')]),
 ('stakes', 'Bronze-tipped stakes', 'film invention', 'spikes',
  'No spike pit is known from an Egyptian tomb: tomb security was blocking slabs, plugs, sand fill, hidden and blind passages, and curses written on the walls. Spikes are from the films and pulp (The Mummy, the Tomb Raider games). Kept for play, re-skinned as acacia shafts with bronze tips so they at least belong to the materials of the place.',
  [('The secret passages and traps of the pyramids (popular account; for what is claimed)', 'https://historyrise.com/article/the-secret-passages-and-hidden-traps-inside-the-pyramids/')]),
]
PULP = ('Left out as film or pulp: mummies walking and curses that kill (the hard limits), scarab swarms, rooms that fill with sand, rolling boulders, '
        'floors of spikes behind false doors, swinging blades, darts from the walls. The game\'s choppers, saws, pendulums, darts and fire vents are of '
        'this kind; their mechanics stay as the owner wants, and they could be framed as the tomb robbers\' own traps, which is the Relic Hunter way '
        '(Sydney Fox\'s rivals rig the site; the place itself is real).')

FONTS = [('rokkitt', 'Rokkitt + Jost', 'Rokkitt: a geometric slab serif by Vernon Adams (finished by Kalapi Gajjar), OFL 1.1, weights 100-900. Slab serifs were sold as "Egyptian" from the 1810s, in the craze that followed Napoleon\'s expedition: a link to Egypt through type history, not a fake-papyrus face. Firm at small sizes, so it can carry the HUD\'s FLOOR n and the timer digits.',
          [('Google Fonts: Rokkitt', 'https://fonts.google.com/specimen/Rokkitt/about'), ('Slab serif: why "Egyptian"', W('Slab_serif'))]),
         ('marcellus', 'Marcellus + Jost', 'Marcellus: a flared serif after Roman inscriptional capitals, by Astigmatic (Brian J. Bonislawsky), OFL 1.1. Monumental and calm, but Roman rather than Egyptian, and a single weight.',
          [('Google Fonts: Marcellus', 'https://fonts.google.com/specimen/Marcellus/about')]),
         ('poiret', 'Poiret One + Jost', 'Poiret One: a geometric Art Deco display face by Denis Masharov, OFL 1.1. Art Deco is itself the Egyptomania of the 1920s, after Tutankhamun\'s tomb was opened (the Relic Hunter adventurer\'s era), but its hairline strokes vanish at HUD sizes on a phone.',
          [('Fontsource: Poiret One, OFL 1.1', 'https://fontsource.org/fonts/poiret-one/about')]),
         ('now', 'Before: Lalezar + Vazirmatn', 'The v62 Persian pair, for comparison.', [])]
BODY = ('Jost, the body and HUD face in all three: a geometric sans after the 1920s German sans-serifs (Futura\'s family), by Owen Earl (indestructible type*), '
        'OFL, variable weights; clear at 7-9 px. Replaces Vazirmatn.', [('Google Fonts: Jost', 'https://fonts.google.com/specimen/Jost/about'), ('github.com/indestructible-type/Jost', 'https://github.com/indestructible-type/Jost')])


WATER = ('<section class="card" id="clock"><h2>The water clock</h2>'
 '<p>The hourglass is a medieval European object (the first sure pictures are 14th-century); Egypt measured the night\'s hours by the stars and by water. The oldest surviving water clock is the '
 '<b>Karnak clepsydra</b> of Amenhotep III (c. 1390-1350 BC; Cairo, JE 37525): an alabaster vessel wider at the mouth than the foot, its water running out through a spout near the base (lost, '
 'below a baboon of Thoth on a djed pillar). Inside, twelve columns of marks, one for each month, give the hours of the <i>night</i>: the scale was long in winter and short in summer. '
 'Outside are the decans, the star groups whose risings marked the night\'s hours, and the king offering to Re-Horakhty with Thoth behind. The Amduat, painted in the Well Corridors\' tombs, is the sun\'s journey '
 'through those twelve hours: the clock measures the night the game climbs through.</p>'
 '<p><b>In the game</b> (look and words only: rules, timings, the save and its keys are unchanged): the checkpoint is a water clock on its pedestal; reaching it fills it, and its water then runs out through the '
 'spout into a basin, the hour slipping away (as the sand ran). The HUD\'s three glasses are three small clocks, full for a measure in hand and dry when spent; a gate\'s timer is a clock whose water is the time left. '
 'The rewind turns the water back: a cool grade instead of sepia, the ripples it always had, drops drawn back to the prince, and the words "The water turns back". The hints, How to play ("Water: '
 'you carry three measures of water; every water clock refills them"), the gate messages and the death screen say water clock and water. It is drawn with Canvas2D calls (no new pass, no clip), '
 'so it is the same in Classic and on the WebGL path.</p>'
 '<ul><li><a href="https://egypt-museum.com/clepsydra-of-karnak/">Egypt Museum: the clepsydra of Karnak</a></li>'
 '<li><a href="https://aea.mcmaster.ca/index.php/en/database/ars/ar1-type-menu/water-clock-amenhotep-iii">Ancient Egyptian Astronomy database (McMaster): water clock of Amenhotep III, its hour scales and decoration</a></li>'
 '<li><a href="https://collection.sciencemuseumgroup.org.uk/objects/co454/egyptian-water-clock">Science Museum Group: Egyptian water clock</a></li>'
 '<li><a href="https://en.wikipedia.org/wiki/Decan">Decans, the star clocks of the night hours</a>; <a href="https://en.wikipedia.org/wiki/Merkhet">the merkhet, sighting them</a></li>'
 '<li><a href="https://en.wikipedia.org/wiki/Amduat">Amduat, the twelve hours of the night</a></li><li><a href="https://en.wikipedia.org/wiki/Hourglass">Hourglass: its first sure picture, Lorenzetti, 1338</a></li></ul>')


def links(src):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(l)) for l, u in src) + '</ul>' if src else ''


def sections(D, REL, img):
    prop = json.load(open(os.path.join(D, 'prop.json')))
    import egyptaudit
    out = [egyptaudit.section()]
    # ---- the name
    out.append('''<section class="card" id="name"><h2>The name: Dawnward</h2>
<p>The title, built in (the page title, title screen, manifest name and short name, home-screen title, bench header). The prince goes up through the twelve hours of the night, as the sun's boat (the barque of Ra) sails through the twelve regions
of the underworld in the Amduat and the Book of Gates, and comes out at dawn: floor 60 is sunrise. <i>Dawnward</i>: toward the dawn.</p>
<p><b>Trademark check (quick, not legal advice):</b> no game, app or trademark named "Dawnward" turned up on 2026-10-17. Searched: the web for "Dawnward" game and
app, Steam, itch.io and the App Store by name, and US trademark listings. Near names, all different: <i>Dawnforge Nightfall</i> (Steam, coming soon),
<i>The Blood of Dawnwalker</i> (Rebel Wolves), <i>Dawnfolk</i>, <i>Dawngrown</i>, <i>20 Minutes Till Dawn</i>; US marks DAWNDAWN (application, 2026) and DAWNFLOWER
(electronics). Before publishing, search the USPTO and EUIPO registers directly, and the App Store and Google Play.</p>''' +
        links([('Steam: Dawnforge Nightfall', 'https://store.steampowered.com/app/4736730'), ('itch.io: Dawnfolk', 'https://itch.io/post/13382640'), ('20 Minutes Till Dawn', W('20_Minutes_Till_Dawn')),
               ('DAWNDAWN, US application 50073863', 'https://trademarkregistration.app/Trademark/Details/50073863'), ('DAWNFLOWER, US 90628480', 'https://www.trademarkelite.com/trademark/trademark-detail/90628480/DAWNFLOWER'),
               ('USPTO trademark search (to do by hand)', 'https://tmsearch.uspto.gov/'), ('Amduat', W('Amduat'))]) +
        '<div class="g2">%s%s</div></section>' % (
            '<figure>%s<figcaption>Title screen, as built (Rokkitt + Jost)</figcaption></figure>' % img('font_rokkitt_title.jpg', 'title'),
            '<figure>%s<figcaption>Floor card</figcaption></figure>' % img('font_rokkitt_card.jpg', 'card')) +
        '')
    out[-1] = out[-1].replace('</section>', '<div class="g2" style="margin-top:8px"><figure>%s<figcaption>HUD and the floor\'s title banner</figcaption></figure><figure>%s<figcaption>HUD, top strip</figcaption></figure></div></section>' % (
        img('font_rokkitt_hud.jpg', 'hud'), img('font_rokkitt_hudtop.jpg', 'hud top')))
    # ---- the water clock
    cl = prop.get('clock', [])
    out.append(WATER + ''.join('<div class="g4" style="margin-top:8px">' + ''.join('<figure>%s<figcaption>%s, %s</figcaption></figure>' % (img(c['shots'][m] + '_' + w + '.jpg', m), E(c['label']), '%s %s' % (m.title(), w)) for m in ('torch', 'classic') for w in ('close', 'wide')) + '</div>' for c in cl) + '</section>')
    # ---- the fonts
    out.append('<section class="card" id="font"><h2>The font</h2><p><b>Built in: Rokkitt for the title, cards and the HUD\'s numbers, with Jost for text.</b> Both are on Google Fonts (the game loads its fonts from there), under the SIL Open Font License 1.1: free for commercial use and embedding, the licence kept with the files, the reserved names not used for changed versions. The pictures replace the game\'s two faces in place (its Google Fonts request answered with the candidate), so the sizes and layout are the game\'s.</p>')
    out.append('<p>%s</p>%s' % (E(BODY[0]), links(BODY[1])))
    for key, lab, note, src in FONTS:
        out.append('<h3>%s</h3><p>%s</p>%s<div class="g2"><figure>%s<figcaption>Title</figcaption></figure><figure>%s<figcaption>Floor card</figcaption></figure></div><figure style="margin-top:6px">%s<figcaption>HUD strip</figcaption></figure>' % (
            E(lab), E(note), links(src), img('font_%s_title.jpg' % key, key), img('font_%s_card.jpg' % key, key), img('font_%s_hudtop.jpg' % key, key)))
    out.append('</section>')
    # ---- the lamps
    out.append('<section class="card" id="lamps"><h2>Lamps</h2><p>The lanterns of pierced brass, the star lanterns of coloured glass and the iron fire baskets are Islamic or medieval in shape. Each theme gets a lamp from its own place and time, drawn in the game (<code>drawLampEg</code>, built in: on by default, <code>EGP.lamps=false</code> turns it off). Only the shape changes: the flame sits where the style\'s light already is, so the light, its colour and its flicker in Torchlight are as before. Each shows the lamp before (v62, Torchlight), then the proposal in Torchlight, in Classic, and unlit (Classic); on a wall, then in an opening (standing, or hanging where the place had hanging lamps). Pictures are 2x, cropped round the lamp.</p>')
    names = {e['look']: e for e in prop['lamps']}
    for look, (what, note, src) in LAMPS.items():
        e = names.get(look)
        if not e:
            continue
        out.append('<h3>%s: %s</h3><p>%s</p>%s' % (E(e['name']), E(what), E(note), links(src)))
        for kind in ('wall', 'free'):
            sh = [s for s in e['shots'] if s['kind'] == kind]
            if not sh:
                continue
            out.append('<div class="g4 lamp">' + ''.join('<figure>%s<figcaption>%s, %s</figcaption></figure>' % (
                img(s['stem'] + '_close.jpg', s['lab']), 'on a wall' if kind == 'wall' else 'in an opening', {'now': 'before, v62 (Torchlight)', 'torch': 'Torchlight', 'classic': 'Classic', 'unlit': 'unlit'}[s['lab']]) for s in sh) + '</div>')
    out.append('</section>')
    # ---- the traps
    out.append('<section class="card" id="traps"><h2>Traps</h2><p>What Egyptian tombs really did against robbers, against what the films invented, and how each would map onto a trap the game already has. The re-skins are built in, on by default (<code>EGP.traps</code>, <code>EGP.plug</code> turn them off), with the same hit boxes and timing; nothing goes into the generator. New trap mechanics are a later round. <i>Real</i> means the device is attested in excavated tombs; <i>film invention</i> means it is not.</p><p>%s</p>' % E(PULP))
    tr = {t['id']: t for t in prop['traps']}
    for tid, name, kind, onto, note, src in TRAPS:
        t = tr.get(tid)
        out.append('<h3>%s · <span style="color:var(--ac)">%s</span> · maps onto: %s</h3><p>%s</p>%s' % (E(name), E(kind), E(onto), E(note), links(src)))
        if not t:
            continue
        for k, p in enumerate(t['poses']):
            out.append('<p class="meta">Pose %d: floor %d, seed %d · %s%s</p><div class="g4">' % (k + 1, p['n'], p['seed'], E(p['name']), (' · ' + E(p['state'])) if p.get('state') else '') + ''.join(
                '<figure>%s<figcaption>%s, %s</figcaption></figure>' % (img(p['shots'][m] + '_' + w + '.jpg', m), m.title(), w) for m in ('torch', 'classic') for w in ('close', 'wide')) + '</div>')
    out.append('</section>')
    return out, [('audit', 'What changes'), ('name', 'The name'), ('clock', 'Water clock'), ('font', 'The font'), ('lamps', 'Lamps'), ('traps', 'Traps')]
