# egyptpage.py [dir]: builds egypt_themes.html (next to the folder egypt_themes/) from the pictures and the JSON that egyptshot.py
# and egyptfx.py leave there, and the themes' notes and sources below. Run from dev/tools after the two capture scripts.
import html, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
D = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'egypt_themes')
REL = os.path.basename(D)
shots = json.load(open(os.path.join(D, 'shots.json')))
fx = json.load(open(os.path.join(D, 'fx.json')))
fxby = {f['look']: f for f in fx['fx']}
W = lambda t: 'https://en.wikipedia.org/wiki/' + t
# per theme: what it is, what changed (for the five that were there), motifs and their sources, its own effects
NOTES = {
 'nun': dict(was='The Cistern', what='The primeval waters of Nun, out of which the world rose; the Amduat puts water in the sun boat\'s second and third hours.',
   changed='Name. The backdrop\'s Roman arcade became papyrus-bundle columns with closed-bud capitals under flat architraves, still standing in the water. Hangings are now painted linen (see the Halls). The vaulted arches stay: the Ramesseum\'s brick store-rooms are barrel-vaulted.',
   src=[('Amduat, hours 2-3: the waters of Wernes and of Osiris', 'https://en.wikipedia.org/wiki/Amduat'), ('Nu, the primeval waters', W('Nu_(mythology)')),
        ('Papyriform columns, bundle shafts and bud capitals', W('Ancient_Egyptian_architecture')), ('Ramesseum: vaulted mudbrick store-rooms', W('Ramesseum'))],
   eff='Water caustics thrown up through the arches and glints on the water (kept from the Cistern, now tied to the theme, not the drawing style); water drips in both modes.'),
 'west': dict(was='Sandstone Halls', what='A mortuary temple on the west bank at Thebes, where the dead went with the setting sun.',
   changed='Name. The domed city with minarets (Islamic-era, centuries out of place) became temple pylons with their flagstaffs, the Theban hills with the pyramid-shaped peak of el-Qurn, palms (the crenellated towers are gone). The "Persian hangings" became Egyptian painted linen: a block border, lotus friezes, a reed mat, a star ceiling under a kheker frieze, the winged sun over a broad collar, a papyrus column. Pointed arches became post and lintel under a cavetto cornice; window views show a pylon, an obelisk and a palm.',
   src=[('Pylon: two battered towers flanking a gate, flagstaffs in their niches', W('Pylon_(architecture)')), ('Al-Qurn, the peak over the Valley of the Kings', W('Al-Qurn')),
        ('Cavetto cornice', W('Cavetto')), ('The painter\'s colours: Egyptian blue among them', W('Egyptian_blue')), ('Winged sun', W('Winged_sun')),
        ('Blue lotus (the petals in the tiled halls)', W('Nymphaea_caerulea'))],
   eff='New: dust hanging in the open arches, lit by the low sun at dusk and dawn and cool under the moon, with more motes in the shafts (1.8x). Based on: the west bank at sunset, the light low over the Theban hills and through the temple courts, and the dust of the desert edge. Torchlight (mist pass); Classic keeps the sand gusts.'),
 'blue': dict(was='Lapis Gallery', what='The rooms under Djoser\'s step pyramid at Saqqara, faced with thousands of small faience tiles set like reed matting.',
   changed='Name, a bluer-green tile. The girih-star dado became rows of small glazed oblongs bound by bands, like the Saqqara panels; the backdrop\'s pavilions and cypresses became the step pyramid and its panelled enclosure wall; the lobed arches and girih stars became lintels and the five-pointed star of the tomb ceilings; the window lattice became upright stone slats.',
   src=[('Djoser\'s blue chambers: faience tiles imitating reed mats (Met catalogue text)', 'https://www.almendron.com/artehistoria/arte/culturas/egyptian-art-in-age-of-the-pyramids/catalogue-third-dynasty/trackback/'),
        ('Pyramid of Djoser and its niched enclosure wall', W('Pyramid_of_Djoser')), ('Egyptian faience', W('Egyptian_faience'))],
   eff='Stronger: long soft highlights slide across the faience walls as the flames move, on top of the glaze sheen on the dado (now 0.8) and the single tiles flashing near the lamps. Based on: Egyptian faience\'s glassy glaze, which throws back lamplight in bright moving highlights. (both modes).'),
 'meroe': dict(was='Ember Forge', what='The iron works of Meroë in Kush: slag heaps that made it "the Birmingham of Africa", iron worked there from the 7th-6th century BC.',
   changed='Name. The steep royal pyramids of Meroë now stand behind the furnaces and their smoke. Kept: the forge, its palette and its heat.',
   src=[('Humphris et al., iron production at Meroë (UCL)', 'https://discovery-pp.ucl.ac.uk/10042893/9/Humphris%20et%20al.%20JFA%20approved.pdf'), ('Pyramids of Meroë: small, steep (about 72 degrees)', 'https://en.wikipedia.org/wiki/Pyramids_of_Mero%C3%AB')],
   eff='New: slag glowing in the cracks of the floor, pulsing slowly, its own light; and the flames\' air shimmers much more (0.8 against the forge\'s 0.5). Based on: Meroë\'s iron-smelting furnaces and the slag heaps they left round the city. Torchlight (mist pass and the heat mask); Classic gets soft glows on fixed spots.'),
 'osiris': dict(was='Jade Crypt', what='The hall of Osiris, green for rebirth, where the heart is weighed against the feather of Ma\'at.',
   changed='Name. The domed tombs of the backdrop became shrines under a cavetto cornice; the muqarnas hoods over the niches became false doors (a doorway carved for the dead to pass); the star window has five points.',
   src=[('Book of the Dead, spell 125 (Cornell)', 'https://exhibits.library.cornell.edu/godsandscholars/feature/cornell-papyrus-egypt-ptolemaic-period-320-30-bce'), ('Osiris, green-skinned', 'https://en.wikipedia.org/wiki/Osiris'),
        ('False door (Penn Museum)', 'https://www.penn.museum/collections/object/335457'), ('Book of Gates: the judgement hall in the fifth hour', 'https://en.wikipedia.org/wiki/Book_of_Gates')],
   eff='New: thin layers of pale green incense smoke drifting across the hall at different heights, lit by the lamps, over the crypt\'s mist and wet sheen. Based on: incense burnt before Osiris and in the judgement scenes of the Book of the Dead, where censers stand before the god. Torchlight (mist pass); Classic draws a few pale bands drifting.'),
 'foggara': dict(what='The Garamantes\' foggaras in the Fezzan: water channels dug under the desert, a shaft every few metres; over 550 counted, in use about 400 BC to AD 700.',
   changed=None, src=[('Garamantes and their foggaras (Oxford Classics)', 'https://www.classics.ox.ac.uk/node/2758756'), ('Garamantes', W('Garamantes')), ('Qanats (the same way of carrying water)', W('Qanat'))],
   eff='The sky\'s shafts fall almost straight down (from overhead, down the foggaras\' shafts) at every time of day, with more dust in them; water caustics through the arches; drips in both modes.'),
 'deffufa': dict(what='Kerma in Kush: the Western Deffufa, a mudbrick temple some 18 m high, three storeys; round huts and acacias around it.',
   changed=None, src=[('Western Deffufa', 'https://en.wikipedia.org/wiki/Western_Deffufa'), ('Kerma culture', W('Kerma_culture'))],
   eff='Dust: a low drift of dust along the floors, blown sideways (the mist pass with wind), and sand gusts in both modes; no wet sheen.'),
 'wells': dict(what='The Valley of the Kings: corridors going down hour by hour, painted with the Amduat, and a deep well shaft across them (KV34, Thutmose III).',
   changed=None, src=[('Amduat (KV34 the earliest complete copy)', 'https://en.wikipedia.org/wiki/Amduat'), ('Minor tombs and the wells', 'https://en.wikipedia.org/wiki/Minor_tombs_in_the_Valley_of_the_Kings'), ('Valley of the Kings', W('Valley_of_the_Kings'))],
   eff='More dust motes in the shafts (2.2x), a faint still dust over the floors; no wet sheen.'),
 'napata': dict(what='Napata in Kush: Gebel Barkal, the holy mountain whose pinnacle was seen as a rearing cobra, and the steep pyramids of Nuri and el-Kurru.',
   changed=None, src=[('Sudan\'s World Heritage sites: Gebel Barkal and the sites of the Napatan region', 'https://en.wikipedia.org/wiki/List_of_World_Heritage_Sites_in_Sudan'), ('Jebel Barkal', W('Jebel_Barkal')), ('Nuri', W('Nuri'))],
   eff='Heat (0.4) and dust blown hard along the floors; no wet sheen.'),
 'aksum': dict(what='Aksum before its churches: the field of stelae carved as many-storeyed houses with false doors and windows, over granite-lined royal tombs. Only the pre-Christian stelae and tombs; no church, cross or Ark.',
   changed=None, src=[('Aksum\'s monumental architecture and stelae (Met essay)', 'https://www.metmuseum.org/ja/essays/monumental-architecture-and-stelae-of-the-aksumite-empire'), ('King Ezana\'s Stele', 'https://en.wikipedia.org/wiki/King_Ezana%27s_Stele'), ('UNESCO, Aksum', 'https://whc.unesco.org/en/news/125')],
   eff='New: a highland mist that rolls along the floor in the wind (deeper and moving, the wet floor kept), and crystals in the granite walls catching the lamps. Based on: Aksum stands at about 2,100 m on the Tigray plateau, where mists form over the plateau in the rains; its stelae and tombs are cut from local granite (nepheline syenite). The mist in the Torchlight mist pass; the crystals as sharp points near the lamps, in both modes.'),
 'hawara': dict(what='Hawara: the mudbrick pyramid of Amenemhat III, its passages with blind turns and sliding roof blocks, and the temple beside it that Herodotus called the Labyrinth.',
   changed=None, src=[('Hawara (Petrie: blind passages, trapdoor roof blocks)', 'https://en.wikipedia.org/wiki/Hawara'), ('History Hit, Hawara pyramid', 'https://www.historyhit.com/locations/hawara-pyramid/')],
   eff='Dry: a slow dust instead of the dungeon style\'s mist, no wet sheen, no drips or caustics.'),
 'shali': dict(what='Shali at Siwa: the fortress town built of kershef (lumps of salt and mud) that a three-day rain in 1926 melted; date palms and salt lakes around it. Architecture only, no people.',
   changed=None, src=[('Siwa Oasis: Shali and the 1926 rain', 'https://en.wikipedia.org/wiki/Siwa_Oasis'), ('Kanaga: the remote Siwa oasis', 'https://www.kanaga-at.com/en/trip-info/egypt/the-remote-siwa-oasis/')],
   eff='Salt: the kershef glitters in the lamplight (a soft shimmer in Torchlight\'s mist pass; single crystals flash in both modes); no wet sheen.'),
}
CARE = ('<p>The two "need care" themes chosen: <b>Shali at Siwa</b> (an abandoned ruin since the 1920s; only its architecture is used, nothing of the '
        'living Siwan community or its dress) and <b>Aksum\'s stelae field</b> (pre-Christian funerary monuments in an archaeological site; nothing of the '
        'churches, no cross, no Ark). Not chosen: Tassili n\'Ajjer (rock art in the Tuareg\'s own land, which would end up as decoration) and Ghadames '
        '(a town whose people were moved out and which was damaged in war; its gender-split streets cannot be a game mechanic).</p>')
