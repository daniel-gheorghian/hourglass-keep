# egyptround24.py: round 24's section of egypt_themes.html: the prince bulkier (owner, after v70: "Still too lean: make it bulkier").
# Numbers from r23bulk.json (r23poses.py); pictures from egyptr24.py.
import html, json, os
E = html.escape
HERE = os.path.dirname(os.path.abspath(__file__))


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def table(head, rows):
    return ('<table><tr>' + ''.join('<th>%s</th>' % E(h) for h in head) + '</tr>' +
            ''.join('<tr>' + ''.join('<td>%s</td>' % E(str(c)) for c in r) + '</tr>' for r in rows) + '</table>')


def links(L):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(t)) for t, u in L) + '</ul>'


SOURCES = [('Proko: idealistic proportions after Loomis (shoulders 2 1/3 heads, hips 1.5; idealised figures 8 heads and more)', 'https://proko.com/human-figure-proportions-idealistic-loomis'),
           ('Loomis, Figure Drawing for All It\'s Worth (1943), ideal and heroic male proportion plates', 'https://ia804504.us.archive.org/14/items/livros-andrew-loomis/1943%20-%20Figure%20Drawing%20For%20All%20It%27s%20Worth%20-%20Andrew%20Loomis_text.pdf'),
           ('Tropedia: Heroic Build (comics heroes: broad shoulders, V-taper, eight and a half heads)', 'https://tropedia.fandom.com/wiki/Heroic_Build'),
           ('Disney\'s Hercules: Andreas Deja and Gerald Scarfe started the hero from Greek statues and pottery (character studies)', 'https://comics.ha.com/itm/animation-art/production-cel/hercules-character-development-and-character-study-drawing-pair-by-disney-legend-andreas-deja-walt-disney-1997-/a/7408-18180.s'),
           ('Art of Hercules (character design references)', 'https://characterdesignreferences.com/art-of-animation-5/art-of-hercules'),
           ('Prince of Persia: The Lost Crown: Sargon\'s well-trained body for fighting and climbing, comic-book cel look (TechRadar DE preview)', 'https://global.techradar.com/de-de/gaming/prince-of-persia-the-lost-crown-vorschau-erhabene-2d-action'),
           ('Prince (Prince of Persia): the Sands of Time redesign maturing with each sequel (Warrior Within\'s rougher, heavier hero)', 'https://en.wikipedia.org/wiki/Prince_(Prince_of_Persia)'),
           ('csanyk: a 16x16 Hulk sprite: bulk only read after ~4 px of girth; thick limbs merge with the body unless a second shade parts them', 'https://csanyk.com/tag/hulk/'),
           ('Silhouette first: a character must read filled solid black (Binus DKV)', 'https://binus.ac.id/bandung/dkv/2025/11/04/the-power-of-silhouette-designing-readable-characters-in-motion/'),
           ('Pixel character guide: silhouette, then colour, then detail', 'https://pixnote.net/en/learn/character')]

TESTS = ('At the game\'s level 1.65: figscan ok against v69 (held hands, crowns, soles, the swing\'s bar, the drink\'s hand); lowceil ALL OK; '
         'swingtest ok (floors 6 to 9); liftscan floors 3 to 12 both modes; rendersmoke floors 7 to 9 in both modes. At 1.85 (window.__MUS): '
         'figscan ok, lowceil ALL OK.')


