# experimentalCardEaseFactor

Dynamically adjusts ease factor on cards automatically, constantly seeking the
right ease adjustment to hit a target success rate.

See: https://eshapard.github.io/anki/thoughts-on-a-new-algorithm-for-anki.html
for the original rationale.

Important: **You must not use an interval modifier in your deck options**.
Your interval modifier must be set to 100% (no change) for all decks. Otherwise
this algorithm could be constantly chasing a moving target.

WARNING: This can make your ease factors move more than normal. Missing a few
reviews can make them drop a lot. But if you get the next review or two, it
will climb back really fast. You can limit these swings in the config, though
arguably it's better not to constrain these moves too much, because they
self-correct over time.

#### Differences from eshapard's version

Unlike eshapard's version, which requires four reviews before the algorithm
kicks in, this version lets the algorithm adjust ease factors as early as
possible, including using information from learning steps. To avoid wild swings
early in a card's life, I limit how much the algorithm can change the ease
factor at first.

Since learning steps provide very low quality data on the ultimate retention of
a card, I also incorporate a moving average, so your most recent success rate
will have much more influence than early reps. This helps adjust the ease more
quickly when it took you a long time to learn a card originally but now you've
really got it down. I also include a 'leash' setting, to tie your ease down at
first, in case you want to limit the swings in the algorithm until you've had
many more reviews.

If you're used to ease factors very close to 250%, without a low leash, this
algorithm can produce some alarmingly low (or high) ease factors. It will
generally auto-adjust very quickly based on your performance. That said, this
add on has not been tested across a population of users to see how it affects
review load. Definitely provide feedback if you feel this is causing
significantly more reviews than expected or fewer reviews than necessary. My
anecdotal experience is that it front loads the work a bit, causing more
reviews with short intervals in the beginning, but backing off rapidly after a
card is well known.

### Installation

#### In Anki,

    Tools > Add-ons > Get Add-ons...

Then use this code:

    1672712021

#### Manual installation

Create a new folder named *experimentalCardEaseFactor* in your Anki 2.1 addons
directory. Save `__init__.py`, `experimentalCardEaseFactor.py` and `YesOrNo.py`
to this folder. If you don't want to use `YesOrNo.py`, don't include it, and
remove it from `__init__.py`.

### Configuration
There are a few options that can be configured by editing the addon:

1. 'target_ratio' is the success rate you want to aim for (e.g. 0.85 for an 85%
success rate)
2. 'leash' controls how much the ease can change per review, so a small leash
of 10 or 50 will not let the algorithm adjust things until it has much more
data.
3. moving_average_weight indicates how much to focus on more recent results
when determining success rate. Higher numbers will focus more on recent
performance. (This is very sensitive, values between 0.07 and 0.3 are
reasonable).
4. min_ and max_ ease set the bounds of how far the algorithm can set the
ease. This is "per mille," so 5000 = 500%.
5. two_button_mode makes the system "pass/fail" -- you can disable that by
setting this to false (though saving mental load on each review is the primary
benefit of this add-on, would recommend you leave this true if you can).

(I personally use a min of 10 and max of 7000 and leash of 300. I try to keep
learning and relearning steps to a minimum, 2-3. Ease changes a lot, but it
ends up working well for me.)

## YesOrNo.py
Hard and easy add more choices that delay reviews and make you responsible for
determing your ideal ease rating. The ease factor algorithm adjusts ease for
you, so you just need to choose either "Again" or "Good" on any given card.

The YesOrNo.py addon changes your options to Pass/Fail to help streamline your
self evaluation, similar to low-key Anki and ja dark's work that inspired it.

I suggest that you use the YesOrNo addon and that you disable
*Show next review time above answer buttons* in Tools > Preferences...
Seeing the next review times will just distract you from studying.

## Acknowledgments
eshapard
ja-dark
cordone
brownbat (me)
(hat tip to the MIA crew for inspiration and to the AnKing for helping me
figure out how all this works)

I am not requesting support, but the original author, eshapard, can receive
tips at this link:
https://paypal.me/eshapard/1

### Changes

#### 2020-08-09

Bugfix for formatted stats on new cards

#### 2020-08-08

Slight formatting adjustment for stats. Also updates "tests[.]py" to be more
accurate. Unfortunately "tests" still does not predict the algorithm's behavior
exactly. I am expecting a better simulator next patch, after some additional
debugging. (In the meantime, if you open "tests[.]py" and hardcode a list of
ease factors, as in the commented-out example from lines 272 to 279, you will
get an accurate simulation.)

#### 2020-08-06

Adding four-button mode as an option, for those who don't want to use the
Pass/Fail mode. I'd caution against using this though, the algorithm's main
benefit is reducing your thinking time on each card.

#### 2020-08-06

Fixes error with filtered decks introduced during last change. Note: Ease
factors may dip to 250% during a filtered review, but should correct themselves
as soon as you return to regularly scheduled reviews. I'm still investigating
to ensure this works for people who rely on filtered reviews for rescheduling,
please comment on the issue in github if you have experience with this and
notice any odd behavior:

https://github.com/brownbat/experimentalCardEaseFactor/issues/5

#### 2020-08-02

Initial ease factor now honors the value in the individual deck settings,
instead of pulling from this add-on's config. Hat tip to blahab for talking
me through this change.

#### 2020-08-01

- Issues enabled on GitHub, thanks for catching that!

Note: The algorithm gets information from learning steps by design. In my
personal experience, if a card was very hard to learn, it often needs to be
reviewed sooner. Once I've got it down, the algorithm will very quickly bring
the ease back up.

**However,** if you prefer esharphard's original approach, where learning steps
are ignored for ease, lower the "leash" value in settings, so that early reps
will not have much of an influence.

For my settings, I'm generally just using a couple learning steps (ie, 15 240)
to let the algorithm take over as quickly as possible. I experimented with much
longer learning periods with specific intervals, but my results were
significantly worse, with many cards having poor retention, and other easy
cards taking learning reps I didn't really need. I prefer performance-based
feedback as quickly as possible. If you prefer setting a very large number of
learning steps, that's fine too, this algorithm will still work, but you may
want to adjust the "leash" value down quite a bit. If you have 10 learning
steps, a leash between 10 and 50 might be best for you.

#### 2020-07-25

- Remove unhandled exception. This may cause errors during review when combined
with other add-ons that create empty Notes. Please report any errors to
https://github.com/brownbat/experimentalCardEaseFactor

#### 2020-06-14

- Added config options that help limit how much the algorithm can change your
ease.
- Corrected moving average initialization to avoid too much weight placed on
first step.

#### 2020-06-11

Added config options.
