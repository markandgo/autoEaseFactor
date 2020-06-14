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

**tooltip_duration**

- Length of time the tooltips persist (only relevant if show_stats is True)
- default: 5000

**starting_ease**

- default: 2500 (250%)
- Note per-mille, so 2500 = 250%.

**min_ease**

- The minimum ease you want any of your cards to retreat to.
- default: 1000 (100%)

**max_ease**

- The maximum ease you want any of your cards to reach.
- default: 5000 (500%)
- Note that once you get over 5-7k the time savings are minimal and the risks
of miscalculation are higher.

**leash**

- Controls how much the algorithm can change ease after any single review
- default 100
- Note: This window expands after every review, so after we have some data on
the card the algorithm will get more aggressive.
