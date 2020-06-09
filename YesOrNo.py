# -*- mode: Python ; coding: utf-8 -*-
# Good / Again (Yes No) 2 buttons only
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# No support. Use it AS IS on your own risk.

# No click bug fixed. Still having layout issues causing scrollbars to appear.
from __future__ import division
from __future__ import unicode_literals
# import os

from aqt import mw
from aqt.reviewer import Reviewer
from aqt.utils import showInfo
from anki.hooks import wrap, addHook, runHook
from aqt.qt import *
import json

debugMsg = False
rightLabel = "Pass"
wrongLabel = "Fail"
showAnswerText = "Show"

# Anki uses a single digit to track which button has been clicked.
RETEST = 5

# default map:
# 2 buttons:    1 (again) 2 (good) 3 (none) 4 (none)
# 3b:           1 (again) 2 (good) 3 (easy) 4 (none)
# 4b:           1 (again) 2 (hard) 3 (good) 4 (easy)
# (also 0 (None) in each row)

# remap:
# 2 buttons:    1 (again) 2 (good) 2 (good) 2 (good)
# 3b:           1 (again) 2 (good) 2 (good) 2 (good)
# 4b:           1 (again) 3 (good) 3 (good) 3 (good)

remap = {2:  [None, 1, 2, 2, 2],
         3:  [None, 1, 2, 2, 2],
         4:  [None, 1, 3, 3, 3]}

# -- width in pixels
# --    Show Answer button, triple, double and single answers buttons
# all 99s - giant fail button
# all 1s - giant fail and good button
# all 50s - normalish, still bug
# beams2 is all that's used. weird.
BEAMS4 = '50%'
BEAMS3 = '50%'
BEAMS2 = '50%'
BEAMS1 = '50%'

black = '#000'
red = '#c33'
# green = '#3c3'
green = '#080'

BUTTON_LABEL = ['<span style="color:' + black + ';">' + wrongLabel + '</span>',
                '<span style="color:' + green + ';">' + rightLabel + '</span>']


# Replace _answerButtonList method
def answerButtonList(self):
    abl = ((
        1, '<style>button small ' +
        '{ color:#999; font-weight:400; padding-left:.35em; ' +
        'font-size: small; }</style><span>' + BUTTON_LABEL[0] + '</span>',
        BEAMS2),)
    cnt = self.mw.col.sched.answerButtons(self.card)
    if cnt == 2 or cnt == 3:  # ease 2 = good if 2 or 3 buttons
        return abl + ((2, '<span>' + BUTTON_LABEL[1] + '</span>', BEAMS2),)
    elif cnt == 4:  # b/c we want ease 3 = good in this version
        return abl + ((3, '<span>' + BUTTON_LABEL[1] + '</span>', BEAMS2),)
    # the comma at the end is mandatory, a subtle bug occurs without it


def AKR_answerCard(self, ease):
    count = mw.col.sched.answerButtons(mw.reviewer.card)  # Get button count
    if count < 4:
        if debugMsg:
            showInfo("Review Type: (Re)Learning")
    else:
        if debugMsg:
            showInfo("Review Type: Review")
    if debugMsg:
        showInfo("Selected: %s" % ease)
    try:
        ease = remap[count][ease]
        if debugMsg:
            showInfo("Remapped to: %s" % ease)
    except (KeyError, IndexError):
        pass
    __oldFunc(self, ease)


__oldFunc = Reviewer._answerCard
Reviewer._answerCard = AKR_answerCard


def myAnswerButtons(self, _old) -> str:
    times = []
    default = self._defaultEase()

    def but(i, label, beam):
        if i == default:
            extra = 'id=defease'
        else:
            extra = ''
        due = self._buttonTime(i)
        # ADDED width:beam
        # outval = f'''<td align=center">{due}
        outval = f'''<td align=center style="width:{beam};">{due}
                     <button {extra} title="Shortcut key: {i}" data-ease="{i}"
                     onclick='pycmd("ease{i}");'>{label}</button></td>'''
        return outval

    buf = '<table cellpading=0 cellspacing=0><tr>'  # REMOVED <center>
    for ease, lbl, beams in answerButtonList(self):
        buf += but(ease, lbl, beams)
    buf += '</tr></table>'
    script = """
    <style>table tr td button { width: 100%; } </style>
<script>$(function () { $('#defease').focus(); });</script>"""
    return buf + script


Reviewer._answerButtons =\
    wrap(Reviewer._answerButtons, myAnswerButtons, 'around')
