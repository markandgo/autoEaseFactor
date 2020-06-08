# experimentalCardEaseFactor
Adjusts ease factor for cards individually during review an Anki.

See: https://eshapard.github.io/anki/thoughts-on-a-new-algorithm-for-anki.html
for rationale.

Unlike eshapard's original, which requires four reviews before the algorithm
kicks in, this version lets the algorithm adjust ease factors as early as
possible. To avoid wild swings early in a card's life, I limit how much the
algorithm can change the ease factor at first.

I also incorporate a moving average, so your most recent success rate will have
more influence than early reviews (in case it took you a long time to learn
a card originally but now you've really got it down).

Important: **You must not use an interval modifier in your deck options**.
Your interval modifier must be set to 100% (no change) for all decks.


### Installation
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
self evaluation, similar to low-key Anki and the add-on by ja dark.

I suggest that you use the YesOrNo addon and that you disable
*Show next review time above answer buttons* in Tools > Preferences...
Seeing the next review times will just distract you from studying.

## Shameless Donation Request
I am not requesting any support, but if you like this add-on, consider
supporting the original author using this link: https://paypal.me/eshapard/1
