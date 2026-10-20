# The prince's proportions (spec)

## The rule (round 22d): the 1989 Prince of Persia kid

Owner, after round 22c: "that is still slightly off. I like best the proportions in the original PoP sprite you downloaded. Replicate
the proportions from there in our prince." The prince's proportions follow the DOS kid's; the ANSUR II section below is background.

Source: the DOS kid's frames from PrinceJS (https://github.com/oklemenz/PrinceJS, assets/gfx/kid.png and kid.json, kept in
`dev/tools/ref/pop_kid.*`; the guards' `guard.*` and `fatguard.*` too). Frame numbers follow Mechner's frame list as SDLPoP names it
(https://github.com/NagyD/SDLPoP, src/types.h: frame_15_stand, frame_7..14_run, frame_121..132_stepping, frame_109_crouch,
frame_87..99_hanging, frame_135..149_climbing, frame_150_parry, frame_151..153_strike, frame_158_stand_with_sword, frame_191..205_drink;
src/seqtbl.c plays them).

Aspect: DOS 320x200 on a 4:3 screen, so a pixel is 1.2 times taller than wide. Every horizontal measure is divided by 1.2 (into rows);
vertical measures are used as they are.

Landmarks (frame 15 unless said; rows from the crown's top edge, standing height 41 rows): crown 0; chin 7 (head 7 rows, the same bitmap in
every upright frame); one row of throat (row 7); the shirt's shoulder line at row 7, level with the chin; the deltoid's top row 8; shoulder
joint ~9.5; elbow 16.5 (run frame 10's bent arm); wrist 21.5; fingertips 25; waist 0.59 of the height over the sole (not drawn on the kid:
the guards' sash, guard frame 29, rows 16-17 of 40); crotch 22.8 (run frame 12 and strike frame 152: the straight back leg from the
split to the sole, 18.0 and 17.6 rows); knee 29.7 (frames 12 and 158); sole 41. Widths, in DOS px: head 8 (6.7 rows), neck under the
chin 4, foot 7, upper arm 4, forearm 3; the trunk's depth per row is the mean silhouette of frames 15, 121, 132 (arm included).

How he reads: a small head on a long, slim, straight body; chin almost on the shoulders; shoulders sloping down and back from the jaw;
head, back and seat on one vertical line; trunk about as deep as the head and barely tapering; long arms (fingertips at the crotch);
small feet. The guards are the same rotoscoped men, broader (chest 0.20 of the height), no neck showing, the sash at 0.59.

Measured with `dev/tools/r22dmeasure.py` (our figure at 10x, the same landmarks and widths at the same fractions of height):

| Measure (share of standing height unless said) | PoP kid | v69 | 22c | 22d |
|---|---|---|---|---|
| height in heads (crown to chin) | 5.86 | 4.60 | 4.77 | 5.86 |
| chin over the sole | 0.829 | 0.782 | 0.791 | 0.829 |
| chin to the shoulder's top (deltoid) | 0.024 | -0.006 | 0.040 | 0.023 |
| ...in heads | 0.14 | -0.03 | 0.19 | 0.13 |
| chin to the pit of the neck | 0.024 | -0.006 | 0.031 | 0.023 |
| shoulder line at the back (C7) | 0.829 | 0.786 | 0.786 | 0.822 |
| shoulder's top | 0.805 | 0.788 | 0.750 | 0.806 |
| shoulder joint | 0.768 | 0.760 | 0.722 | 0.763 |
| elbow | 0.598 | 0.590 | 0.565 | 0.594 |
| wrist | 0.476 | 0.456 | 0.420 | 0.458 |
| fingertips | 0.390 | 0.397 | 0.361 | 0.391 |
| shoulder joint to fingertips | 0.378 | 0.363 | 0.361 | 0.372 |
| crotch (split along a straight leg) | 0.444 | 0.335 | 0.335 | 0.360 |
| knee | 0.276 | 0.250 | 0.250 | 0.250 |
| head depth / head height | 0.95 | 0.94 | 0.94 | 0.96 |
| neck depth under the chin | 0.081 | 0.096 | 0.119 | 0.089 |
| neck depth / head height | 0.48 | 0.44 | 0.57 | 0.52 |
| depth at the chest, arm in (0.25-0.36 down) | 0.154 | 0.184 | 0.178 | 0.159 |
| depth at the waist (0.40-0.55 down) | 0.164 | 0.169 | 0.169 | 0.155 |
| depth at the hips (0.60-0.68 down) | 0.148 | 0.156 | 0.159 | 0.140 |
| depth at the knees (0.72-0.80 down) | 0.138 | 0.127 | 0.127 | 0.118 |
| foot length | 0.142 | 0.183 | 0.183 | 0.154 |

