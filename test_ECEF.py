from anki_testing import anki_running
import pytest

# test examples
##
## https://github.com/JDongian/python-jamo/blob/master/tests/test_jamo.py
## https://github.com/krassowski/anki_testing/blob/master/README.md
## https://github.com/krassowski/Anki-Night-Mode/blob/master/tests/
## https://github.com/AwesomeTTS/awesometts-anki-addon/blob/master/tests

test_reviews = [[0, 0, 0, 0, 0, 3, 3, 3, 3, 3],
                [3, 3, 3, 3, 3, 0, 0, 0, 0, 0],
                [0, 3, 0, 3, 0, 3, 0, 3, 0, 3],
                [3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

## generate fake revlog. sigh.
##  edit the below snippet for sensible reviews with various timings.
revlog =   [[1590761106130, 1589630888414, 109, 2, -129600, -900, 0, 12657, 0],
            [1590761109388, 1589630888418, 109, 2, -129600, -900, 0, 3221, 0],
            [1590761131077, 1589220257070, 109, 1, -900, -900, 0, 21684, 0],
            [1590761141638, 1589220257078, 109, 2, -129600, -900, 0, 10553, 0],
            [1590761149510, 1589220257079, 109, 1, -900, -900, 0, 7867, 0],
            [1590761158055, 1589220257081, 109, 2, -129600, -900, 0, 8539, 0],
            [1590761169743, 1589220257088, 109, 1, -900, -900, 0, 11683, 0],
            [1590761172639, 1589220257090, 109, 2, -129600, -900, 0, 2890, 0],
            [1590761829087, 1590368217706, 109, 1, -900, -900, 0, 45392, 0],
            [1590761875850, 1590368217727, 109, 1, -900, -900, 0, 46756, 0],
            [1590761908252, 1590368217708, 109, 2, -129600, -900, 0, 32396, 0],
            [1590761968168, 1590368217687, 109, 2, -129600, -900, 0, 59910, 0],
            [1590761988545, 1590368217717, 109, 2, -129600, -900, 0, 20371, 0],
            [1590761998187, 1590368217700, 109, 2, -129600, -900, 0, 9635, 0],
            [1590762059447, 1590368217685, 109, 1, -900, -900, 0, 61254, 0],
            [1590762069222, 1589220257070, 109, 2, -129600, -900, 0, 9768, 0],
            [1590762080336, 1589220257079, 109, 2, -129600, -900, 0, 11107, 0],
            [1590762087097, 1589220257088, 109, 1, -900, -900, 0, 6724, 0],
            [1590762125003, 1590368217723, 109, 2, -129600, -900, 0, 37900, 0],
            [1590762267878, 1590368217725, 109, 2, -129600, -900, 0, 6848, 0],
            [1590762308072, 1590368217697, 109, 1, -900, -900, 0, 40175, 0],
            [1590762326490, 1590368217712, 109, 2, -129600, -900, 0, 18411, 0]]

'''get this to work:
mw.col.db.list("select (1000*ivl/lastIvl) from revlog where cid = ? "
               "and lastIvl > 0 and ivl > 0", card_id)
(does anki_tests have a way to load a fake revlog or do i overwrite the db.list
method?)
               '''


'''
-- revlog schema
    id              integer primary key,
       -- epoch-seconds timestamp of when you did the review
    cid             integer not null,
       -- cards.id
    usn             integer not null,
       -- all my reviews have -1
    ease            integer not null,
       -- which button you pushed to score your recall. 1(wrong), 2(hard), 3(ok), 4(easy)
    ivl             integer not null,
       -- interval (negative for seconds if under 1 day)
    lastIvl         integer not null, (0 until out of learning)
       -- last interval
    factor          integer not null,
      -- factor
    time            integer not null,
       -- how many milliseconds your review took, up to 60000 (60s)
    type            integer not null
);
'''

def test_ECEF():
    with anki_running() as anki_app:
        import experimentalCardEaseFactor
        import YesOrNo

        for reviews in test_reviews:
            find_success_rate()
            assert True

        def test_calculate_moving_average():
            assert True

        def test_find_success_rate():
            assert True

        def test_find_average_ease():
            assert True


        def test_calculate_ease():
            assert True
