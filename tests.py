import pytest

# TODO: replace with https://github.com/krassowski/anki_testing


target_ratio = .85
moving_average_weight = .2
starting_ease = 2500

# Limit how aggressive the algorithm is, especially early on
# These were left out of the config intentionally - adjust at your own risk!
min_ease = 100
# over 7k the time savings are minimal and the risk of miscalculation is higher
max_ease = 7000
# let ease change by leash * card views, so leash gets longer quickly
# prevents wild swings from early reviews
leash = 350


def calculate_moving_average(l):
    assert len(l) > 0
    result = l[0]
    for i in l[1:]:
        result = (result * (1 - moving_average_weight))
        result += i * moving_average_weight
    return result


def find_average_ease(ease_list):
    average_ease = 0
    if not ease_list:
        average_ease = starting_ease
    else:
        average_ease = self.calculate_moving_average(ease_list)
    #   ~ # Replacement on true intervals failed testing. Revisit, implement.
    #   ~ # time of each review in milliseconds
    #   ~ review_times = mw.col.db.list("select id from revlog where cid = ? "
                                  #   ~ "order by id", card_id)
    #   ~ if not review_times or len(review_times) < 3:
        #   ~ average_ease = starting_ease
        #   ~ real_intervals = [t1 - t0 for t0, t1 in zip(review_times[:-1],
                                                    #   ~ review_times[1:])]
        #   ~ ratios = [(i1 / i0) * 1000 for i0, i1 in zip(real_intervals[:-1],
                                                     #   ~ real_intervals[1:])]
        #   ~ average_ease = self.calculate_moving_average(ratios)
    return average_ease


def calculate_ease(review_list, ease_list):
    success_rate = self.find_success_rate(review_list)
    # Ebbinghaus formula
    if success_rate > 0.99:
        success_rate = 0.99  # ln(1) = 0; avoid divide by zero error
    if success_rate < 0.01:
        success_rate = 0.01
    delta_ratio = math.log(target_ratio) / math.log(success_rate)
    average_ease = self.find_average_ease(ease_list)
    suggested_factor = int(round(average_ease * delta_ratio))

    # anchor this to starting_ease initially
    number_of_reviews = len(ease_list)
    ease_cap = min(max_ease, (starting_ease + leash * number_of_reviews))
    if suggested_factor > ease_cap:
        suggested_factor = ease_cap
    ease_floor = max(min_ease, (starting_ease - leash * number_of_reviews))
    if suggested_factor < ease_floor:
        suggested_factor = ease_floor

    return suggested_factor


def test_calculate_moving_average():
    # a = []
    b = [1, 2, 3, 4, 5]
    c = [5, 5, 5, 5, 5]
    d = [5, 4, 3, 2, 1]
    e = [7]
    assert calculate_moving_average =

    def find_success_rate(review_list):
        if not review_list or len(review_list) < 1:
            success_rate = target_ratio  # no reviews: assume we're on target
        else:
            success_list = [int(i > 1) for i in review_list]
            success_rate = self.calculate_moving_average(success_list)
        return success_rate


def test_find_average_ease():
    pass


def test_calculate_ease():
    pass
