# The prince's proportions (spec)

Owner's rule (round 22b): the figure follows researched real proportions of an athletic youth. The head keeps the style's size;
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
