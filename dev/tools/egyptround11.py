# egyptround11.py: round 11's section of egypt_themes.html (built in): the prince's belt a thin muted band. Pictures from egyptr11.py
# (round 10 and round 11 at the phone's resolution, both modes, standing, running, jumping, hanging, fighting).
import html
E = html.escape


def sections(D, REL, img):
    return ['<section class="card" id="belt11"><h2>The belt, round 11 (built in)</h2><p>Owner: "Ok, the sash stands out too much, it looks like a circle."</p>'
            '<p>Why it read as a circle: a bright yellow band 3 px tall (with its outline), straight across the waist, and the scabbard\'s gold guard below it. A tie with two links hung at the front and tails trailed behind. '
            'At the phone\'s size these merged into a yellow ring round his middle.</p><ul>'
            '<li><b>A thin band</b> about a third of the height, roughly 1 px of gold between two fine dark edges, following the waist. Seen side on it is a short band across the body. It dips a little toward the front as a wrapped belt does, so it never closes into an ellipse.</li>'
            '<li><b>Muted gold</b>, a darker ochre close to the kilt\'s linen in value, with one hairline of bright gold along its top edge on the lit side only. It is drawn colour, not light, so it does not bloom.</li>'
            '<li><b>One short, slim end</b> hangs at the front. The trailing tails behind are dropped for the prince; the robbers keep theirs.</li></ul>'
            '<p>Checked at the phone\'s resolution in both modes, standing, running, in a jump, hanging (climbing) and fighting, with the bot playing. Every in-game shot on this page has been re-taken with the current figure, apart from the earlier rounds\' own comparisons.</p>'
            '<h3>Round 10 (top) and round 11 (bottom), crops of the 1704 px canvas at 1:1</h3>'
            '<figure>%s<figcaption>Torchlight</figcaption></figure><figure style="margin-top:8px">%s<figcaption>Classic</figcaption></figure></section>' % (
                img('r11_sash_torch.png', 'belt, Torchlight'), img('r11_sash_classic.png', 'belt, Classic'))]
