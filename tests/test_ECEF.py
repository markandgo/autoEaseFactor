# from anki_testing import anki_running
import pytest

# test examples
##
## https://github.com/JDongian/python-jamo/blob/master/tests/test_jamo.py
## https://github.com/krassowski/anki_testing/blob/master/README.md
## https://github.com/krassowski/Anki-Night-Mode/blob/master/tests/
## https://github.com/AwesomeTTS/awesometts-anki-addon/blob/master/tests
## DB Structure https://github.com/ankidroid/Anki-Android/wiki/Database-Structure

# test for divide by zero in the delta ratio methods

test_reviews = [[0, 0, 0, 0, 0, 3, 3, 3, 3, 3],
                [3, 3, 3, 3, 3, 0, 0, 0, 0, 0],
                [0, 3, 0, 3, 0, 3, 0, 3, 0, 3],
                [3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]


## generate fake revlog. sigh.
##  edit the below snippet for sensible reviews with various timings.
#  id cid usn ease ivl lastIvl factor time type
revlog =   [[1100000000000, 1000000000000, 109, 1, -129600, 0, 0, 12657, 0],
            [1100000011111, 1000000000000, 109, 1, -129600, 0, 0, 3221, 0],
            [1100000022222, 1000000000000, 109, 1, -900, -900, 0, 21684, 0],
            [1100000033333, 1000000000000, 109, 1, -129600, -900, 0, 10553, 0],
            [1100000044444, 1000000000000, 109, 1, -900, -900, 0, 7867, 0],
            [1100000055555, 1000000000000, 109, 1, -129600, -900, 0, 8539, 0],
            [1100000066666, 1000000000000, 109, 1, -900, -900, 0, 11683, 0],
            [1100000077777, 1000000000000, 109, 1, -129600, -900, 0, 2890, 0],
            [1100000088888, 1000000000000, 109, 1, -900, -900, 0, 45392, 0],
            [1100000099999, 1000000000000, 109, 1, -900, -900, 0, 46756, 0],
            [1100000100000, 1000000000000, 109, 1, -129600, -900, 0, 32396, 0],
            [1100000111111, 1000000000000, 109, 1, -129600, -900, 0, 59910, 0],
            [1100000122222, 1000000000000, 109, 1, -129600, -900, 0, 20371, 0],
            [1100000133333, 1000000000000, 109, 1, -129600, -900, 0, 9635, 0],
            [1100000144444, 1000000000000, 109, 1, -900, -900, 0, 61254, 0],
            [1100000155555, 1000000000000, 109, 1, -129600, -900, 0, 9768, 0],
            [1100000166666, 1000000000000, 109, 1, -129600, -900, 0, 11107, 0],
            [1100000177777, 1000000000000, 109, 1, -900, -900, 0, 6724, 0],
            [1100000188888, 1000000000000, 109, 1, -129600, -900, 0, 37900, 0],
            [1100000199999, 1000000000000, 109, 1, -129600, -900, 0, 6848, 0],
            [1100000200000, 1000000000000, 109, 1, -900, -900, 0, 40175, 0]]

mv_avg_test_lists = {(1, 1, 1, 0, 0, 0):0.3809,
                     (0, 0, 0, 1, 1, 1):0.6191,
                     (1, 0, 1, 0, 1, 0):0.4590,
                     (0, 1, 0, 1, 0, 1):0.5410,
                     (1, 1, 1, 0, 0, 0):0.3405,
                     (0, 0, 0, 1, 1, 1):0.6953,
                     (1, 0, 1, 0, 1, 0):0.3672,
                     (0, 1, 0, 1, 0, 1):0.6328,
                     (2500, 3100, 3500, 3700, 1444, 638, 1800):2166.9092,
                     (2500, 3100, 3500, 3700, 3900, 4500, 4700):3900.0273}

def test_ECEF():
    print('__file__={0:<35} | __name__={1:<20} | __package__={2:<20}'.format(__file__,__name__,str(__package__)))
    #    with anki_running() as anki_app:
    from experimentalCardEaseFactor import EaseAlgorithm
    print(dir(experimentalCardEaseFactor))
    alg = EaseAlgorithm
    # import YesOrNo


    def get_reviews(self, card_id):
        return [rev[3] for rev in revlog if rev[1] == card_id]
    alg.get_reviews = get_reviews

    def get_ease_list(self, card_id):
        outval = []
        for rev in revlog:
            if rev[4] > 0 and rev[5] > 0 and rev[1] == card_id:
                outval.append(1000*rev[4]/rev[5])
        return outval
    alg.get_ease_list = get_ease_list

    def test_calculate_moving_average():
        for l in mv_avg_test_lists.keys():
            assert (round(alg.calculate_moving_average(l), 2) ==
                    round(mv_avg_test_lists[l], 2))
        assert True

    def test_find_success_rate():
        assert True

    def test_find_average_ease():
        assert True


    def test_calculate_ease():
        assert True

if __name__ == "__main__":
    test_ECEF()
