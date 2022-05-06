import os
import datetime
import requests
import time
from celery import Celery
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from api_parser_cel import settings
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api_parser_cel.settings')
app = Celery("api_parser_cel")
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


# Расписание запуска парсеров и удаление старых новстей
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(30, habr_news, name='test_parser')
    sender.add_periodic_task(crontab(hour=3, minute=0, day_of_week='sunday'), cleaner,
                             name='delete old articles')
    sender.add_periodic_task(crontab(hour='5, 17', minute=0, day_of_week='*'), habr_news,
                             name='parser habr_news')
    sender.add_periodic_task(crontab(hour='5, 17', minute=1, day_of_week='*'), threednews,
                             name='parser threednews')
    sender.add_periodic_task(crontab(hour='5, 17', minute=2, day_of_week='*'), itproger_news,
                             name='parser itproger_news')
    sender.add_periodic_task(crontab(hour='5, 17', minute=3, day_of_week='*'), officelife_news,
                             name='parser officelife_news')
    sender.add_periodic_task(crontab(hour='5, 17', minute=4, day_of_week='*'), rbc_news,
                             name='parser rbc_news')
    sender.add_periodic_task(crontab(hour='5, 17', minute=5, day_of_week='*'), unetway_news,
                             name='parser unetway_news')


ua = UserAgent()
current_time = datetime.datetime.now()
headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "User-Agent": ua.random
    }


@app.task
def cleaner():
    print("Starting cleaning DataBase")
    from main_parser.models import Article

    articles = Article.objects.all()
    date = datetime.datetime.now(datetime.timezone.utc)
    for article in articles:
        delta = date - article.created
        if delta.days > 7:  # Если новость старше 7 дней, удаляется из БД
            print(f'delete article {article.title}, created {delta.days} day/-s ago.')
            article.delete()


@app.task
def habr_news():
    from main_parser.models import Article

    for number_page in range(1, 5):
        actual = True
        try:
            response = requests.get(url=f"https://habr.com/ru/news/page{number_page}/", headers=headers).text
            time.sleep(0.5)
        except:
            print("Request ERROR")

        print(f"<====== page {number_page} of habr ======>")
        soup = BeautifulSoup(response, "lxml")
        article_list = soup.find("div", class_="tm-articles-list").find_all("div", class_="tm-article-snippet")

        for article in article_list:
            print(f'parsed {article_list.index(article)+1} of {len(article_list)} from {number_page} page')
            source = article.find("h2", class_="tm-article-snippet__title tm-article-snippet__title_h2")
            source_url = "https://habr.com" + source.find("a").get("href")
            title = source.text
            date_time = article.find("time").get("title")
            try:
                image = article.find("div", class_="tm-article-body tm-article-snippet__lead").find("img").get("src")
            except:
                image = None
                print("No image")
            try:
                if article.find("div",
                                class_="article-formatted-body article-formatted-body article-formatted-body_version-1"):
                    description = article.find("div",
                                                        class_="article-formatted-body article-formatted-body article-formatted-body_version-1").text.strip()
                elif article.find("div",
                                  class_="article-formatted-body article-formatted-body article-formatted-body_version-2"):
                    description = article.find("div",
                                                        class_="article-formatted-body article-formatted-body article-formatted-body_version-2").text.strip()
                else:
                    description = None
                    print("Some error")
            except:
                description = None
                print("No description")

            time.sleep(0.1)
            # Условие проверки новости не старше суток.
            dt = date_time.split(",")
            date_ = dt[0].strip().split("-")
            time_ = dt[1].strip().split(":")
            year, month, day, hour, minutes = int(date_[0]), int(date_[1]), int(date_[2]), int(time_[0]), int(time_[1])
            t = datetime.datetime(year, month, day, hour, minutes)
            delta = current_time - t
            if delta.days >= 1:
                actual = False
                break

            a = Article()

            if Article.objects.filter(title=title).exists():
                print("Exist")
                continue
            else:
                a.title = title
                a.source_url = source_url
                a.date_time = date_time
                a.description = description
                a.image = image
                a.save()

        if actual == False:
            break


@app.task
def threednews():
    from main_parser.models import Article

    # Запрос на сайт
    print(f"<===================== parser of 3dnews =====================>")
    try:
        response = requests.get(url="https://3dnews.ru/software", headers=headers).text
        time.sleep(0.5)
    except:
        print("Ошибка запроса")
    # Суп из ответа
    soup = BeautifulSoup(response, "lxml")
    # Список урлов новостей
    article_list = soup.find("div", class_="content-block-data white sub-section-list").find_all("li")
    # Список для последующего сохранения в файл json

    for article in article_list:
        print(f"parsed {article_list.index(article)+1} of {len(article_list)}")
        # Сдоварь для группировки данных одной новости
        src_url = article.find("a").get("href")
        source_url = "https://3dnews.ru" + src_url
        title = article.find("a").text.strip()
        date_time = article.find("span", class_="strong").text. strip()
        time.sleep(0.1)
        dt = date_time.split(' ')[0].split('.')
        t = datetime.datetime(int(dt[2]), int(dt[1]), int(dt[0]))
        delta = current_time - t
        if delta.days >= 1:
            break

        a = Article()

        if Article.objects.filter(title=title).exists():
            print("Exist")
            continue
        else:
            a.title = title
            a.source_url = source_url
            a.date_time = date_time
            a.save()


