# egyptaudit.py: the "What changes from the current game" section of egypt_themes.html, an audit of the egypt branch's diff against
# v61 (main, fd7ad8e): git diff fd7ad8e -- dev/hourglass-keep.html. egyptround2.py puts it first. The floor table is computed here.
TOD = ['dusk', 'night', 'dawn']


def where(i, k, first=200):
    out = []
    for f in range(1, first + 1):
        if ((f - 1) // 4) % k == i and (f - 1) % 4 == 0:
            out.append('%d %s' % (f, TOD[((f - 1) // 20) % 3]))
    return out


def night(i, k):
    for f in range(1, 1000):
        if ((f - 1) // 4) % k == i and ((f - 1) // 20) % 3 == 1:
            return f


OLD = [('The Cistern', 'The Waters of Nun'), ('Sandstone Halls', 'The Halls of the West'), ('Lapis Gallery', 'The Blue Chambers'),
       ('Ember Forge', 'The Forges of Meroë'), ('Jade Crypt', 'The Green Hall of Osiris')]


def section():
    rows = ''.join('<tr><td>%s → %s</td><td>%s</td><td>%s</td><td>%d → %d</td></tr>' % (a, b, ', '.join(where(i, 5, 60)), ', '.join(where(i, 12, 160)), night(i, 5), night(i, 12))
                   for i, (a, b) in enumerate(OLD))
    nf, ng = night(3, 12), night(4, 12)
    return '''<section class="card" id="audit"><h2>What changes from the current game</h2>
<p>An audit of the egypt branch against v61 (main, fd7ad8e), from <code>git diff fd7ad8e -- dev/hourglass-keep.html</code>; every item below is in that diff.
<b>Headline: nothing in the game is left without something in its place.</b> What goes for good is a set of Persian and Islamic <i>motifs</i>; their drawing code is deleted, though v61 still holds it,
and each has an Egyptian counterpart drawn where it was. The real losses are smaller, and worth knowing:</p><ul>
<li>the crenellated towers of the palace backdrop, which have no counterpart;</li>
<li>the five old names;</li>
<li><b>how often the old looks are seen.</b> With twelve themes, each of the five old looks comes round every 48 floors instead of every 20. The Forges and the Green Hall are not seen by moonlight until floors %d and %d (in v61: floors 33 and 37).</li></ul>
<h3>(a) Dropped for good: deleted from the code, recoverable only from v61</h3><ul>
<li><b>The five names:</b> The Cistern, Sandstone Halls, Lapis Gallery, Ember Forge, Jade Crypt. The "by Moonlight / at Dawn / The Ruined" naming stays.</li>
<li><b>The Persian hangings,</b> all six designs and the shaft runner, and the dye palette (madder, indigo, weld) they used. The designs: cypress and birds in the qalamkar manner, vases of flowers, the boteh field, the peacock with its diamond border, the medallion with tiraz bands, the mihrab-arch niche hanging.</li>
<li><b>The crenellated towers</b> among the palms of the palace backdrop. <b>This is the one thing with no counterpart in its layer;</b> the pylons are a separate, nearer layer.</li>
<li><b>The pointed Persian arch</b> for open arches, doors and windows.</li>
<li><b>The eight-pointed girih star,</b> everywhere it was drawn: door leaves, spandrels, the tiled dado, the tiled pedestal, the hangings, and the crypt window's open cut-out (fixed in this round).</li>
<li><b>The muqarnas hoods</b> over the crypt niches and crypt doors, and <b>the lobed cusps</b> along the tiled halls' arches.</li>
<li><b>The windows' insides:</b> the diagonal lattice over the tiled halls' windows, and the dome-and-minaret silhouette seen through the palace windows.</li>
<li><b>The little-arch cornice</b> along the tops of walls.</li></ul>
<h3>(b) Replaced by an Egyptian counterpart, drawn where the old one was</h3><ul>
<li><b>Arches, doors, windows:</b> post and lintel under a cavetto cornice; the Cistern/Nun style keeps its round vaults. A winged sun disc over the doorways of the palace, tiled and crypt styles.</li>
<li><b>Stars:</b> the five-pointed star of the tomb ceilings, wherever the girih star was.</li>
<li><b>Hangings:</b> painted linen and reed mats (a lotus pool, lotus friezes, a reed mat, a star ceiling under a kheker frieze, the winged sun over a broad collar, a papyrus column) and a lotus and reed-mat runner.</li>
<li><b>Small parts:</b>
  <ul><li>niches: false doors;</li>
  <li>wall-top cornice: the kheker frieze of tied reeds;</li>
  <li>tiled dado: Djoser's faience oblongs;</li>
  <li>window lattice: upright stone slats;</li>
  <li>palace window view: a pylon, an obelisk and a palm.</li></ul></li>
<li><b>Backdrops:</b>
  <ul><li>the domed city with minarets: temple pylons and the Theban hills with el-Qurn;</li>
  <li>pavilions and cypresses: Djoser's step pyramid and its niched wall;</li>
  <li>the Roman arcade: papyrus-bundle columns;</li>
  <li>domed tombs: shrines;</li>
  <li>the forge also gains Meroë's pyramids.</li></ul></li>
<li><b>Petals</b> in the tiled halls: rose petals become blue and white lotus petals.</li>
<li><b>Colours:</b> the old five keep their palettes, except the Blue Chambers (a bluer wall, a blue-green faience instead of the lapis tile) and the Halls' inlay (a redder ochre).</li></ul>
<h3>(c) Still in the code behind a switch, or easy to bring back</h3><ul>
<li><b>Lamps:</b> the game still draws the brass lanterns, star lanterns, pitch torches, fire baskets and niche lamps. The Egyptian lamps are behind <code>EGP.lamps</code>, which is off.</li>
<li><b>Traps:</b> unchanged on screen. The granite portcullis, roof block, sand floor and stakes are behind <code>EGP.traps</code>, the granite plug behind <code>EGP.plug</code>; both are off. Choppers, saws, pendulums, darts and fire vents are unchanged.</li>
<li><b>Fonts:</b> the game still loads Lalezar and Vazirmatn. Rokkitt + Jost is a proposal: one line in the page head, plus the canvas font strings.</li>
<li><b>Name:</b> the game is still titled Hourglass Keep.</li>
<li><b>Unused backdrop layers</b> still in the code: the domed city, the pavilions, the cypresses, the domed tombs, the Roman arcade. Each is a layer kind in <code>bgPaint</code>, and one line in <code>BGART</code> brings any of them back.</li>
<li><b>Effects:</b> nothing the old five had is lost.
  <ul><li>The Cistern's caustics and drips stay with the Waters of Nun. They are now set per theme (<code>LFX</code>), not per drawing style, so the dungeon-style Labyrinth of Hawara does not get them.</li>
  <li>Per drawing style as before: the wet sheen, the crypt and dungeon mist, the night mist, sand gusts, ash and sparks, fireflies, wisps and bats.</li>
  <li>Changed: the Forges' flames shimmer a little more (0.6 against 0.5), and the Blue Chambers gain a faience glint.</li>
  <li>Some new themes switch style effects off: the Deffufa, the Well Corridors, Napata, Hawara and Shali have no wet sheen, and the dust themes among them have dust instead of mist. This touches none of the old looks.</li></ul></li></ul>
<h3>How often the old looks appear</h3><p>Themes now repeat every 48 floors; the time of day still turns every 20.</p>
<table><tr><th>Look</th><th>v61: first floor of each visit, floors 1-60</th><th>Now: floors 1-160</th><th>First by moonlight</th></tr>%s</table>
<p>Each old look took 20%% of the floors (4 in 20); now it takes 8%% (4 in 48). Within the first 60 floors each was seen three times, once in each light. Now Nun, the Halls and the Blue Chambers are seen twice (dusk and dawn), the Forges and the Green Hall once. If the Forge by Moonlight (the owner's look of v56-57) matters early on, the order could put two old themes inside floors 21-40.</p>
<h3>What stays</h3><ul>
<li><b>Play:</b> mechanics, physics, controls, the bot, and every trap's behaviour, hit box and timing.</li>
<li><b>The generator.</b> It builds by the old five-theme turn (<code>L.gstyle</code>). Floors 1-72, three seeds each, have the same walls, floors, traps, route and guard count as v61. From floor 49 on, where the drawing style differs from v61's, some look-only placements that depend on it differ: the wall breaches, where the hangings go, and which lamps the wear relights.</li>
<li><b>The rest of the game:</b>
  <ul><li>the hourglass: checkpoints, the HUD's glasses, the rewind and its words, the gates' timers;</li>
  <li>the guards and their art (each new theme has its own two guard colours);</li>
  <li>the HUD layout and the floor card;</li>
  <li>the sounds (no audio line changed);</li>
  <li>the Graphics switches.</li></ul></li>
<li><b>Torchlight's rules:</b> <code>AMB_MIN</code>, the sky beams, the mask atlas, and the five drawing styles' light, grade and mist tables.</li></ul></section>''' % (nf, ng, rows)
