# egyptround18c.py: round 18c's section of egypt_themes.html (built in): the jet stream hint made organic, after research into how
# games draw wind, dust and smoke that guide the player. Pictures and videos from egyptr18c.py; the floors used in egypt_themes/r18c.json.
import html, json, os
E = html.escape


def links(src):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(l)) for l, u in src) + '</ul>'


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def vid(REL, f, cap):
    return ('<figure><video src="%s/%s" controls loop muted playsinline autoplay preload="metadata" style="width:100%%;border-radius:6px"></video>'
            '<figcaption>%s (<a href="%s/%s">%s</a>)</figcaption></figure>' % (REL, f, E(cap), REL, f, f))


def sections(D, REL, img):
    J = json.load(open(os.path.join(D, 'r18c.json'))) if os.path.exists(os.path.join(D, 'r18c.json')) else {}
    B = J.get('bench', {})
    bench = ''.join('<tr><td>%s</td><td>%s</td><td>%.3f</td><td>%.3f</td></tr>' % (E(k.split('/')[0]), E(k.split('/')[1]), v[0], v[1]) for k, v in sorted(B.items()))
    return ['<section class="card" id="r18c"><h2>Round 18c (built in): the jet stream, made organic</h2>'
            '<p>Owner, on round 18a\'s stream: "Needs to be more organic. Try checking how games are doing something similar". '
            'What was wrong: the grains were large leaf-shaped blades of one size in one neat wavy column, each wobbling on its own sine: a stylised graphic, not blowing sand or smoke.</p>'
            '<h3>What games and the real thing do</h3><ul>'
            '<li><b>Ghost of Tsushima</b> (Guiding Wind; GDC 2021, Bill Rockenbeck, "Blowing from the West"): the wind is one vector from the hero to the goal, steady in direction, and only its <b>strength gusts</b> (Perlin noise); '
            'small things in it (leaves, pampas fluff, ash: tens of thousands on screen) add higher-frequency swirl, and local wind comes from <b>vorticles</b>, invisible particles that each add a vortex, a gust or a blast and are summed where a particle is. '
            'The particles look ahead and lift over obstacles rather than drive into a cliff. Taken: one steady way through the path, gusts in strength only, many small grains, <b>summed eddies</b> for the swirl, lifting off walls.</li>'
            '<li><b>Curl noise</b> (Bridson, Hourihan, Nordenstam, SIGGRAPH 2007; used for smoke without a fluid solver, Brochu and Bridson 2009): take the curl of a noise or of a sum of vortex blobs, and the flow is divergence-free, '
            'so particles swirl round each other and never bunch or open holes the way independent sine wobbles do; it can be laminar or turbulent and respect walls. Taken: each eddy turns the grains round its centre by an angle that falls off as a Gaussian (a vortex blob\'s displacement).</li>'
            '<li><b>Incense and chimney plumes</b>: the thread leaves the stick laminar, speeds up, and a little way up its shear layer rolls up into <b>counter-rotating Kelvin-Helmholtz curls</b>; buoyant plumes <b>puff</b> at a steady rate through the change. '
            'Taken: the eddies are weak at the entry and strong further on, and turn each way in turn (a vortex street) drifting at about half the stream\'s speed, so grains overtake them and curl round them; the grains come in puffs.</li>'
            '<li><b>Saltation streamers</b> (Baas; Yan, Lin, Zhang and Baas 2026; Dupont et al., saltation intermittency): wind-blown sand moves in narrow flow-aligned ribbons that are the footprint of eddies passing; each rises quickly and fades slowly (a head and a tail), and a <b>fine dust</b> rides higher and wider. '
            'Taken: each puff has a dense head and a tail that stretches behind it as it travels (fast grains ahead, slow behind); a second, fainter layer of finer, slower dust spreads wider round the core.</li>'
            '<li><b>Journey</b> (John Edwards, GDC 2013, "Sand Rendering in Journey"): the sand reads as sand by its <b>glitter</b>, single grains catching the light now and then. Taken: a few grains flash briefly.</li>'
            '<li><b>Breath of the Wild</b> and stylised smoke (realtimevfx threads; 80.lv): wind dust as camera-facing billboards stretched and panned along the wind, smoke as soft blobs that grow and <b>erode</b> over their life; '
            'soft swirling shapes read as smoke, jagged angular ones as fire. Taken: soft round sprites stretched along each grain\'s own motion (so a curling grain draws a curved streak), a haze of faint added wisps that grow as they go, every grain fading in and out over a life of its own (some disperse before the exit).</li>'
            '<li><b>Hollow Knight</b> and other 2D games: drifting motes in depth layers with long fades and a slight noise drift (no public breakdown; Unity forum analysis). Taken: the two layers above. '
            'Searched without a usable breakdown: Ori and the Will of the Wisps, Sea of Thieves\' wind lines, Gris, Sable, Inside and Limbo (Playdead\'s GDC talk is on lighting and volumetrics), The Lost Crown, the Dune games.</li>'
            '<li><b>Readable without an arrow</b>: Ghost of Tsushima keeps the direction steady and varies only strength; streamers\' head-tail shape and the puffs travelling up the shaft show the way; the draft still quickens toward the exit, and at the exit the jet fans out, slows and rises (warm air).</li></ul>'
            '<h3>What changed in jetStream</h3><ul>'
            '<li><b>Grains</b>: up to 200 a stream (about one per 1.8 px of path), 1 to 2.5 px, each a soft sprite stretched along the way it moved over the last 0.05 s (computed from two moments of its flow), so blur follows speed and curls; 30% are fine far dust, dimmer, wider, slower.</li>'
            '<li><b>Flow</b>: the draft\'s quickening (kept), a slow sway of the whole thread, a faster ripple further on, and 2 to 12 drifting eddies (one per 48 px of path) that twirl the grains. Weak at the entry (laminar), strong past a third of the way (turbulent).</li>'
            '<li><b>Puffs</b>: seven clumps a cycle, each pass different (thick or thin, wide or narrow, from a hash of its cycle); a quarter of the core grains run steady between them.</li>'
            '<li><b>Haze</b>: 6 to 26 faint added wisps a stream, growing from 1.5 to 4 times the stream\'s half width and stretched along it, carried by the same eddies; a faint glow round the larger grains so it reads in the darkest rooms.</li>'
            '<li><b>Walls</b> (the kick shaft): a soft clamp at the shaft\'s inner faces up to the ledge: a grain thrown wide piles against the wall and slides up it, and peels off where the path turns back (Coanda-like).</li>'
            '<li><b>Glints</b>: one in five core grains flashes now and then (added).</li>'
            '<li><b>Kept</b>: the places (the kick shaft, the swing\'s throw once it will carry him, the jump up to a ledge until learned), the strengths and the learned logic, the speed and width per place, the theme\'s sand colour. '
            'Still a pure function of the clock and each grain\'s index: nothing kept, nothing allocated a frame, the same after a rewind; drawn only when in view; the same calls in Torchlight and Classic. Look only: the generator, the floors, the moves and the bot are unchanged.</li>'
            '<li><b>Cost</b>: three sprite batches a stream (the haze and glows added; the grains; the glints): one drawImage per grain or wisp, which Torchlight\'s G2D gathers into one draw a batch (18a: four alpha bands in three passes, up to twelve fills). '
            'The hint\'s own CPU time a frame with a shaft in view, this Mac\'s Chromium (ms; 18b then 18c):</li></ul>'
            + ('<table><tr><th>mode</th><th>place</th><th>18b</th><th>18c</th></tr>%s</table>' % bench if bench else '') +
            '<p class="meta">bench.py on floors 7 and 17 (the shafts\' floors): %s</p>' % E(J.get('benchpy', '')) +
            '<h3>Pictures</h3>' +
            vid(REL, 'r18c_shaft.mp4', 'The kick shaft, 8 s: 4 s at its foot, then the climb; the Halls of the West (above), the Green Hall of Osiris (below); round 18a (left), 18c (right); Torchlight, the game\'s canvas at 2x') +
            vid(REL, 'r18c_swing.mp4', 'The swing, 8 s: pumping until it will carry him, the stream on the throw, the throw; 18a (left), 18c (right); Torchlight, 2x') +
            fig(img, 'r18c_sheet.png', 'Stills: the shaft mid-climb before and after, Torchlight and Classic, 1:1 and 2x crops; the swing; the jump up to a ledge (18c)') +
            links([('Game Developer: Using "vorticles" to simulate wind in Ghost of Tsushima', 'https://gamedeveloper.com/design/using-vorticles-to-simulate-wind-in-i-ghost-of-tsushima-i-'),
                   ('GDC Vault: Blowing from the West: Simulating Wind in Ghost of Tsushima (Bill Rockenbeck, 2021)', 'https://gdcvault.com/play/1027124/Blowing-from-the-West-Simulating'),
                   ('PlayStation Blog: How stunning visual effects bring Ghost of Tsushima to life (the windicator; pampas, leaves, ash)', 'https://blog.playstation.com/2021/01/12/how-stunning-visual-effects-bring-ghost-of-tsushima-to-life/'),
                   ('realtimevfx: VFX of Ghost of Tsushima (the global wind field, opt-in emitters)', 'https://realtimevfx.com/t/vfx-of-ghost-of-tsushima-a-recent-blog/15815'),
                   ('Bridson, Hourihan, Nordenstam: Curl-noise for procedural fluid flow (SIGGRAPH 2007)', 'https://www.dneg.com/wp-content/uploads/2022/11/2007.pdf'),
                   ('Brochu and Bridson: Animating smoke as a surface (vortex rings and curl noise, SCA 2009)', 'https://www.cs.ubc.ca/~rbridson/docs/brochu-sca09-smoke.pdf'),
                   ('COMSOL: an incense stick\'s plume, laminar then turbulent 40 to 50 cm up', 'https://doc.comsol.com/6.4/doc/com.comsol.help.models.cfd.incense_stick/incense_stick.html'),
                   ('APS DFD 2018: counter-rotating Kelvin-Helmholtz vortices in a smoke plume', 'https://gfm.aps.org/meetings/dfd-2018/5b9c4e1bb8ac3105e5ac91dc'),
                   ('APS DFD 2012: plumes from localised heating, the puffing instability', 'https://meetings-archive.aps.org/dfd/2012/l2/4/'),
                   ('Dupont et al.: Modelling saltation intermittency (streamers, the footprint of eddies)', 'https://hal.archives-ouvertes.fr/hal-00931428'),
                   ('Characterization of aeolian streamers using time-average videography (Windsor)', 'https://scholar.uwindsor.ca/environmentalsciencepub/39'),
                   ('Utrecht thesis: streamers on a beach (head-tail shape: a quick rise, a slow fade)', 'https://studenttheses.uu.nl/handle/20.500.12932/36346'),
                   ('GDC Vault: Sand Rendering in Journey (John Edwards, 2013)', 'https://gdcvault.com/play/1017742/Sand-Rendering-in'),
                   ('Alan Zucconi: A Journey into Journey\'s sand shader (glitter)', 'https://www.alanzucconi.com/2019/10/08/journey-sand-shader-1/'),
                   ('realtimevfx: Zelda Breath of the Wild dust particles (stretched billboards panned along the wind)', 'https://realtimevfx.com/t/zelda-breath-of-the-wild-dust-particles/10639'),
                   ('realtimevfx: Zelda BotW VFX fan art (stretched and round billboards; erosion)', 'https://realtimevfx.com/t/zelda-breath-of-the-wild-vfx-fan-art/4899'),
                   ('realtimevfx: EStampes sketch 15 (erode, then fade; soft swirls read as smoke, angular shapes as fire)', 'https://realtimevfx.com/t/estampes-sketch-15-wip/5388'),
                   ('80.lv: stylised fire in UE4 (alpha erosion over a particle\'s life)', 'https://80.lv/articles/tutorial-stylized-fire-effect-in-ue4'),
                   ('Unity forum: Hollow Knight\'s drifting points in depth layers', 'https://forum.unity.com/threads/how-to-get-this-effect.881980/'),
                   ('80.lv: The rendering of INSIDE (Playdead: volumetrics, not particles)', 'https://80.lv/articles/the-rendering-of-inside-low-complexity-high-fidelity/')]) + '</section>']
