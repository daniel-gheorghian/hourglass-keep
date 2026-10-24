# Dawnward: an interlude between floors (research and recommendation)

Research only; nothing implemented. Sources are linked. A ° marks a detail from knowledge of the game that I could not check
against a source this session (the fetch tool could not reach most sites, so many facts below come from search-result
summaries; PoP 1989's numbers come from SDLPoP's source).

## 0. How a floor ends and the next begins today (dev/hourglass-keep.html)

| Step | Code | Time |
|---|---|---|
| Up at the open door: he walks to the doorway, climbs the treads, is cut at the jambs, whitens and fades "into the light"; the door light swells | `P.state 'exit'`, `EX_*`, `exitSwell`, `drawPTint`, sounds `stairsaway`, `exitlight` | about 1.7 s (`EX_N` 4.6 at `EX_RATE` 3.2) |
| `levelComplete()`: `mode='card'`, **saves at once** (`S.level=n+1`, `S.cp=-1`, floor time and falls reset, `S.time+=ft`), plays `clear` (a six-note triangle arpeggio) and shows the HTML `#card` panel: "Floor n cleared", the theme name, Time / Falls / Lives, "Next: Floor n+1, <theme>." plus a rare flag's text; **Climb on** / **Title screen** | line ~4418 | waits for a tap (Space/Enter) |
| While the card is up, `loop()` runs no update and redraws the canvas only every 20th frame: the picture behind the panel is frozen | `loop`, `else{...idleFrames%20}` | |
| `nextFloor()` → `startLevel(n+1,-1,true)`: `genLevel`, rewind ring cleared (`REW.length=0`), hours refilled (`S.sands=SANDS`), the entry through the start door (`startEntry`, control at `EN_CTL` 0.62 s) and the floor's title banner (`intro` 2.6 s) | line 2814 | 0.62 s to control |

Facts that shape the design:
- A new theme starts every 4 floors, always (consecutive blocks differ in drawing style, so in theme). Over floors 4 to 60 the
  changes are: 4→5 Nun→West, 8→9 West→Blue, 12→13 Blue→Meroë, 16→17 Meroë→Osiris (dusk); 20→21 Osiris→Foggara, 24→25
  Foggara→Deffufa, 28→29 Deffufa→Wells, 32→33 Wells→Meroë, 36→37 Meroë→Osiris (night); 40→41 Osiris→Hawara, 44→45 Hawara→Shali,
  48→49 Shali→Blue, 52→53 Blue→Napata, 56→57 Napata→Aksum (dawn); 60→61 Aksum→Hawara (dusk again). (`themeOf`, `SCHED`, `progOf`)
- The exit already ends in white light and the entry already begins with him stepping out of a dark doorway. An interlude that
  fades in from white and ends with him walking into a dark doorway joins both ends with no new seam.
- The save is already written when the card appears, so anything played between the exit and the entry changes no save state.
- The view is 320 by 192 game pixels (`VW`, `ROOM_H`). The backdrop system (`BGART` per theme; `paintBackdrop`, `bgLayerY`, `BGK`
  periodic strips 640 by 210, `f = h/(s H)` depths from round 27b) already has `stars`, `moon`, `clouds`, `farridge`, `hills`,
  `dunes`, `palms`, `acacia`, `trees`, `saltlake`, `mounds`, `huts`, `qurn`, `steppyr`, `kushpyr`, `barkal`, `near` (reeds, scrub,
  stone). Sound is all synthesized WebAudio (`Snd.tone`, `Snd.noise`); the game has no music.
- The game's own frame: the keep is the twelve hours of the night (Amduat), climbed through dusk, night and dawn (sunrise at
  floor 60); the land seen through windows sinks each floor because he is climbing.

## 1. Games surveyed