def sections(D, REL, img):
    J = json.load(open(os.path.join(HERE, 'r23bulk.json')))
    T = {q['m']: q['table'] for q in J['levels']}
    LV = [1.28, 1.45, 1.65, 1.85]
    R = T[1.28]

    def w(t, k, i, rob=False):
        if k == 'T':
            return (t['Fo'][i] + t['BQ'][i]) * (t['robK'] if rob else 1) + 0.75
        return t[k + ('R' if rob else '')][i] + 0.75
    meas = [('deltoid (profile)', 'arm', 0, 'delt'), ('upper arm', 'arm', 1, 'arm'), ('above the elbow', 'arm', 2, 'armLo'), ('forearm', 'arm', 4, 'fore'),
            ('thigh at the fold', 'leg', 0, 'thigh'), ('calf', 'leg', 4, 'calf'), ('chest depth', 'T', 6, 'chest'), ('lower ribs (lats)', 'T', 4, 'lowch'),
            ('waist depth', 'T', 2, 'waist'), ('seat depth', 'T', 0, 'seat'), ('elbow, wrist, knee, ankle', 'arm', 3, None)]
    rows = []
    for lab, k, i, g in meas:
        rows.append([lab, '%.2f / %.2f' % (J['grow'][g], J['grow2'][g]) if g else '0 (joints)'] +
                    ['%.2f' % w(T[m], k, i) for m in LV] + ['%.2f' % w(R, k, i, True)])
    return ['<section class="card" id="r24"><h2>Round 24: bulkier (MUS 1.65)</h2>'
            '<p>Owner, after seeing v70 in the game: "Still too lean: make it bulkier". v70 drew MUS 1.28, the natural near-limit of round 23b, '
            'and round 23b had already noted that it moved the outline by under a pixel at 1x: on the phone he still read as lean. This round goes '
            'past the natural range into a stylised, heroic one, renders three levels and <b>puts the middle one in the game (1.65)</b>, so the owner '
            'can move one step either way.</p>'
            '<h3>Research: the heroic young hero, and what reads at 50 px</h3><ul>'
            '<li><b>Heroic proportion.</b> Loomis\'s idealised man is wider in the shoulders than the real one (2 1/3 heads, hips 1.5), and comics '
            'push further: broad deltoids and lats, a deep chest, thick forearms and calves over a narrow waist, the V-taper that reads as strong '
            'and agile at once (a blocky, waistless trunk reads as a brute). Disney\'s Hercules (Deja and Scarfe) was built from Greek statues: a '
            'classical young hero\'s mass, exaggerated in the limbs, not a bodybuilder. Ubisoft\'s princes went the same way from the 1989 kid: The '
            'Sands of Time\'s lithe athlete, Warrior Within\'s heavier fighter, The Lost Crown\'s Sargon a "well-trained" hero drawn in a comic-book '
            'cel look. God of War\'s Kratos is past what an acrobat could be: our ceiling.</li>'
            '<li><b>Side view.</b> In profile the V-taper is a depth taper: chest and lats deep, the abdomen flat, the seat full; the deltoid is a '
            'cap that tapers down the arm to its insertion, the calf swells behind the shin. Mass behind the shoulder must run from the nape to '
            'the lats as one slope, or it reads as a hump (the owner\'s round 21a rule).</li>'
            '<li><b>Small sprites.</b> Bulk reads only in the silhouette (fill him black: does he look strong?), and only with whole pixels: a '
            '16x16 Hulk needed about 4 px more girth before it read, and thick limbs merge with the trunk unless a second shade parts them. So '
            'each level here adds about 0.5 to 0.6 px to the upper arm and forearm, 0.6 px to the calf, about 1 px to the deltoid and 1.1 px to '
            'the chest\'s depth at 1x (2 to 3 device pixels on the phone), and the arm keeps its soft contour over the body. The outline stays '
            '1.25 px: a thicker line reads as a cartoon, not as mass.</li></ul>' + links(SOURCES) +
            '<h3>What changed</h3><ul>'
            '<li>r23poses.py: <b>MUS 1.65</b> (was 1.28); levels 1.45, 1.65, 1.85 added to R23MUS. Up to <b>NAT = 1.28</b> every measure grows at '
            'round 23b\'s measured rates (GROW), so 1.28 is v70 to the pixel; past it at the stylised rates <b>GROW2</b>: deltoid 1.2, the upper '
            'arm 1.0, above the elbow 1.0, the forearm 1.15 (was 0.55), chest 0.85, lats 1.0, trapezius 1.0, thigh 0.8, above the knee 0.75, calf '
            '0.95 (was 0.55), soleus 0.7, seat 0.6, neck 0.6, and the waist only 0.06: the V-taper sharpens. Joints, bones, skeleton, poses, '
            'grips, hit boxes and timers are unchanged.</li>'
            '<li><b>TRUNK_G2</b> lays the trunk\'s growth past 1.28 further behind at the armpit and upper back (lats 60%, the upper chest 65-70% '
            'behind): with round 23b\'s shares the lats bulged lower than the shoulder blades and the big rear deltoid stood out of the back with '
            'a notch under it.</li>'
            '<li><b>RD.du</b>: past 1.28 the biceps\' point moves down the upper arm (0.22 to 0.32 of it by 1.85), so the bigger deltoid tapers '
            'to its insertion instead of standing as a ball.</li>'
            '<li>The muscle lines (deltoid V, pectoral border, RD.mh) strengthen a little: 0.6 at 1.28, 0.76 at 1.65, 0.85 at 1.85.</li>'
            '<li><b>Robbers keep v70\'s widths</b>: a new table R23DR (level 1.28) is used for every robber whatever the prince\'s level '
            '(drawFigureHD swaps it in for figures that are not the prince). At 1.65 the prince is now about as broad as a robber: his deltoid '
            '(7.11 px) and chest (10.03) pass the robber\'s (6.30, 9.06), his upper arm (4.88) passes the robber\'s 4.47, while the robber keeps '
            'the heavier waist (6.25 against 5.65), seat and joints.</li></ul>'
            '<h3>Widths across at 1x, outline included (px)</h3>' +
            table(['measure', 'rate to 1.28 / past it'] + ['MUS %s%s' % (m, ' (v70)' if m == 1.28 else ' (game)' if m == 1.65 else '') for m in LV] + ['robber (v70)'], rows) +
            fig(img, 'r24_bulk.png', 'v70 (1.28) | 1.45 | 1.65 (the game) | 1.85: standing at 10x; at 1x, 2x, 3x beside a robber (unchanged); '
                'stand, run, hang, climb, en garde, crouch and drink at 4x; the widths table') +
            fig(img, 'r24_game.png', 'In the game at the phone\'s resolution, Torchlight and Classic: standing, running, hanging behind a wall\'s '
                'face (only his hands show, as before), climbing, fighting a robber; v70 (1.28) | round 24 (1.65)') +
            '<h3>Choosing another level</h3><p>window.__MUS = 1.45 or 1.85 before the page loads, or __HK.setMus(m) at run time, draws another level '
            '(the pictures use it); to make one the game\'s, set MUS in r23poses.py and run it.</p>'
            '<h3>Tests</h3><p>' + E(TESTS) + '</p>'
            '<p class="meta">Retired to keep the page at 505 pictures: round 9\'s r9_prince_before.png and r9_prince_after.png.</p></section>']
