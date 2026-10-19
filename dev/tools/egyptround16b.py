# egyptround16b.py: round 16b's section of egypt_themes.html (built in): the swing bar made easy to pump on a phone. Pictures and the
# table's numbers from egyptr16b.py (egypt_themes/r16b.json, measured with swingfeel.py).
import html, json, os
from egyptr16b import NAMES
E = html.escape


def links(src):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(l)) for l, u in src) + '</ul>'


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def table(D):
    S = json.load(open(os.path.join(D, 'r16b.json')))
    cell = lambda q: ('never (0/%d)' % q['n']) if not q['cleared'] else '%.1f s (p90 %.1f), %d/%d' % (q['med'], q['p90'], q['cleared'], q['n'])
    rows = ''.join('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%d/%d</td><td>%d/%d</td></tr>' % (
        E(NAMES.get(k, k)), cell(S['before'][k]), cell(S['after'][k]), S['after'][k]['kicks'] if S['after'][k]['cleared'] else '-',
        S['before'][k]['landed'], S['before'][k]['n'], S['after'][k]['landed'], S['after'][k]['n']) for k in S['after'])
    return ('<table><tr><th>input style (touch, from a still hang)</th><th>before: time to the cue</th><th>after</th><th>pumps (after)</th>'
            '<th>landed, before</th><th>landed, after</th></tr>' + rows + '</table>')


