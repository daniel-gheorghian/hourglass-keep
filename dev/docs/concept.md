# Dawnward: the concept

Dawnward (repo `hourglass-keep`, formerly Hourglass Keep) is a single-file HTML5 canvas platformer in the manner of Prince of Persia
(1989), played as an offline PWA on an iPhone held in landscape. Every floor is generated; the run goes on floor after floor through
twelve themes of ancient Egypt, Kush and the Sahara, from dusk through the night to dawn. This file is the game's frame: setting, rules,
modes, progression and saving. The moves and their numbers are in [gameplay.md](gameplay.md).

## A floor, start to exit

Floor 5 as `__HK.genLevel(5, 1)` builds it (a player's floor 5 comes from the run's own seed, `levelSeed(n)`, so it differs):

| Step | What happens | Code |
|---|---|---|
| 1. The card | Floor 4 is cleared: its time, falls and lives, "Next: Floor 5, The Halls of the West." Climb on. | `levelComplete`, `nextFloor` |
| 2. The Crossing | Floor 5 changes theme, so the interlude plays: Nebamun's pool garden, a heron lifting off the coping, a whitewashed pylon at the end of the path. Right held walks him there; Jump skips. | `crossDue`, `crossBegin` |
| 3. The entry | He walks out of the start door's dark opening (column 190, row 9); its leaf drops behind him with a thud. Control at 0.62 s. The banner names the floor. | `startEntry`, `EN_CTL`, `intro` |
| 4. The floor | 157 segments over 360 columns and 61 rows, 305 bot actions. It features lifts (18 of them), the alcove puzzle and tunnels (`L.feature`). It opens with a climb, a slicer to time, a one-tile pit, cracked floor to run over and stakes to tiptoe across. Then a lift up three storeys, tunnels to crawl, a hanging to slide down four storeys and lifts going down; eight sky clocks stand along the floor (`L.cps`). | `L.segs`, `L.path` |
| 5. Gates and guards | On row 45 two gates, a guard (two hearts) posted past the first, and a remote plate for a gate in the next turn (`rem-plate`). The exit's plate (`xplate`) lies on row 42, far from the door: stepping on it opens the door somewhere on the floor. | `gateDue`, `remotePlate`, `xplate` |
| 6. The captain | On row 54 the captain (four hearts) stands before the exit, as on every fifth floor. | `guardBudget` |
| 7. The exit | Up at the open door (column 334, row 54): he climbs its stairs, whitens into the light and is gone. The card comes. | `exit`, `EX_N` |

## What the game is

| | |
|---|---|
| Manner | Prince of Persia 1989: a side view of stone rooms (10 by 3 tiles of 32 by 64 px), run, jump, hang, climb, careful steps, sword fights, traps that kill outright, timed gates |
| Platform | an iPhone in landscape (portrait pauses behind a "turn your phone" prompt), touch pad plus Jump and Grab; keys work on a computer |
| Offline | a PWA: `manifest.webmanifest` (fullscreen, landscape), `sw.js` caches the page and icons and keeps the Google Fonts files after the first online launch; GitHub Pages serves `main` |
| Source | `dev/hourglass-keep.html` is the source of truth; `dev/tools/build.py` makes `index.html` and `sw.js` (cache `hourglass-keep-vN`) |
| Length | endless: floors are numbered from 1 and each is generated from the run's seed (`S.seed`, `levelSeed(n)`) |
| Difficulty | `L.d = min(1, (n-1)/24)`: it ramps to full at floor 25 (guards' skill and rank, gate timers, the chase's lead); traps and guards per floor grow by floor band ([level-design.md](level-design.md)) |

## The setting

The keep is the tomb-world of the twelve hours of the night (the Amduat and the Book of Gates: the sun's boat goes through one region
an hour and is reborn at dawn), set in places of Egypt, Kush and the Sahara. Twelve themes (`THEMES`), four floors each.

| Theme (`name`) | `look` | `style` | First floors |
|---|---|---|---|
| The Waters of Nun | nun | dungeon | 1-4 |
| The Halls of the West | west | palace | 5-8 |
| The Blue Chambers | blue | tile | 9-12 |
| The Forges of Meroë | meroe | forge | 13-16 |
| The Green Hall of Osiris | osiris | crypt | 17-20 |
| The Foggaras of Garama | foggara | dungeon | 21-24 |
| The Deffufa of Kerma | deffufa | palace | 25-28 |
| The Well Corridors | wells | tile | 29-32 |
| The Labyrinth of Hawara | hawara | dungeon | 41-44 |
| The Salt Fortress of Shali | shali | palace | 45-48 |
| The Pyramids of Napata | napata | forge | 53-56 |
| The Stelae of Aksum | aksum | crypt | 57-60 |