def img(fn, alt):
    return '<a href="%s/%s"><img loading="lazy" src="%s/%s" alt="%s"></a>' % (REL, fn, REL, fn, html.escape(alt))
out = []
out.append('''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Dawnward: themes, lamps, traps, name</title>
<style>:root{--bg:#f6f2ea;--fg:#1f1a14;--mu:#6b6156;--card:#fffdf8;--ln:#e2d9c8;--ac:#8a3a1c}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#15120f;--fg:#eee6d8;--mu:#a59a8b;--card:#1e1a16;--ln:#332c25;--ac:#e09a6a}}
:root[data-theme="dark"]{--bg:#15120f;--fg:#eee6d8;--mu:#a59a8b;--card:#1e1a16;--ln:#332c25;--ac:#e09a6a}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,sans-serif}main{max-width:1180px;margin:0 auto;padding:16px}
h1{font-size:26px;margin:8px 0}h2{font-size:20px;margin:0 0 4px}h3{font-size:14px;margin:14px 0 6px;color:var(--mu);text-transform:uppercase;letter-spacing:.04em}
a{color:var(--ac)}.card{background:var(--card);border:1px solid var(--ln);border-radius:10px;padding:14px;margin:18px 0}
.meta{color:var(--mu);font-size:13px}.g2{display:grid;grid-template-columns:1fr 1fr;gap:8px}.g4{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}
img{width:100%;height:auto;display:block;border-radius:6px}figure{margin:0}figcaption{font-size:12px;color:var(--mu);margin-top:2px}
nav a{display:inline-block;margin:2px 8px 2px 0;font-size:13px}table{border-collapse:collapse;font-size:13px}td,th{border-bottom:1px solid var(--ln);padding:4px 8px;text-align:left}
@media (max-width:720px){.g2,.g4{grid-template-columns:1fr}}.lamp img{image-rendering:auto}</style></head><body><main>
<h1>Dawnward: twelve themes of Egypt, Kush and the Sahara</h1>
<p class="meta">Branch <code>egypt</code>. Pictures from <code>egyptshot.py</code> and <code>egyptfx.py</code> (this Mac's Chromium; Torchlight and Classic), the page from <code>egyptpage.py</code>.</p>
<div class="card" style="border-color:var(--ac)"><p><b>Built into the game.</b> Everything on this page is now the game on the egypt branch (merged with v62, the WebGL release), on by
default: the twelve themes and their order, the lamps, the re-skinned traps (granite portcullis, roof block, sand floor, bronze-tipped stakes, granite plugs for the
chase), the water clock in place of the hourglass, the title Dawnward and the fonts Rokkitt and Jost. Mechanics, timings, the generator, the bot, saves and the cache
key are unchanged. <code>EGP={lamps,traps,plug}</code> turns the look of the lamps and traps back to v61 for debugging. The pictures show the game as built.</p></div>
<div class="card"><p><b>How it is laid out.</b> Twelve themes, four floors each. Each block of four floors takes the drawing style the generator builds it by
(dungeon, palace, tile, forge, crypt in turn), and within that style the theme is chosen by the light (dusk 1-20, night 21-40, dawn 41-60, then round again)
and by which 60-floor turn of the day it is; the schedule repeats every 180 floors (<code>SCHED</code>, <code>themeOf</code>). Floors 1-20 are the five reworked themes
at dusk; the Forges and the Green Hall come back by moonlight on floors 33-40; all twelve appear by floor 60. Each theme keeps one of the five drawing styles
(stone courses, arches, lamps, metal, windows) and adds its own backdrop, hangings, palette, Torchlight light and effects.</p>
<p><b>The floors are unchanged.</b> The generator never reads the theme; it builds by the five-style turn (<code>GEN_STYLE</code>), and now every floor's theme has that
same style. Checked: floors 1-72 with three seeds each are identical to v62, walls, floors, traps, the bot's route, guards and lamp placement.
<code>metrics40.py</code>: FLAGS none.</p>''' + CARE + '''
<p><b>Everywhere</b> (all styles): pointed arches, doors and windows became post and lintel under a cavetto cornice (the Cistern-style vaults stay round); the girih stars became the
five-pointed star of the tomb ceilings; the niches\' muqarnas became false doors; the little-arch cornice became a kheker frieze; the hangings became painted linen and reed mats;
the tiled halls\' rose petals became blue lotus petals. Built in since: the lamps, the traps\' looks, the water clock, the title and the fonts (sections below). The guards are unchanged.</p></div><nav>''')
for t in shots['themes']:
    out.append('<a href="#t%d">%d. %s</a>' % (t['i'], t['i'] + 1, html.escape(t['name'])))
