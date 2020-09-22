import PySimpleGUIQt
import math

sg = PySimpleGUIQt

# TODO isolate discrepancies, align with main
# maybe just copy these functions to main, separate out the db calls
# for easier, more consistent testing 


def calculate_moving_average(value_list, weight, init=None):
    assert len(value_list) > 0
    if init is None:
        result = sum(value_list)/len(value_list)
    else:
        result = init
    for this_item in value_list:
        result = (result * (1 - weight))
        result += this_item * weight
    return result


def find_success_rate(review_list, weight):
    success_list = [int(_ > 1) for _ in review_list]
    success_rate = calculate_moving_average(success_list, weight)
    return success_rate


def find_average_ease(factor_list, weight):
    average_ease = factor_list[-1]
    if factor_list and len(factor_list) > 0:
        average_ease = calculate_moving_average(factor_list, weight)
    return average_ease


def calculate_ease(config_settings, card_settings):
    leash = config_settings['leash']
    target = config_settings['target']
    max_ease = config_settings['max_ease']
    min_ease = config_settings['min_ease']
    weight = config_settings['weight']

    review_list = card_settings['review_list']
    factor_list = card_settings['factor_list']

    starting_ease = factor_list[-1]
    success_rate = find_success_rate(review_list, weight)

    # Ebbinghaus formula
    if success_rate > 0.99:
        success_rate = 0.99  # ln(1) = 0; avoid divide by zero error
    if success_rate < 0.01:
        success_rate = 0.01
    delta_ratio = math.log(target) / math.log(success_rate)
    average_ease = find_average_ease(factor_list, weight)
    suggested_factor = int(round(average_ease * delta_ratio))

    # anchor this to starting_ease initially
    number_of_reviews = len(review_list)
    ease_cap = min(max_ease, (starting_ease
                   + (leash * number_of_reviews)))
    if suggested_factor > ease_cap:
        suggested_factor = ease_cap
    ease_floor = max(min_ease, (starting_ease
                     - (leash * number_of_reviews)))
    if suggested_factor < ease_floor:
        suggested_factor = ease_floor

    return suggested_factor


layout = [[sg.Text('Leash', size=(10, 1)), sg.Input('300', key='leash')],
          [sg.Text('Min Ease', size=(10, 1)), sg.Input('10', key='min_ease')],
          [sg.Text('Max Ease', size=(10, 1)), sg.Input('7000', key='max_ease')],
          [sg.Text('MAvg Weight', size=(10, 1)), sg.Input('0.2', key='weight')],
          [sg.Text('Target', size=(10, 1)), sg.Input('0.85', key='target')],
          [sg.Text('Answer History', size=(10, 1)),
           sg.Input('1 3 3', key='answers')],
          [sg.Text('Factor History', tooltip='Or initial ease factor if '
                   'recalculating ease history', size=(10, 1)),
              sg.Input('2500 1900 1700', tooltip='If recalculting history, '
                       'starting ease factor will be taken from first value',
                       key='factors')],
          [sg.Checkbox('Recalculate Ease History', default=True,
                       key='recalculate')],
          [sg.Text('_'*40)],
          [sg.Button('Calculate'), sg.Text('', key='suggested_factor')],
          ]

window = sg.Window('Table Simulation', layout)


def calculate(card_settings=None):
    config_settings = {}
    config_settings['leash'] = int(values['leash'])
    config_settings['min_ease'] = int(values['min_ease'])
    config_settings['max_ease'] = int(values['max_ease'])
    config_settings['weight'] = float(values['weight'])
    config_settings['target'] = float(values['target'])
    if card_settings is None:
        card_settings = {}
        card_settings['review_list'] = [int(_) for _ in
                                        values['answers'].split()]
        card_settings['factor_list'] = [int(_) for _ in
                                        values['factors'].split()]
    new_factor = calculate_ease(config_settings, card_settings)
    return new_factor


def calculate_all(card_settings):
    new_factor_list = [card_settings['factor_list'][0]]
    for count in range(1, 1 + len(card_settings['review_list'])):
        tmp_review_list = card_settings['review_list'][:count]
        new_factor = calculate({'review_list': tmp_review_list,
                                'factor_list': new_factor_list})
        new_factor_list.append(new_factor)
    card_settings['factor_list'] = new_factor_list
    return card_settings


def validate_all():
    valid = True
    field_labels = ['leash', 'min_ease', 'max_ease', 'weight',
                    'target', 'answers', 'factors']
    for field_label in field_labels:
        if values[field_label] in ['', None]:
            valid = False
    int_field_labels = ['leash', 'min_ease', 'max_ease']
    for field_label in int_field_labels:
        for character in values[field_label].strip():
            if character not in '0123456789':
                valid = False
    float_field_labels = ['weight', 'target']
    for field_label in float_field_labels:
        for character in values[field_label].strip():
            if character not in '.0123456789':
                valid = False
        if values[field_label].count('.') != 1:
            valid = False
    list_field_labels = ['answers', 'factors']
    for field_label in list_field_labels:
        for character in values[field_label].strip():
            if character not in ' 0123456789':
                valid = False
    return valid


while True:
    event, values = window.read()
    if event is None or event in (sg.WIN_CLOSED, 'Exit'):
        break
    elif event == 'Calculate':
        if validate_all():
            if values['recalculate']:
                recalc_settings = {}
                recalc_settings['review_list'] = [int(_) for _ in
                                                  values['answers'].split()]
                recalc_settings['factor_list'] = [int(values['factors'].split()[0])]
                new_factors = calculate_all(recalc_settings)['factor_list']
                window['suggested_factor'].update(new_factors)
            else:
                window['suggested_factor'].update(calculate())
        else:
            window['suggested_factor'].update("Invalid entry")

print(values)
window.close()