def sections(D, REL, img):
    return ['<section class="card" id="r16b"><h2>Round 16b (built in): the swing bar</h2>'
            '<p>Owner: "I would also add the swing trap: I find it difficult to get the prince swinging enough. Check it."</p>'
            '<h3>Why it was hard</h3><ul>'
            '<li><b>Measured.</b> <code>swingfeel.py</code> plays the bar from a still hang with simulated people on the touch controls, 40 runs per style with its own jitter, and times how long until the swing will carry him (<code>SW_CLEAR</code>, 0.55 rad). '
            'Before, a person who switches 0.2 s after each turn (a normal reaction to a seen turn) needed about 5 s and 9 presses; at 0.35 s, or with short taps instead of holds, never got there; only someone anticipating every turn exactly managed it in 2 s.</li>'
            '<li><b>The cause.</b> Holding a way was a steady push (4.5 rad/s&sup2;) for as long as it was held, so a press made after the turn pushed against him until it was switched. The swing\'s whole half is only 0.58 s: a 0.2 s late switch spends a third of each half braking. '
            'On top of that the swing was damped hard (dies down in about 4 s) the whole time, eating most of what was left, and a tap did almost no work. People keep time with a seen motion far less well than with a sound (tapping in time with flashes fails above about 2.5 Hz, with tones not until 8 to 10 Hz: Repp 2006), so a scheme that needs presses inside a window of 0.1 to 0.2 s is a timing test, not a swing.</li>'
            '<li><b>The cue.</b> A 0.45 s glint a few pixels long on the bar and a quiet creak: easy to miss on a phone.</li>'
            '<li><b>Touch.</b> The pad registers alternation (each change of sector is a new press), but a thumb rocking from left to right a little low passes through the Down sector, and a Down press let go of the bar at once.</li></ul>'
            '<h3>Research</h3><ul>'
            '<li><b>Real swings.</b> A seated pumper adds a fixed amount of amplitude each cycle by rotating his body when the swing turns; a standing pumper multiplies it by squatting at the ends and standing at the bottom, where the speed is highest (Wirkus, Rand and Ruina; Case and Swanson). Seated pumping is the better one at small amplitudes, and it starts from rest. A gymnast on a bar does the same with the tap: a whip of the body through the bottom.</li>'
            '<li><b>Games.</b> Most make the swing itself automatic and leave only the let-go to time: Rayman Origins\' swingmen ("cannot be controlled by the heroes manually"), and, from play rather than a source, the horizontal poles of Prince of Persia: The Sands of Time and of Tomb Raider: Legend. Where the player builds it, it is forgiving: Tomb Raider: Legend\'s rope is swung by holding the way she faces ("press up, while facing the direction"); Bionic Commando (2009) lets you put momentum back with the stick if you mistime it, and shows an indicator for when to let go. '
            'Spider-Man 2\'s swinging began from realism and moved away from it where realism did not serve the feel (Fristrom, GDC 2019). Celeste\'s rule of thumb: windows wider than they look (coyote time, buffered input) that no one notices.</li></ul>'
            '<h3>Now</h3><ul>'
            '<li><b>A press is a pump.</b> Left or right, the way he will swing next or is swinging, arms one pump; it fires as he next passes the bottom going that way (within 0.8 s of the press), or at once if the press comes just after the bottom or he hangs still: a kick spread over 0.12 s, the tap through the bottom. A tap is enough; holding adds nothing. '
            'So the window for each press is the whole of the turn and the swing down into the bottom, about 0.8 s, instead of a moment.</li>'
            '<li><b>Mistakes cost nothing.</b> A press the wrong way or out of time does nothing; it never brakes him (the small lean of a held key only ever helps). Two opposite presses within 0.2 s cancel, so mashing does not pump (3 of 40 runs in 12 s), and holding one way gives one pump, then nothing.</li>'
            '<li><b>The swing holds while pumped.</b> Within a swing of the last pump it is damped less (his own effort keeps it going); left alone it still comes to rest in about 3.4 s.</li>'
            '<li><b>The cue.</b> When it will carry him a bright rising chime sounds over the creak, the glint is bigger, and his hands keep a warm glow for as long as it will carry him, full while he swings forward (Jump now), dim on the way back; it stays lit down to 0.5 rad, which still clears from a let-go at -0.2 to 0.2 rad. Each pump makes a low whoosh. The hint reads "press the way he swings, each time he turns... when it chimes, Jump as you swing forward".</li>'
            '<li><b>Down</b> lets go when held 0.15 s with no side pressed (a thumb crossing the pad no longer drops him).</li>'
            '<li><b>Unchanged.</b> The throw, the let-go window, the running catch (0.73 rad, over the cue at once), the levels and the bot (it still pumps by holding the way he moves; <code>run2</code> floors 7, 8, 16, 21 pass with 0 damage). <code>swingtest.py</code> now also checks the cue from a still hang within 2 s and that mashing never clears.</li></ul>' +
            fig(img, 'r16_swing.gif', 'From a still hang: a person pressing the way he swings 0.2 s (+-0.15) after each turn; three pumps, the chime and the glow, Jump on the next forward swing (touch input, real time; Torchlight at half size)') +
            fig(img, 'r16_swingchart.png', 'Time from a still hang until the swing will carry him, before and after, per input style (swingfeel.py, floor 6, touch input)') +
            '<h3>The numbers</h3>' + table(D) +
            '<p class="meta">"Landed": the simulated person presses Jump on the forward swing after the cue, near the bottom (0.17 to 0.49 s after the turn), and lands on the far side.</p>' +
            links([('Wirkus, Rand and Ruina, How to Pump a Swing, College Mathematics Journal 29 (1998): seated pumping adds a fixed amount per cycle, standing multiplies it', 'https://pi.math.cornell.edu/files/Community/5080/2017mar11/swing2017.pdf'),
                   ('Case and Swanson, The pumping of a swing from the seated position, Am. J. Phys. 58, 463 (1990), and a later control study of it (arXiv 2206.09579)', 'https://arxiv.org/pdf/2206.09579'),
                   ('Smithsonian: the best way to swing a playground swing (seated at low amplitude, standing above)', 'https://www.smithsonianmag.com/smart-news/whats-the-best-way-to-swing-a-playground-swing-180948084/'),
                   ('UMD lecture demonstration: pumping by pulling at the bottom and releasing near the top', 'https://lecdem.physics.umd.edu/d/d3/1619-d3-12.html'),
                   ('Repp, Rate limits of sensorimotor synchronization, Advances in Cognitive Psychology 2 (2006): tapping with flashes fails above about 2.5 Hz, with tones up to 8-10 Hz', 'https://doaj.org/article/dc3f29b3977e4adf8dfe9aa998eb40de'),
                   ('Tomb Raider: Legend, the rope swing (moves)', 'https://tombraiderwiki.org/index.php/Tomb_Raider_Legend_Moves'),
                   ('Rayman: the swingmen swing by themselves', 'https://raymanpc.com/wiki/en/Swingmen'),
                   ('Bionic Commando (2009): swinging and the let-go indicator (GamesRadar review)', 'https://www.gamesradar.com/bionic-commando-11/'),
                   ('Bionic Commando: momentum, putting it back with the stick (Giant Bomb)', 'https://giantbomb.com/articles/bionic-dreadlocks/1100-92/'),
                   ('Fristrom, Classic Game Design Postmortem: Swinging with Spider-Man (GDC 2019)', 'https://gdcvault.com/play/1025725/Classic-Game-Design-Postmortem-Swinging'),
                   ('Thorson, Celeste and Forgiveness', 'https://maddymakesgames.com/articles/celeste_and_forgiveness/index.html')]) + '</section>']
