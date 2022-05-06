import json
import requests
import datetime
import time
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from .models import Article

"""
    Установить предварительно: fake_useragent, bs4, requests, lxml
"""


def collect_news():
    parsed = []
    current_time = datetime.datetime.now()

    ua = UserAgent()

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "User-Agent": ua.random
    }

    response = requests.get(url=f"https://devby.io/news", headers=headers).text
    time.sleep(2)
    soup = BeautifulSoup(response, "lxml")

    article_list = soup.find("div", class_="cards-group cards-group_list").find_all("div", class_="card card_media")

    for article in article_list:
        print(f'parsed {article_list.index(article) + 1} of {len(article_list)}')
        src_url = article.find("a", class_="card__link").get("href")
        source_url = "https://devby.io" + src_url
        title = article.find("img", class_="card__img").get("alt")
        img = article.find("img", class_="card__img").get("src")
        image = "https://devby.io" + img

        a = Article()
        a.source_url = source_url
        a.title = title
        a.image = image
        a.save()
        break
    # with open(f"main_devby_{current_time.strftime('%Y-%m-%d')}.json", "w") as file:
    #     json.dump(parsed, file, indent=4, ensure_ascii=False)


collect_news()


