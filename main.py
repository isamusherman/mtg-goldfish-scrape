import requests
import uuid
import json
from bs4 import BeautifulSoup


def scrape_deck_page(html_deck):
    """
    Get Tuple with Deck Name, Mainboard dict and Sideboard dict from html of deck page.
    :param html_deck: html page of deck e.g.: https://www.mtggoldfish.com/archetype/standard-jeskai-fires#paper
    :return: tuple (deck_name: str, mainboard: dict, sideboard: dict)
    """
    soup = BeautifulSoup(html_deck, "html.parser")
    
    deck_name = str(uuid.uuid4())

    # Find the input tag with id 'deck_input_deck'
    deck_input = soup.find("input", {"id": "deck_input_deck"})
    
    if deck_input:
        # Extract the value attribute which contains the decklist
        decklist = deck_input.get("value")
        
        # Split the decklist string by newlines
        lines = decklist.split("\n")
        
        mainboard = {}
        sideboard = {}
        is_sideboard = False  # Flag to indicate if we're parsing sideboard cards
        
        for line in lines:
            line = line.strip()
            if not line:  # Skip empty lines
                continue
            if line.lower() == "sideboard":  # When encountering the sideboard marker, switch to sideboard mode
                is_sideboard = True
                continue
            if not is_sideboard:  # If not in sideboard mode, add cards to the mainboard
                card_data = line.split()  # Split the line by whitespace
                if len(card_data) >= 2:  # Ensure it's a valid card line
                    count = int(card_data[0])
                    card_name = " ".join(card_data[1:])
                    mainboard[card_name] = count
            else:  # If in sideboard mode, add cards to the sideboard
                card_data = line.split()  # Split the line by whitespace
                if len(card_data) >= 2:  # Ensure it's a valid card line
                    count = int(card_data[0])
                    card_name = " ".join(card_data[1:])
                    sideboard[card_name] = count
        
        return deck_name, mainboard, sideboard
    else:
        return None, None, None  # Return None if the decklist input tag is not found

def scrape_all_standard_decks():
    standard_decks = {}
    deck_links = set()
    deck_play_counts ={}
    
    url = "https://www.mtggoldfish.com/metagame/vintage/full#paper"
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        deck_links_elements = soup.select('span.deck-price-paper a')
        
        for link in deck_links_elements:
            if link['href'].startswith("/archetype/"):
                deck_url = "https://www.mtggoldfish.com" + link['href']
                deck_links.add(deck_url)
        
                parent_div = link.find_parent('div', class_='archetype-tile-description-wrapper')
                if parent_div:
                    # Find the span element containing the play count
                    play_count_span = parent_div.select_one('span.archetype-tile-statistic-value-extra-data')
                    if play_count_span:
                        play_count_text = play_count_span.text.strip()
                        play_count = int(play_count_text.strip('()'))  # Extracting the number within parentheses
                        deck_play_counts[deck_url] = play_count

        print("Number of deck links found:", len(deck_links))  # Add this line to check the number of deck links found
        print("Deck play counts:", deck_play_counts)

        for deck_url in deck_links:
            print("Processing deck link:", deck_url)  # Add this line to see which deck link is being processed
            deck_name, mainboard, sideboard = scrape_deck_page(requests.get(deck_url).content)
            standard_decks[deck_name] = {"Mainboard": mainboard, "Sideboard": sideboard, "Play Count": deck_play_counts.get(deck_url, 0)}
    
    return standard_decks

if __name__ == "__main__":
    pioneer_decks = scrape_all_standard_decks()
    
    def save_deck_data_as_py(dictionary, file_path):
        with open(file_path, "w") as file:
            file.write("deck_data = " + repr(dictionary))

    # Example usage:
    save_deck_data_as_py(pioneer_decks, "vintage_decks_data.py")