@app.task
def itproger_news():
    from main_parser.models import Article

    print(f"<===================== parser of itproger =====================>")

    try:
        response = requests.get(url=f"https://itproger.com/news", headers=headers).text
        time.sleep(0.5)
    except:
        print("Error request")

    soup = BeautifulSoup(response, "lxml")
    article_list = soup.find("div", class_="allArticles").find_all("div", class_="article")

    for article in article_list:
        print(f'parsed {article_list.index(article) + 1} of {len(article_list)}')
        src_url = article.find("a").get("href")
        source_url = "https://itproger.com/" + src_url
        title = article.find("a").get("title").strip()
        img = article.find("img").get("src")
        image = "https://itproger.com/" + str(img)
        description = article.find_all("span")[1].text.strip()
        date_time = article.find("span", class_="time").text.strip().split(" ")
        date_time = date_time[0] + ' ' + date_time[1] + ' ' + date_time[2] + ' ' + date_time[-1]
        time.sleep(0.1)
        if int(current_time.strftime('%d')) - int(date_time.split(' ')[0]) >= 1:
            break

        a = Article()

        if Article.objects.filter(title=title).exists():
            print("Exist")
            continue
        else:
            a.title = title
            a.source_url = source_url
            a.description = description
            a.date_time = date_time
            a.image = image
            a.save()


@app.task
def officelife_news():
    from main_parser.models import Article

    print(f"<===================== parser of officelife =====================>")

    # Запрос на сайт
    try:
        response = requests.get(url="https://officelife.media/search/?q=it", headers=headers).text
        time.sleep(0.5)
    except:
        print("Error request")

    # Суп из ответа
    soup = BeautifulSoup(response, "lxml")

    article_list = soup.find("div", class_="col-12 col-sm-8 col-md-9").find_all("div", class_="search-item nav-insert")

    for article in article_list:
        print(f"parsed {article_list.index(article) + 1} of {len(article_list)}")

        source_url = article.find("a", class_="search-item__title").get("href")
        source_url = "https://officelife.media" + source_url
        title = article.find("a", class_="search-item__title").text.strip()
        date_time = article.find("div", class_="search-item__date").text.strip().split()[0]
        description = article.find("a", class_="search-item__descr").text.strip()
        date_ = date_time.split(".")
        t = datetime.datetime(int(date_[2]), int(date_[1]), int(date_[0]))
        delta = current_time - t
        if delta.days >= 1:
            break

        time.sleep(0.1)

        a = Article()

        if Article.objects.filter(title=title).exists():
            print("Exist")
            continue
        else:
            a.title = title
            a.source_url = source_url
            a.description = description
            a.date_time = date_time
            a.save()


@app.task
def rbc_news():
    from main_parser.models import Article

    print(f"<===================== parser of rbc =====================>")

    actual_article_time = datetime.datetime(day=current_time.day - 5, month=current_time.month, year=current_time.year)
    try:
        response = requests.get(url=f"https://www.rbc.ru/tags/?tag=IT&dateFrom={actual_article_time.strftime('%d.%m.%Y')}&dateTo={current_time.strftime('%d.%m.%Y')}", headers=headers).text
        time.sleep(0.5)
    except:
        print("Erorr request")

    soup = BeautifulSoup(response, "lxml")
    article_list = soup.find("div", class_="l-row g-overflow js-search-container").find_all("div", class_="search-item__wrap l-col-center")

    for article in article_list:
        print(f'parsed {article_list.index(article)+1} of {len(article_list)}')
        source_url = article.find("a").get("href")
        title = article.find("span", class_="search-item__title").text
        date_time = article.find("span", class_="search-item__category").text
        date_time = date_time.split(",")
        date_time = date_time[-2].strip() + " " + date_time[-1].strip()
        try:
            image = article.find("span", class_="search-item__image-block").find("img").get("src")
        except:
            image = None
            print("No image")
        try:
            description = article.find("span", class_="search-item__text").text.strip()
        except:
            description = None
            print("No description")

        time.sleep(0.1)

        a = Article()

        if Article.objects.filter(title=title).exists():
            print("Exist")
            continue
        else:
            a.title = title
            a.image = image
            a.source_url = source_url
            a.description = description
            a.date_time = date_time
            a.save()


@app.task
def unetway_news():
    from main_parser.models import Article

    print(f"<===================== parser of unetway =====================>")

    # Запрос на сайт
    try:
        response = requests.get(url="https://unetway.com/blog", headers=headers).text
        time.sleep(0.5)
    except:
        print("Error request")
    # Суп из ответа
    soup = BeautifulSoup(response, "lxml")
    # Список урлов новостей
    article_list = soup.find("div", class_="section-content").find_all("article", class_="post-block")

    for article in article_list:
        print(f'parsed {article_list.index(article) + 1} of {len(article_list)}')

        source_url = article.find("header", class_="post-header").find("a").get("href")
        title = article.find("header", class_="post-header").text.strip()
        try:
            img = article.find("div", class_="post-image").find("img").get("src")
            image= "https://unetway.com" + str(img)
        except:
            image = None
            print("No image")
        description = article.find("div", class_="post-content").text.strip()
        date_time = article.find("footer", class_="post-footer").find("span", class_="post-date-create").text.strip()
        dt = date_time.split("-")
        date = datetime.datetime(int(dt[0]), int(dt[1]), int(dt[2]))
        delta = current_time - date

        if delta.days >= 1:
            break

        time.sleep(0.1)

        a = Article()

        if Article.objects.filter(title=title).exists():
            print("Exist")
            continue
        else:
            a.title = title
            a.image = image
            a.source_url = source_url
            a.description = description
            a.date_time = date_time
            a.save()
