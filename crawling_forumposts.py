from bs4 import BeautifulSoup
import requests
import re
import json
from langdetect import detect
import os

def get_forum_links(page_url):
    main_boards = []
    sub_boards = []

    response = requests.get(page_url)
    html_content = response.text
    
    soup = BeautifulSoup(html_content, 'html.parser')

    boards = soup.find_all('a', class_='subject')
    for board in boards:
        board_name = board.text
        board_url = board['href']
        main_boards.append((board_name, board_url))

    sub_boards_elements = soup.find_all('a', title=lambda x: x and "Keine neuen Beiträge" in x)
    for i, board in enumerate(sub_boards_elements):
        board_name = f"Untergeordnete_Boards_{i+1}: {board.text}"
        board_url = board['href']
        sub_boards.append((board_name, board_url))

    return main_boards + sub_boards

# Code from crawling_forumposts.ipynb to scrape specific board page
def extract_details_from_post(post_div):
    text = " ".join([s.strip() for s in list(post_div.find_all("div", class_="inner")[0].strings)])
    text = re.sub(r'« Antwort #\d+ am:.*?»', '', text)
    quotes = [quote.get_text().strip() for quote in post_div.find_all('blockquote')]
    return {
        "text": clean_text(text),
        "quote": clean_text(quotes[0] if quotes else "None")
    }

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def is_german(text):
    try:
        lang = detect(text)
        return lang == 'de'
    except:
        return False

def filter_valid_details(details):
    text = details['text']
    if len(text) < 20 or not is_german(text):
        return False
    return True

def scrape_thread(url):
    author_post, antworts = None, []
    current_page_number = 1
    while url:
        response = requests.get(url)
        response.encoding = 'ISO-8859-1'
        soup = BeautifulSoup(response.text, 'html.parser')

        posts_divs = soup.find_all('div', class_='post_wrapper')
        for index, post_div in enumerate(posts_divs):
            details = extract_details_from_post(post_div)
            if not filter_valid_details(details):
                continue
            
            if index == 0 and current_page_number == 1:
                author_post = details
            else:
                antworts.append(details)

        page_links_div = soup.find('div', {'class': 'pagelinks floatleft'})
        if page_links_div:
            next_page_links = [a for a in page_links_div.find_all('a', {'class': 'navPages'}) if a.text.strip() == str(current_page_number + 1)]
            url = next_page_links[0]['href'] if next_page_links else None
            current_page_number += 1
        else:
            url = None

    return author_post, antworts

def scrape_forum(base_url):
    forum_data = {"board": {"Externe Umfragen/Studien": []}}

    for page_number in range(6):
        url = base_url + str(page_number * 20) + '.html'
        response = requests.get(url)
        response.encoding = 'ISO-8859-1'
        soup = BeautifulSoup(response.text, 'html.parser')

        threads_table = soup.find('table', {'class': 'table_grid'})
        threads = threads_table.find_all('tr')[1:]

        for thread in threads:
            title = thread.find('td', class_='subject').find('a').text.split('Begonnen')[0].strip()
            antworten_aufrufe = clean_text(thread.find('td', class_='stats').text)
            letzter_beitrag = clean_text(thread.find('td', class_='lastpost').text)
            thread_url = thread.find('td', class_='subject').find('a')['href']
            author_post, antworts = scrape_thread(thread_url)

            thread_data = {
                "Betreff / Begonnen von": title,
                "author_post": author_post,
                "antwort": {f"antwort_{i+1}": antwort for i, antwort in enumerate(antworts)},
                "Antworten / aufrufe": antworten_aufrufe,
                "Letzter_Beitrag": letzter_beitrag
            }

            forum_data["board"]["Externe Umfragen/Studien"].append(thread_data)

    return forum_data

page_url = 'https://www.forum.diabetesinfo.de/forum/index.php'
board_links = get_forum_links(page_url)
for i, (board_name, board_url) in enumerate(board_links):
    print(f"Board Name_{i+1}: {board_name}, Link: {board_url}")

for i, (board_name, board_url) in enumerate(board_links):
    print(f"Scraping {board_name}...")
    forum_data = scrape_forum(board_url)
    board_key = list(forum_data["board"].keys())[0] 
    filename = os.path.join('output', f'forum_data_{i}.jsonl')
    with open(filename, 'w', encoding='utf-8') as file:
        for thread_data in forum_data["board"][board_key]: 
            json_line = json.dumps(thread_data, ensure_ascii=False)
            file.write(json_line + '\n')
    print(f"Data saved to {filename}")

print("Scraping completed!")