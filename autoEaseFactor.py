# inspired by https://eshapard.github.io/

from __future__ import annotations

import math

# anki interfaces
from anki import version
from aqt import mw
from aqt import gui_hooks
from aqt import reviewer
from aqt.utils import tooltip
from aqt.qt import QMessageBox
from anki.lang import _

# version
anki213 = version.startswith("2.1.3")
anki2126 = version.startswith("2.1.26") or anki213

# add on utilities
from . import ease_calculator
if anki2126:
    from . import deck_settings
# from . import menu_action

config = mw.addonManager.getConfig(__name__)

target_ratio = config.get('target_ratio', 0.85)
moving_average_weight = config.get('moving_average_weight', 0.2)
stats_enabled = config.get('stats_enabled', True)
stats_duration = config.get('stats_duration', 5000)

# Limit how aggressive the algorithm is
min_ease = config.get('min_ease', 1000)
# over 7k the time savings are minimal and the risk of miscalculation is higher
max_ease = config.get('max_ease', 5000)
# let ease change by leash * card views, so leash gets longer quickly
# prevents wild swings from early reviews
leash = config.get('leash', 100)

config_settings = {
    'leash': leash,
    'min_ease': min_ease,
    'max_ease': max_ease,
    'weight': moving_average_weight,
    'target': target_ratio,
    'starting_ease_factor': None
                  }

def get_reviews(card=mw.reviewer.card):
    return mw.col.db.list(("select ease from revlog where cid = ?"), card.id)

def get_ease_factors(card=mw.reviewer.card):
    return mw.col.db.list("select factor from revlog where cid = ?"
                               " and factor > 0", card.id)

def get_starting_ease(card=mw.reviewer.card):
    deck_id = card.did
    if card.odid:
        deck_id = card.odid
    try:
        deck_starting_ease = mw.col.decks.confForDid(
                deck_id)['new']['initialFactor']
    except KeyError:
        deck_starting_ease = 2500
    return deck_starting_ease


def suggested_factor(card=mw.reviewer.card, new_answer=None):
    """Loads card history from anki and returns suggested factor"""

    """Wraps calculate_ease()"""
    card_settings = {}
    card_settings['review_list'] = get_reviews(card)
    if new_answer is not None:
        card_settings['review_list'].append(new_answer)
    card_settings['factor_list'] = get_ease_factors(card)

    deck_starting_ease = get_starting_ease(card)
    config_settings['starting_ease_factor'] = deck_starting_ease

    return ease_calculator.calculate_ease(config_settings, card_settings)


def get_stats(card=mw.reviewer.card, new_answer=None):
    review_list = get_reviews(card)
    if new_answer:
        review_list.append(new_answer)
    factor_list = get_ease_factors(card)
    weight = config_settings['weight']
    target = config_settings['target']

    if review_list is None or len(review_list) < 1:
        success_rate = target
    else:
        success_list = [int(_ > 1) for _ in review_list]
        success_rate = ease_calculator.moving_average(success_list, weight, init=target)
    if factor_list and len(factor_list) > 0:
        average_ease = ease_calculator.moving_average(factor_list, weight)
    else:
        average_ease = config_settings['starting_ease_factor']

    # add last review (maybe simplify by doing this after new factor applied)
    printable_review_list = ""
    if len(review_list) > 0:
        abbr_review_list = review_list[-10:]
        if len(review_list) > 10:
            printable_review_list += '..., '
        printable_review_list += str(abbr_review_list[0])
        for review_result in abbr_review_list[1:]:
            printable_review_list += ", " + str(review_result)
    if factor_list and len(factor_list) > 0:
        last_factor = factor_list[-1]
    else:
        last_factor = None
    card_types = {0: "new", 1: "learn", 2: "review", 3: "relearn"}
    queue_types = {0: "new",
                   1: "relearn",
                   2: "review",
                   3: "day (re)lrn",
                   4: "preview",
                   -1: "suspended",
                   -2: "sibling buried",
                   -3: "manually buried"}

    msg = f"card ID: {card.id}<br>"
    msg += (f"Card Queue (Type): {queue_types[card.queue]}"
            f" ({card_types[card.type]})<br>")
    msg += f"MAvg success rate: {round(success_rate, 4)}<br>"
    msg += f"Last factor: {last_factor}<br>"
    msg += f"MAvg factor: {round(average_ease, 2)}<br>"
    msg += f"Suggested factor: {suggested_factor(card, new_answer)}<br>"
    msg += f"Review list: {printable_review_list}<br>"
    return msg


def display_stats(new_answer=None):
    card = mw.reviewer.card
    msg = get_stats(card, new_answer)
    tooltip_args = {'msg': msg, 'period': stats_duration}
    if anki213:
        tooltip_args.update({'x_offset': 12, 'y_offset': 240})
    tooltip(**tooltip_args)


def adjust_factor(ease_tuple,
                  reviewer=reviewer.Reviewer,
                  card=mw.reviewer.card):
    assert card is not None
    new_answer = ease_tuple[1]
    card.factor = suggested_factor(card, new_answer)
    if stats_enabled:
        display_stats(new_answer)
    return ease_tuple


gui_hooks.reviewer_will_answer_card.append(adjust_factor)