import egyptround2
R2, R2NAV = egyptround2.sections(D, REL, img)
out.append(' · ' + ''.join('<a href="#%s"><b>%s</b></a>' % (k, l) for k, l in R2NAV + [('objects', 'Light on objects'), ('r7prince', 'Plain prince'), ('robbers', 'Robbers'), ('barque', 'Barque clock'), ('jars', 'Jars'), ('hearts', 'Hearts, panels'), ('tints', 'Softer tints'), ('prince', 'Round 6 prince')]))
out.append('</nav>')
out.extend(R2)
import egyptround7
R7, R7NAV = egyptround7.sections(D, REL, img)
out.extend(R7)
import egyptround6
R6, R6NAV = egyptround6.sections(D, REL, img)
out.extend(R6)
OB = fx.get('obj', [])
if OB:
    out.append('<section class="card" id="objects"><h2>Light on the new objects</h2><p>Drawn with Canvas2D calls in the shared code (added light, no new pass, no clip), so they are the same in Classic and on the WebGL path: the water clock\'s water catches the nearest lamp (the key light the figures use) and its stream glints; the sand\'s grains catch the light as they turn; rose granite crystals in the portcullis and the plugs flash in the torchlight, more near a lamp (granite\'s feldspar and mica cleavage faces); the calcite lamps glow through their stone (the Osiris chalice\'s painted figures show through it, as in Tutankhamun\'s lit chalice); the rewind\'s cool wash now reads on the red and gold floors. Torchlight left, Classic right, 0.1 s a frame.</p>' +
               ''.join('<h3>%s</h3><div class="g2">%s</div>' % (html.escape(o['label']), ''.join('<figure>%s<figcaption>%s</figcaption></figure>' % (img(o['gif'][m], m), m.title()) for m in ('torch', 'classic') if m in o['gif'])) for o in OB) + '</section>')
