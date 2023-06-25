from typing import List, Tuple, Dict, Optional, Any, Callable
from pathlib import Path
from datetime import datetime

from anki.collection import Collection
from anki.cards import Card
from anki.rsbackend import NotFoundError

from aqt import mw
from aqt.gui_hooks import sync_will_start, sync_did_finish
from aqt.utils import tooltip

from . import ease_calculator
from . import autoEaseFactor

def display_sync_info(count: int):
    MSG = (
        f"Adjusted ease factor to {count} card!"
        if count == 1
        else f"Adjusted ease factor to {count} cards!"
    )
    tooltip(MSG)

def maybe_to_card(revcid: int) -> Optional[Card]:
    try:
        return Card(mw.col, revcid)
    except AssertionError:
        # card does not exist in this db yet, probably created on another platform
        return None
    except NotFoundError:
        # card was reviewed remotely, but deleted locally
        return None

def check(revcid: int, count: int) -> List[int]:
    if card := maybe_to_card(revcid):
        # if a card was reviewed multiple times
        # we need to skip the most recent reviews for consideration
        autoEaseFactor.suggested_factor(card)
        return 1
    return 0


#For each card, count the number of reviews done since last time
def make_cid_counter(reviewed_cids: List[int]) -> Dict[int, int]:
    cid_counter = {}

    for cid in reviewed_cids:
        cid_counter[cid] = cid_counter[cid] + 1 if cid in cid_counter else 1

    return cid_counter


def flat_map(f: Callable[[Any], List[Any]], xs: List[Any]) -> List[Any]:
    ys = []
    for x in xs:
        ys.extend(f(x))
    return ys

def check_cids(reviewed_cids: List[int]) -> int:
    cid_counter = make_cid_counter(reviewed_cids)
    count = 0
    for cid_and_review_count in cid_counter.items():
        count += check(*cid_and_review_count)
    return count

def create_comparelog(oldids: List[int]) -> None:
    path = mw.pm.collectionPath()

    # flatten ids
    oldids.extend(
        [id for sublist in mw.col.db.execute("SELECT id FROM revlog") for id in sublist]
    )


def after_sync(oldids: List[int]) -> None:
    if len(oldids) == 0:
        return

    oldidstring = ",".join([str(oldid) for oldid in oldids])

    # exclude entries where ivl == lastIvl: they indicate a dynamic deck without rescheduling
    reviewed_cids = [
        cid
        for sublist in mw.col.db.execute(
            f"SELECT cid FROM revlog WHERE id NOT IN ({oldidstring}) and ivl != lastIvl"
        )
        for cid in sublist
    ]

    count = check_cids(reviewed_cids)
    display_sync_info(count)

    oldids.clear()


def init_sync_hook():
    oldids = []

    #create log of past reviews before syncing
    sync_will_start.append(lambda: create_comparelog(oldids))
    
    sync_did_finish.append(lambda: after_sync(oldids))
