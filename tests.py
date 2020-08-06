import math
import random
import statistics

# Adjust "ideal_ease_to_target" to simulate a card of a certain difficulty
# the new algorithm tends to stay much closer to the target ratio
# for cards of a difficulty anywhere between 1000 and 3000.
# You're often doing the same number of reps, but you are succeeding on them
# more often, so it's less discouraging, and the time it takes to do the reps
# is shorter.

# On a typical card you're only going to see it 5-15 times per year, so there
# really isn't that much room for optimization. Tweaking these numbers barely
# seems to matter, so try not to worry about them too much.

ideal_ease_to_target = 2800
lapse_new_ivl_percent = 4

target_ratio = 0.85
moving_average_weight = 0.2


# Limit how aggressive the algorithm is
min_ease = 1000
# over 7k the time savings are minimal and the risk of miscalculation is higher
max_ease = 5000
# let ease change by leash * card views, so leash gets longer quickly
# prevents wild swings from early reviews
leash = 100

starting_ease = 2500


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


def find_success_rate(reviews=None):
    if not reviews or len(reviews) < 1:
        success_rate = target_ratio  # no reviews: assume we're on target
    else:
        success_list = [int(i > 0) for i in reviews]
        success_rate = calculate_moving_average(success_list)
    return success_rate


def calculate_ease(reviews=None, ease_list=None):
    success_rate = find_success_rate(reviews)

    # Ebbinghaus formula
    if success_rate > 0.99:
        success_rate = 0.99  # ln(1) = 0; avoid divide by zero error
    if success_rate < 0.01:
        success_rate = 0.01
    delta_ratio = math.log(target_ratio) / math.log(success_rate)
    average_ease = calculate_moving_average(ease_list)
    suggested_factor = int(round(average_ease * delta_ratio))

    # anchor this to starting_ease initially
    number_of_reviews = len(reviews)
    ease_cap = min(max_ease, (starting_ease + (leash * number_of_reviews)))
    if suggested_factor > ease_cap:
        suggested_factor = ease_cap
    ease_floor = max(min_ease, (starting_ease -
                                (leash * number_of_reviews)))
    if suggested_factor < ease_floor:
        suggested_factor = ease_floor

    return suggested_factor


def ease_ivls(answer_list, use_lapse_ivl = True):
    this_ivl = 1
    factor = starting_ease
    ease_list = [factor]
    ivl_list = [1]
    for i in answer_list:
        if i == 1:
            if lapse_new_ivl_percent == None or not use_lapse_ivl:
                this_ivl = 1
            else:
                this_ivl = this_ivl * lapse_new_ivl_percent / 100
            factor -= 200
        if i == 2:
            this_ivl = this_ivl * 1.3
            factor -= 150
        if i == 3:
            this_ivl = this_ivl * factor / 1000
        if i == 4:
            this_ivl = this_ivl * factor / 1000
            factor += 150
        this_ivl = round(this_ivl, 2)
        ivl_list.append(this_ivl)
        ease_list.append(factor)
    return (ease_list, ivl_list)


def ease(answer_list):
    return ease_ivls(answer_list)[0]


def ivls(answer_list):
    return ease_ivls(answer_list)[1]


def reviews_to_pass_fail(reviews):
    return [int(_ > 1) for _ in reviews]


def new_ease_ivls(reviews):
    pf_revs = reviews_to_pass_fail(reviews)
    this_ivl = 1

    factor = starting_ease
    ease_list = [factor]
    ivl_list = [1]
    for idx in range(len(pf_revs)):
        ease_list.append(calculate_ease(pf_revs[:idx+1], ease_list))
        if pf_revs[idx]:
            ivl_list.append(round(ivl_list[-1] * ease_list[-1] / 1000,2))
        else:
            if lapse_new_ivl_percent == None:
                next_ivl = 1
            else:
                next_ivl = ivl_list[-1] * lapse_new_ivl_percent / 100
            ivl_list.append(round(next_ivl,2))
    return (ease_list, ivl_list)


def new_ease(reviews):
    return new_ease_ivls(reviews)[0]


def new_ivls(reviews):
    return new_ease_ivls(reviews)[1]

