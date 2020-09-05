# inspired by https://eshapard.github.io/

from __future__ import annotations

import math

from anki import version
from aqt import mw
from aqt import gui_hooks
from aqt import reviewer
from aqt.utils import tooltip

anki213 = version.startswith("2.1.3")
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


class EaseAlgorithm(object):

    def __init__(self):
        self.factor = 2500
        self.last_tooltip_msg = None
        self.last_ease = None

    @staticmethod
    def calculate_moving_average(l, init=None):
        assert len(l) > 0
        if init is None:
            result = sum(l)/len(l)
        else:
            result = init
        for i in l:
            result = (result * (1 - moving_average_weight))
            result += i * moving_average_weight
        return result

    def set_last_ease(self, new_last_ease):
        self.last_ease = new_last_ease

    def get_reviews(self, card_id):
        reviews = mw.col.db.list(("select ease from revlog where cid = ?"),
                                 card_id)
        if self.last_ease is not None:
            reviews.append(self.last_ease)
        return reviews

    def get_ease_list(self, card_id):
        return mw.col.db.list(
                "select factor from revlog where cid = ? and factor > 0",
                card_id)

    def find_success_rate(self, card_id):
        review_list = self.get_reviews(card_id)
        if not review_list or len(review_list) < 1:
            success_rate = target_ratio  # no reviews: assume we're on target
        else:
            success_list = [int(i > 1) for i in review_list]
            success_rate = self.calculate_moving_average(success_list)

        return success_rate

    def find_average_ease(self, card_id):
        average_ease = 0
        ease_list = self.get_ease_list(card_id)
        if not ease_list:
            deck_id = mw.reviewer.card.did
            try:
                deck_starting_ease = mw.col.decks.confForDid(
                        deck_id)['new']['initialFactor']
            except KeyError:
                deck_starting_ease = 2500
            average_ease = deck_starting_ease

        else:
            average_ease = self.calculate_moving_average(ease_list)
        return average_ease

    def calculate_ease(self, card_id):
        deck_id = mw.reviewer.card.did
        try:
            deck_starting_ease = mw.col.decks.confForDid(
                    deck_id)['new']['initialFactor']
        except KeyError:
            deck_starting_ease = 2500
        starting_ease = deck_starting_ease

        success_rate = self.find_success_rate(card_id)

        # Ebbinghaus formula
        if success_rate > 0.99:
            success_rate = 0.99  # ln(1) = 0; avoid divide by zero error
        if success_rate < 0.01:
            success_rate = 0.01
        delta_ratio = math.log(target_ratio) / math.log(success_rate)
        average_ease = self.find_average_ease(card_id)
        suggested_factor = int(round(average_ease * delta_ratio))

        # anchor this to starting_ease initially
        number_of_reviews = len(self.get_reviews(card_id))
        ease_cap = min(max_ease, (starting_ease + (leash * number_of_reviews)))
        if suggested_factor > ease_cap:
            suggested_factor = ease_cap
        ease_floor = max(min_ease, (starting_ease -
                                    (leash * number_of_reviews)))
        if suggested_factor < ease_floor:
            suggested_factor = ease_floor

        return suggested_factor

    def adjust_ease(self):
        card_id = mw.reviewer.card.id
        ease_list = self.get_ease_list(card_id)
        last_factor = None
        if len(ease_list) > 0:
            last_factor = ease_list[-1]
        calculated_ease = self.calculate_ease(card_id)
        self.factor = calculated_ease

        # tooltip messaging
        if stats_enabled:
            review_list = self.get_reviews(card_id)
            success_rate = self.find_success_rate(card_id)
            '''
            if success_rate > 0.99:
                success_rate = 0.99  # ln(1) = 0; avoid divide by zero error
            if success_rate < 0.01:
                success_rate = 0.01
            delta_ratio = math.log(target_ratio) / math.log(success_rate)
            average_ease = self.find_average_ease(card_id)'''

            avg_ease = self.find_average_ease(card_id)
            ease_list = self.get_ease_list(card_id)

            printable_review_list = ""
            if len(review_list) > 0:
                abbr_review_list = review_list[-10:]
                if len(review_list) > 10:
                    printable_review_list += '..., '
                printable_review_list += str(abbr_review_list[0])
                for _ in abbr_review_list[1:]:
                    printable_review_list += ", " + str(_)

            card_types = {0: "new", 1: "learn", 2: "review", 3: "relearn"}
            queue_types = {0: "new",
                           1: "relearn",
                           2: "review",
                           3: "day (re)lrn",
                           4: "preview",
                           -1: "suspended",
                           -2: "sibling buried",
                           -3: "manually buried"}

            msg = f"card ID: {card_id}<br>"
            msg += (f"Card Queue (Type): {queue_types[mw.reviewer.card.queue]}"
                    f" ({card_types[mw.reviewer.card.type]})<br>")
            msg += f"MAvg success rate: {round(success_rate, 4)}<br>"
            msg += f"Last factor: {last_factor}<br>"
            msg += f"MAvg factor: {round(avg_ease, 2)}<br>"
            msg += f"Suggested factor: {calculated_ease}<br>"
            msg += f"Review list: {printable_review_list}<br>"
            tooltip_args = {'msg': msg, 'period': stats_duration,
                            'x_offset': 12, 'y_offset': 240}

            if not anki213:
                msg = f"card ID: {card_id}<br>"
                msg += (f"Card Queue (Type): "
                        f"{queue_types[mw.reviewer.card.queue]}"
                        f" ({card_types[mw.reviewer.card.type]})<br>")
                msg += f"MAvg success rate: {round(success_rate, 4)}<br>"
                msg += (f"MAvg factor (Last factor): {round(avg_ease, 2)}  "
                        f"({last_factor})<br>")
                msg += f"Suggested factor: {calculated_ease}<br>"
                msg += f"Review list: {printable_review_list}<br>"
                tooltip_args = {'msg': msg, 'period': stats_duration}

            tooltip(**tooltip_args)


alg = EaseAlgorithm()


def on_answer(ease_tuple, reviewer=reviewer.Reviewer, card=None):
    last_ease = ease_tuple[1]
    alg.set_last_ease(last_ease)
    alg.adjust_ease()
    card.factor = alg.factor
    return ease_tuple


gui_hooks.reviewer_will_answer_card.append(on_answer)
