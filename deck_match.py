def deck_match(deck_name, deck_list):
    def parent_deck(dn):
        if "::" not in dn:
            return None
        else:
            return "::".join(dn.split("::")[:-1])

    this_deck = deck_name
    if this_deck is None:
        return None
    elif this_deck in deck_list:
        return this_deck
    else:
        return deck_match(parent_deck(this_deck), deck_list)

def tests():
    test_list = [
    "Abacus",
    "China::Second",
    "China",
    "China::First::Former"
    ]

    test_decks = [
    "Abacus",
    "China::Second::Second",
    "China",
    "China::Third::Fourth",
    "Second"
    ]

    test_out = ""
    for td in test_decks:
        test_out += str(deck_match(td, test_list)) + ", "
    # print(test_out)
    if test_out == "Abacus, China::Second, China, China, None, ":
        return True
    else:
        return False

# print(tests())