def gen_revs_for_ideal_ease(ideal = 2900, num_reviews = 25, use_new = False):
    rev_list = [3]
    ivl_list = [1]
    for r in range(num_reviews):
        this_ivl = ivls(rev_list)[-1]
        if use_new:
            this_ivl = new_ivls(rev_list)[-1]
        max_ivl = max(ivl_list)
        ideal_ivl = (max_ivl * ideal / 1000)
        if this_ivl < ideal_ivl * 0.9:
            rev_list.append(4)
        elif this_ivl < ideal_ivl * 1.1:
            rev_list.append(3)
        elif this_ivl < ideal_ivl * 1.3:
            rev_list.append(2)
        elif this_ivl >= ideal_ivl * 1.3:
            rev_list.append(1)
        else:
            assert False, f"Unexpected comparison between this_ivl {this_ivl} and ideal_ivl {ideal_ivl}"
        ivl_list.append(this_ivl)
    return rev_list
old_reviews = gen_revs_for_ideal_ease(ideal = ideal_ease_to_target)
new_reviews = gen_revs_for_ideal_ease(ideal = ideal_ease_to_target, use_new = True)

print("Ans:  Ease (Ivl) SR% -> New-Ease (New-Ivl) :: Adj. Success Rate%")
print(f'^: {ease(old_reviews)[0]} ({ivls(old_reviews)[0]:8}) :: --.--% -> ^: {new_ease(new_reviews)[0]} ({new_ivls(new_reviews)[0]:8} :: --.--%)')
for _ in range(1,len(old_reviews)):
    old_sr = round(find_success_rate(reviews_to_pass_fail(old_reviews[:_]))*100,1)
    new_sr = round(find_success_rate(reviews_to_pass_fail(new_reviews[:_]))*100,1)
    print(f'{old_reviews[_-1]}: {ease(old_reviews)[_]} ({ivls(old_reviews)[_]:8}) :: {old_sr:5}% -> '
          f"{new_reviews[_-1]}: {new_ease(new_reviews)[_]} ({new_ivls(new_reviews)[_]:8}) :: {new_sr:5}%")
print()

def success_rate_list(reviews):
    sr_list = []
    for _ in range(len(reviews)):
        sr_list.append(find_success_rate(reviews_to_pass_fail(reviews[:_])))
    return sr_list

old_sr_list = success_rate_list(old_reviews)
old_sr_gap = [abs(x - target_ratio) for x in old_sr_list]
old_sr_mean = round(100 * statistics.mean(old_sr_gap),2)

new_sr_list = success_rate_list(new_reviews)
new_sr_gap = [abs(x - target_ratio) for x in new_sr_list]
new_sr_mean = round(100 * statistics.mean(new_sr_gap),2)

print(f"Old avg distance from target: {old_sr_mean}%\n"
      f"New avg distance from target: {new_sr_mean}%")

print(f"Reviews until 1 year ivl (old): {sum([_ < 365 for _ in ivls(old_reviews)])}")
print(f"Reviews until 1 year ivl (new): {sum([_ < 365 for _ in new_ivls(new_reviews)])}")

year_one_revs_old = None
for idx in range(len(ivls(old_reviews))):
    if sum(ivls(old_reviews)[:idx]) > 365:
        year_one_revs_old = idx
        break
year_one_revs_new = None
for idx in range(len(ivls(old_reviews))):
    if sum(ivls(old_reviews)[:idx]) > 365:
        year_one_revs_new = idx
        break

print(f"Revs during first year (old): {year_one_revs_old}")
print(f"Revs during first year (new): {year_one_revs_new}")

print()
print("Interactive mode")
while True:
    print("Type in a list of reviews to see recommended ease under each algorithm")
    print("e.g.: '3, 2, 3, 1, 1'")
    print('(ctrl+c to quit)')
    reviews = [int(_.strip()) for _ in input().split(',')]
    print(f"New ease: {new_ease(reviews)[-1]}\n"
          f"{new_ease(reviews)}\n"
          f"Old ease: {ease(reviews)[-1]}\n"
          f"{ease(reviews)}\n"
          )

# Tried this at first, just a random list of button presses.
# But if you generate totally random review data,
# it's not an apples to apples comparison
# because different buttons would change the ivls in different ways
# for the different algorithms, which would affect your next button press

# The revised gen_revs_for_ideal_ease() function presses buttons the way
# someone might if they were facing a card that really needed a certain
# ease factor, fail if the ivl is longer than 2900 * the last ivl, say, but
# passed if it was under that.
'''def generate_random_review_data(num_reviews=10):
    answer_button_list = []
    for i in range(num_reviews):
        answer_button_list.append(random.randint(1, 4))
    return answer_button_list
'''
# That's closer, but probably need to model some probabilistic modifiers,
#   sometimes you have bad days.
# Also, some cards are just really stubborn, and take a ton of reviews before
#   they stick, while others click right away. Not yet sure how to model that.
