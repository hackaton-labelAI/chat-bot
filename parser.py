import json
import os
import re

import requests
from bs4 import BeautifulSoup

def generate_request_body(prompt):
    return {
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }


headersApi = {
    "MLP-API-KEY": os.environ.get("MLP-API-KEY"),
    "Content-Type": "application/json"
}

account = "just-ai"
model = "vllm-qwen2-72b-awq"
def prompt(elem):
    return  f"""
Отвечай на русском!
Сейчас тебе придёт html элемент table.
Тебе надо будет его распарсить по следующему правилу, каждая строчка это новый обзац.
Далее мы сопоставляем элемент строки с её заголовком
Ответить должна только получившимся текстом.

Вот элемент.
{elem}
"""

url = f"https://caila.io/api/mlpgate/account/{account}/model/{model}/predict"


def load_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

# Функция для сохранения данных в JSON файл
def save_json(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def parseTable(table):
    headers = table.find('thead') or table.find_all('tr')[0]
    if not headers:
        return [" "]
    headers_html = str(headers)
    rows = table.find_all('tr')
    if not rows:
        return [" "]
    if headers in rows:
        rows.remove(headers)
    text = ""

    for i in range(0, len(rows), 5):
        # Создаем новую таблицу для текущей страницы
        page_table = "<table>"

        # Добавляем заголовки
        page_table += headers_html

        # Добавляем строки для текущей страницы
        page_table += "<tbody>"
        for row in rows[i:i + 5]:
            page_table += str(row)
        page_table += "</tbody>"

        # Закрываем таблицу
        page_table += "</table>"

        rq = generate_request_body(prompt(page_table))
        response = requests.post(url, json=rq, headers=headersApi)
        if response.status_code == 200:
            # print("Request succeeded!")
            # print("Response:", response.json())
            choices = response.json().get('choices', [])
            if choices:
                first_choice = choices[0]
                message = first_choice.get('message', {})
                content = message.get('content', '')
                text += content + "\n"
                # print("Content:", content)
        else:
            print(f"Request failed with status code {response.status_code}")
            print("Response text:", response.text)

        # Добавляем текущую страницу в массив страниц
        # pages.append(page_table)
        #
    print(text)
    return text

def parseImg(img):
    # Ваша логика для обработки изображения
    return "Parsed Image Text"


def getData(cc):
    soup = BeautifulSoup(cc["html"], 'html.parser')
    h1_tag = soup.find('h1')
    if not h1_tag:
        return [{"title": "", "text": "", "url": cc["url"]}]
    title = h1_tag.text.strip()
    current_title = title
    text_by_headline = []
    frame = {"title": current_title, "text": "", "url": cc["url"]}
    element = h1_tag.find_next_sibling()
    while element:
        if element.name == 'h1':
            element = element.next_element
            continue
        elif element.name and re.match(r'^h[2-6]$', element.name):
            text_by_headline.append(frame)
            current_title = element.get_text().strip()
            frame = {"title": current_title, "text": "", "url": cc["url"]}
        elif element.name == 'table':
            frame["text"] += parseTable(element)
        elif element.name == 'img':
            frame["text"] += parseImg(element)
        elif element.name == 'img':
            frame["text"] += parseImg(element)
        else:
            # if isinstance(element, NavigableString):
            #     frame["text"] += element
            frame["text"] += element.text.strip()
        element = element.find_next_sibling()
    text_by_headline.append(frame)
    return text_by_headline

def length(text_by_headline):
    totalSize = 0
    for data in text_by_headline:
        totalSize+=len(data["text"])
    return totalSize

def clean_data(articles, min=100, max=2000):
    final_data = []
    for article in articles:
        size = length(article)
        if size <= min:
            continue
        if size <= max:
            final_data.append(article)
        else:
            size = 0
            chunk_data =[]
            for i in range(len(article)):
                if size + len(article[i]["text"]) <= max:
                    chunk_data.append(article[i])
                    size += len(article[i]["text"])
                else:
                    if len(chunk_data) > 0:
                        final_data.append(chunk_data)
                        chunk_data = []
                        size = 0
                    if len(article[i]["text"]) <= max:
                        chunk_data.append(article[i])
                        size += len(article[i]["text"])
                    else:
                        split_points = re.compile(r'(?<=\.)\s|\n')
                        parts = []
                        current_part = ''
                        for segment in split_points.split(article[i]["text"]):
                            if len(current_part) + len(segment) + 1 <= max:
                                if current_part:
                                    current_part += ' '
                                current_part += segment
                            else:
                                parts.append(current_part)
                                current_part = segment

                        if current_part:
                            parts.append(current_part)
                        for part in parts:
                            final_data.append([{"title": article[i]["title"], "text": part, "url": article[i]["url"]}])
    return final_data

if __name__ == "__main__":
    try:
        data = load_json("html.json")
    except FileNotFoundError:
        data = []
    tt = []
    for cc in data:
        tt.append(getData(cc))
    final = clean_data(tt)
    print(final)
    print(len(final))
    save_json(final, "doc.json")
