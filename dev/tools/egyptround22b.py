# egyptround22b.py: round 22b's section of egypt_themes.html (built in): the prince's proportions, after research on young men's bodies
# (ANSUR II), the drawing canons and other games. Pictures from egyptr22b.py; the gameplay check is figscan.py.
import html
E = html.escape


def links(src):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(l)) for l, u in src) + '</ul>'


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def table(head, rows):
    return ('<table><tr>' + ''.join('<th>%s</th>' % E(h) for h in head) + '</tr>' +
            ''.join('<tr>' + ''.join('<td>%s</td>' % E(str(c)) for c in r) + '</tr>' for r in rows) + '</table>')


PROP = [
    ('Height in heads (chin to crown)', '7.7 (1753 / 228 mm); canons: 7.5 real, 8 ideal (Loomis)', 'the style\'s: 4.5 to 6', '4.85', '5.09'),
    ('Head, chin to crown', '228 mm, 0.130 of stature (Drillis and Contini, Winter)', '10.4 px (about 1.6 times the body\'s scale)', '10.9 px', '10.4 px'),
    ('Chin over the shoulder (acromion)', '94 mm = 0.41 of a head (chin 1525, acromion 1431 mm)', '4.3 px at the head\'s scale (2.5 at the body\'s)', '1.8 px = 0.17 h', '4.2 px = 0.41 h'),
    ('C7 (cervicale) under the chin', '15 mm = 0.07 h (cervicale 1510 mm)', '0.7 px', 'over the chin (21a), 0.5 px under (22)', '1.4 px under (the torso\'s nape point; the neck\'s back edge carries the line above)'),
    ('Neck depth', 'circumference 381 mm (base 419): about 121 mm, 0.6 of the head\'s length (199 mm)', '5.4 px, 5.9 at the base', '4.0 / 3.0 px (5.0 / 3.7 in 22)', '5.5 / 4.6 px (+1.25 outline)'),
    ('Ear in front of C7', '93 mm (craniovertebral angle about 50 degrees)', '4.2 px', 'about 1 px', 'about 2.4 px (neck leaning 14 degrees)'),
    ('Shoulder joint to hip', 'acromion to trochanter 531 mm; the joint about 40 mm under the acromion: 491 mm', '13.3 px', '15 px', '13 px'),
    ('Hip over the sole (legs)', 'trochanter 900 mm', '24.3 px', '24 px', '24 px (unchanged)'),
    ('Shoulder joint to the middle of the hand', 'about 643 mm', '17.4 px', '9 + 8.5 = 17.5 px', '8.3 + 9.2 = 17.5 px (the elbow at the waist)'),
    ('Chest depth in profile', '236 mm', '6.4 px (body) to 10.7 (head)', '9.2 px', '9.2 px (unchanged: the outline style\'s)'),
    ('Shoulder breadth (front view only)', 'biacromial 411 mm = 1.8 h', '-', '-', '-'),
    ('Total height, sole to crown', '-', '-', '52.9 px', '52.8 px (the crown kept)'),
]

GAMES = [
    ('Prince of Persia (1989)', 'rotoscoped from film of David Mechner', 'about 6.5', 'a real neck, low relaxed shoulders', 'the motion read as a person\'s because it was one'),
    ('Another World (1991)', 'rotoscoped, flat polygons', 'about 7', 'real', 'silhouette-only shapes: proportions carry the reading'),
    ('Flashback (1992)', 'rotoscoped, over 1,500 frames', 'about 7', 'real', 'realism of movement first'),
    ('Blackthorne (1994)', 'rotoscoped like Prince of Persia', 'about 6.5', 'short, broad shoulders', 'a heavier hero, shoulders exaggerated'),
    ('Blasphemous (2019)', 'hand pixel art', 'about 6', 'hidden under the helmet', 'a tall, gaunt silhouette; the head is a helmet'),
    ('Dead Cells (2018)', '3D models rendered to pixels', 'about 6 (a flame for a head)', 'no neck to read', 'broad shoulders and long limbs for action'),
    ('Prince of Persia: The Lost Crown (2024)', 'stylised 3D, anime-influenced', 'about 6', 'visible, slender', 'heroic but readable at a distance'),
    ('Limbo, Inside', 'black or muted silhouettes', 'about 5 (a child)', 'thin, clearly visible', 'a big head reads as a child; the neck keeps it from reading as a lump'),
    ('Oddworld: Abe\'s Oddysee (1997)', 'pre-rendered 3D', 'about 4', 'very long and thin, sloped shoulders', 'a huge head for expression on a long neck: the opposite of a hump'),
    ('Celeste, Shovel Knight, Hollow Knight', 'small pixel or hand-drawn sprites', '2 to 3', 'none: the head sits on the body', 'chibi: at 2 to 3 heads there is no neck to draw'),
    ('Rayman', 'hand-drawn (UbiArt)', 'about 3', 'none: limbs float', 'animation economy, made a style'),
    ('Cuphead', '1930s rubber hose, hand-inked', 'about 3', 'a short stalk', 'joints left out; a big head for expression'),
]


