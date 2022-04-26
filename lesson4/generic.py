import re
import locale

import dateutil.parser
from datetime import datetime

import requests
from lxml import html
from lxml.etree import _ElementTree as Dom, XPathEvalError

PROT = 'https://'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0'
}

SRC_NAME_K = 'source'
TITLE_K = 'title'
DATE_K = 'date'
URL_K = 'url'
DATE_FORMAT = '%d.%m.%Y %H:%M:%S'

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')


def get_parse_dom(url: str, headers: dict = None) -> Dom:
    """
    Makes a request, parses DOM tree and returns it.

    :param url: URL to parse.
    :param headers: additional headers.
    :return: DOM tree object.
    """

    headers = HEADERS if headers is None else headers
    request = requests.get(url if PROT in url else f'{PROT}{url}', headers=headers)

    dom = html.fromstring(request.text)
    dom.make_links_absolute(url)

    return dom


def parse(dom: Dom, xpath: str) -> list:
    """
    Parses DOM with xpath, used to catch errors properly.

    :param dom: DOM tree object.
    :param xpath: xpath path to evaluate.
    :return: list result of search.
    """

    try:
        return dom.xpath(xpath)
    except XPathEvalError as e:
        raise XPathEvalError(e)


def parse_news(url: str, sources_xpath: str, titles_xpath: str, dates_xpath: str,
               links_xpath: str, from_links: bool = True, headers: dict = None,
               date_format: str = DATE_FORMAT) -> list:
    """
    Parses news on a given URL with given xpaths.

    :param url: news website URL.
    :param sources_xpath: xpath sources text paths.
    :param titles_xpath: xpath title text paths.
    :param dates_xpath: xpath published dates' paths.
    :param links_xpath: xpath article URL paths.
    :param from_links: get source and date data from links.
    :param headers: additional request headers.
    :param date_format: date format to parse date with.
    :return: result as a list of dicts.
    """

    dom = get_parse_dom(url, headers)
    sources, titles, dates, links = [], [], [], []

    links = list(set(parse(dom, links_xpath)))

    for title in list(set(parse(dom, titles_xpath))):
        titles.append(title.replace(u'\xa0', u' ').strip())

    if from_links:
        for link in links:
            dom = get_parse_dom(link)
            post_sources = []
            for source in parse(dom, sources_xpath):
                post_sources.append(source.replace(u'\xa0', u' ').strip())
            if len(post_sources) == 1:
                sources.extend(post_sources)
            else:
                sources.append(post_sources)

            post_dates = []
            for date in parse(dom, dates_xpath):
                try:
                    post_dates.append(dateutil.parser.parse(date))
                except ValueError:
                    try:
                        post_dates.append(datetime.strptime(date, date_format))
                    except ValueError:
                        res = re.search(r'(вчера|сегодня)[^\d]+(\d+):(\d+)', date.lower())
                        if res and (when := res.group(1)) and (hours := res.group(2)) and (minutes := res.group(2)):
                            date = datetime.now()
                            if when == 'вчера':
                                date = date.replace(day=date.day - 1)
                            date = date.replace(hour=int(hours), minute=int(minutes), second=0, microsecond=0)
                        post_dates.append(date)
            if len(post_dates) <= 1:
                dates.extend(post_dates)
            else:
                dates.append(post_dates)
    else:
        sources_raw = parse(dom, sources_xpath)
        for src in sources_raw:
            sources.append(src.replace(u'\xa0', u' ').strip())

        dates = parse(dom, dates_xpath)

    max_len = max(len(sources), len(titles), len(dates), len(links))
    check_lists = [sources, titles, dates, links]
    if not all(len(lst) == max_len for lst in check_lists):
        raise ValueError('Not all lists have the same length')

    obj_list = []
    for source, title, date, link in zip(sources, titles, dates, links):
        obj_list.append({
            TITLE_K: title,
            URL_K: link,
            SRC_NAME_K: source,
            DATE_K: date.strftime(DATE_FORMAT)
        })

    return obj_list
