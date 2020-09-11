# inspired by https://eshapard.github.io/

from __future__ import annotations

import math

from anki import version
from aqt import mw
from aqt import gui_hooks
from aqt import reviewer
from aqt.utils import tooltip
from aqt.qt import QMessageBox
from anki.lang import _
# for import/export ease values
from aqt.utils import getFile, getSaveFile
import datetime
from ast import literal_eval


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

    def get_reviews(self, card):
        reviews = mw.col.db.list(("select ease from revlog where cid = ?"),
                                 card.id)
        if self.last_ease is not None:
            reviews.append(self.last_ease)
        return reviews

    def get_ease_list(self, card):
        return mw.col.db.list(
                "select factor from revlog where cid = ? and factor > 0",
                card.id)

    def find_success_rate(self, card):
        review_list = self.get_reviews(card)
        if not review_list or len(review_list) < 1:
            success_rate = target_ratio  # no reviews: assume we're on target
        else:
            success_list = [int(i > 1) for i in review_list]
            success_rate = self.calculate_moving_average(success_list)

        return success_rate

    def find_average_ease(self, card):
        average_ease = 0
        ease_list = self.get_ease_list(card)
        if not ease_list:
            deck_id = card.did
            try:
                deck_starting_ease = mw.col.decks.confForDid(
                        deck_id)['new']['initialFactor']
            except KeyError:
                deck_starting_ease = 2500
            average_ease = deck_starting_ease

        else:
            average_ease = self.calculate_moving_average(ease_list)
        return average_ease

    def calculate_ease(self, card):
        deck_id = card.did
        try:
            deck_starting_ease = mw.col.decks.confForDid(
                    deck_id)['new']['initialFactor']
        except KeyError:
            deck_starting_ease = 2500
        starting_ease = deck_starting_ease

        success_rate = self.find_success_rate(card)

        # Ebbinghaus formula
        if success_rate > 0.99:
            success_rate = 0.99  # ln(1) = 0; avoid divide by zero error
        if success_rate < 0.01:
            success_rate = 0.01
        delta_ratio = math.log(target_ratio) / math.log(success_rate)
        average_ease = self.find_average_ease(card)
        suggested_factor = int(round(average_ease * delta_ratio))

        # anchor this to starting_ease initially
        number_of_reviews = len(self.get_reviews(card))
        ease_cap = min(max_ease, (starting_ease + (leash * number_of_reviews)))
        if suggested_factor > ease_cap:
            suggested_factor = ease_cap
        ease_floor = max(min_ease, (starting_ease -
                                    (leash * number_of_reviews)))
        if suggested_factor < ease_floor:
            suggested_factor = ease_floor

        return suggested_factor

    def adjust_ease(self, card=None):
        if card is None:
            card = mw.reviewer.card
            deck_options_mode = False
        else:
            deck_options_mode = True
        ease_list = self.get_ease_list(card)
        last_factor = None
        if len(ease_list) > 0:
            last_factor = ease_list[-1]
        calculated_ease = self.calculate_ease(card)
        self.factor = calculated_ease

        # tooltip messaging
        if stats_enabled and not deck_options_mode:
            review_list = self.get_reviews(card)
            success_rate = self.find_success_rate(card)
            '''
            if success_rate > 0.99:
                success_rate = 0.99  # ln(1) = 0; avoid divide by zero error
            if success_rate < 0.01:
                success_rate = 0.01
            delta_ratio = math.log(target_ratio) / math.log(success_rate)
            average_ease = self.find_average_ease(card)'''

            avg_ease = self.find_average_ease(card)
            ease_list = self.get_ease_list(card)

            printable_review_list = ""
            if len(review_list) > 0:
                abbr_review_list = review_list[-10:]
                if len(review_list) > 10:
                    printable_review_list += '..., '
                printable_review_list += str(abbr_review_list[0])
                for review_result in abbr_review_list[1:]:
                    printable_review_list += ", " + str(review_result)

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
            msg += f"MAvg factor: {round(avg_ease, 2)}<br>"
            msg += f"Suggested factor: {calculated_ease}<br>"
            msg += f"Review list: {printable_review_list}<br>"
            tooltip_args = {'msg': msg, 'period': stats_duration,
                            'x_offset': 12, 'y_offset': 240}

            if not anki213:
                msg = f"card ID: {card.id}<br>"
                msg += (f"Card Queue (Type): "
                        f"{queue_types[card.queue]}"
                        f" ({card_types[card.type]})<br>")
                msg += f"MAvg success rate: {round(success_rate, 4)}<br>"
                msg += (f"MAvg factor (Last factor): {round(avg_ease, 2)}  "
                        f"({last_factor})<br>")
                msg += f"Suggested factor: {calculated_ease}<br>"
                msg += f"Review list: {printable_review_list}<br>"
                tooltip_args = {'msg': msg, 'period': stats_duration}

            tooltip(**tooltip_args)