def sections(D, REL, img):
    return ['<section class="card" id="r22b"><h2>Round 22b (built in): the prince\'s proportions</h2>'
            '<p>Owner, after round 22: "Redo according to the research to match the proportions, that must be the rule. And yes check that we haven\'t broken '
            'anything else. Additionally, did you include in your research what other games are doing?" Round 22 had studied only Prince of Persia (1989) among '
            'games and had changed only the outline. This round changes the skeleton, and the figure now follows the research\'s proportions.</p>'
            '<h3>The cause</h3><p>The skeleton put the chin only 1.8 px over the shoulder joint, 0.17 of a head; a young man\'s chin is 0.41 of a head over the top '
            'of his shoulder. The trunk was long (15 px, against 13.3) and the neck short (2.5 px), so the shoulders rose up round the jaw: the hump the owner '
            'saw, which rounds 21a and 22 had tried to hide in the outline. The figure\'s head is the style\'s, about 1.6 times a real head on that body, but the neck '
            'had been sized to the body: a big head on a body-sized neck sits on the shoulders.</p>'
            '<h3>Research: the body</h3><ul>'
            '<li><b>ANSUR II</b> (US Army, 2012; the public data, 4,082 men): I took the 422 men aged 17 to 20. Means: stature 1753 mm, cervicale (C7) 1510, '
            'acromion 1431, suprasternale 1432, trochanter 900, crotch 850, wrist 835; acromion to radiale 334, radiale to stylion 269, hand 192; head length 199, '
            'tragion to the top of the head 132; neck circumference 381 (base 419); chest depth 236, waist depth 211, buttock depth 229; biacromial breadth 411.</li>'
            '<li><b>Segment proportions</b> (Drillis and Contini 1966, as drawn in Winter\'s Biomechanics and Motor Control of Human Movement): the chin at 0.870 of '
            'stature, the shoulder at 0.818, the hip at 0.530, the knee at 0.285; the head 0.130 of stature. So the chin is 0.052 of stature over the shoulder, '
            '0.40 of a head, the same as ANSUR\'s youths (94 mm, 0.41 h).</li>'
            '<li><b>Canons</b>: a real adult is about 7.5 heads (ANSUR\'s youths 7.7); Loomis draws the ideal man at 8, with one head from the chin to the nipples, '
            'another to the navel, another to the crotch, the shoulders 2 1/3 heads wide. The pit of the neck lies level with the shoulders\' tops (suprasternale '
            '1432, acromion 1431 mm); C7 is a little under the chin (15 mm), and the line from C7 to the ear rises at about 50 degrees (round 22).</li></ul>'
            '<h3>Research: other games</h3>'
            '<p>My reading of each hero in profile, from published footage and art (heads are estimates; the panel below is my own schematic, not game art):</p>' +
            table(('Game', 'How the figure is made', 'Heads tall', 'Neck', 'Why'), GAMES) +
            '<p>Two families. The rotoscoped and realistic games (Prince of Persia, Another World, Flashback, Blackthorne, Blasphemous, Lost Crown) stay at 6 to 7 '
            'heads, and the neck comes for free from the real body. The chibi games (Celeste, Shovel Knight, Hollow Knight, Rayman) go to 2 or 3 heads and drop the '
            'neck altogether: the head sits on the body and nothing reads as a hump because there are no shoulders above the chin. In between, where Dawnward is '
            '(about 5 heads, a big head for a readable face on a phone), the designs that work keep a long, slender neck and sloped shoulders: Abe\'s head is '
            'huge and his neck long; the boy of Limbo and Inside has a big head and a thin neck clearly drawn. A big head on a short neck reads as a hunch. So the rule: '
            'the head may be the style\'s size, but what joins it to the body (the neck\'s length and depth, C7) follows the head\'s scale, and the body below follows '
            'the body\'s.</p>'
            '<h3>The proportions (1 px is about 3.7 cm of the body; the head 1.6 times that)</h3>' +
            table(('Measure', 'Research', 'At the figure\'s scale', 'v69 and round 22', 'Round 22b'), PROP) +
            '<p class="meta">The games schematic (r22b_games) was retired in round 23.</p>' +
            '<h3>What changed</h3><ul>'
            '<li><b>The skeleton</b> (<code>LEN</code>): the trunk from the hip to the shoulder joint 13 px (was 15), the neck 4.9 (was 2.5), the head\'s radius 4.4 '
            '(was 4.6), the upper arm 8.3 and the forearm 9.2 (were 9 and 8.5: the same reach, the elbow at the waist). The crown stands where it stood (27.7 px '
            'over the hip; the figure 52.8 px tall against 52.9), the legs and feet are unchanged. The chin is now 4.2 px over the shoulder, 0.41 of a head.</li>'
            '<li><b>Hands that hold something keep their place</b>: ledges, floors, the hilt, the flask and the sword in a fight were placed for v69\'s arm, and '
            'gameplay\'s numbers (HANG, the climb\'s offsets) were tuned to it. Poses that hold something carry <code>hold</code> (the front hand) and '
            '<code>hb</code> (the back one), blended with the pose: the hands go where v69\'s arm put them and both arms are solved again with two bones, the elbow '
            'bending the way it bent; in the air a grip out of reach lifts the body just enough (the shorter trunk hangs 2 px higher under the same grip). In the '
            'drink, <code>mh</code> moves the hand with the mouth. The swing draws him nearer the bar by the difference in the lift that brings the bar into reach.</li>'
            '<li><b>The head in the low poses</b>: the low leaps hold the head 0.11 rad less far back, the crawl 0.29 and the drink\'s reach 0.08, so the crown never '
            'rises past v69\'s on the longer neck (under low stone and in crawl tunnels).</li>'
            '<li><b>The outline</b>, revisited: the neck is 0.6 of the head\'s depth (5.5 px at its base, 4.6 under the skull) and leans forward about 14 degrees '
            '(its base 1.6 px behind the spine), so its back edge is the slope from the nape to C7; the torso\'s nape point (C7) is NB(2.8, 3.5), under the chin; the '
            'back runs from it nearly straight to the shoulder blades on the wall line (<code>BQ</code>: 4.25 at the shoulder, 4.5 at the blades). Round 22\'s lower '
            'arm roots are gone (the deltoid\'s top is now 5 px under the chin) and the shoulders\' sheen is back where round 21a put it. Round 19\'s arms-up back, '
            'round 20b\'s kilt and sword and round 21a\'s lift ropes are unchanged. The robbers share the skeleton and the outline (their own deeper build); the '
            'skeleton enemies get two cervical vertebrae on the longer neck.</li></ul>'
            '<h3>Checking that nothing else broke</h3>'
            '<p><code>figscan.py</code> reads, before (the v69 release) and after, every pose the game draws (the pose table, the run cycle, the crawl, the drink, '
            'the climb onto a ledge, the swing, the wall run, the kick-shaft plant: 80 in all): both hands, both feet, the hip, the sword\'s tip, figReach, the head '
            'and the mouth, and from a silhouette at 8x the crown, the sole and the reach. Its rules: hands that hold something within 0.35 px (0.75 for the lunges\' '
            'straight arms), the crown never higher (0.25 px), feet and hip on the ground unchanged, the hands no further from the swing\'s bar than before, the hand '
            'at the mouth while drinking. Result: <b>ok</b>. The differences it reports, and why each is safe:</p><ul>'
            '<li>Hands in free poses (standing, running, jumping, falling, hurt, the wall run, the kick shaft): 1 to 2.3 px lower, the shoulder being 2 px lower. Look '
            'only: no hit box reads the skeleton. The only readers of <code>skel()</code> and <code>LEN</code> are the figure\'s drawing, <code>handFlask</code> '
            '(the flask in his hand), <code>swordTip</code> (the blade\'s trail), <code>figReach</code> (drawing him pressed against a wall, and lowceil\'s check), '
            'the swing\'s arm solver and <code>legIK</code> (legs, unchanged). Gameplay\'s boxes (<code>BW</code>, <code>HEAD_UP</code>, <code>HANG</code>, the '
            'guards\' reach) are numbers that never read the figure.</li>'
            '<li>Held hands: hang, reach, pull, press, kneel, the slide\'s hilt, the crawl and the climb within 0.01 px; the sword hand in garde, windup and parry '
            'within 0.01 px; the lunge and the low strike 0.6 px (the straight arm cannot reach quite as far from the lower shoulder); the back hand in a fight is '
            'free (2 px lower).</li>'
            '<li>In the air with a grip (hang, reach, the slide, the first frames of the climb, the swing): the body hangs 2 px higher (up to 3.5 px nearer the bar '
            'at a 0.8 rad swing). Only the hands show over a ledge on a wall\'s near face, as before; the swing\'s hands are on the bar as before (at most 0.11 px further).</li>'
            '<li>The crown: at most 0.13 px higher (the drink\'s reach), within the 8x silhouette\'s step; lowceil (every low room, standing and running, figReach\'s '
            'top now taken from the head\'s size) has no head in the stone.</li>'
            '<li>The drink: the hand moves with the mouth (1 to 1.6 px), the hand-to-mouth offset within 0.6 px of before.</li>'
            '<li>figReach\'s front reach: up to 1.5 px less in the low leap, 1.2 px more crawling (the head reaches further on the longer neck): the figure is drawn '
            'pressed back from a wall face that much more. Look only.</li></ul>'
            '<p><b>Tests</b>: figscan ok (80 poses); lowceil ALL OK; lifttest 0 failures (its paternoster case passes); swingtest ok on floors 6 to 9; stairscan ALL '
            'OK (feet on the treads); run2 3 to 6, two seeds, 8/8 passed, no damage; run2 fight on 6, 7 and 12, all passed, no damage; rendersmoke 7 to 9 both '
            'modes, no errors (0.54 ms a frame against v69\'s 0.51 on this Mac).</p>' +
            '<p class="meta">(Round 22c: this round\'s guide, every-pose, game and moves sheets retired; round 22c\'s supersede them. Round 22c found that the "0.41 h over the acromion" above was measured to the shoulder joint, see there.)</p>' +
            '<p class="meta">Retired to stay at 505 files: round 22\'s three sheets (the guide, every pose, the game: superseded by this round\'s), round 21a\'s '
            'picture of the prince and round 19\'s arms-up sheet.</p>' +
            links([('ANSUR II anthropometric survey: the public data (Penn State OpenLab)', 'https://www.openlab.psu.edu/ansur2/'),
                   ('Gordon et al. 2014: 2012 Anthropometric Survey of U.S. Army Personnel, methods and summary statistics', 'https://hero.epa.gov/hero/index.cfm/reference/details/reference_id/8211558'),
                   ('Proportionality constants (Drillis and Contini, after Winter)', 'https://www.openlab.psu.edu/category/tools'),
                   ('Wisner et al.: upper body segment lengths as a proportion of height (Drillis and Contini checked)', 'https://ojs.ub.uni-konstanz.de/cpa/article/view/292'),
                   ('D. A. Winter, Biomechanics and Motor Control of Human Movement (segment lengths as fractions of stature, fig. 4.1)', 'https://onlinelibrary.wiley.com/doi/book/10.1002/9780470549148'),
                   ('A. Loomis, Figure Drawing for All It\'s Worth (1943): ideal proportion, proportions at various ages', 'https://archive.org/details/AndrewLoomisFigureDrawingForAllItsWorth2010TitanPublishingGroup'),
                   ('Proko: human proportions, idealistic figures (Loomis\'s landmarks)', 'https://proko.com/course-lesson/human-proportions-idealistic-figures/notes'),
                   ('Titcomb et al. 2024: craniovertebral angle in young adults', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC11042887/'),
                   ('Boing Boing (2014): the Prince of Persia rotoscope footage', 'https://boingboing.net/2014/10/30/how-prince-of-persias-famous.html'),
                   ('Flashback (1992): rotoscoped animation', 'https://en.wikipedia.org/wiki/Flashback_(1992_video_game)'),
                   ('Another World: rotoscoped polygons', 'https://en.wikipedia.org/wiki/Another_World_(video_game)'),
                   ('Blackthorne: sprites rotoscoped like Prince of Persia', 'https://en.wikipedia.org/wiki/Blackthorne'),
                   ('Oddworld: Abe\'s Oddysee', 'https://en.wikipedia.org/wiki/Oddworld:_Abe%27s_Oddysee'),
                   ('Inside (Playdead)', 'https://en.wikipedia.org/wiki/Inside_(video_game)'),
                   ('Prince of Persia: The Lost Crown', 'https://en.wikipedia.org/wiki/Prince_of_Persia:_The_Lost_Crown'),
                   ('T. Vasseur: Art design deep dive, a 3D pipeline for 2D animation in Dead Cells (Game Developer)', 'https://gamedeveloper.com/program/gama-archive'),
                   ('Blasphemous', 'https://en.wikipedia.org/wiki/Blasphemous_(video_game)'),
                   ('Celeste', 'https://en.wikipedia.org/wiki/Celeste_(video_game)'),
                   ('Rayman: limbless for want of processing power', 'https://en.wikipedia.org/wiki/Rayman_(character)'),
                   ('Cartoon Brew: the rubber hose classics behind Cuphead', 'https://www.cartoonbrew.com/classic/the-rubber-hose-classics-that-inspired-the-cuphead-show-213700.html'),
                   ('Pixel-art people: head share of sprite height, chibi to heroic', 'https://blakecrosley.com/blog/pixel-art-characters-on-iphone')]) + '</section>']
