def create_dict_from_two_lists(keys_list, values_list):
    zip_iterator = zip(keys_list, values_list)
    dictionary = dict(zip_iterator)
    return dictionary


def handle_user_meter_input(user_input):
    without_zeros = _remove_zeros_in_user_input(user_input)
    return without_zeros


def _remove_zeros_in_user_input(user_input):
    flag = True
    x_char = user_input
    while flag:
        if x_char[0] == '0':
            x_char = x_char[1:]
        else:
            flag = False
    return x_char
