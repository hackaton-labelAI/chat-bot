import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re


def get_page_text(url, base_url):
    """
    Отправляет запрос на указанный URL, парсит HTML-контент страницы,
    извлекает текст и абсолютные ссылки, ведущие на другие страницы внутри
    того же сайта

    :param url:
    :param base_url:
    :return: text (str), absolute_links (list)
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    text = soup.get_text(separator="\n").strip()
    links = soup.find_all('a', href=True)
    absolute_links = [urljoin(base_url, link['href']) for link in links if re.match(r'^/help/', link['href'])]

    return text, absolute_links


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
            current_url = urls_to_visit.pop(0)
            if current_url in visited_urls:
                continue

            visited_urls.add(current_url)
            print(f"Парсинг: {current_url}")

            text, new_links = get_page_text(current_url, base_url)
            file.write(f"URL: {current_url}\n")
            file.write(f"{text}\n\n{'=' * 80}\n\n")

            for link in new_links:
                if link not in visited_urls and link not in urls_to_visit:
                    urls_to_visit.append(link)


start_url = "https://www.rustore.ru/help/"
crawl_and_save_text(start_url)