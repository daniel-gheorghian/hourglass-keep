# egyptaudit.py: the "What changes from the current game" section of egypt_themes.html, an audit of the egypt branch against the game
# before it (v61, fd7ad8e, for the looks; v62, b4de22f, the WebGL release it is merged on). egyptround2.py puts it first. The floor
# table is computed from SCHED below, a copy of the game's own (themeOf in dev/hourglass-keep.html: keep the two the same).
TOD = ['dusk', 'night', 'dawn']
STYLE = ['dungeon', 'palace', 'tile', 'forge', 'crypt']
SCHED = [{'dungeon': ['nun', 'foggara', 'hawara'], 'palace': ['west', 'deffufa', 'shali'], 'tile': ['blue', 'wells', 'blue'], 'forge': ['meroe', 'meroe', 'napata'], 'crypt': ['osiris', 'osiris', 'aksum']},
         {'dungeon': ['hawara', 'nun', 'foggara'], 'palace': ['shali', 'west', 'deffufa'], 'tile': ['wells', 'blue', 'wells'], 'forge': ['napata', 'napata', 'meroe'], 'crypt': ['aksum', 'aksum', 'osiris']},
         {'dungeon': ['foggara', 'hawara', 'nun'], 'palace': ['deffufa', 'shali', 'west'], 'tile': ['blue', 'wells', 'wells'], 'forge': ['meroe', 'napata', 'napata'], 'crypt': ['osiris', 'aksum', 'aksum']}]


