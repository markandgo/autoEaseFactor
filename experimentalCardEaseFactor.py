# inspired by https://eshapard.github.io/
#
# KNOWN BUGS / TODO:
# - Undo seems to mess up scheduling. Monkey patching might work, not sure if
# there's a better option.
# Long tooltips fall off the screen, so I've both monkey patched tooltip() here
#   and also submitted a PR to anki to let tooltip() take x and y offsets
# https://gist.github.com/cordone/38317befecfbda6e12d4f04df4555065
# - Clicking on buttons no longer works, only keyboard shortcuts.
# - if reviews are empty (because learning) maybe assume 50%?
from __future__ import annotations


from anki.hooks import addHook
from aqt import mw
from aqt.utils import tooltip
import math

target_ratio = 0.85
moving_average_weight = 0.2
last_tooltip_msg = None
show_stats = True

def calculate_moving_average(l):
    result = l[0]
    for i in l[1:]:
        result = (result * (1 - moving_average_weight))
        result += i * moving_average_weight
    return result


def find_success_rate(card_id):
    review_list = mw.col.db.list(("select ease from revlog where cid = ?"),
                                 card_id)
    if not review_list:
        return 0

    success_list = [int(i > 1) for i in review_list]
    success_rate = calculate_moving_average(success_list)
    return success_rate


def find_average_ease(card_id):
    average_ease = 0
    ease_list = mw.col.db.list("select (1000*ivl/lastIvl) from revlog"
                               " where cid = ? and lastIvl > 0 and ivl > 0",
                               card_id)
    if not ease_list or ease_list is None:
        average_ease = 2500
    else:
        average_ease = calculate_moving_average(ease_list)
    return average_ease


def calculate_ease(card_id):
    success_rate = find_success_rate(card_id)
    # Ebbinghaus formula
    if success_rate > 0.99:
        success_rate = 0.99  # ln(1) = 0; avoid divide by zero error
    if success_rate < 0.01:
        success_rate = 0.01
    delta_ratio = math.log(target_ratio) / math.log(success_rate)
    average_ease = find_average_ease(card_id)
    suggested_factor = int(round(average_ease * delta_ratio))

    # anchor this to 2500 starting out
    number_of_reviews = len(mw.col.db.list(("select ease from revlog where"
                                            " cid = ?"), card_id))
    ease_cap = min(7000, (2500 + 350 * number_of_reviews))
    if suggested_factor > ease_cap:
        suggested_factor = ease_cap
    ease_floor = max(100, (2500 - 350 * number_of_reviews))
    if suggested_factor < ease_floor:
        suggested_factor = ease_floor

    return suggested_factor


def adjust_ease():
    global last_tooltip_msg
    card_id = mw.reviewer.card.id
    calculated_ease = calculate_ease(card_id)

    mw.reviewer.card.factor = calculated_ease

    # tooltip messaging
    if show_stats:
        review_list = mw.col.db.list(("select ease from revlog where cid = ?"),
                                     card_id)

        success_rate = find_success_rate(card_id)

        msg = ("cardID: {}<br/> sRate: {} curFactor: {} sugFactor: {}<br> rlist: "
               "{}<br>".format(card_id, round(success_rate, 4),
                               round(mw.reviewer.card.factor), calculated_ease,
                               review_list))
        if last_tooltip_msg is not None:
            new_msg = (last_tooltip_msg + "<br><br>  *   *   *   <br><br>" + msg)
            tooltip_args = {'msg': new_msg, 'period': 9000, 'x_offset': 12,
                            'y_offset': 250}
            tooltip(**tooltip_args)
        else:
            tooltip_args = {'msg': msg, 'period': 9000, 'x_offset': 12,
                            'y_offset': 140}
            tooltip(**tooltip_args)
        last_tooltip_msg = msg


addHook('showQuestion', adjust_ease)

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
