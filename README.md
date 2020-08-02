# experimentalCardEaseFactor
Dynamically adjusts ease factor on cards automatically, constantly seeking the
right ease adjustment to hit a target success rate.

See: https://eshapard.github.io/anki/thoughts-on-a-new-algorithm-for-anki.html
for the original rationale.

Important: **You must not use an interval modifier in your deck options**.
Your interval modifier must be set to 100% (no change) for all decks. Otherwise
this algorithm could be constantly chasing a moving target.

WARNING: This makes your ease factors move much more than you are probably used
to. Missing a few reviews can make them drop a lot. But if you get the next
review or two, it will climb back really fast. You can limit these swings in
the config, though arguably it's ok not to constrain these moves too much,
because they self-correct over time. Strongly advise you ignore your ease after
installing this add on and just let it do its thing.

### Differences from eshapard's version

Unlike eshapard's version, which requires four reviews before the algorithm
kicks in, this version lets the algorithm adjust ease factors as early as
possible. To avoid wild swings early in a card's life, I limit how much the
algorithm can change the ease factor at first.

I also incorporate a moving average, so your most recent success rate will have
more influence than early reviews. This helps adjust the ease more quickly when
it took you a long time to learn a card originally but now you've really got it
down.

If you're used to ease factors very close to 250%, this algorithm will produce
some alarmingly low (or high) ease factors. It will generally auto-adjust very
quickly based on your performance. That said, this add on has not been tested
across a population of users to see how it affects review load. Definitely
provide feedback if you feel this is causing significantly more reviews than
expected or fewer reviews than necessary. My anecdotal experience is that it
front loads the work a bit, causing more reviews with short intervals in the
beginning, but backing off rapidly after a card is well known.

### Installation
In Anki, 

    Tools > Add-ons > Get Add-ons...

Then use this code: 

    1672712021

Manual installation

Create a new folder named *experimentalCardEaseFactor* in your Anki 2.1 addons
directory. Save `__init__.py`, `experimentalCardEaseFactor.py` and `YesOrNo.py`
to this folder. If you don't want to use `YesOrNo.py`, don't include it, and
remove it from `__init__.py`.

### Configuration
There are a couple options that can be configured by editing the addon:

1. 'target_ratio' is the success rate you want to aim for (e.g. 0.85 for an 85%
success rate)
2. show_stats indicates whether or not to show the pop-up with some card stats
for the current and last card, including the history of reviews and how that is
affecting its ease
3. moving_average_weight indicates how much to focus on more recent results
when determining success rate. Higher numbers will focus more on recent
performance. (This is very sensitive, values between 0.07 and 0.3 are
reasonable).

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
- eshapard
- ja-dark
- cordone
- Also, hat tip to the MIA crew for inspiration and to the AnKing for helping me
figure out how all this works

I am not requesting support, but the original author, eshapard, can receive
tips at this link:
https://paypal.me/eshapard/1

On AnkiWeb here: 
https://ankiweb.net/shared/info/1672712021
