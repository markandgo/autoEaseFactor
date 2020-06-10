There are three configurable options for this add on:

**target_ratio**

- Specifies your target success rate between 0 and 1. Note: Exponentially
higher numbers of reviews are required the closer you get to 1, most people
will find mid 80s or low 90s about right.
- default: 0.85

**moving_average_weight**

- Specifies how much weight to place on more recent reviews over old reviews.
Note: this is very senstive, values between 0.07 and 0.3 are about right for
most people.
- default: 0.2

**show_stats**

- Show debugging information about recent reviews in a tooltip. Includes
information on past reviews and suggested ease.
- default: True

The following are unimplemented and outlined for future use:

- "starting_ease": 2500, (Starts with an assumption of 250% ease. Note per-mille, so 2500 = 250%.)
- "min_ease": 100, (Will not lower beneath 10% ease)
- "max_ease": 10000, (Will not raise above 1000% ease)
- "anchor_to_previous_ease": 0.2
Will not raise or lower ease more than 0.2 times the current ease per step.
Smaller values lead to smaller ease adjustments.