for t in shots['themes']:
    N = NOTES[t['look']]
    LT = ['dusk', 'night', 'dawn']
    fl = ', '.join('%d-%d %s' % (n, n + 3, LT[((n - 1) // 20) % 3]) for n in t.get('floors', []))
    out.append('<section class="card" id="t%d"><h2>%d. %s</h2><p class="meta">Floors %s (in 180; the schedule repeats) · drawing style <code>%s</code> · look <code>%s</code>%s</p><p>%s</p>' % (
        t['i'], t['i'] + 1, html.escape(t['name']), fl, t['style'], t['look'], (' · was <b>%s</b>' % N['was']) if N.get('was') else ' · new', html.escape(N['what'])))
    if N.get('changed'):
        out.append('<p><b>What changed:</b> %s</p>' % html.escape(N['changed']))
    out.append('<h3>Sources</h3><ul>' + ''.join('<li><a href="%s">%s</a></li>' % (html.escape(u), html.escape(l)) for l, u in N['src']) + '</ul>')
    out.append('<h3>Its own effects</h3><p>%s</p>' % html.escape(N['eff']))
    f = fxby.get(t['look'])
    if f:
        cost = '<table><tr><th>?prof stage, ms a frame (Mac, 240 frames)</th><th>masks</th><th>atmo</th><th>compose</th></tr>' + ''.join(
            '<tr><td>%s</td><td>%.3f</td><td>%.3f</td><td>%.3f</td></tr>' % (k, f[k2]['masks'], f[k2]['atmo'], f[k2]['compose']) for k, k2 in (('with its effects', 'on'), ('without (LFX emptied)', 'off'))) + '</table>'
        out.append('<div class="g2"><figure>%s<figcaption>Torchlight, 0.1 s a frame (floor %d)</figcaption></figure><div>%s</div></div>' % (img(f['gif'], 'effect'), f['n'], cost))
    strips = fx['strips'].get(t['look'], [])
    if strips:
        out.append('<h3>Backdrop</h3><div class="g2">' + ''.join('<figure>%s<figcaption>%s</figcaption></figure>' % (img(s, 'backdrop'), ['dusk', 'night', 'dawn'][int(s.split('_')[-1][0])]) for s in strips) + '</div>')
    for k, p in enumerate(t['poses']):
        out.append('<h3>Pose %d: floor %d, seed %d · %s · traps near: %s</h3>' % (k + 1, p['n'], p['seed'], html.escape(p.get('label', '')), ', '.join(p['traps'])))
        sh = p['shots']
        out.append('<div class="g2">' + ''.join('<figure>%s<figcaption>%s, wide</figcaption></figure>' % (img(sh[m] + '_wide.jpg', m), m.title()) for m in ('torch', 'classic')) + '</div>')
        out.append('<div class="g4" style="margin-top:8px">' + ''.join('<figure>%s<figcaption>%s, close</figcaption></figure>' % (img(sh[m] + '_close.jpg', m), m.title()) for m in ('torch', 'classic')))
        if 'before_torch' in sh:
            out.append(''.join('<figure>%s<figcaption>v61 before: %s, close</figcaption></figure>' % (img(sh['before_' + m] + '_close.jpg', m), m.title()) for m in ('torch', 'classic')))
        out.append('</div>')
        if 'before_torch' in sh:
            out.append('<div class="g2" style="margin-top:8px">' + ''.join('<figure>%s<figcaption>v61 before (%s): %s, wide</figcaption></figure>' % (img(sh['before_' + m] + '_wide.jpg', m), html.escape(p.get('before_label', '')), m.title()) for m in ('torch', 'classic')) + '</div>')
    out.append('</section>')
out.append('<div class="card"><h3>Follow-ups not in this pass</h3><ul><li>The hourglass to a water clock (Karnak clepsydra): checkpoint, the HUD\'s glass, the rewind\'s words, the gates\' timers.</li><li>New traps from the research: a granite blocking slab in grooves (closer and gate), Hawara\'s dropping roof block (a chopper variant), a floor of draining sand (a loose-floor variant), a sand-lowered lift, a gate serpent puzzle, the scales.</li><li>Second round, now proposals on this page: the lamps, the traps, the name and the font (switches EGP.lamps, EGP.traps, EGP.plug; the font not yet in the game).</li></ul></div></main></body></html>')
open(os.path.join(HERE, 'egypt_themes.html') if D == os.path.join(HERE, 'egypt_themes') else os.path.join(os.path.dirname(D), 'egypt_themes.html'), 'w').write('\n'.join(out))
print('written')