Not matched on purpose: the knee (the legs are gameplay's: hip 24 px over the ankle, thigh = shin) and the crotch as read along a straight
leg (our thighs are round tubes about the hip joint, under the kilt; the kid's baggy trousers split low). The waist depth is his blousing
shirt. Robbers share the skeleton with their own heavier build.

Skeleton (round 22d): `LEN={th:12,sh:12,to:15,nk:4.66,hd:3.52,ua:8.9,fa:8.6}`: the head 9.0 px of 52.75 (5.86 heads), v69's trunk (15)
and arm (17.5, so every held hand and overhead reach is v69's), the crown 27.7 px over the hip (never above v69's). `NJ` (the neck's
junction): the pit of the neck and the deltoid's top ~1.2 px under the chin, C7 just under it, the neck's top `NJ.hn` heads under the
head's centre. Check a new pose or skeleton with `figscan.py` (gameplay positions) and `r22dmeasure.py` (these numbers).

## Background: ANSUR II (rounds 22b and 22c)

Background (rounds 22b and 22c, superseded as the rule by round 22d). Owner's rule then (round 22b): the figure follows researched real proportions of an athletic youth. The head keeps the style's size;
the neck, shoulders and trunk follow the body's scale. Measured in this session from downloaded data (2026-10-20).

## Source data: ANSUR II, US Army men aged 17 to 20 (n = 422)

File: `ergonomics.csv` from calmcode.io (the public ANSUR II working databases, 6,068 subjects; the openlab.psu.edu
CSV links now return a web page). Means in mm:

| Landmark (height over the floor) | mm | Depth or length | mm |
|---|---|---|---|
| stature | 1753 | head length (front to back) | 199 |
| cervicale (C7) | 1510 | tragion to top of head | 132 |
| suprasternale (pit of the neck) | 1432 | menton to sellion | 122 |
| acromion (top of the shoulder) | 1431 | neck circumference / base | 382 / 419 |
| chest height | 1291 | chest depth | 237 |
| omphalion (waist) | 1061 | waist depth | 212 |
| trochanterion (hip) | 900 | buttock depth | 229 |
| crotch | 850 | biacromial breadth | 411 |

ANSUR has no chin height. Head height (chin to crown) is taken as 0.130 of stature (Drillis and Contini), 228 mm; a second
estimate (tragion to top plus three quarters of menton to sellion) gives 223 mm. Both agree within 5 mm.

## Derived ratios (scale-free)

| Measure | Value |
|---|---|
| chin over acromion | 94 to 99 mm, 0.054 of stature |
| chin over the pit of the neck | 94 to 99 mm (the pit is level with the acromion) |
| C7 under the chin | 15 to 20 mm |
| C7 over the acromion | 79 mm |
| chin-to-acromion / acromion-to-hip | 0.177 to 0.186 |
| acromion-to-hip / hip-to-floor (trunk / leg) | 0.590 |
| neck depth (circumference / pi) / chest depth | 0.51 |
| neck depth / head length | 0.61 |

## Other games, measured

- Prince of Persia (1989, DOS), standing frame 15 from the sprite sheet (`PrinceJS` assets, 12 by 41 px): head 7 rows, so
  5.9 heads tall; chin to the shirt's shoulder line about 1 to 1.5 rows, 0.024 to 0.037 of height (a little shorter than real,
  at a 7-row head); the neck shows as one row of skin. Rotoscoped, so the body is real and the head close to real.
- Limbo, Abe's Oddysee: the screenshots that could be downloaded (Wikipedia; it then rate-limited) show the figures at 10 to 15 px,
  too small to measure a neck. Not used.

## The figure (53 px tall, head 10.4 px, about 3.7 cm a px in the body's scale)

| Measure | Target (body scale) | v69 | round 22b | round 22c |
|---|---|---|---|---|
| chin over acromion top, px | 2.5 to 2.7 | -0.1 | 2.33 | 2.53 |
| ...over acromion to hip | 0.177 to 0.186 | -0.006 | 0.156 | 0.172 |
| C7 under the chin, px | 0.4 to 0.5 | 0.39 | 4.22 | 0.82 |
| trunk / leg | 0.590 | 0.671 | 0.591 | 0.583 |
| neck depth / chest depth | 0.51 | 0.46 | 0.60 | 0.60 |

Round 22c meets the targets but for C7 (0.4 px further down, so the nape line does not form a bump) and the neck's depth
against the stylised chest (it matches the head: 0.59 against 0.61). Measure the neck from the chin to the acromion's top, never
to the shoulder joint, in the body's scale, never the head's. Check a new pose or skeleton with `figscan.py` (gameplay positions)
and `r22cmeasure.py` (these numbers).
