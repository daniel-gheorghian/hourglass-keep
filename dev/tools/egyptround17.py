# egyptround17.py: round 17's section of egypt_themes.html (built in): the gold sparkle where the climb or the drop to a secret
# passage's gold flask starts. Pictures from egyptr17.py; the floors used and the scan in egypt_themes/r17.json.
import html, json, os
E = html.escape


def links(src):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(l)) for l, u in src) + '</ul>'


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def sections(D, REL, img):
    J = json.load(open(os.path.join(D, 'r17.json')))
    sc = J['scan']
    return ['<section class="card" id="r17"><h2>Round 17 (built in): a gold sparkle where the way to the gold flask starts</h2>'
            '<p>Owner: "add the sparkling hint somewhere on the corridor when there is an ascent or descent for getting a yellow life up potion".</p>'
            '<h3>What it is based on</h3><ul>'
            '<li><b>Prince of Persia (1989)</b> hides its extra-life potions behind ordinary moves (a ledge to climb, a floor to drop through), and its only cues are at the spot itself: a loose tile shows by its rattle where he stands; the hint books\' advice was to jump in place in every new screen. '
            'Dawnward\'s cue was only on the flask, a storey away and usually off screen.</li>'
            '<li><b>Glints mean "look here"</b> across games: "investigate anything that glows" (items picked out by sparkles; Tomb Raider 2013 and Uncharted mark grabbable ledges by their colour, at the ledge). '
            '<b>Celeste</b> marks its hidden strawberries with something a little out of place where the hidden way starts (a block, a wall of another colour), not at the berry.</li>'
            '<li>A study of cues in Metroidvania levels: subtle cues keep the sense of discovery, emphasised ones are best for marking one item or secret. '
            'So: a few small stars, at the place he stands to make the move, in the flask\'s own gold, never a beacon.</li></ul>'
            '<h3>What it does</h3><ul>'
            '<li>Five small gold four-point stars (the hidden flask\'s own, with a white core and a soft added glow so they read gold on any stone and under any tint) twinkle on the lip\'s <b>top face</b>, spread in depth along the edge as the floor tiles\' edges run (the oblique view), a few at a time. '
            '<b>Ascent</b> (the passage\'s gallery a storey up, or a gold flask on an alcove\'s ledge): on the ledge he grabs from the corridor, on its open side, lifting a few pixels off it. '
            '<b>Descent</b> (the passage a storey down): on the edge of the floor he hangs from, slipping over the edge toward the hole as they fade. '
            'They go with the flask: once it is drunk (and on a floor whose gold flask was drunk before) there is none.</li>'
            '<li>The place is found once per floor from the tiles (<code>secretCues</code>: <code>L.secret</code> and which neighbour is open), so the generator, the floors and the bot are unchanged; drawn only when the lip is in view, with fixed colours and the cached light sprite (no allocation a frame), in the shared drawing code, so the same in Torchlight and Classic in every theme. '
            'The hint card now says "down there" for a descent.</li>'
            '<li>Floors 1-48 (seed 4400+n): %d gold flasks, %d up a ledge and %d down a drop, each with its cue; %d alcove fallbacks.</li></ul>' % (sc['secret'] + sc['alcove'], sc['up'], sc['down'], sc['alcove']) +
            fig(img, 'r17_cue.png', 'An ascent and a descent in the Waters of Nun and the Halls of the West, Torchlight and Classic, at 1:1 (above) and 2x (below)') +
            '<figure style="max-width:620px;margin-top:8px">%s<figcaption>The Waters of Nun: ascent (left) and descent (right), Torchlight, 0.1 s a frame</figcaption></figure>' % img('r17_cue.gif', 'sparkle') +
            links([('TV Tropes, "Experience has taught me to investigate anything that glows" (sparkling items; Tomb Raider 2013 and Uncharted ledges)', 'https://tvtropes.org/pmwiki/pmwiki.php/Main/NotIceThis'),
                   ('Utilization of visual cues to improve navigation in Metroidvania-style level design (subtle, integrated and emphasised cues)', 'https://core.ac.uk/works/156889970'),
                   ('Prince of Persia hints (jump in place to find loose tiles; the extra-life potions)', 'https://discmaster.textfiles.com/file/13455/September%2093.iso/Archives/Games/Cheats%E2%81%84hacks%E2%81%84hints/Prince%20of%20Persia/Prince%20of%20Persia%20Hints/Prince%20of%20Persia%20Hints.pdf'),
                   ('Celeste wiki, Shrine: the out-of-place block where a hidden way starts', 'https://celestegame.fandom.com/wiki/Shrine'),
                   ('Celeste wiki, Crossing: a smashable wall hiding a strawberry', 'https://celestegame.fandom.com/wiki/Crossing'),
                   ('Game Maker\'s Toolkit, Why Nathan Drake doesn\'t need a compass (cues built into the level)', 'https://www.youtube.com/watch?v=k70_jvVOcG0')]) + '</section>']
