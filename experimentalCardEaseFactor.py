# inspired by https://eshapard.github.io/

from __future__ import annotations

import math
import random
import time
from heapq import heappush

from anki.decks import DeckManager

from anki import version
from anki.hooks import addHook
from aqt import mw
from aqt.utils import tooltip

anki21 = version.startswith("2.1.")

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

    def get_reviews(self, card_id):
        return mw.col.db.list(("select ease from revlog where cid = ?"),
                              card_id)

    def get_ease_list(self, card_id):
        return mw.col.db.list("select (1000*ivl/lastIvl) from revlog where "
                              "cid = ? and lastIvl > 0 and ivl > 0",
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
            row_limit = max(20, len(review_list)//3)
            for idx, i in enumerate(review_list[:-1]):
                if idx % row_limit == 0:
                    printable_review_list += '<br>'
                printable_review_list += str(i) + ', '
            if len(review_list) > 0:
                printable_review_list += str(review_list[-1])

            msg = f"card ID: {card_id}<br>"
                   # f"average ease: {round(avg_ease, 4)}<br>"
                   # f"ease_list: {ease_list}<br>"
            msg += f"success rate (weighted): {round(success_rate, 4)}<br>"
            msg += f"current ease factor: {round(mw.reviewer.card.factor)}<br>"
            msg += f"suggested ease factor: {calculated_ease}<br>"
            msg += f"review list: {printable_review_list}<br>"

            # extended_msg = ("delta_ratio: {} average_ease: {}<br>"
            #                 "".format(delta_ratio, average_ease))
            # msg += extended_msg
            # debug_msg = ""
            # msg = debug_msg + msg
            if self.last_tooltip_msg is not None:
                new_msg = (self.last_tooltip_msg
                           + "<br><br>  *   *   *   <br><br>"
                           + msg)
                tooltip_args = {'msg': new_msg, 'period': stats_duration,
                                'x_offset': 12, 'y_offset': 350}
                tooltip(**tooltip_args)
            else:
                tooltip_args = {'msg': msg, 'period': stats_duration,
                                'x_offset': 12, 'y_offset': 240}
                tooltip(**tooltip_args)
            self.last_tooltip_msg = msg


# OVERRIDING SCHEDULER V2 FUNCTIONS EASE CALCULATIONS

def rescheduleLapse_V2(self, card):
    conf = self._lapseConf(card)

    card.lapses += 1
    # card.factor = max(1300, card.factor-200)
    card.factor = alg.factor
    # showInfo("New Card Ease:%s" % card.factor)
    suspended = self._checkLeech(card, conf) and card.queue == -1

    if conf['delays'] and not suspended:
        card.type = 3
        delay = self._moveToFirstStep(card, conf)
    else:
        # no relearning steps
        self._updateRevIvlOnFail(card, conf)
        self._rescheduleAsRev(card, conf, early=False)
        # need to reset the queue after rescheduling
        if suspended:
            card.queue = -1
        delay = 0

    return delay


def rescheduleRev_V2(self, card, ease, early):
    # update interval
    card.lastIvl = card.ivl
    if early:
        self._updateEarlyRevIvl(card, ease)
    else:
        self._updateRevIvl(card, ease)

    # then the rest
    # card.factor = max(1300, card.factor+[-150, 0, 150][ease-2])
    card.factor = alg.factor
    # showInfo("New Card Ease: %s" % card.factor)
    card.due = self.today + card.ivl

    # card leaves filtered deck
    self._removeFromFiltered(card)


# SCHEDULER V1 FUNCTIONS

def rescheduleLapse_V1(self, card):
    conf = self._lapseConf(card)
    card.lastIvl = card.ivl
    if self._resched(card):
        card.lapses += 1
        card.ivl = self._nextLapseIvl(card, conf)
        # card.factor = max(1300, card.factor-200)
        card.factor = alg.factor
        # showInfo("New Card Ease: %s" % card.factor)
        card.due = self.today + card.ivl
        # if it's a filtered deck, update odue as well
        if card.odid:
            card.odue = card.due
    # if suspended as a leech, nothing to do
    delay = 0
    if self._checkLeech(card, conf) and card.queue == -1:
        return delay
    # if no relearning steps, nothing to do
    if not conf['delays']:
        return delay
    # record rev due date for later
    if not card.odue:
        card.odue = card.due
    delay = self._delayForGrade(conf, 0)
    card.due = int(delay + time.time())
    card.left = self._startingLeft(card)
    # queue 1
    if card.due < self.dayCutoff:
        self.lrnCount += card.left // 1000
        card.queue = 1
        heappush(self._lrnQueue, (card.due, card.id))
    else:
        # day learn queue
        ahead = ((card.due - self.dayCutoff) // 86400) + 1
        card.due = self.today + ahead
        card.queue = 3
    return delay


def rescheduleRev_V1(self, card, ease):
    # update interval
    card.lastIvl = card.ivl
    if self._resched(card):
        self._updateRevIvl(card, ease)
        # card.factor = max(1300, card.factor+[-150, 0, 150][ease-2])
        card.factor = alg.factor
        # showInfo("New Card Ease: %s" % card.factor)
        card.due = self.today + card.ivl
    else:
        card.due = card.odue
    if card.odid:
        card.did = card.odid
        card.odid = 0
        card.odue = 0


from anki.sched import Scheduler as V1

V1._rescheduleLapse = rescheduleLapse_V1
V1._rescheduleRev = rescheduleRev_V1

if anki21:
    from anki.schedv2 import Scheduler as V2

    V2._rescheduleLapse = rescheduleLapse_V2
    V2._rescheduleRev = rescheduleRev_V2


alg = EaseAlgorithm()
addHook('showQuestion', alg.adjust_ease)

# Patching tooltip() to allow x and y offsets
# TODO - clean up imports
# NOTE - the change in arguments to tooltip() was accepted by the Anki devs,
# so everything below this can be removed as soon as that goes live
import os
import re
import subprocess
import sys
from typing import TYPE_CHECKING, Any, Optional, Union

import anki
import aqt
from anki.lang import _
from anki.rsbackend import TR  # pylint: disable=unused-import
from anki.utils import (invalidFilename, isMac, isWin, noBundledLibs,
                        versionWithBuild)
from aqt.qt import *
from aqt.theme import theme_manager

if TYPE_CHECKING:
    from anki.rsbackend import TRValue

_activeTooltips = []
_tooltipTimer: Optional[QTimer] = None
_tooltipLabel: Optional[QLabel] = None


def tooltip(msg, period=3000, parent=None, x_offset=0, y_offset=100):
    global _tooltipTimer, _tooltipLabel

    class CustomLabel(QLabel):
        silentlyClose = True

        def mousePressEvent(self, evt):
            evt.accept()
            self.hide()

    closeTooltip()
    aw = parent or aqt.mw.app.activeWindow() or aqt.mw

    # prevent tooltip values outside of main window
    if y_offset > aw.size().height():
        y_offset = aw.size().height()
    if y_offset < 100:
        y_offset = 100
    if x_offset > mw.size().width() - 390:
        x_offset = mw.size().width() - 390
    if x_offset < 0:
        x_offset = 0

    lab = CustomLabel(
        """\
<table cellpadding=10>
<tr>
<td>%s</td>
</tr>
</table>"""
        % msg,
        aw,
    )
    lab.setFrameStyle(QFrame.Panel)
    lab.setLineWidth(2)
    lab.setWindowFlags(Qt.ToolTip)
    if not theme_manager.night_mode:
        p = QPalette()
        p.setColor(QPalette.Window, QColor("#feffc4"))
        p.setColor(QPalette.WindowText, QColor("#000000"))
        lab.setPalette(p)
    lab.move(aw.mapToGlobal(QPoint(0+x_offset, aw.height() - y_offset)))
    lab.show()
    _tooltipTimer = aqt.mw.progress.timer(
        period, closeTooltip, False, requiresCollection=False
    )
    _tooltipLabel = lab


def closeTooltip():
    global _tooltipLabel, _tooltipTimer
    if _tooltipLabel:
        try:
            _tooltipLabel.deleteLater()
        except:
            # already deleted as parent window closed
            pass
        _tooltipLabel = None
    if _tooltipTimer:
        _tooltipTimer.stop()
        _tooltipTimer = None