alg = EaseAlgorithm()


def announce(announcement):
    msg = QMessageBox(mw)
    msg.setStandardButtons(QMessageBox.Ok)
    msg.setText(_(announcement))
    msg.exec_()


def on_answer(ease_tuple, reviewer=reviewer.Reviewer, card=None):
    last_ease = ease_tuple[1]
    alg.set_last_ease(last_ease)
    alg.adjust_ease()
    card.factor = alg.factor
    return ease_tuple


gui_hooks.reviewer_will_answer_card.append(on_answer)


def adjust_ease_factors(deck_id):
    deck_name = mw.col.decks.nameOrNone(deck_id)
    card_ids = mw.col.find_cards(f'deck:"{deck_name}"')
    for card_id in card_ids:
        card = mw.col.getCard(card_id)
        alg.adjust_ease(card)
        card.factor = alg.factor
        card.flush()
    announce("Ease adjustment complete!")


def export_ease_factors(deck_id):
    '''For some deck `deck_id`, prompts to save a file containing a dictionary
    that links card id keys to ease factors.
    '''
    deck_name = mw.col.decks.nameOrNone(deck_id)
    if deck_name is None:
        return

    # open file picker to store factors
    dt_now_str = str(datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
    suggested_filename = "ease_factors_" + str(deck_id) + dt_now_str
    export_file = getSaveFile(mw, _("Export"), "export",
                              key="",
                              ext="",
                              fname=suggested_filename)
    if not export_file:
        return

    factors = {}
    card_ids = mw.col.find_cards(f'deck:"{deck_name}"')
    for card_id in card_ids:
        card = mw.col.getCard(card_id)
        factors[card_id] = card.factor
    with open(export_file, 'w') as export_file_object:
        export_file_object.write(str(factors))
    announce("Export complete!")


def import_ease_factors(deck_id, factors=None):
    '''For deck `deck_id` and `factors`--a dictionary linking card id keys to
    ease factors--set the ease factors of the cards in the deck to the ease
    factors provided in `factors`.

    If factors is not provided, prompt user to load a file of ease values,
    such as one saved by `export_ease_factors()`.
    '''
    deck_name = mw.col.decks.nameOrNone(deck_id)
    if deck_name is None:
        print("Deck name not found on import_ease_factors, exiting...")
        return

    if factors is None:
        # open file picker to load factors
        import_file = getFile(mw, _("Import"), None,
                              key="import")
        with open(import_file, 'r') as import_file_object:
            factors = literal_eval(import_file_object.read())

    card_ids = mw.col.find_cards(f'deck:"{deck_name}"')
    for card_id in card_ids:
        card = mw.col.getCard(card_id)
        card.factor = factors.get(card_id, card.factor)
        card.flush()
    announce("Import complete!")


def add_deck_options(menu, deck_id):
    export_action = menu.addAction("Export Ease Factors")
    export_action.triggered.connect(lambda _,
                                    did=deck_id: export_ease_factors(did))
    import_action = menu.addAction("Import Ease Factors")
    import_action.triggered.connect(lambda _,
                                    did=deck_id: import_ease_factors(did))
    adjust_action = menu.addAction("Adjust Ease Factors To Performance")
    adjust_action.triggered.connect(lambda _,
                                    did=deck_id: adjust_ease_factors(did))


gui_hooks.deck_browser_will_show_options_menu.append(add_deck_options)
