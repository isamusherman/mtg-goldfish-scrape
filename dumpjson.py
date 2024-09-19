import json
from pauper_decks_data import deck_data

def accumulate_card_quantities(deck_data):
    mainboard_totals = {}
    sideboard_totals = {}
    
    for deck in deck_data.values():
   
        mainboard = deck['Mainboard']
        sideboard = deck['Sideboard']
        playcount = deck['Play Count']

        if mainboard and sideboard:         
            for card, quantity in mainboard.items():
                mainboard_totals[card] = mainboard_totals.get(card, 0) + quantity * playcount
            
            for card, quantity in sideboard.items():
                sideboard_totals[card] = sideboard_totals.get(card, 0) + quantity * playcount
            
    return mainboard_totals, sideboard_totals

def write_json_file(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

mainboard_totals, sideboard_totals = accumulate_card_quantities(deck_data)

write_json_file(mainboard_totals, 'pauper_mainboard_totals.json')
write_json_file(sideboard_totals, 'pauper_sideboard_totals.json')
