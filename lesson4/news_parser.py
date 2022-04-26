"""
Collects news from various sources using xpath.
"""
from pymongo import MongoClient

from lesson4.generic import parse_news, URL_K

MONGODB_URI = '127.0.0.1:27017'
DB_NAME = 'news_db'
COLLECTION_NAME = 'news'

MAILRU_URL = 'news.mail.ru/'
LENTA_URL = 'lenta.ru/'
YA_URL = 'yandex.ru/news/'


def get_mailru_news():
    """Parses news from mail.ru."""

    top_news_xpath = '//a[contains(@class, "topnews__item")]'
    top_news_title_xpath = f'{top_news_xpath}//span[contains(@class, "photo__title ")]/text()'
    top_news_link_xpath = f'{top_news_xpath}/@href'

    list_news_xpath = '//a[@class="list__text"]'
    list_news_title_xpath = f'{list_news_xpath}/text()'
    list_news_link_xpath = f'{list_news_xpath}/@href'

    newsitem_xpath = '//a[contains(@class, "newsitem__title")]'
    newsitem_title_xpath = f'{newsitem_xpath}/span/text()'
    newsitem_link_xpath = f'{newsitem_xpath}/@href'

    list_newsitem_xpath = '//span[@class="list__text"]/a'
    list_newsitem_title_xpath = f'{list_newsitem_xpath}/span/text()'
    list_newsitem_link_xpath = f'{list_newsitem_xpath}/@href'

    sources_xpath = f'//a[contains(@class, "breadcrumbs__link")]/span/text()'
    titles_xpath = f'{top_news_title_xpath}|{list_news_title_xpath}|{newsitem_title_xpath}|{list_newsitem_title_xpath}'
    dates_xpath = f'//span[contains(@class, "breadcrumbs__item")]/*/span[contains(@class, "js-ago")]/@datetime'
    links_xpath = f'{top_news_link_xpath}|{list_news_link_xpath}|{newsitem_link_xpath}|{list_newsitem_link_xpath}'
    data = parse_news(MAILRU_URL, sources_xpath, titles_xpath, dates_xpath, links_xpath)
    return data


def get_lenta_news():
    """Parses news from lenta.ru"""

    news_xpath = '//a[contains(@class, "_topnews")]'
    news_titles_xpath = f'{news_xpath}//span[contains(@class, "mini__title")]/text()'
    news_titles_xpath = f'{news_titles_xpath}|{news_xpath}//h3/text()'
    news_links_xpath = f'{news_xpath}/@href'

    mini_xpath = '//a[contains(@class, "compact")]'
    mini_titles_base_xpath = 'span[contains(@class, "card-mini__title")]/text()'
    mini_titles_xpath = f'{mini_xpath}//{mini_titles_base_xpath}'
    mini_links_xpath = f'{mini_xpath}/@href'

    longgrid_xpath = '//a[contains(@class, "longgrid")]'
    longgrid_title_base_xpath = 'h3[contains(@class, "__title")]/text()'
    longgrid_titles_xpath = f'{longgrid_xpath}//{longgrid_title_base_xpath}'
    longgrid_titles_xpath = f'{longgrid_titles_xpath}|{longgrid_xpath}//{mini_titles_base_xpath}'
    longgrid_links_xpath = f'{longgrid_xpath}/@href'

    article_xpath = '//a[contains(@class, "article")]'
    article_titles_xpath = f'{article_xpath}//{longgrid_title_base_xpath}'
    article_links_xpath = f'{article_xpath}/@href'

    titles_xpath = f'{news_titles_xpath}|{mini_titles_xpath}|{longgrid_titles_xpath}|{article_titles_xpath}'
    links_xpath = f'{news_links_xpath}|{mini_links_xpath}|{longgrid_links_xpath}|{article_links_xpath}'
    sources_xpath = '//a[contains(@class, "topic-header__rubric")]/text()|' \
                    '//header//a[contains(@title, "moslenta.ru") and contains(@aria-label, "Лого")]/@title'
    dates_xpath = '//time[contains(@class, "topic-header__time")]/text()|' \
                  '//div[contains(@class, "topline")]//span[contains(@class, "time")]/text()'
    data = parse_news(LENTA_URL, sources_xpath, titles_xpath, dates_xpath, links_xpath, date_format='%H:%M, %d %B %Y')
    return data


def get_ya_news():
    """Parses news from ya.ru."""

    sources_xpath = '//span[contains(@class, "news-story__subtitle-text")]/text()'
    titles_xpath = '//a[contains(@class, "mg-card__link")]/text()'
    dates_xpath = '//meta[contains(@property, "article:published_time")]/@content'
    links_xpath = '//a[contains(@class, "mg-card__link")]/@href'
    data = parse_news(YA_URL, sources_xpath, titles_xpath, dates_xpath, links_xpath)
    return data


def main():
    mailru_data = get_mailru_news()
    lenta_data = get_lenta_news()
    ya_data = get_ya_news()
    data_set = [*mailru_data, *lenta_data, *ya_data]

    mongodb = MongoClient(MONGODB_URI)
    db = mongodb[DB_NAME]
    news = db[COLLECTION_NAME]
    news.create_index(URL_K, name='search_index', unique=True)
    for data in data_set:
        news.replace_one({URL_K: data[URL_K]}, data, upsert=True)


if __name__ == '__main__':
    main()
