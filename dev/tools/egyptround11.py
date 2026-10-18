# egyptround11.py: the belt, hips and seat (rounds 11 and 12, built in) for egypt_themes.html. Pictures from egyptr11.py (round 11
# and round 12 at the phone's resolution, both modes, standing, running, jumping, hanging, fighting; the standing hips at 4x).
import html
E = html.escape


def sections(D, REL, img):
    return ['<section class="card" id="belt11"><h2>The seat, hips and belt, round 12 (built in)</h2>'
            '<p>Owner, on the area circled on round 11\'s sheet: "I was referring to that area: the sash should be close to the waist line also the loin cloth. That area is the ass of the prince and should be round and merge into the back, '
            'the sash is just above and follows the waist line. Now it is bulging straight and looks weird."</p>'
            '<p><b>What was wrong.</b> The kilt was a four-sided shape. Its top edge ran straight across the body, wider than the waist, and its back edge ran straight down to the hem. The belt was drawn across the same width. '
            'So behind him the belt and the kilt\'s top stood off the body as a flat shelf, past the line of the lower back, with a corner where the seat should be. Round 11 thinned the belt but kept that shelf.</p><ul>'
            '<li><b>The body:</b> the back\'s outline goes in at the waist (the narrowest point, just above the seat) and out over the buttocks, which are the rearmost point below the waist, at about the height of the hip joint. '
            'From there it curves back in under the seat into the back of the thigh: one S-curve with no corner. When the hips flex (a crouch, a landing, a tuck) the seat rounds further.</li>'
            '<li><b>The kilt</b> is now one rounded outline laid on that body. Its top sits on the waist line, a little higher at the back and lower at the front, as it is worn. At the back the linen wraps the seat closely and follows its curve into the back of the thigh. '
            'At the front the pleated panel still hangs a little forward to the hem above the knee. The hem runs between the thighs\' front and back edges, whichever leg is forward or back, so it follows the stride.</li>'
            '<li><b>The belt</b> runs along the waist line from the back\'s outline to the front\'s and never past them, higher at the back and lower at the front. The prince keeps round 11\'s thin, muted gold band with its one short end.</li>'
            '<li><b>The robbers</b> get the same back, seat and kilt. Their plain kilts wrap the seat, and their wider belts hug the waist the same way; their sash ends hang from the belt at the back.</li></ul>'
            '<p>Checked in stand, run, jump, hang or climb, fight, crouch, fall, land and kneel, facing both ways. The figures\' masks follow the new outline, since they are drawn from the same shapes.</p>'
            '<p><b>Round 11</b> (owner: "the sash stands out too much, it looks like a circle"): the belt went to about a third of its height, a muted gold close to the kilt, with a hairline of bright gold on the lit side and one short slim end; the prince\'s trailing tails were dropped.</p>'
            '<h3>Round 11 (top) and round 12 (middle), crops of the 1704 px canvas at 1:1; below, the standing hips and back at 4x</h3>'
            '<figure>%s<figcaption>Torchlight</figcaption></figure><figure style="margin-top:8px">%s<figcaption>Classic</figcaption></figure></section>' % (
                img('r11_sash_torch.png', 'seat and belt, Torchlight'), img('r11_sash_classic.png', 'seat and belt, Classic'))]
