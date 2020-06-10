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
