# egyptround18.py: round 18's section of egypt_themes.html (built in): the jet stream hint, a stream of the theme's sand along a
# move's path, in place of the kick shaft's chevrons, on the swing's throw and on the jump up to a ledge; the paternoster's chevrons
# removed. Pictures from egyptr18.py; the floors used and the swing's landings in egypt_themes/r18.json.
import html, json, os
E = html.escape


def links(src):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(l)) for l, u in src) + '</ul>'


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def sections(D, REL, img):
    J = json.load(open(os.path.join(D, 'r18.json')))
    sw = J['swing']
    err = max(abs(q['pred'][0] - q['land'][0]) for q in sw)
    return ['<section class="card" id="r18"><h2>Round 18 (built in): the jet stream hint</h2>'
            '<p>Owner: "the paternoster - remove the arrows; when doing wall jumps from side to side there is also a arrow hint, maybe we can change it to a wind hint, some particles clearly visible, like sand in a jet stream fashion flowing from the entry towards the exit of that; think of a chimney and how smoke would look like - do some research here; and we should use this kind of jet stream hint in other places like for the swing jump, or else where where it makes sens - do reserch here as well."</p>'
            '<h3>The arrows in the game, and what became of them</h3><ul>'
            '<li><b>The paternoster</b>: brass chevrons on the two upright strands of its chain, pointing up on the way in and down on the way out. <b>Removed</b>, nothing in their place: the links (or the rope\'s lay) travel with the chain and the slabs ride up and down in plain sight, which already says which strand climbs.</li>'
            '<li><b>The kick shaft</b>: a pulse of two chevrons rising up the shaft\'s back wall (and only where its ledge was on the right: a shaft heading left had none). <b>Converted</b> to the jet stream, in both kinds of shaft. The light down its back wall and the chipped grips stay: they are the shaft\'s look, not a pointer.</li>'
            '<li>No other arrow is drawn in the world (the touch pad\'s arrows are controls, not hints).</li></ul>'
            '<h3>What it is based on</h3><ul>'
            '<li><b>A chimney\'s draft</b> (the stack effect): warm, lighter air rises and the room\'s air is drawn in at the foot, the more strongly the taller the stack. '
            'So the grains are drawn in slowly at the shaft\'s foot and <b>speed up</b> as they climb (continuity: flow quickens through a narrowing, the Venturi effect).</li>'
            '<li><b>A rising plume</b> leaves its source laminar and turns turbulent further up (the cigarette or incense thread that breaks into curls): the grains\' sideways wander grows along the path; one in three curls in a small eddy, as smoke wisps curl where it meets a wall; at the exit the jet <b>fans out</b> and fades, as a free jet spreads once it leaves its nozzle.</li>'
            '<li><b>Wind-blown sand</b> travels in saltation <b>streamers</b> ("sand snakes"): narrow ribbons about 0.2 m wide that meander, and each one comes up quickly and dwindles slowly. The grains ride in <b>gusts</b> that run down the stream with that quick-rise, slow-fade shape, which is what tells the way it flows without an arrow head.</li>'
            '<li><b>Motion stretch</b>: a moving particle is drawn stretched along its velocity (the velocity-stretched billboard of Unity, Blender\'s pseudo motion blur), longer where it is faster. Here each grain is a long lens, fine at both ends and widest near its head, with a small bright grain at the head: a streak, never an arrow head.</li>'
            '<li><b>Games</b>: Ghost of Tsushima\'s "windicator" (the Guiding Wind: wind and particles point the way instead of a marker); Sea of Thieves\' wind lines (gentle, wavy, semi-transparent white streaks every crew member reads); Journey\'s wind and sand (gusts that lift and push, glowing ribbons that lead); Breath of the Wild\'s updrafts (rising streaks and dust as velocity-stretched billboards); Ori\'s wind tunnels (Kuro\'s Feather rides the visible current up). '
            'And the other side: level designers warn that over-lit or explicit cues "come off a lot more hand holdy", and that cues should be subtle yet noticeable. So the stream is used only where the move\'s path cannot be read from the rooms, and fades once the move is learned.</li></ul>'
            '<h3>What it does</h3><ul>'
            '<li><b>One routine</b> (<code>jetStream(ctx, path, strength, speed, width, seed, view)</code>): a path is a polyline built from arcs once (<code>jsPath</code>, <code>jsQuad</code>), the grains are a pure function of the clock and their index (nothing kept, nothing allocated a frame, the same after a rewind), gathered into four alpha bands of one path each, in three fills (a soft added glow so it reads in the darkest rooms, the streak in the floor\'s sand colour <code>sandC().grain</code>, a bright grain <code>sandC().hi</code>): at most twelve fills a stream, drawn only when its box is in view, with the same calls in Torchlight and Classic. Look only: the generator, the floors, the moves and the bot are unchanged.</li>'
            '<li><b>The kick shaft</b>: from the foot into the wall on the ledge\'s side, then kick to kick (each arc steep off the wall and topping out at the far one, as his kicks do: the plants alternate and the last is on the ledge\'s side), over the lip and out onto the ledge. Always shown (it replaces chevrons that were); full until the wall kick is learned, then 65%%; a little lower while he is in it.</li>'
            '<li><b>The swing</b>: shown only once the swing will carry him (the chime, <code>P.swRdy</code>), fading in over 0.4 s, full while he swings forward (Jump now) and half on the way back: a stream from behind him through the bottom of his swing and along the flight his Jump would give at this amplitude, down to where he would land. The prediction uses the release\'s own numbers: on floors %s at amplitudes 0.6 to 1.0 it ends within %d px of where he really lands.</li>'
            '<li><b>The jump up to a ledge</b> (jgrab: run, jump across the pit, hold Grab to catch a ledge a storey up): the run-up, the leap and the catch at the ledge\'s edge, then up onto it. Shown only until the move is learned: it is the one jump whose landing is not on his own level, so the plain gap jump\'s reading (PoP\'s "run and jump") does not carry over.</li>'
            '<li><b>Not used</b> on: the gap jumps (read from the floor itself, and there are many: a stream on each would be clutter); the lifts (a straight ride up or down a shaft you can see; the call plate and its hint carry it); the banner slide (the cloth is the path); the damaging drop (its look must say "this hurts", owner\'s rule, and a guiding stream would say "go"); the secret passage (round 17\'s sparkle is its cue: a stream would give the secret away).</li></ul>' % (', '.join(str(n) for n in sorted({q['n'] for q in sw})), err) +
            '<h3>Pictures</h3>' +
            '<p class="meta">The pictures of round 18a\'s stream (the shaft, the swing, the jump up to a ledge) are retired: round 18c made it organic; its videos show 18a and 18c side by side.</p>' +
            fig(img, 'r18_chain.png', 'The paternoster: round 17 with its chevrons and round 18 without, Torchlight and Classic') +
            links([('Stack effect (chimney draft)', 'https://en.wikipedia.org/wiki/Stack_effect'),
                   ('Plume (fluid dynamics): laminar near the source, turbulent further on', 'https://en.wikipedia.org/wiki/Plume_(fluid_dynamics)'),
                   ('Flow visualization: incense smoke from laminar to turbulent (flowvis.org)', 'https://www.flowvis.org/wp-content/uploads/2020/12/IV1_SL.pdf'),
                   ('Physics Classroom: the Venturi equation (flow speeds up through a narrowing)', 'https://www.physicsclassroom.com/interactive/fluids/VENTURI-EQUATIONS'),
                   ('Kok, Parteli, Michaels, Karam: The physics of wind-blown sand and dust (streamers about 0.2 m wide)', 'https://arxiv.org/pdf/1201.4353'),
                   ('Baas and Sherman: sand streamers on a beach (head-tail shape: a quick rise, a slow fade), EGU 2007', 'https://meetings.copernicus.org/www.cosis.net/abstracts/EGU2007/03586/EGU2007-J-03586.pdf'),
                   ('Video-imagery analysis of aeolian sand transport over a beach (EGU22)', 'https://meetingorganizer.copernicus.org/EGU22/EGU22-7639.html'),
                   ('80.lv: Insights into building VFX for Ghost of Tsushima (the "windicator")', 'https://80.lv/articles/insights-into-building-vfx-for-ghost-of-tsushima/'),
                   ('Sea of Thieves wiki: Wind (wavy, semi-transparent white lines)', 'https://seaofthieves.wiki.gg/wiki/Wind'),
                   ('Journey hands-on (GamesRadar): riding the wind and the sand', 'https://gamesradar.com/journey-hands-on-preview'),
                   ('realtimevfx: Breath of the Wild\'s dust particles (stretched billboards following the wind)', 'https://realtimevfx.com/t/zelda-breath-of-the-wild-dust-particles/10639'),
                   ('Zelda Wiki: Updraft', 'https://zeldawiki.wiki/wiki/Updraft'),
                   ('Ori and the Blind Forest walkthrough: Kuro\'s Feather lifts Ori in a wind tunnel', 'https://gamerwalkthroughs.com/ori-and-the-blind-forest/'),
                   ('Unity: ParticleSystemRenderer.velocityScale (stretched billboards)', 'https://docs.unity3d.com/kr/2023.1/ScriptReference/ParticleSystemRenderer-velocityScale.html'),
                   ('Blender: velocity-scaled billboards as pseudo motion blur', 'https://projects.blender.org/archive/blender-archive/src/commit/587b51831d7c7b40ba94eef941fbe4fe91ad8230/source'),
                   ('Game Developer: Level design tricks of the trade (over-lit cues come off hand holdy)', 'https://www.gamedeveloper.com/design/level-design-tricks-of-the-trade'),
                   ('GameAnalytics: five simple ways to use level design (contrast and framing guide without taking agency)', 'https://www.gameanalytics.com/blog/five-simple-ways-use-level-design-improve-player-experience')]) + '</section>']