- `style` is the family of drawing (stone courses, arches, lamps, metal, windows: the style-keyed tables); `look` is the theme's own
  backdrop (`BGART`), hangings (`TAP`), Torchlight light (`lk`) and effects (`LFX`).
- **`themeOf(n)`**: floors go in blocks of four. Block b takes the style `GEN_STYLE[b % 5]`, and `SCHED[turn][style][light]` picks the
  theme by the light the block falls in (`floor((n-1)/20) % 3`) and the 60-floor turn of the day (`floor((n-1)/60) % 3`). The order
  repeats every 180 floors. Two blocks in a row never share a theme, so the theme changes at every fourth floor from 5. Some themes
  come back early in another light: the Forges and the Green Hall by moonlight on floors 33-40, the Blue Chambers at dawn on 49-52.
- **`progOf(n)`**: a cycle every 20 floors (`CYCLE`). `tod` is dusk, night, dawn in turn (0, 1, 2), then the day repeats; sunrise is
  floor 60. `wear` (0 to 3) is the keep's ruin: more breaches, rubble, cobwebs and cracks, fewer lit lamps. `sink` lowers the land
  seen through the windows a little every floor: he is climbing a tower.
- **`themeName(n)`**: from floor 21 the name carries the light ("by Moonlight", "at Dawn", "at Dusk"); from floor 41 (wear 2) it is
  "The Ruined ..." (for example "The Ruined Labyrinth of Hawara at Dawn").
- **The generator never reads the theme.** It builds each floor by the old five-style turn (`L.gstyle`, `GEN_STYLE`), so a change of
  theme never moves a tile, and a floor's theme always has the style its floor is built by.
- Sources for each theme's motifs: `dev/tools/egypt_themes.html` (`egyptpage.py`).

## The owner's content rules

