# egyptround12.py: round 12's traps for egypt_themes.html (built in): the portcullis, the roof block (now an obstacle), the sand-filled
# shaft under a slab and the plugs, each after the owner's standing rule (perspective, texture, no pixelation), with the shared sand
# routine and the themes' own stone and wear. Pictures from egyptr12.py.
import html
E = html.escape


def links(src):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(l)) for l, u in src) + '</ul>'


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def sections(D, REL, img):
    o = []
    o.append('<section class="card" id="rule12"><h2>The standing rule for anything drawn (owner, round 12)</h2><p>Owner: "note in all future agent instructions the mandatory perspective research and the mandatory texture research. And the mandatory non pixelated research".</p><ol>'
             '<li><b>Perspective.</b> How the game projects things, and how the real object sits in space; match it; before and after.</li>'
             '<li><b>Texture.</b> Real material references with sources; a texture that reads as that material at phone size.</li>'
             '<li><b>Not pixelated.</b> No noise pixel by pixel and no blocky scaling; soft-edged mid-scale patterns, cached, stable in motion; judged in 1:1 crops of the phone\'s 1704 px canvas.</li></ol>'
             '<p><b>How the game projects (what every item below follows).</b> The view is a cutaway seen from the front, a little to the right and above. A block shows three faces:</p><ul>'
             '<li>its <b>front face</b>, at the front of the corridor;</li>'
             '<li>its <b>right side face</b>, drawn DX = 16 px to the right and DY = 8 px up across the corridor\'s depth;</li>'
             '<li>its <b>top</b>, where nothing in front hides it.</li></ul>'
             '<p>Undersides and left faces are never seen. Walls and ceilings are front faces at the front plane, HX = 8 px left of a tile\'s middle. Floors are tops with a front lip. A doorway shows its left jamb\'s inside face. Gates span the depth from the floor\'s front edge to its back edge.</p></section>')
    o.append('<section class="card" id="gate12"><h2>The portcullis, round 12 (built in)</h2><p>Owner: "check the perspective, now it doesn\'t look right; check the actual granite texture, do some research, now it is too pixelated; add some kind of carvings or painting that is level theme appropriate".</p><ul>'
             '<li><b>Perspective.</b> The slab runs across the corridor, 7 px thick, from the floor\'s front edge to the back wall. Its narrow front face is toward us. Its broad face is the right side face, sheared up with the depth, and the texture and carving shear with it. Its top is hidden in the ceiling. '
             'It runs in a slot across the floor and a groove up the back wall (Khufu\'s antechamber has such grooves in its granite walls); both show only where the slab is raised, in the theme\'s stone, dark with a lit lip. A dark slot opens at the ceiling\'s front edge, and the ceiling\'s shadow falls on the slab. '
             'Before, there was a log with ropes hanging in front of the wall above; it would really be inside the ceiling, so it is gone. Before, there was also a pale band at the slab\'s foot, which read as its underside; a face the camera never shows, so it is gone too.</li>'
             '<li><b>Texture.</b> Aswan rose granite is a coarse porphyritic hornblende-biotite granite: about half pink potassium feldspar, in crystals up to a few centimetres, about a quarter glassy grey quartz, and specks of black biotite and hornblende. Old Kingdom faces were dressed and polished. '
             'The new texture is drawn once per stone into a canvas at 4 px per game pixel: soft mottles first, then soft-edged angular feldspar crystals in two pinks, grey quartz, a few pale grains, and small black specks, with a light polish. It is drawn smoothed onto the faces and anchored to the slab, so it travels with it. The old squares of single pixels are gone. The glints sit on the stone\'s own crystals.</li>'
             '<li><b>Stone by theme.</b> Granite where the kings used it (the Halls of the West, the Blue Chambers, the Green Hall, Nun). Where no one would have used granite, the theme\'s own hard stone: Aksum\'s nepheline syenite, a grey granite-like rock (its stelae\'s stone); Hawara\'s quartzite (its burial chamber); sandstone for Napata, Meroë, Kerma, the Garamantes and the wells; limestone for Shali, since kershef cannot make a slab. The grooves and slot are the theme\'s wall stone.</li>'
             '<li><b>Wear.</b> The slab reads the walls\' own wear at its place (<code>wearLevel</code>), so it is consistent, deterministic and restored by rewind. In a ruined stretch it has broken corners, a short crack, chips and rubble at its foot; in a kept stretch it is clean.</li>'
             '<li><b>Carvings.</b> One emblem per theme, in sunk relief: the cut\'s floor in shadow, its lower edge catching the light, with faint paint where the originals were painted. Each is generated once with its stone:'
             '<ul><li>Halls of the West: a winged sun disc (Behdety, over temple and tomb doors);</li><li>Green Hall: the djed pillar of Osiris;</li><li>Blue Chambers: a kheker frieze in faience blue;</li><li>Napata and Meroë: Amun of Napata\'s ram head with the sun disc;</li>'
             '<li>Aksum: the pre-Christian disc and crescent;</li><li>Nun: the water ripples;</li><li>Hawara: Sobek\'s crocodile;</li><li>Kerma: a lion, as on the faience inlays of the Eastern Deffufa\'s façade;</li><li>the Garamantes: a giraffe of the Messak\'s engravings;</li><li>the wells: a date palm;</li>'
             '<li>Shali: a plain carved band of chevrons, kept to geometry; nothing of the meanings of Siwan (Amazigh) needlework is borrowed.</li></ul></li></ul>' +
             '<h3>Raised, half-way and closed, before and after, both modes (1:1); below, the closed slab at 3x</h3>' + fig(img, 'r12_gate_persp.png', 'Portcullis, before and after') +
             '<h3>The stones as generated (granite, syenite, quartzite, sandstone, limestone, greywacke, mud brick, kershef) and each theme\'s carved slab</h3>' + fig(img, 'r12_stones.png', 'Stones and carvings') +
             '<h3>Each theme\'s slab at gate size, closed (Torchlight above, Classic below)</h3>' + fig(img, 'r12_gate_themes.png', 'Slabs by theme') +
             links([('UCL Digital Egypt: granite (Aswan: ~50% pink potassium feldspar, 25% grey quartz, biotite and hornblende)', 'https://www.ucl.ac.uk/museums-static/digitalegypt/stone/granite.html'),
                    ('Hall of Maat: monumental red granite, coarse-grained, porphyritic, phenocrysts up to ~4 cm', 'https://www.hallofmaat.com/granite-hornblende-biotite-granite-monumental-red-granite-red-granite-rose-granite-pink-granite-monumental-black-granite-black-granite-grey-granite-syenite-pyrrhopoecilon/'),
                    ('MDPI (2021): the Aswan Monumental Granite', 'https://www.mdpi.com/2076-3417/11/14/6471'),
                    ('The Great Pyramid antechamber\'s portcullis grooves (Petrie, as quoted)', 'https://pretraziva.rs/show/the-great-pyramid-passages-and-chambers/301'),
                    ('The Met: the monumental stelae of Aksum (nepheline syenite)', 'https://www.metmuseum.org/en/essays/the-monumental-stelae-of-aksum-3rd-4th-century'),
                    ('The Met: Aksum, the disc and crescent replaced by the cross under Ezana', 'https://www.metmuseum.org/essays/monumental-architecture-and-stelae-of-the-aksumite-empire'),
                    ('Global Egyptian Museum: a temple gate with the winged disc of Behdet on its lintel', 'https://globalegyptianmuseum.org/detail.aspx?id=14594'),
                    ('Penn Museum: Merenptah\'s lintel, wing tips of a winged sun disc in sunk relief', 'https://www.penn.museum/collections/object/496639'),
                    ('Global Egyptian Museum: the djed pillar', 'https://globalegyptianmuseum.org/glossary.aspx?id=134'),
                    ('The Met: relief fragment with a kheker frieze', 'https://www.metmuseum.org/art/collection/search/565089'),
                    ('Archaeology: the cult of Amun at Dangeil; the ram-headed Amun of Napata', 'https://archaeology.org/issues/may-june-2015/features/sudan-nubia-dangeil-cult-of-amun-ra/'),
                    ('Egyptian hieroglyph N35, the water ripple', 'https://en.wikipedia.org/wiki/Egyptian_Hieroglyph_N035'),
                    ('Hawara: Sobek, Shedet and the Labyrinth', 'https://en.wikipedia.org/wiki/Hawara'),
                    ('MFA Boston: faience wall inlay of a lion, probably from the Eastern Deffufa at Kerma', 'https://www.mfa.org/collections/object/wall-inlay-of-a-lion-142740'),
                    ('British Museum: Messak engravings (Fezzan), a giraffe', 'https://www.britishmuseum.org/collection/object/E_2013-2034-2906'),
                    ('Egyptian Streets: Siwan embroidery and its Amazigh context', 'https://egyptianstreets.com/2016/07/01/adeles-egypt-inspired-dress-sparks-cultural-appropriation-controversy/')]) + '</section>')
    o.append('<section class="card" id="roof12"><h2>The roof block, round 12 (built in; now an obstacle)</h2><p>Owner: "again the perspective, it is wrong; the sand shader needs work: starts with slow trickles of sand, quickly increasing, exponentially, a large puff of sands; collapses to the floor, occupies the full width of the corridor and becomes an obstacle over which the prince needs to jump"; '
             'then "respect the level theme for the stone and the level of damage and crumbling to that area of the level".</p><ul>'
             '<li><b>Perspective.</b> Before, it hung below the ceiling at the tile\'s middle, as a flat card. Now it is a block of the ceiling\'s lowest course. Its front face is flush with the ceiling\'s front face (the walls\' front plane), and while it hangs only that face shows, a hair proud of the ceiling, with sand in its joints. '
             'When it lets go, its slot is a dark hole in the ceiling with its left inner face showing, as a doorway\'s jamb does. The falling block shows its front, top and right faces. It lands across the whole depth of the corridor and lies there.</li>'
             '<li><b>Stone and wear.</b> Each theme\'s own stone: limestone in the Halls of the West and the Blue Chambers, greywacke in the Green Hall, granite at Nun (the Osireion), sandstone at Napata, Meroë and in the Garamantes\' and wells\' corridors, mud brick at Kerma, Aksum\'s syenite, Hawara\'s quartzite (its burial chamber\'s stone), and kershef at Shali. '
             'It is worn as the walls round it are (<code>wearLevel</code>), and once fallen it has fresh chips, dust and rubble.</li>'
             '<li><b>The sand</b> uses one routine shared with the sand shaft and the plugs. A few thin, slow trickles fall from its joints while it waits; that is the warning, and it starts as early as before. The trickles grow exponentially into streams through the 0.3 s it shifts. A billow of sand goes up as it lets go and another as it lands, and the dust settles over two seconds.</li>'
             '<li><b>Gameplay.</b> Once fallen, the block lies across the corridor, 22 px long and 10 px high. It is solid to him and to guards below its top. Any jump clears it, since his body\'s box stops 6 px above his feet: the standing and running jumps, and the low leaps under a ceiling. '
             'A pair side by side, in a side passage, takes a running jump; the bot\'s way back over them is now a running jump instead of a walk. One who lands on it slides off to the nearer side. It stays where it fell, and rewind and respawn restore it (the trap\'s state and the rubble set). Its damage when it falls on him is unchanged. '
             'The bot runs under the blocks before they fall, so on the main route it never has to jump one. The generator is unchanged apart from the side passage\'s return.</li></ul>' +
             '<h3>Before and after: hanging and lying, both modes (1:1)</h3>' + fig(img, 'r12_roof_persp.png', 'Roof block, before and after') +
             '<h3>In four themes (Halls of the West, Napata, Kerma, Aksum), clean and worn</h3>' + fig(img, 'r12_roof_themes.png', 'Roof block by theme and wear') +
             '<div class="g4" style="margin-top:8px">%s%s%s%s</div>' % (fig(img, 'r12_roof_pour.gif', 'The pour: trickle, the exponential rise, letting go, the fall, the landing billow'), fig(img, 'r12_roof_jump.gif', 'The prince jumping a fallen block'),
                                                                     fig(img, 'r12_sandfloor.gif', 'The sand-filled shaft under a slab: trickles, the drain, the collapse, the billow'), fig(img, 'r12_plug.gif', 'The plugs in the chase')) +
             links([('Hawara: the pyramid of Amenemhat III (its quartzite burial chamber)', 'https://en.wikipedia.org/wiki/Hawara'),
                    ('Vacek (2013): building stones of Meroë (Nubian sandstone; bricks)', 'https://publikace.nm.cz/file/1a15d29aea90c2f60e2ee6f206cd1410/17849/182-2013-29-Vacek-Sudan.pdf'),
                    ('Shali: kershef, salt blocks in salty mud (Rovero et al.)', 'https://flore.unifi.it/handle/2158/359981'),
                    ('Aga Khan Trust: the restoration of Shali with kershef', 'https://next.archnet.org/sites/21598')]) + '</section>')
    o.append('<section class="card" id="sand12"><h2>The sand-filled shaft under a slab, round 12 (built in)</h2><p>Owner: "the sand shader needs to be similar to the sliding roof block".</p><p>It uses the same routine as the roof block. Through the half second the slab gives way, it sinks a little, grains run over it to its seams as the sand under it drains, and thin trickles from its joints grow exponentially into streams. '
             'When it collapses, a billow rises from the hole and the dust settles. Its timing, warning, hit box and gameplay are unchanged.</p>'
             '<p><b>The sand.</b> Each theme now has its own desert sand: the pale sands of the Theban hills and Saqqara, the orange of the Nubian and Fezzan ergs, the Aksum plateau\'s reddish soil, Siwa\'s near-white. '
             'A stream is now one body whose density swells down it, with round grains, not a string of dashes. It is drawn through the same scene path in both modes (Torchlight\'s recording 2D, Classic\'s canvas). There is no new shader pass: per the WebGL rules, nothing is drawn element by element and nothing jitters per pixel.</p>'
             '<p>The GIF is beside the roof block\'s, above.</p>' +
             links([('Iufaa\'s shaft tomb at Abusir (Late Period sand-filled shafts)', 'https://en.wikipedia.org/wiki/Iufaa'),
                    ('Bareš, Smoláriková, Janák: Late Period shaft tombs at Abusir', 'https://pes.ff.cuni.cz/wp-content/uploads/sites/13/2022/11/Ladislav_Bares_-_Kveta_Smolarikova_-_Jiri_Janak_7-26.pdf')]) + '</section>')
    o.append('<section class="card" id="plug12"><h2>The plugs, round 12 (built in)</h2><p>Owner: "granite plugs sliding down the corridors: same perspective, texture, shader, damage as for the others".</p><ul>'
             '<li><b>Perspective.</b> Each plug is a block in the corridor\'s projection: its long front face toward us, its top receding up and to the right wherever the ceiling leaves it in view, and its polished leading face across the corridor\'s depth. Before, it was a flat front with no top.</li>'
             '<li><b>Stone and wear.</b> The same cached granite as the portcullis, carried with the block as it moves. It stays granite as in the Great Pyramid, except Aksum\'s syenite and Hawara\'s quartzite, the builders\' own hard stones there. It is worn as the walls it passes.</li>'
             '<li><b>Sand.</b> Sand runs off its leading top edge, grit is scraped off the back wall, sand is pushed ahead, and a dust billow rolls at its foot, all from the shared sand routine.</li>'
             '<li><b>Gameplay</b> is unchanged: the front, speed, rows and kill line.</li></ul>' +
             '<h3>Before and after, both modes (1:1)</h3>' + fig(img, 'r12_plug_persp.png', 'Plugs, before and after') + '</section>')
    return o
