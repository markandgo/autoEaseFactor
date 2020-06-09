# -*- mode: Python ; coding: utf-8 -*-
# Good / Again (Yes No) 2 buttons only
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# No support. Use it AS IS on your own risk.

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

black = '#000'
red = '#c33'
green = '#080'

BUTTON_LABEL = ['<span style="color:' + black + ';">' + wrongLabel + '</span>',
                '<span style="color:' + green + ';">' + rightLabel + '</span>']


# Replace _answerButtonList method to reduce buttons to Pass/Fail always
def answerButtonList(self):
    # https://git.io/JfykM
    abl = ((1, BUTTON_LABEL[0]),)
    cnt = self.mw.col.sched.answerButtons(self.card)
    if cnt == 2 or cnt == 3:
        return abl + ((2, BUTTON_LABEL[1]),)
    else:
        return abl + ((3, BUTTON_LABEL[1]),)


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

    def but(i, label):
        if i == default:
            extra = 'id=defease'
        else:
            extra = ''
        due = self._buttonTime(i)
        outval = f'''<td align=center>{due}
                     <button {extra} title="Shortcut key: {i}" data-ease="{i}"
                     onclick='pycmd("ease{i}");'>{label}</button></td>'''
        return outval

    buf = "<center><table cellpading=0 cellspacing=0><tr>"
    for ease, lbl in answerButtonList(self):
        buf += but(ease, lbl)
    buf += '</tr></table>'
    script = """<script>$(function () { $('#defease').focus(); });</script>"""
    return buf + script


Reviewer._answerButtons =\
    wrap(Reviewer._answerButtons, myAnswerButtons, 'around')
