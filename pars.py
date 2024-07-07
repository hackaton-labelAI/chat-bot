import json

import markdownify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import time

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'if-modified-since': 'Fri, 05 Jul 2024 14:12:28 GMT',
    'if-none-match': 'W/"6687ff4c-1017e"',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
}

cookies = {
    '_ym_uid': '172019103369178952',
    '_ym_d': '1720191033',
    'oid': '6Uhim7ZNDA5ZpyrnF3aS4',
    'tmr_lvid': '8079f8295a035981379e4459540e5e20',
    'tmr_lvidTS': '1720191033402',
    '_ym_isad': '2',
    '_ga': 'GA1.1.1758689794.1720191034',
    'domain_sid': 'e0CmoUkJfoPIbwAhzHHkZ%3A1720191033586',
    'tmr_detect': '0%7C1720194523883',
    'solution429': 'z5HxA3CMmGXLYUkqz_h17n4BljdZ3nvrY-QHA22pNms-ipllQGi7rngwUmWyGyF5m8qnW133EJrJdnU_iklKNdLM3h1uhCJSaiqh0Yl1mPBpBoIQP4Kvd8QXIcDD9fgTpkPAdcRAOSURx1HB',
    '_ym_visorc': 'b',
    '_ga_3R5JQM4WFB': 'GS1.1.1720212964.3.1.1720214142.0.0.0'
}

def load_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

# Функция для сохранения данных в JSON файл
def save_json(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def get_page_text(url, base_url):
    """
    Отправляет запрос на указанный URL, парсит HTML-контент страницы,
    извлекает текст и абсолютные ссылки, ведущие на другие страницы внутри
    того же сайта

    :param url:
    :param base_url:
    :return: text (str), absolute_links (list)
    """

    try:
        data = load_json("htmls.json")
    except FileNotFoundError:
        data = []
    try:
        response = requests.get(url, headers=headers, cookies=cookies)
        print(response.status_code)
        if response.status_code != 200:
            return []
        assert response.status_code == 200
        soup = BeautifulSoup(response.content, "html.parser")

        title_tag = soup.find('h1')
        title = title_tag.text.strip() if title_tag else ""
        assert title != 'У вас большие запросы!'
        article = soup.find('article')
        if article is None:
            links = soup.find_all('a', href=True)
            absolute_links = [urljoin(base_url, link['href']) for link in links if re.match(r'^/help/', link['href'])]
            return absolute_links

        data.append({"html": str(article), "url": url})
        save_json(data, "htmls.json")
        links = soup.find_all('a', href=True)
        absolute_links = [urljoin(base_url, link['href']) for link in links if re.match(r'^/help/', link['href'])]

        return absolute_links
    except:
        print("error")
        time.sleep(2)
        return get_page_text(url, base_url)


def crawl_and_save_text(start_url):
    """

    :param start_url:
    :return:
    """
    base_url = "https://www.rustore.ru"
    visited_urls = set()
    urls_to_visit = [start_url]




    with open("rustore_help_full.txt", "w", encoding="utf-8") as file:
        while urls_to_visit:
            time.sleep(2)
            current_url = urls_to_visit.pop(0)
            if current_url in visited_urls:
                continue

            visited_urls.add(current_url)
            print(f"Парсинг: {current_url}")

            new_links = get_page_text(current_url, base_url)

            for link in new_links:
                if link not in visited_urls and link not in urls_to_visit:
                    urls_to_visit.append(link)



if __name__ == "__main__":
    start_url = "https://www.rustore.ru/help/"
    crawl_and_save_text(start_url)