| Game | What the interlude is | Length | Interactive? | Skippable? | How often | Source |
|---|---|---|---|---|---|---|
| Prince of Persia (1989) | The princess alone in her chamber beside the great hourglass, which shows the time left; Jaffar's visit at the start; the mouse later on | 26 to 72 cutscene frames at 6 ticks of 60 Hz = about 2.6 to 7 s plus fades | No | Yes, any key (`proc_cutscene_frame`: `if(!disable_keys && do_paused())` ends it); not the ending or time-out | Before levels 2, 4, 6, 8, 9, 12 (`tbl_cutscenes`): 6 in a 12-level game, about one every 10 min | [SDLPoP data.h](https://github.com/NagyD/SDLPoP/blob/master/src/data.h), [seg001.c](https://github.com/NagyD/SDLPoP/blob/master/src/seg001.c), [Ubisoft, 35th anniversary](https://news.ubisoft.com/de-de/article/6yLrRf7b0U1MBYxmlxE225/prince-of-persia-35th-anniversary-a-look-back-at-the-original-game) |
| PoP: The Sands of Time (2003) | Drinking at a sand fountain shows a short vision of the way ahead°; sand tornadoes give visions ("Destiny") | a few s° | No | ° | At each save point | [GameRevolution review](https://www.gamerevolution.com/?p=32383), [Wikipedia](https://en.wikipedia.org/wiki/Prince_of_Persia:_The_Sands_of_Time) |
| PoP: The Lost Crown (2024) | None between regions; travel is by statues, Wak-Wak trees are rest stops | | | | | [Prima Games](https://primagames.com/tips/how-to-fast-travel-in-prince-of-persia-the-lost-crown) |
| Journey (2012) | At each area's end he rests at a stone and sees a white-robed elder in a round room; pictographic murals tell the past and future, and the mural fills as you progress. Between them, traversal itself (sand surfing) is the breather | about 30 to 60 s° | No | ° | Once per area (about 8 in 2 h) | [Wikipedia](https://en.wikipedia.org/wiki/Journey_(2012_video_game)), [Giant Bomb](https://giantbomb.com/wiki/Games/Journey_2012), [sand surfing](https://journey.fandom.com/wiki/File:Sand_Surfing_gif.gif) |
| Limbo, Inside (Playdead) | None: no loading screens, no cutscenes; the world itself carries the transition | 0 | | | | [Giant Bomb, Limbo](https://giantbomb.com/wiki/Games/Limbo), [Gamereactor, Inside](https://www.gamereactor.eu/inside-review/) |
| Ori and the Blind Forest / Will of the Wisps | Narrated story scenes, mostly at the opening and at key areas; players complained the sequel has many more | 10 to 60 s° | No | ° | A handful per game | [Wikipedia](https://en.wikipedia.org/wiki/Ori_and_the_Blind_Forest), [Den of Geek](https://www.denofgeek.com/games/ori-and-the-will-of-the-wisps-preview-impressions/) |
| Celeste | Each chapter ends in a scene (Ch. 1: Madeline camps at the memorial for the night), then a "complete" screen over the chapter's art with time, deaths and strawberries; the chapter select is a 3D mountain the camera flies around to the next chapter° | 5 to 15 s° | Menu only | Yes° | Every chapter (8) | [Celeste wiki, Ch. 1](https://celestegame.fandom.com/wiki/Chapter_1:_Forsaken_City), [Wikipedia](https://en.wikipedia.org/wiki/Celeste_(video_game)) |
| Hollow Knight | The stag ride: the Knight on the Last Stag running down a dark tunnel | a few s° | No | No° | Every stag journey | [Hollow Knight wiki](https://hollowknight.wiki/w/Last_Stag), [Uppercut on the stag](https://uppercutcrit.com/the-wistful-optimism-of-hollow-knights-last-stag/) |
| Shovel Knight | A campfire rest after major stages, then a **playable** dream: catch Shield Knight as she falls (enemies join later). Devs: "a breathing time, a time to relax after the level"; playable "to get you more invested" | about 20 to 30 s° | Yes | ° | After each major stage | [Game Informer interview](https://gameinformer.com/b/features/archive/2014/07/29/shovel-knight-devs-discuss-co-op-pogo-jumping-and-beyond), [Giant Bomb](https://www.giantbomb.com/games/3030-42034/) |
| Spelunky (HD, 2) | A short transition room between levels with the run's money and time; a rescued pet or damsel gives a heart there° | about 3 to 5 s° | Walk out° | Yes° | Every level | [Giant Bomb](https://giantbomb.com/wiki/Games/Spelunky) |
| Alto's Odyssey | No interlude at all: endless ride; biomes, weather and the day-night cycle change while you play; Zen mode has no score. The look: minimalist layered silhouettes, purer foreground colours, tinted background | 0 | | | | [Wikipedia](https://en.wikipedia.org/wiki/Alto%27s_Odyssey), [Dice on the art](https://insights.dice.com/2018/02/23/altos-odyssey-winning-mobile-game), [TNW](https://thenextweb.com/gaming/2018/03/05/how-altos-odyssey-transports-players-to-a-whole-new-world/) |
| Gris | At each chapter's end the statue, and a colour returns to the world; at most a short scene per transition; no death | short | Partly | ° | 5 chapters | [TechRaptor](https://techraptor.net/content/gris-preview-melancholy-magnificence), [GDC narrative review](https://media.gdcvault.com/gdc2020/GameNarrativeReview/Emma%20Stone.pdf) |
| Monument Valley | A chapter title card with one line ("In which Ida embarks on a quest for forgiveness") | a few s | Tap on | Yes | 10 chapters | [Escapist walkthrough](https://www.escapistmagazine.com/monument-valley-complete-walkthrough/) |
| Sayonara Wild Hearts | Five instrumental intermissions, "Heartbreak I to V", between sections; each level lasts its song; Album Arcade runs straight through | about 30 to 60 s | Light | ° | 5 in 23 tracks | [GameRevolution](https://www.gamerevolution.com/review/597003-sayonara-wild-hearts-review), [NPR/WFAE](https://www.wfae.org/2020-09-14/the-sweet-escape-of-sayonara-wild-hearts-where-pop-music-is-recovery) |
| Super Mario Bros. 3, Kirby | A world map: he walks from stage to stage; each world's map has its own look | seconds | Yes | n/a | Every stage | [SMB3 hubs](https://gamedev.net/tutorials/game-design/game-design-and-theory/super-mario-bros-3-level-design-lessons-part-1-r4682), [WiKirby](https://wikirby.com/wiki/World_Map) |
| Rayman Origins | Freeing the Electoons and a photo op at each level's end | a few s | No | ° | Every level | [GodisaGeek](https://godisageek.com/2011/12/rayman-origins-review/) |
| Hades | None: the next chamber's reward is shown on its door; a short fade° | ~1 s | | | Every room | [Hades wiki](https://hades.fandom.com/wiki/Chambers_and_Encounters) |
| Dead Cells | Passages: a safe "transition biome" between biomes (shops, healing fountain, looks like the next biome) | 20 to 60 s° | Yes, no danger | Walk through | Every biome | [Dead Cells wiki](https://deadcells.wiki.gg/wiki/Passages) |
| Super Meat Boy | A replay of all your attempts after each level; chapter intro cutscenes; players complained the warp-zone entry could not be skipped | a few s | No | Replays yes; warp entry no | Every level | [Wikipedia](https://en.wikipedia.org/wiki/Super_Meat_Boy), [Steam thread](https://steamcommunity.com/app/40800/discussions/0/2183537632754968492) |
| Katana Zero | A VHS-styled replay of the successful run at each segment's end; a reviewer "found myself skipping them almost every time" | a few s | No | Yes | Every segment | [Nintendo World Report](https://www.nintendoworldreport.com/review/50314), [Katana Zero wiki](https://katanazero.wiki.gg/wiki/Katana_Zero) |
| Mobile interstitials (AdMob) | Google's guidance: place them at natural transition points, such as after a level; pause the app; don't show them too often (users uninstall) | | | | | [AdMob developer docs](https://developers.google.com/admob/unity/interstitial.md.txt), [AdMob help](https://support.google.com/admob/answer/7311435?hl=en), [Appradar](https://appradar.com/aso-glossary/interstitial-ads) |

What the survey shows:
- **Length:** the games closest to Dawnward (PoP 1989, Spelunky, Hollow Knight, Rayman, Celeste's complete screen) keep it to
  3 to 10 s. The long ones (Journey, Shovel Knight, Sayonara) are rare, and they carry the story or the music.
- **Frequency:** a short one every level (Spelunky, Meat Boy, Katana Zero) gets skipped: reviewers say so, and players complain
  when they can't. The memorable ones come at chapter breaks: PoP after 6 of 12 levels, Shovel Knight after major stages,
  Journey once per area, Gris once per colour.
- **Skip:** every one of these short interludes can be skipped except Hollow Knight's stag and Meat Boy's warp entry, and those
  draw complaints. There is no hard survey data; developers report that a "significant" share skip and have tried "fast forward"
  in place of "skip" ([Kingdom Come II director](https://www.gamereactor.eu/kingdom-come-deliverance-ii-cinematic-director-explains-how-to-make-cutscenes-unskippable-1649193/),
  [PC Gamer](https://www.pcgamer.com/do-you-ever-skip-cutscenes/)).
- **Tone and pacing:** an interlude is the valley between peaks in Schell's interest curve: rest makes the next climb feel
  harder, and a calm stretch can show what lies ahead ([Game Developer, intensity ramps](https://www.gamedeveloper.com/design/trinity-part-6-intensity-ramps)).
  Shovel Knight's devs said the same of the campfire.
- **Progress:** PoP's hourglass, Journey's mural and Gris's colours each show how far you have come. Dawnward has its own measure:
  the light turns from dusk to night to dawn, sunrise at floor 60.

## 2. Options for Dawnward

| Option | What | Pros | Cons |
|---|---|---|---|
| A. Living card | The card's frozen picture becomes a slow pan of a dune, oasis or garden; no walk | Adds 0 s (the card already waits for a tap); cheap | Little sense of travel; the panel hides half of it |
| B. Auto-walk crossing (Spelunky / stag ride / PoP cutscene) | He walks across the land on his own; tap to skip | Short, readable on a phone, the same every time; reuses the walk cycle and backdrop; joins the exit's white to the entry's dark door | Watching, not playing |
| C. Walk-it-yourself breather (Dead Cells passage, Journey, Shovel Knight's dream) | He walks across himself with the pad; no danger | Agency; feels like the game | Needs a control layer and a way out for players who don't move; longer; one more thing for the bot and tests |
| D. Map view (Mario, Celeste's mountain) | The route up the keep, or the land from above, with a marker | Shows progress clearly | Breaks the side view and the look; a second art style; little feeling of place |
| E. Title card only (Monument Valley) | A card with the next land's name and a line about it | Almost free | Already done by the floor banner and the card's "Next:" line |
| F. Story vignette (PoP's princess, Journey's elder) | A scene with a character | Strong story beat | Dawnward has no cast; the rules forbid living peoples as decoration; it would need writing |

## 3. Recommendation: "the crossing" (option B, with a touch of C)

| Decision | Recommendation | Why |
|---|---|---|
| What | A side-on auto-walk through the open land between two parts of the keep: the land of the theme he is going to, under the hour's sky | Joins the exit "into the light" to the start door; the land seen till now only through windows is finally seen whole |
| When | At each **theme change, every 4 floors** (after floors 4, 8, 12 …: 12 per 48 floors). Ordinary floors unchanged | PoP's rhythm (6 in 12 levels) and the chapter-break pattern; a short one every floor gets skipped |
| Length | **9 s**: 0.6 s fade in from the exit's white; about 7 s of walking; about 1.2 s settling at the next doorway | PoP's 3 to 7 s, Spelunky's, the stag's; long enough for one beat and a caption |
| Order | Exit (white) → crossing → the **card appears over its last frame** (prince facing the dark doorway of the next part, "Next: Floor 5, The Halls of the West") → **Climb on** → he steps into the dark (0.5 s) → the entry as now | The card stays the one place to choose; the save is already written; the walk into the dark matches the entry out of the dark |
| Interactive | Auto-walk. Holding right makes him run (the crossing takes about half as long); the jump button or a tap anywhere skips to the card | "Fast forward", not only skip; agency without danger or tests |
| Skip | Always, from 0.5 s, including the first time; a quick 0.25 s fade. Never plays on Continue, Restart, checkpoints, respawns or from the title; never under the bot or tests | Mobile, repeated runs; complaints about unskippable scenes |
| Setting option | A pause-menu toggle "Crossings" (on by default) and `?cross=0` | Same pattern as Battery saver and Softer flashes |
| Caption | The next theme's name and one plain line of place, fading in at about 2 s for 3 s (e.g. "The Salt Fortress of Shali · Siwa, the oasis of Amun") | Monument Valley's line; places the theme honestly |
| People | None. Animals only (geese, ibis, a jackal on a far crest, fish rings, a gazelle); empty kiosks, an idle shaduf | Owner's rule: no living peoples as decoration |
| Generated | The scenery of each crossing comes from the floor's seed (a hash, no generator stream); the theme picks the setting and the hour picks the light | "Levels stay fully generated"; look only; no layout changes |

### What each crossing shows

| Next theme (look) | Setting | Seen | His beat |
|---|---|---|---|
| Halls of the West (west) | Garden | Nebamun's pool: a pool with lotus, fish and geese, ringed by sycomore figs, date and dom palms; the Theban hills and el-Qurn behind (`qurn`) | Walks along the pool; geese lift off |
| Blue Chambers (blue) | Dunes | The desert edge at Saqqara: low dunes and ripples, the step pyramid on the skyline (`steppyr`), then the valley's palms | Walks down from the sand onto the path |
| Forges of Meroë (meroe) | Oasis (Kush) | A hafir (a rain-fed reservoir) with acacias; the furnaces' smoke and the steep pyramids far off (`kushpyr`, `smoke`) | Crouches at the water's edge (1 s) |
| Green Hall of Osiris (osiris) | Garden (mythic) | The Field of Reeds of Book of the Dead spell 110 (Sennedjem's tomb): canals, grain, rows of trees, the sun in the sky's top band | Walks along the canal |
| Foggaras of Garama (foggara) | Dunes → oasis | A corridor between long seif dunes, the foggara shaft mounds in a line (`mounds`), palm gardens at the end | Wind lifts grains off the crests |
| Deffufa of Kerma (deffufa) | Oasis (Nile) | Dunes of the west bank, acacias, empty round huts (`huts`), the Deffufa's mass | Walks between the acacias |
| Well Corridors (wells) | Desert wadi (not dunes) | A limestone wadi path over the Theban hills: scree and pale cliffs (no dunes there) | Walks up a gentle rise |
| Labyrinth of Hawara (hawara) | Garden / lake | The Fayum's lake shore: reeds, fields, the mudbrick pyramid far off | Reeds sway as he passes |
| Salt Fortress of Shali (shali) | Oasis | Siwa: date palms, a spring pool, the salt lake (`saltlake`), the Aghurmi rock with the temple of Amun | Crouches at the spring (1 s) |
| Pyramids of Napata (napata) | Dunes | Barchans before Gebel Barkal (`barkal`) and the steep pyramids | Walks along a barchan's flank |
| Stelae of Aksum (aksum) | Highland fields (no dunes, no gardens) | Terraced grain fields, junipers, the stelae on the skyline (no churches) | Walks along a terrace |
| Waters of Nun (nun) | Marsh garden | Papyrus thickets and still water | Walks a raised dyke |

### The three settings, done honestly

| Setting | What to draw (ancient, Nile/Kush/Sahara) | Sources |
|---|---|---|
| **Dunes** | Seif (linear) dunes in long parallel ridges with flat corridors between them (so his path is level, and accurate): ridges 20 to 30 m high, 1.5 to 2.5 km apart in the Great Sand Sea. Barchans: crescents that creep 10 to 100 m a year at Kharga. Ripples a few cm apart, crossways to the wind, gentle (8 to 10°) on the windward side; the slip face stands at the angle of repose (about 34°, the game's `WELL_SL` already). Light: at dawn and dusk the low sun puts the slip faces in shadow and makes the ripples show; at night a silver crest line under the moon. Grains streaming off the crests: the game's `jetStream` is a stateless sand-grain flow already | [Great Sand Sea](https://en.wikipedia.org/wiki/Great_Sand_Sea), [fjexpeditions GSS](https://fjexpeditions.com/desert/geography/GSS/GSS.htm), [Bagnold's barchan, 57 yr record](https://resolve.cambridge.org/core/journals/quaternary-research/article/bagnolds-barchan-a-57yr-record-of-dune-movement-in-the-eastern-sahara-and-implications-for-dune-origin-and-paleoclimate-since-neolithic-times/4068A111A84A2BE9CF73BB0F6CF441A6), [Kharga dunes and forts](https://arxiv.org/pdf/1706.06765), [ripple physics](https://personal.math.ubc.ca/~njb/Research/ripples.pdf), [Dune](https://en.wikipedia.org/wiki/Dune) |
| **Oasis** | Siwa: thermal springs, salt lakes 19 m below sea level, date palms and olives, the Aghurmi rock with Amun's oracle temple (Alexander, 331 BC), Shali's mudbrick. Kharga: the temple of Hibis; at Ain Manawir about 20 qanats from the 5th century BC watering gardens below the hill. Kush: hafirs (Musawwarat's Great Hafir, 250 m across) and Meroë's Royal Baths beside the palace. Garama: foggara shaft lines (already the theme's backdrop) | [Siwa](https://www.Wikipedia.com/wiki/Siwah), [Afar on Siwa](https://www.afar.com/magazine/siwa-oasis-egypt-is-a-desert-dream), [Ain Manawir qanats (IFAO)](https://halshs.archives-ouvertes.fr/halshs-02051616v1/file/The_Qanats_of_Ayn_Manawir_Kharga_Oasis_E.pdf), [Hibis (Iranica)](https://www.iranicaonline.org/?p=11631), [Musawwarat Great Hafir](https://musawwarat.com/about-musawwarat/the-great-hafir), [Musawwarat](https://en.wikipedia.org/wiki/Musawwarat_es-Sufra) |
| **"Hanging gardens"** | The Hanging Gardens are Babylonian (Dalley argues they were really Sennacherib's at Nineveh), and no ancient source puts them in Egypt, so don't use the name or the stepped ziggurat look. Egypt's own versions: **terraced temple gardens** at Deir el-Bahari (Hatshepsut's terraces, 32 incense trees from Punt in walled pits watered by pipes; Mentuhotep's temple beside it with rows of tamarisk and sycomore pits); **walled pool gardens** (Nebamun's pool: fish, lotus, geese, sycomore, date and dom palms; Ineni's list in TT81: sycomores, date and dom palms, persea, pomegranate); **water gardens** (Amarna's Maru-Aten: walled enclosures, pools, tree gardens, a kiosk on an island, T-shaped basins); **the Karnak "botanical garden"** (Thutmose III's foreign plants in relief); the **shaduf** lifting water to a garden (Ipuy's tomb, TT217); and the mythic **Field of Reeds** (Sennedjem). Draw it with vine pergolas, palms, sycomores, T-shaped pools and lotus | [Dalley (Biblical Archaeology)](https://www.biblicalarchaeology.org/daily/news/hanging-gardens-of-babylon-in-assyrian-nineveh/), [Hamburg CSMC](https://www.csmc.uni-hamburg.de/publications/mesopotamia/2018-01-30.html), [Deir el-Bahari gardens](https://gardenhistoryresearchfoundation.com/2021/11/12/plant-collections-of-the-pharaohs-digging-into-the-origins-of-botanical-gardens/), [garden history blog](https://thegardenhistory.blog/2020/02/01/hatshepsut-and-thutmosis/), [Nebamun's pool](https://www.worldhistory.org/image/19186/garden-painting-tomb-of-nebamun/), [Tomb of Nebamun](https://en.wikipedia.org/wiki/Tomb_of_Nebamun), [Gardens of ancient Egypt](https://en.wikipedia.org/wiki/Gardens_of_ancient_Egypt), [Maru-Aten (Amarna Project)](https://www.amarnaproject.com/amarna-the-place/maru-aten/), [Karnak botanical garden](https://sachsen.museum-digital.de/pdf/object/43164.pdf?lang=en), [Ipuy's shaduf (Met)](https://www.metmuseum.org/art/collection/search/557816), [Sennedjem, Fields of Iaru (Met)](https://www.metmuseum.org/art/collection/search/548354) |

### Light and time of day

- The sky is the next theme's `BGART.sky` gradient under its `progOf` grade: dusk on floors 1 to 20 (a low warm sun, long shadows to
  the right, slip faces dark), night on 21 to 40 (moon and stars, crest lines silvered, cool palm silhouettes, still water holding
  the moon), dawn on 41 to 60. In the dawn cycle the sun stands a little higher at each crossing, so the climb toward sunrise at
  floor 60 is seen: Dawnward's progress marker, as PoP's hourglass was.
- After a chase floor ("the dark"), the crossing opens a touch brighter: release after the chase.
- Classic-style 2D lighting only: open air, no lamps. A soft cast shadow under him from the sun or moon.

### Sound (synthesized, as now; the "Climb on" tap has already unlocked audio)

| Cue | Built from |
|---|---|
| Wind bed for the whole crossing (stronger in dunes) | `Snd.noise` bandpass sweeps |
| Footfalls: soft in sand, firmer on a path | the `step` cue, lowpassed, on the walk's foot contacts |
| Palm fronds, reeds | short high bandpass noise bursts |
| Spring or pool | sparse sine blips |
| Geese or ibis | short tone glides |
| Caption | a two-note sine swell like `exitlight` |
| Step into the doorway | the wind cut off, a low `thud` |

## 4. Technical outline and cost

| Part | How | Reuses |
|---|---|---|
| Mode | `mode='cross'` in `loop()`: its own clock and render, no `update(STEP)`; `levelComplete()` saves as now, then runs the crossing; the `#card` panel appears at its end; `nextFloor()` plays the 0.5 s step into the dark, then `startLevel` | `levelComplete`, `nextFloor`, `show('card')` |
| Picture | Drawn on the 2D canvas in both modes with the GL canvas hidden (as `render()` already does for Classic); no light map | `render`'s Classic path |
| Backdrop | A `CROSS` table per destination look (setting, layer list, ground, beat, gate). Far layers come from the existing kinds; new kinds: `erg` (seif ridges with lit and shaded flanks, slip face at 34°), `ripples` (ground band), `pool` (lotus, fish rings, the sky reflected), `sycomore`, `pergola`, `shaduf`, `kiosk`, `terrace`, `reedfield`, `wadi`. **Near and foreground layers are new**: the keep's layers sit at f 0.002 to 0.25 because they are seen past the walls, but out here the play plane is his path, so things a few metres off move at f 0.5 to 1 and a sparse silhouette layer in front of him at f 1.2 to 1.4 (palm trunks, reeds; never covering him more than 0.3 s). The round-27b rule f = Z0/Z still sets every factor | `BGART`, `paintBackdrop`, `bgLayerY`, `BGK`, `bgClosed`, `bgBlurR`, `bgHaze` |
| Prince | Walk cycle at walking pace (`MCK` walk/run, `cycPose`, `runPoseHD`, `drawFigureHD`, `followPose`); level ground (the corridor between dunes, a garden path) so feet stay planted; the crouch pose for the spring beat | the round-23 figure |
| Effects | Sand blown off crests (`jetStream`: stateless, rewind-safe already); `SAND_LOOK` colours and `sandTex` for the ground | round 18c, 21b |
| Gate | Each crossing ends at a dark doorway in the next theme's material (pylon, mudbrick, rock); he is cut at the jambs as in the exit | `doorClip`, `doorHead` |
| Next floor's generation | Measure `genLevel` on the phone; if it costs more than a frame, run it under the step into the dark (or during the crossing) and hand the result to `startLevel` | `genLevel` |
| Run state | Nothing changes: the save is written before the crossing (killing the app resumes at the next floor's start, no replay); no rewind (the ring is cleared at `startLevel` anyway; Grab does nothing); no floor or run time counted (as the card now); hours refilled as now | |
| Frame budget | Layers baked once per crossing into strips (as the backdrop does); per frame: about 8 strip blits, one figure, a few hundred grains. Should run well under the play frame; Battery saver halves the frame rate as in play | |
| Load | No assets: procedural like everything else; about 600 to 900 lines (40 to 60 KB) in a 1.25 MB file; offline unaffected | |
| Tests | `crossscan.py`: every look × dusk/night/dawn renders without errors, CPU per frame within budget, a non-blank frame, his feet on the ground line, skip works, the save is unchanged, the entry follows; into `suite.py quick`. The bot and the existing tests never see a crossing (`opts`/`?cross=0`). Pictures: `egyptr35.py` (a strip per setting and a GIF) | `slowguard.py` |
| Cost | About 3 to 5 rounds: 1) mode, flow, skip, walk on a placeholder land; 2) dunes; 3) oasis; 4) gardens; 5) sound, captions, polish. Most of the work is the art layers | |

## 5. Questions for the owner

1. **How often:** at each theme change, every 4 floors (recommended), or after every floor (then 4 s, and the card's frozen frame becomes option A on the other floors)?
2. **Order:** crossing then card, with the card over him at the next doorway (recommended), or the card first and the crossing after Climb on?
3. **Control:** auto-walk with hold-right-to-run and tap-to-skip (recommended), or should he only move while you hold the pad (Dead Cells, Journey)?
4. **Captions:** the next theme's name and one line of place, or wordless?
5. **The misfits:** the Well Corridors (Valley of the Kings) and Aksum are neither dunes, oasis nor gardens. Is a limestone wadi and terraced highland fields acceptable for them?
6. **Animals:** geese, ibis, fish, a gazelle, and a jackal on a far crest (an echo of the dark): all right? And no people at all, so an idle shaduf and empty huts and kiosks?
7. **Light:** plain 2D sunlight and moonlight in both modes, or Torchlight's bloom and haze on the sun and the pools too (more cost, more work)?
8. **After the dark:** should a crossing that follows a chase floor be marked (dawn breaking more strongly, ash settling)?
9. **Music:** the game has none. Keep the crossing to wind and footsteps, or give it a short melodic phrase per setting?
10. **Name:** "crossing", "interlude", or something from the Amduat's hours (each crossing is the boat passing the gate of the next hour)?