| Rule | In the game |
|---|---|
| Levels are fully generated | no hand-made levels or rooms; every floor comes from `genLevel(n, seed)` |
| No churches, crosses or the Ark | Aksum is shown "before its churches": stelae, tombs, granite; nothing Christian in its crossing either |
| No living peoples as enemies or decoration | the enemies are tomb robbers (guards), skeletons, snakes and the dark; the crossings have animals only, no people |
| No chains | everything that hangs is rope (`barRope`, `ropeOf`): the swing, the pendulum's lashing, lamps, lifts, backdrops. Iron chains only behind `EGP.traps`/`EGP.lamps` off |
| No arrows in the world | hints of a way (kick shafts, the swing's throw, the jgrab jump) are sand blown along a path (`jetStream`), not chevrons |
| The sky clock, not an hourglass | the checkpoint is Nut's sky clock (`nutClock`, drawn by `drawHourglass`; round 8, after round 4's clepsydra and round 7's barque clock were rejected); the HUD's sands and gate timers are the same clock (`drawGlass`); the words are "sky clock" and "hours". `S.sands` and every timing are unchanged |
| Post and lintel | arches, doors and windows are post and lintel; the dungeon style's vaults stay round |
| A damaging drop must be worth it and look like one | a `hurtdrop` has its own broken look, and is kept only if it saves 25% of the route and 10 tiles of walking ([hurtdrop](elements/hurtdrop.md)) |
| Floors never shorter | a change must not shorten floors or remove the plain floor after each trap (`breathe()`; `metrics40.py`) |

## Lighting modes

| Mode | What it is | Who chooses |
|---|---|---|
| **Torchlight** | the scene drawn by WebGL2 through `G2D` (the recording Canvas2D look-alike), lit by a light map of lamps, sky openings and fire, with shadows, relief, bloom and grade. The default since v42 (set once per save by `S.set.lightDef`) | the player |
| **Classic** | the 2D canvas, "the lighting this game shipped with": the same drawing with 2D glows and cuts | the player |

- The switch is the Graphics screen's "Lighting: Torchlight / Classic" button (`gShader`, `S.set.lightMode`); only the player switches
  (owner, v63). Torchlight also needs the Graphics toggle "Lighting" on (`shaderOn()`).
- Slow frames never switch to Classic. They only scale Torchlight's scene down (`GLP.rs` 1, 0.75, 0.5) after two 2 s windows in a row
  average over 38 ms; it steps back up one level after `UP_N` 3 windows under `UP_MS` 17.2 ms (`glTime`).
- A missing or lost WebGL context falls back to Classic (`glKill`), since the screen would otherwise be black; the button then says
  "Not available on this device". `?wgl=0` takes the old v60 path (2D scene copied into WebGL).
- Looks are made and checked in both modes. How each pass works: [rendering.md](rendering.md).

## Progression

```
title -> floor n: entry -> play (deaths: rewind or rise) -> exit stairs -> card -> Climb on
                                                                          |
                                     theme changes at n+1? -> the Crossing -> floor n+1: entry
```

- **The floor's banner**: "Floor n" and the theme's name for 2.6 s as play starts (`intro`); hints wait for it.
- **The card** (`levelComplete`, mode `card`): "Floor n cleared", the theme's name, the floor's time, falls and lives, and "Next:
  Floor n+1, <name>." A rare flag on the next floor is named (`FLAG_TEXT`: tower, rotten, barracks, longway, maze). The ordinary
  featured families are left for the player to find. Climb on, or Title screen.
- **The Crossing** (round 36): at each change of theme (`crossDue(n)`: floors 5, 9, 13, ...), between Climb on and the next floor's
  entry. He crosses the open land of the new theme's setting at the hour of `progOf`, moving only while the pad is held, and goes in
  at a doorway; Jump skips. Never on Continue, Restart, a checkpoint, a respawn or the title, under `?bench`, the bot or a test, with
  "Crossings" off, or with `?cross=0`. Look only: the save, `S`, the floor clock and the rewind ring are untouched.
  [the Crossing](elements/the-crossing.md).
- **The entry** (round 26f): on a fresh floor only (next floor, new run, Restart). He comes out of the start door and its leaf drops.
  [doors](elements/doors.md).
- **Inside a floor**: runs and the chambers between them, forks, puzzles, traps, guards, a chase from floor 6, checkpoints, the exit
  plate and the door. [level-design.md](level-design.md).

## The sands

The sands are the run's rewinds: three "hours" (`SANDS` 3, `S.sands`) shown as three sky clocks in the HUD.

- After a death, Grab turns time back about five seconds (to a calm moment at least 4.5 s back in a 10 s ring of snapshots) for one
  hour. Jump, or no hours left, rises at the last checkpoint instead.
- Hours come back in full at every checkpoint lit, every rise and every new floor.
- Example: two slicer deaths in a row leave one hour; the next sky clock lights "and your hours are restored".

Numbers and rules: [gameplay.md](gameplay.md#death-the-sands-and-checkpoints).

## Save, Continue, Restart

| | |
|---|---|
| Where | `localStorage`, key `hourglass-keep-v1` (`KEY`; not renamed): one save per browser and site, on the device only |
| What | the run (`level`, `seed`, `maxHp`, `time`, `deaths`, `lifeTaken`), the floor in progress (`cp`, `floorTime`, `floorDeaths`, `cpPlates`, `resume`), `sands`, `hints`, `learned`, `set` (settings) |
| When | every 3 s of play (`snapshotResume`, only in a stable state and not on a lift), on pause, on leaving the page, at checkpoints, deaths and floor ends |
| Generator version | `GEN` 9: a save from another generator version keeps the run but drops the checkpoint, the resume point and the floor time |
| Continue on Floor N | the floor rebuilt at the last lit checkpoint (`startLevel(S.level, S.cp)`), then the resume point laid on it (`applyResume`): his place and hearts, dead guards and snakes, taken flasks, fallen slabs, rubble, lit clocks, the opened door, fallen roof blocks, latched gates. A death clears the resume point, so Continue after a death starts at the checkpoint |
| Restart floor | the floor from its start door, with the entry; checkpoints and pressed plates cleared; the floor's clock runs on |
| New run | asks first if a run exists ("Start over?"); a new seed and floor 1; settings, hints and learned moves are kept (`newSave(prev)`) |
| Benchmark | `?bench` never writes the save (`writeSave` returns while `BENCH.run`) |

## Title, fonts, names

- The title screen: eyebrow "Twelve hours of night" (or the floor and theme of the run in progress), **Dawnward**, a line on the
  game, and Continue on Floor N, New run (or "Into the night" for a first run), How to play, Graphics; the version (`APP_VERSION`,
  stamped by the build). A preview of the current floor is drawn behind it (`previewTitle`).
- Fonts (Google Fonts): **Rokkitt** for display (titles, the floor's banner, the HUD's FLOOR label and gate timer), **Jost** for text.
- Not renamed from Hourglass Keep: the cache key `hourglass-keep-vN`, the save key, the repo and its URLs.

## How changes are made

- **Research first.** A change to feel or level design is usually asked for with research first: how the Prince of Persia games (and
  other games) handled it, reported with sources. Example: round 35a's shorter running jump was measured against PoP 1989's runjump in
  SDLPoP's `seqtbl.c` (5 ticks in the air, 0.42 s) and Celeste's run; the bot's floors 1-27 were measured before and after.
- **Look only vs play.** Most rounds change only the drawing: hit boxes, timings, the generator's layouts and the bot's frames stay
  identical, and looks use hashes, not the generator's random streams.
- **Measured, with pictures.** Each round has its picture tool (`egyptrNN.py`) and, where a rule can be checked, a scan in the
  regression suite (`suite.py`); the release routine is in CLAUDE.md.
- The rules of every element: `elements/`; the round-by-round log: CLAUDE.md.
