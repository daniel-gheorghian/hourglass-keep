# egyptround25b.py: round 25b's section of egypt_themes.html: both arms in the standing jumps, and the head up in the crawl (owner: "when the
# prince is jumping from a standstill on a lower coridor the raises this right arm but his left remains besides him. That is weird"; "nobody
# crawls with their head pointing down, should be pointing forward"). Pictures from egyptr25b.py.
import html
E = html.escape


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def table(head, rows):
    return ('<table><tr>' + ''.join('<th>%s</th>' % E(h) for h in head) + '</tr>' +
            ''.join('<tr>' + ''.join('<td>%s</td>' % E(str(c)) for c in r) + '</tr>' for r in rows) + '</table>')


def links(L):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(t)) for t, u in L) + '</ul>'


SOURCES = [
    ('Ashby and Heegaard 2002, role of arm motion in the standing long jump (J Biomech): free arms 21% farther, 2.09 against 1.72 m; '
     'mostly a faster take-off; the arms swung back in flight to check forward rotation (post-print, Brunel)', 'https://bura.brunel.ac.uk/bitstream/2438/537/1/%27Standing%20Long%20Jump%27%20Post-print.pdf'),
    ('Hara, Shibayama, Takeshita, Fukashiro 2006: the arm swing in the standing long jump and its timing (review in PMC)', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC7762633'),
    ('Kretch, Franchak and Adolph 2014, crawling and walking infants see the world differently (Child Development): with the neck neutral a '
     'crawler\'s face points at the floor; crawlers crane the head up to see ahead', 'https://faculty.ucr.edu/~franchak/publications/2014-KretchFranchakAdolph-ChiDev.pdf'),
    ('UBC kinesiology wiki: crawling (hands and knees in about 88% of infants; the abdomen raised and the head up)', 'https://wiki.ubc.ca/Course:KIN366/ConceptLibrary/Crawling'),
    ('Pathways.org: lifting the head in prone is the neck\'s extensors at work, before crawling', 'https://pathways.org/wp-content/uploads/2020/05/Typical-Movements-at-1-4Months_Final.pdf'),
    ('US Army FM 21-75, Combat Skills of the Soldier, ch. 4 (movement: the high and low crawl)', 'https://discmaster.textfiles.com/file/12458/Ebooks.tar/Text%20-%20Millitary%20-%20US%20ARMY%20-%20FM%2021-75%20-%20Combat%20Skills%20Of%20The%20Soldier%20%5B08-03-84%5D%20(PDF).zip/US%20ARMY%20FM%2021-75%20Combat%20Skill%20Of%20The%20Soldier/ch4.pdf'),
    ('Metal Gear wiki: crawl (Snake, Big Boss, Raiden crawl into small passages)', 'https://metalgear.fandom.com/wiki/Crawl'),
    ('CMU Graphics Lab Motion Capture Database (13_11 forward jump; 16_05 forward jump; 49_04 run, leap; 111_03 crawling)', 'http://mocap.cs.cmu.edu')]

ARMS = [
    ['16_05 (rounds 23 to 25a)', 'f110 crouch', '-34 / -31', '60 / 58', 'the elbows held bent by his sides the whole jump; 16_06 and 16_07 the same'],
    ['13_11 (round 25b)', 'f176-208 crouch', '-55 / -58', '20 / 13', 'both arms swung back, nearly straight'],
    ['13_11', 'f224-240 take-off', '+21 to +53 / +28 to +56', '62 / 68', 'both swung forward together'],
    ['13_11', 'f244 (jumpLowS)', '+52 / +49', '64 / 78', 'forward, hands at chest height'],
    ['13_11', 'f252 (jumpS)', '+42 / +34', '60 / 77', 'forward in flight'],
    ['13_11', 'f288-312', '-1 to -5 / -9 to -15', '', 'down by his sides to land'],
]

TESTS = ('figscan ok against v69 (crowns: the crawl 4.1 to 5.3 px under v69\'s crawl crown, 6.5 to 7.8 before; jumpLowS 1.25 under v69\'s, '
         '0.62 before; jumpS 2.25 under); lowceil ALL OK (no drawn pixel into the stone, open jumps carry as before); primtest: FAILURES 0; run2 floors 3 to 6, two seeds: 8 of 8 passed, 0 runs with damage (0.03 ms/frame); '
         'rendersmoke floors 7 to 9, both modes: no errors (0.56 ms/frame).')


def sections(D, REL, img):
    return ['<section class="card" id="r25b"><h2>Round 25b: both arms in the jump, the head up in the crawl</h2>'
            '<p>Owner: "when the prince is jumping from a standstill on a lower corridor ... raises this right arm but his left remains besides him. '
            'That is weird." And, of the crawl in a low tunnel: "nobody crawls with their head pointing down, should be pointing forward."</p>'
            '<h3>The cause of the arm</h3>'
            '<p>The standing jumps, open (jumpS) and low (jumpLowS), were CMU 16_05 frame 150 since round 23. That subject jumps with both elbows bent '
            'at 90 degrees, held by his sides through the crouch, take-off and flight (his upper arms 45 to 52 degrees back, forearms forward; 16_06 '
            'and 16_07, the same subject, do the same). Both arms had the same angles, so the far arm lay hidden behind the body while the near '
            'forearm stuck out level in front of the kilt: one arm raised, the other apparently hanging. The low leap pitches the trunk forward '
            'under the ceiling, which made the near forearm stand out more. Nothing procedural raised it; it was the clip. The running low leap '
            '(jumpLow, 49_04) already carries both arms forward and is unchanged.</p>'
            '<h3>Research</h3><ul>'
            '<li><b>The standing broad jump.</b> Both arms swing back as he crouches, then forward and up together through take-off. In flight '
            'they stay forward, and come down and back for the landing. The arms add about a fifth to the distance, mostly by a faster take-off '
            '(Ashby and Heegaard 2002: 2.09 m free against 1.72 m held). Under a low ceiling the same swing goes forward, not up: the hands lead '
            'the body along the corridor at chest height.</li>'
            '<li><b>The crawl.</b> On hands and knees with the neck held neutral, the face points at the floor. Infants crane the head up to see '
            'ahead (Kretch, Franchak and Adolph 2014), and lifting the head is the neck\'s extensors at work from the first months. A soldier\'s '
            'high crawl looks along the line of advance (FM 21-75). Games draw the crawl in profile with the head up and the face along the path: '
            'Metal Gear\'s crawl, and the low passages of Prince of Persia\'s descendants. Studies find crawlers often look down at the floor '
            'just ahead, so the face is set a little under the horizontal, not level.</li></ul>' + links(SOURCES) +
            '<h3>A: the standing jumps from 13_11 (forward jump)</h3>' +
            table(['clip', 'frames', 'upper arms, near / far (deg from down, + forward)', 'elbows (deg)', 'what the arms do'], ARMS) +
            '<ul><li><b>jumpS</b> (an open room): 13_11 frame 252, both arms forward in flight (was 16_05 f150).</li>'
            '<li><b>jumpLowS</b> (a ceiling at his height): 13_11 frame 244, just after take-off, both arms forward. As before, the trunk is pitched '
            'forward until the head is no higher than v69\'s (lean -0.14 to 0.59; was 0.31). The hands stay at chest height, '
            'under the crown: figReach\'s top in the low rooms is unchanged in lowceil.py.</li>'
            '<li>Unchanged: the crouch before the jump (16_05 f110), the landing (16_05 f203), the kick-shaft tuck and reach, jumpLow and jumpR, and '
            'every timing, launch speed, hit box and distance.</li></ul>'
            '<h3>B: the crawl looks ahead</h3><ul>'
            '<li>A new pose value <b>hp</b>: the skull\'s pitch on the top of the neck, at the atlas. The head\'s shape, the eye and the hair turn by it '
            'while the neck and the skeleton keep lean+head. It is 0 in every pose but the crawl.</li>'
            '<li>All 16 crawl keys (111_03, a weak clip whose subject carries her head on the trunk\'s line, the face to the floor: neck line 1.2 rad '
            'from straight up): the neck line is set to 0.80 rad (CRAWL_NECK, 28 degrees of extension at the base of the neck against the trunk\'s 74 '
            'degrees), keeping the clip\'s own small nod, and the skull turns up on it by 0.45 rad (CRAWL_HP, 26 degrees). The face looks about 20 '
            'degrees under the horizontal, the chin forward, the eye clear of the shoulder. 54 degrees in all, within the neck\'s range of '
            'extension.</li>'
            '<li>The sword held low and the poke use the crawl\'s keys, so they look ahead too. Going in and coming out, the pose eases between the '
            'standing pose (hp 0) and the crawl, so the head lifts as he goes down.</li>'
            '<li>The crown rises 2.4 px and is still 4 to 5 px under v69\'s crawl crown, and far under the tunnel\'s 30 px of headroom. Palms on '
            'the floor, knees, feet, hit boxes and timing are unchanged.</li></ul>' +
            fig(img, 'r25b_poses.png', 'At 4x, round 25a (before) above round 25b (after), each frame as the game makes it: the low standing leap '
                'through take-off, flight and landing; the running low leap; the open standing jump; the crawl\'s keys, the sword held low and the poke '
                'in a tunnel, then going in and coming out. Red: the ceiling\'s underside') +
            fig(img, 'r25b_game.png', 'In the game at the phone\'s resolution, Torchlight and Classic, round 25a | round 25b: the low standing leap '
                'in mid-flight (top), the crawl in a tunnel (bottom)') +
            '<h3>Tests</h3><p>' + E(TESTS) + '</p>'
            '<p class="meta">Retired to keep the page at 505 pictures: round 9\'s r9_hair_sheet.png and r9_flasks_drink.gif.</p></section>']