def look_at(n):
    b = (n - 1) // 4
    return SCHED[((n - 1) // 60) % 3][STYLE[b % 5]][((n - 1) // 20) % 3]


def visits(look, upto=180):
    return [(n, TOD[((n - 1) // 20) % 3]) for n in range(1, upto + 1, 4) if look_at(n) == look]


OLD = [('nun', 'The Cistern', 'The Waters of Nun'), ('west', 'Sandstone Halls', 'The Halls of the West'), ('blue', 'Lapis Gallery', 'The Blue Chambers'),
       ('meroe', 'Ember Forge', 'The Forges of Meroë'), ('osiris', 'Jade Crypt', 'The Green Hall of Osiris')]


def v61(i):
    return ', '.join('%d %s' % (n, TOD[((n - 1) // 20) % 3]) for n in range(4 * i + 1, 61, 20))


def section():
    rows = ''
    for i, (lk, a, b) in enumerate(OLD):
        vs = visits(lk)
        first = {t: next((n for n, tt in vs if tt == t), None) for t in TOD}
        rows += '<tr><td>%s → %s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (a, b, v61(i), ', '.join('%d %s' % v for v in vs if v[0] <= 120),
                                                                                 ' · '.join('%s %s' % (t, first[t]) for t in TOD))
    return '''<section class="card" id="audit"><h2>What changes from the current game</h2>
<p>An audit of the egypt branch against the game before it: v61 (fd7ad8e) for the looks, and v62 (b4de22f), the WebGL release it is merged on. Every item is in the diff.
<b>Headline: nothing in the game is left without something in its place.</b> What goes for good is a set of Persian and Islamic <i>motifs</i>; v61 still holds their code, and each has an
Egyptian counterpart drawn where it was. The real losses are small:</p><ul>
<li>the crenellated towers of the palace backdrop, which have no counterpart;</li>
<li>the five old names, and the names Hourglass Keep, Lalezar and Vazirmatn;</li>
<li>a share of the floors: each old look takes 4 floors in 20 in v61, and fewer now that twelve themes share them. In return the Forges and the Green Hall come back by moonlight on floors 33-40, and every old look is still seen in every light (the first 180 floors).</li></ul>
<h3>(a) Dropped for good: recoverable only from v61</h3><ul>
<li><b>The names:</b>
  <ul><li>the five old theme names: The Cistern, Sandstone Halls, Lapis Gallery, Ember Forge, Jade Crypt (the "by Moonlight / at Dawn / The Ruined" naming stays);</li>
  <li>the title Hourglass Keep. The cache key, the save key, the repo and its URLs keep the old name, so installed copies and saves go on working.</li></ul></li>
<li><b>The Persian hangings</b> (six designs and the shaft runner) and their dye palette.</li>
<li><b>The crenellated towers</b> among the palms of the palace backdrop. <b>The only thing with no counterpart in its layer.</b></li>
<li><b>Islamic architecture:</b>
  <ul><li>the pointed arch;</li>
  <li>the eight-pointed girih star;</li>
  <li>the muqarnas hoods and the lobed cusps;</li>
  <li>the diagonal window lattice;</li>
  <li>the dome-and-minaret window view;</li>
  <li>the little-arch cornice.</li></ul></li>
<li><b>The hourglass</b> as an object: the checkpoint's glass, the HUD's glasses and the gates' timers, and the word "sands" for the rewind.</li>
<li><b>The look of the old objects:</b> the brass lanterns, star lanterns, pitch torches, fire baskets and niche lamps; the iron-barred gate; the falling stone's rough rock; the cracked tile; the steel spikes; the sandstorm's wall of dust. All are kept in the code behind <code>EGP</code> (see c).</li>
<li><b>The fonts</b> Lalezar and Vazirmatn.</li></ul>
<h3>(b) Replaced by an Egyptian counterpart, built into the game</h3><ul>
<li><b>Twelve themes</b> instead of five. Each floor's theme has the drawing style its floor is built by, chosen by a schedule (see the table).</li>
<li><b>Architecture:</b> post and lintel under a cavetto cornice, and the winged sun over doorways; five-pointed stars; false doors; the kheker frieze; Djoser's faience; stone window slats; pylons, obelisks and palms in the windows.</li>
<li><b>Hangings:</b> painted linen and reed mats. <b>Backdrops:</b> one for each theme.</li>
<li><b>Lamps:</b> each theme's own lamp, on the wall and in openings.</li>
<li><b>Traps, as a look only:</b>
  <ul><li>the gate: a granite portcullis;</li>
  <li>the falling stone: a roof block running with sand;</li>
  <li>the loose tile: a sand floor;</li>
  <li>the spikes: bronze-tipped stakes;</li>
  <li>the sandstorm chase: granite plugs, one passage high, in every corridor row of the chase.</li></ul>
  The hints, How to play and the death notices name them.</li>
<li><b>The sky clock</b> (round 8: Nut arched over the earth, the sun disc travelling her body through the twelve hours; it replaced round 7's barque clock) for the hourglass:
  <ul><li>the checkpoint lights, then its night runs out;</li>
  <li>the HUD's three hours and the gates' timers are small sky clocks;</li>
  <li>the rewind runs the sun back, in a cool grade with ripples ("The hours turn back");</li>
  <li>every "hourglass" and "sands" in the text now says sky clock or hours.</li></ul></li>
<li><b>Title and fonts:</b> Dawnward, on the title screen, the page title, the manifest, the home-screen title and the bench header. Rokkitt and Jost.</li>
<li><b>Petals:</b> rose petals become lotus petals.</li>
<li><b>Rounds 7 and 8:</b> the prince as the original figure, bare-chested in a pleated shendyt with a thin muted gold belt (round 11), dark-skinned and lean, his natural hair cropped close (round 9), his build drawn in the silhouette and broad planes so it reads at the phone's size (round 10); all characters athletic, with oiled skin; the guards as tomb robbers (kilts, head cloths and caps; club, axe, khopesh); the flasks as core-formed glass jars; the lives as faience ib hearts; a thin cornice over the title and pause panels.</li>
<li><b>Colours:</b> the old five keep their palettes, except the Blue Chambers and the Halls' inlay.</li></ul>
<h3>(c) Still in the code behind a switch, or easy to bring back</h3><ul>
<li><code>EGP={lamps,traps,plug}</code> turns off the lamps, the trap re-skins and the plug: the v61 lamps, iron gate, rock, cracked tile, steel spikes and the sandstorm (its shader too) come back. The tests use it: metaltest's gate scene and stormfair check the iron gate and the storm.</li>
<li><b>Unused backdrop layers:</b> the domed city, the pavilions, the cypresses, the domed tombs, the Roman arcade (layer kinds in <code>bgPaint</code>).</li>
<li><b>Effects:</b> nothing the old five had is lost; the effects are set per theme in <code>LFX</code>. The Cistern's caustics and drips stay with the Waters of Nun.</li></ul>
<h3>How often the old looks appear</h3>
<p>Each block of four floors takes the drawing style the generator builds it by. Within that style, the theme is picked by the light and by which 60-floor turn of the day it is (<code>SCHED</code>). The schedule repeats every 180 floors.</p>
<table><tr><th>Look</th><th>v61: floors 1-60</th><th>Now: floors 1-120</th><th>First floor in each light</th></tr>%s</table>
<p>Within the first 60 floors:</p><ul>
<li>the Forges and the Green Hall are seen at dusk and by moonlight;</li>
<li>the Blue Chambers at dusk and at dawn;</li>
<li>Nun and the Halls at dusk.</li></ul>
<p>The Blue Chambers, the Forges and the Green Hall are seen in every light within 120 floors, Nun and the Halls within 180 (the dungeon and palace styles have three themes each, which take the three lights in turn). All twelve themes appear by floor 60.</p>
<h3>What stays</h3><ul>
<li><b>Play:</b> mechanics, physics, controls, the bot, and every trap's behaviour, hit box and timing. The plug's leading face is the storm's kill line, at the storm's speed, on the storm's rows.</li>
<li><b>The generator.</b> Floors 1-72, three seeds each, are identical to v62: walls, floors, traps, the bot's route, guards and lamp placement. <code>metrics40.py</code>: FLAGS none.</li>
<li><b>The rest of the game:</b> checkpoints and the rewind's rules (three measures, five seconds), the guards and their art, the HUD layout, the floor card, the sounds (no audio line changed), the Graphics switches, the save format and keys.</li>
<li><b>Torchlight's rules:</b> <code>AMB_MIN</code>, the sky beams, the mask atlas, and v62's WebGL scene path.</li></ul></section>''' % rows
