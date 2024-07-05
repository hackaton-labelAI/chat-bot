import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import time
import json


def clean_text(text):
    """
    Убирает лишние символы из текста
    :param text: Исходный текст
    :return: Очищенный текст
    """
    text = re.sub(r'\n+', '\n', text).strip()
    unwanted_characters = [
        '© ', '✔', '✖', '​', '🟦', '🗃️'
    ]
    for char in unwanted_characters:
        text = text.replace(char, '')
    return text


def get_page_data(url, base_url):
    """
    Отправляет запрос на указанный URL, парсит HTML-контент страницы,
    извлекает заголовок, текст и абсолютные ссылки, ведущие на другие страницы внутри
    того же сайта.

    url (str): URL страницы для парсинга.
    base_url (str): Базовый URL для создания абсолютных ссылок.

    page_data (dict): Словарь с данными страницы, включая заголовок, URL, текст и ссылки.
    """

    # headers = {
    #     'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    #     'accept-language': 'en-US,en;q=0.9',
    #     'cache-control': 'max-age=0',
    #     'if-modified-since': 'Fri, 05 Jul 2024 14:12:28 GMT',
    #     'if-none-match': 'W/"6687ff4c-1017e"',
    #     'priority': 'u=0, i',
    #     'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    #     'sec-ch-ua-mobile': '?0',
    #     'sec-ch-ua-platform': '"Linux"',
    #     'sec-fetch-dest': 'document',
    #     'sec-fetch-mode': 'navigate',
    #     'sec-fetch-site': 'same-origin',
    #     'sec-fetch-user': '?1',
    #     'upgrade-insecure-requests': '1',
    #     'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    # }
    #
    # cookies = {
    #     '_ym_uid': '172019103369178952',
    #     '_ym_d': '1720191033',
    #     'oid': '6Uhim7ZNDA5ZpyrnF3aS4',
    #     'tmr_lvid': '8079f8295a035981379e4459540e5e20',
    #     'tmr_lvidTS': '1720191033402',
    #     '_ym_isad': '2',
    #     '_ga': 'GA1.1.1758689794.1720191034',
    #     'domain_sid': 'e0CmoUkJfoPIbwAhzHHkZ%3A1720191033586',
    #     'tmr_detect': '0%7C1720194523883',
    #     'solution429': 'z5HxA3CMmGXLYUkqz_h17n4BljdZ3nvrY-QHA22pNms-ipllQGi7rngwUmWyGyF5m8qnW133EJrJdnU_iklKNdLM3h1uhCJSaiqh0Yl1mPBpBoIQP4Kvd8QXIcDD9fgTpkPAdcRAOSURx1HB',
    #     '_ym_visorc': 'b',
    #     '_ga_3R5JQM4WFB': 'GS1.1.1720212964.3.1.1720214142.0.0.0'
    # }

    response = requests.get(url) #, headers=headers, cookies=cookies
    time.sleep(1)
    soup = BeautifulSoup(response.content, "html.parser")
    label = soup.find('h1').get_text(strip=True) if soup.find('h1') else "Без заголовка"
    text = soup.get_text(separator="\n").strip()
    text = clean_text(text)

    # Обработка ссылок
    links = soup.find_all('a', href=True)
    absolute_links = {}
    for link in links:
        href = urljoin(base_url, link['href'])
        if re.match(r'^/help/', link['href']):
            link_text = link.get_text(strip=True)
            absolute_links[link_text] = href

    page_data = {
        "label": label,
        "url": url,
        "text": text,
        "links": absolute_links
    }

    return page_data


def crawl_and_save_text(start_url):
    """
    Рекурсивно обходит страницы, начиная с указанного URL, извлекает данные и сохраняет их в JSON и текстовый файл.

    start_url (str): Начальный URL для начала обхода.
    """
    base_url = "https://www.rustore.ru"
    visited_urls = set()
    urls_to_visit = [start_url]
    all_data = []

    with open("rustore_help_full.txt", "w", encoding="utf-8") as text_file:
        while urls_to_visit:
            current_url = urls_to_visit.pop(0)
            if current_url in visited_urls:
                continue

            visited_urls.add(current_url)
            print(f"Посещение: {current_url}")

            page_data = get_page_data(current_url, base_url)
            all_data.append(page_data)

            # Запись в текстовый файл
            text_file.write(f"URL: {current_url}\n")
            text_file.write(f"Заголовок: {page_data['label']}\n")
            text_file.write(f"{page_data['text']}\n\n{'=' * 80}\n\n")

            for link_text, link_url in page_data["links"].items():
                text_file.write(f"{link_text}: {link_url}\n")

            for link_url in page_data["links"].values():
                if link_url not in visited_urls and link_url not in urls_to_visit:
                    urls_to_visit.append(link_url)

    # Сохранение всех данных в JSON-файл
    with open("rustore_help_full.json", "w", encoding="utf-8") as json_file:
        json.dump(all_data, json_file, ensure_ascii=False, indent=4)



START_URL = "https://www.rustore.ru/help/"

crawl_and_save_text(START_URL)