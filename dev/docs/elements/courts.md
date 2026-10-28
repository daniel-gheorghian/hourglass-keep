# Courts

Stretches of a corridor open to the sky, mixed into the halls (round 45). The owner asked for outdoor play "as courts mixed into the halls",
with "a portico or pergola overhead is enough". From round 45's alternatives (C1-C5) the owner chose one kind per theme family, the pool as
the courts' water ("a fall into water kills"), and the light well for the interior themes' halls.

He walks the covered side of a court: a portico or a vine pergola. The ceiling's stone overhead is drawn as that roof's edge. Behind the
back plane the court opens: its ground, its far side and the theme's own sky and land.

Courts are look only. They are laid last in `genLevel` from hashes, with no generator stream. Tiles, features, the bot's path, lamps and
windows are untouched (`layoutcmp.py` against v86: same, 144 of 144). The one play change is the pool: a fall into it drowns him at the
water's surface instead of impaling him on the stakes a storey lower.

## Round 45c: thresholds, Meroë's grade, Aksum's depth (owner)

**Thresholds** (owner chose C, "respecting the theme: no standard single way of doing it"). At each end of a court a near jamb stands on the
front plane and he (and the guards) pass behind it. It is the layering rule's one exception: an L3 part in a cell that is not a wall, drawn
live after the figures and the air (`ctJambs`, after `windDraw`; see [layers](../layers.md)). Its form follows the theme (`jambKind`, `JAMB_W`;
two forms each, by a hash of the court and the end, so a court's two ends may differ):

| Themes | Kind | Width | Form A | Form B |
|---|---|---|---|---|
| West, Blue, Hawara, Osiris | `pap` | 12 | a dressed anta with an engaged papyrus half-column (bud capital, painted bands, sepals) | a papyrus-bundle column, round and ribbed |
| Napata, Meroë (and Meroë's light wells) | `pylon` | 14 | a battered pylon edge with its torus roll and painted cavetto | the same with an incised relief (the king smiting) |
| Garama, Kerma, Shali | `mud` | 12 | a mudbrick pier with a whitewashed reveal | a palm-log post (its leaf-base scars) before the wall's whitewashed end |
| Aksum | `aks` | 13 | a monkey-head frame: a timber post with its square beam ends proud, rubble beside it | a double frame |
| Well Corridors | `rock` | 12 | a jamb cut in the cliff, rough edge, chisel marks | with a smoothed drafted margin |
| Nun (light wells) | `nun` | 11 | a papyrus-bundle post tied with bands, an open umbel | a square pier with a lotus capital and a lotus in relief |

**Wear** (owner: "the threshold pillars respect any damage in their immediate vicinity"): `ctJambsOf` reads the wall's wear beside it
(`wearLevel` on its cell and the next, three heights), a breach beside it (`inBreach`), a fallen lamp's scar (a broken lamp within a cell) and
rubble at its foot. Wear 1 gives chips along its edges, wear 2 cracks and a corner of its capital gone, wear 3 one in two broken off part way up
with a jagged top (`jambClip`); beside a breach it is always broken (never an intact pillar over a breach), its pieces on the court's floor
beside it (`jambPieces`). Floors 1-48 x 3 (courtscan): 1,951 jambs worn, 668 of them broken off.

What the exception needs, all done: `SHC` kind `jamb` (no lamp shadow on it), the relief rubbed over it (`ctRel`), a beam blocker
(`beamBlockers`: no haze, footprint or figure light on it, both modes), cut back into Classic's fill (`fillCut`), the dapple and the light
well's shaft clipped inside the jambs, drawn exactly its own width (nothing on the faces or lips beside it), `layerscan` kind `jamb` (its own
cells' lips are its own, `OWN`), `shadowscan` kind `jamb`.

**Minimum length**: 4 cells (owner). The widest jamb is 14 px, so at least 100 px (3.1 cells) stays open between the two (courtscan checks
3 cells); the 7-8 courts a floor are unchanged.

**Meroë's grade** (owner: G2 "plus a true per-court grading in Torchlight ... even if it is harder it is more accurate"). Meroë's courts show
their own outdoor sky with Meroë's steep pyramids far off (`ctOwnSky`, in `ctBg`; the theme's view is the furnace halls). In Torchlight the
composite takes up to four court boxes in view (`u_cgb`, `ctGradeU`) and mixes there, feathered at the edges, to the court's own grade
(`CT_GRADE.meroe`: cooler shadows and lights, saturation 0.84, a white balance toward daylight); the furnace halls keep their warm forge grade.
Classic gets the matching grade after its light pass (`ctGrade2D`: a cool multiply and a partial desaturation over the same boxes).

**Aksum's depth** (owner chose S1): the court beyond in layers: flat-topped ambas far off, storeyed stelae at three depths with their shade
sides, storeys, false windows and long shadows, a low rubble-and-timber wall, the Great Stela lying broken in front, paving converging to a
vanishing point at eye height, darker near, loose stones with their shadows (`ctBake`'s granite far side).

**Gusts**: a court's open side is one of the wind's openings (25% of courts, times the floor's mood; see [wind](wind.md)): gusts through
courts on floors 7-48 x 3: 46 (0.37 a floor), varying by floor.

Pictures: `egyptr45c.py old=FILE` (r45c_jambs.png, r45c_jambs_phone.png, r45c_meroe.png, r45c_aksum.png, r45c_gust.gif).

## At a glance

| | |
|---|---|
| Code | `L.courts` (`{k, r, c0, c1, pits, h, far}`): `k` is the kind, `r` the row he walks in, `c0..c1` its cells, `pits` the pools' columns, `far` a pylon court's far side. `L._ctS` holds the court's cells (rows `r-1` and `r`) and `L._ctP` the pools by cell. Placement: `placeCourts`, `ctKindOf`, `CT_KIND`, `CT_FAR`, `CT_MIN` 4, `CT_MAX` 8, `CT_WANT` 7, `CT_GAP` 14, `CT_DR` 3, `CT_PD` 11. Drawing: `ctBack`, `ctStruct`, `ctColumn`, `ctWell`, `ctOver`, `ctBake` (`CTB`), `ctBg`, `ctOpen`, `ctBox`, `ctLights`, `ctLive`, `ctEmis`, `ctRel`. Play: `ctPoolHit`, `die('drown')`. Wind: `ctGustSrc` |
| Layer | The cut and what stands on the back plane (colonnade, posts and vine, parapet, piers, the light well's recess) are L1 in the room picture. The ceiling's face over a court is L3 in the room picture. The court beyond is L0 (`ctBg`, under `G2D.na`). A pool is L2x: its far half before the figures, its near half and cut face after them. The hanging vine is L2, near side, after the figures. The dapple and the well's shaft are light. See [layers](../layers.md) |
| Generated by | `placeCourts`, after `placeHills` and before `placeWinds`: hashes of the seed, the row and the cells (no generator stream) |
| Bot | No new action. The bot never falls into a pool (pools are only off the route's own way) |
| Checks | `courtscan.py` (in suite.py, gen); `layoutcmp.py` (same); `windscan.py` (a court is a gust source); `lampscan.py`, `doorscan.py`, `openscan.py`; `layerscan.py kinds=court,pool,vine,dapple,lwell`; `shadowscan.py kinds=pool,vine`; `run2.py`, `featbot.py`, `p4bot.py`, `forktest.py`; `rendersmoke.py` |
| Pictures | `egyptr45.py old=FILE`: r45_courts.png (each kind and hour, before and after, 3x, both modes), r45_phone.png, r45_pool.png (a fall into a pool), r45_gust.gif, r45_vine.gif |

## Example

Floor 5, seed 1, the Halls of the West at dusk.

1. A run heading right has eight cells of headroom under stone on row 42.
2. The back wall there gives way to a colonnade of closed-bud papyrus columns with the dusk sky above them.
3. Through the columns lies the court: its paving, the far portico's shade and columns, and sycomores.
4. Overhead, the ceiling's face is the near portico's architrave with its painted cavetto.
5. The two lamps of that stretch stand on free stands, as in an open arch.
6. The windows of the wall are gone with it, and no sky beam comes through.

Floor 5, seed 2: a court on row 27 holds a one-storey spiked pit at column 78. It is a sunken pool, its water 11 px under the coping, with
lotus and rings and the sky in it. He walks off the coping and drowns at the surface: a splash, the card "Drowned in the pool", and he goes
under.

## In play

| Rule | Example or number | Why |
|---|---|---|
| Courts are look only | layoutcmp v86: same, 144 of 144 | the generator never reads them |
| A pool kills at its surface | `ctPoolHit` in `stAir`: falling through the water's surface (`SURF(r)+CT_PD`, 11 px under the walking floor) calls `die('drown')` | the owner: "a fall into water kills". It is the pit's own death (its stakes killed on any landing) a storey sooner, at the surface |
| Only pools change play | the death moment of a fall into a court's one-storey spiked pit: at the surface instead of 53 px lower on the stakes, cause `drown` (card "Drowned in the pool", sound `splash`) | nothing else in a court touches play |
| Guards and fights | allowed in courts (owner) | a duel under a colonnade |
| Wind | from floor 13 a wind stretch that holds a court takes the wind first, and its gust pours in through the court (`ctGustSrc`, round 44's W2) | the owner: "the court's open side is a gust source" |
| Heaps and drifts | stay as placed (owner: courts need not hold them); 7-8 courts a floor share stretches with them where they fall | |

## Placement

`placeCourts`, from floor 3, with hashes only:

| Rule | Value |
|---|---|
| A court cell | headroom (`EMPTY` over the walking row) with the ceiling's stone straight over it (`WALL` two rows up), nothing in either. The walking cell is `FLOOR` with any feature but a kick shaft's foot, a banner, a lift or a damaging drop, or a pool's pit. Not within 2 cells of a lift's shaft, nor 3 of a door |
| A pool | a one-storey spiked pit inside the court (`EMPTY` over spikes on `FLOOR`, not a deeper drop), not on the route's own way (no seg covers its floor). Every such pit inside a court is a pool, and its stakes are not drawn (`L._ctP`). The bot only jumps over them |
| Length | 4-8 cells (`CT_MIN`, `CT_MAX`), part of a stretch (a stretch longer than 22 gives several candidates); both ends are floor; a light well is 2 cells |
| How many | 7 or 8 a floor (`CT_WANT` + a hash), never two in view at once: none within 3 rows and 14 cells of another (`CT_DR`, `CT_GAP`; the view is 13 cells and 3 rows). Floors 3-48 x 3 seeds: 7 or 8 on every floor |
| Kind | by theme (`CT_KIND`): West, Blue Chambers, Hawara a peristyle; Shali, Kerma a vine pergola; Napata, Meroë, Garama, the Well Corridors, Aksum a pylon court; Nun a light well. Meroë: one court in three is a light well. Osiris: one of peristyle or pergola a floor, by a hash of the floor and seed |
| Far side (pylon courts, `CT_FAR`) | Napata, Meroë: a Kushite pylon with flagstaffs, pennants, relief panels and ram sphinxes (Musawwarat, Naqa); Garama: a mudbrick pylon; the Well Corridors: a cliff in beds with rock-cut doorways; Aksum: storeyed stelae behind a wall of rubble between timber beams with their round ends (the Crossing's Aksum doorway) |
| Under it | a window, open arch or breach of the wall inside a court is not drawn and sends no beam (`inOpening`, `isArchTop`, `ctBox`); a lamp there stands or hangs free (`lampFree`); a hanging planned there is dropped |

Floors 1-48 x 3 seeds (courtscan): 7.44-7.50 courts a floor from floor 13 (6.33 over 1-12, as floors 1-2 have none), 30-40 cells a floor,
41 pools in all, kinds 347 peristyles, 286 pergolas, 304 pylon courts, 99 light wells; of 79 gusts on floors 13-48, 9 come in through a court.

## How it is drawn

### The back plane (room picture, stage 0, after the AO; L1)

`ctBack` cuts the back wall away (`destination-out`) from the headroom's top down to the cut line: 6 px over the floor's back edge for a
peristyle, 26 for a pergola's garden wall, 3 for a pylon court. With Graphics' background off it paints the sky's gradient instead. Under the
cut the wall is redrawn plain (stone, or whitewashed mudbrick for the garden wall). Then comes `ctStruct`:

| Kind | On the back plane |
|---|---|
| peri | Closed-bud papyrus columns, one a 64 px bay: bulb, base, stems, painted bands, sepals on the bud. Backlit by the sky, so the face toward us is in shade and the edge toward the sun (dusk: left; dawn and the moon: right) is lit, silver at night. Architrave and painted cavetto over them; the sky above |
| perg | Timber posts on the garden wall, a beam across their top, the vine climbing them with grape bunches |
| fore | Two masonry piers at the ends, nothing between: the court is open from the sill |
| well | Not cut: a 2-cell recess rising out of sight behind the ceiling. Its brick is lit from far above and the light falls off down the shaft (`(1 - y/52)^1.6`). Its left side faces us. A basin of dark water at its foot catches the light |

### The ceiling's face (room picture, stage 1, after the front faces; L3)

`ctOver` redraws the face of the stone over the court:

- **Peristyle and pylon court:** the portico's architrave with a torus moulding, a painted cavetto and a band of signs; the pylon court has a
  winged sun disc in it.
- **Pergola:** the vine canopy's edge: the front beam with the rafters' ends, leaves thick over all, grapes.
- **Kerma's pergola:** palm-log ends in mudbrick with the vine over them.
- **Aksum:** timber ends in rubble.

It stays the front plane: nothing live is drawn over it.

### The court beyond (L0)

`ctBake` paints three strips once per kind, far side, look, hour and scale (`CTB`, nine kept): the ground (`f` 0.7), the far side (0.18)
and the near trees and sphinxes (0.5). Each strip is 640 world px wide, tiled seamlessly, at 0.6 of the view's scale (at most 3). The ground
at depth `f` lies at `eye + (floor - eye) f`, with the eye 44 px over the floor's back edge, as in the Crossing. Things fade toward the sky's
horizon colour with depth. At night every edge facing the moon takes a silver rim (`crossRim`).

`ctBg` lays them inside each court's opening after the theme's own backdrop, in `drawBackdrop` under `G2D.na`. Each strip moves by its depth
factor about the court's middle (round 27b) and vertically by round 25e's rule from the court's rest (`BG_VK`). The pylon's pennants are
live: they stream with the wind (`windAt`) and flutter faster in it.

The court's bays (two cells each) are openings (`ctOpen`): the theme's view is painted there, each sends its `sky` light, and they share
one anchor (`bgAnchors`).

### Live parts

| Part | Drawn | Notes |
|---|---|---|
| A pool's water | `ctLive` 0: the surface's far half (the sky's horizon colour, glitter of the sun or moon) before the figures; `ctLive` 1: the near half, the cut through the water at the front plane, rings, lotus pads and flowers (blue and white) after them | Clipped to the pit's columns, down to the pit floor's lip (L3 stays in front). Recorded in `SHC` (kind `pool`); the relief is rubbed over it (`ctRel`, `glRelBox`). After a drowning: a splash crown at the surface, then rings |
| The hanging vine | `ctLive` 1, after the figures: tendrils 4-15 px long with leaves and grapes hanging from the canopy's edge | L2 near side, clipped to the court's x and 24 px under the ceiling; it sways and streams with the wind; `SHC` kind `vine` |
| The dapple | `ctEmis` (light, `lighter`): soft spots of the hour's light on the floor's top face, on the garden wall and a few on him | Clipped above the lips; moves with the leaves (a pure function of the clock) and shivers in the wind; none over a pool |
| The light well's shaft | `ctEmis`: a soft column of light from the recess's top down to the floor in front, its footprint and slow motes | |

All live parameters are made once a court (`ctPrep`: typed arrays); colours once a pool and hour. Nothing is allocated a frame, and nothing
keeps state: rewind-safe.

## Light, shadows and effects

| Pass / effect | This element |
|---|---|
| Light map (`gatherLights`) | `ctLights`: broad `sky` lights every 88 px along a court in a pale tone of the hour's light (r 120, 0.3 day, 0.26 night; times 0.5 in Torchlight, whose map is stronger and grade warm); a light well's two. Lamps in a court stand free and burn as before |
| Sky beams | none from a court: a court-wide beam is a slab of haze, so the ops inside a court are dropped (`ctBox` in `ryOps`) |
| Lamp shadow | the columns, posts, parapets and the well are L1 and take it; the sky does not (alpha 0); the pool and the vine are carved (`SHC` kinds `pool`, `vine`) |
| Relief | the room picture's stone (columns, architrave) as any wall; rubbed back over the pools' water (`ctRel`) |
| Theme looks | the arch dust (`LFX` `archdust`, mist pass) is softer since round 45: lower, rotated frequencies and a wide ramp (`smoothstep(.18,.95)`, 0.3), so it reads as haze in an opening, not square patches (owner: "blotchy"). It shows in every open arch and court |
| Bloom, grade, vignette | as the scene |
| Classic equivalents | the same drawing; Classic's light pass takes the same `sky` lights |

## Relations to other elements

| Element | Relation |
|---|---|
| [openings and backdrop](openings-and-backdrop.md) | a court is an opening (`inOpening`): no arch, window or breach inside it; its bays in `openingsIn` share an anchor |
| [lamps and light](lamps-and-light.md) | a lamp inside a court stands or hangs free (`lampFree`) |
| [stonework](stonework.md) | the wall decor and hangings give way to the court |
| [spikes](spikes.md) | a court's one-storey spiked pit is a pool: its stakes are not drawn, nor their glint |
| [wind](wind.md) | a court's open side is a gust source from floor 13; the vine, pennants and dapple move with the wind |
| [heaps and drifts](heaps-and-drifts.md) | they stand in courts where they fall; drawn as anywhere |
| [guards and snakes](guards-and-snakes.md) | guards may stand and fight in a court |
| [the Crossing](the-crossing.md) | the depth rule, `crossRim` and the Aksum kit are the Crossing's |

## Rules for changing it

- Look only, by hashes: never a generator stream, and never a change to tiles, features, lamps or windows. `layoutcmp.py` must print
  `layoutcmp: same`.
- The pool's death is the only play: a court's pool is a pit the route never enters.
- The ceiling's face over a court is the front plane, in the room picture. Nothing live is drawn over it.
- The court beyond is baked once (strips) and laid down live. A new far side is one more case in `ctBake`, in whole periods of 640 px.
- `courtscan.py` must print `courtscan: ok`; `layerscan.py` with the new kinds and `shadowscan.py kinds=pool,vine` must pass.

## History

- round 45: courts (peristyle, vine pergola, pylon court, light well, pool); the arch dust softened.
- round 45c: thresholds (a near jamb of the theme's architecture at each end, worn with the wall), Meroë's own sky and grade, Aksum's depth in layers, court gusts from the openings' rule.

Details in CLAUDE.md.
