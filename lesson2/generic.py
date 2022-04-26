import re
from typing import Callable, Tuple, Dict, Union, List

import requests
from bs4 import BeautifulSoup, Tag
from bs4.element import ResultSet

POSITIONS_K = 'Position'
URL_K = 'URL'
MIN_SALARY_K = 'Minimum Salary'
MAX_SALARY_K = 'Maximum Salary'
CURRENCY_K = 'Currency'
WEBSITE_K = 'Website'
SALARY_RE = re.compile(r'(\d+\s?\d+)')
CURRENCY_RE = re.compile(r'\d+\s+([a-zA-Zа-яА-я]+)\.*$')

GenericFindType = Union[Tuple[str, Dict[str, re.Pattern]], str]
FindType = Union[GenericFindType, Tuple[GenericFindType, int]]


def find(to_find: FindType, loc: Union[BeautifulSoup, Tag]) -> Union[ResultSet, Tag, List[Tag]]:
    position = None
    # Check if position is specified
    if isinstance(to_find, tuple) and isinstance(to_find[-1], int):
        to_find, position = to_find
    # Find stuff
    if isinstance(to_find, str):
        query = loc.select(to_find)
    elif isinstance(to_find, tuple):
        query = loc.find_all(*to_find)
    else:
        raise Exception(f'Unknown expression {to_find}')
    if len(query) > 1 and position is not None:
        return query[position]
    return query if not query or len(query) > 1 else query[0]


def vacancy_parser(response: requests.Response,
                   container_t: FindType,
                   position_t: FindType,
                   url_t: FindType,
                   salary_t: FindType) -> tuple:
    """

    :param response: website get response to a
        vacancy list.
    :param container_t: BeautifulSoup select
        string for vacancy card container.
    :param position_t: BeautifulSoup select
        string for position container.
    :param url_t: BeautifulSoup select
        string for URL container.
    :param salary_t: BeautifulSoup select
        string for salary container.
    :return: positions, urls, salaries lists
    """
    dom = BeautifulSoup(response.text, 'html.parser')
    vacancies = find(container_t, dom)
    positions, urls, min_salaries, max_salaries, currencies = [], [], [], [], []
    for vacancy in vacancies:
        position = find(position_t, vacancy).get_text()
        url = find(url_t, vacancy).get('href')
        salary_tag = find(salary_t, vacancy)
        salary = salary_tag.get_text() if salary_tag else ''
        salary = salary.replace(u'\xa0', ' ').replace(u'\u202f', ' ')
        salary_search = re.findall(SALARY_RE, salary)
        salary_min, salary_max, currency = '', '', ''
        if len(salary_search) == 1:
            currency = re.search(CURRENCY_RE, salary).group(1)
            salary_value = int(salary_search[0].replace(' ', ''))
            if 'от' in salary:
                salary_min = salary_value
            elif 'до' in salary:
                salary_max = salary_value
            else:
                salary_min = salary_value
        elif len(salary_search) == 2:
            currency = re.search(CURRENCY_RE, salary).group(1)
            salary_min, salary_max = int(salary_search[0].replace(' ', '')), int(salary_search[1].replace(' ', ''))
        positions.append(position)
        urls.append(url)
        min_salaries.append(salary_min)
        max_salaries.append(salary_max)
        currencies.append(currency)
    return positions, urls, min_salaries, max_salaries, currencies


def get_max_pages(response: requests.Response, pages_t: FindType) -> int:
    """
    Gets maximum number of pages from a page.

    :param response: website get response to a
        vacancy list.
    :param pages_t: BeautifulSoup select
        string for pagination container.
    :return: maximum number of pages.
    """
    dom = BeautifulSoup(response.text, 'html.parser')
    pages = find(pages_t, dom)
    return int(pages[-1].getText())


def get_vacancies_from_pages(website_url: str,
                             pages: int,
                             requester: Callable,
                             pages_t: FindType,
                             container_t: FindType,
                             position_t: FindType,
                             url_t: FindType,
                             salary_t: FindType) -> dict:
    """
    Gets certain positions from a given
    website within a number of pages and
    returns them as a DataFrame.

    :param website_url: website to collect data.
    :param pages: amount of pages to cover.
    :param requester: function to request data
        with page as argument.
    :param pages_t: BeautifulSoup select
        string for pagination container.
    :param container_t: BeautifulSoup select
        string for vacancy card container.
    :param position_t: BeautifulSoup select
        string for position container.
    :param url_t: BeautifulSoup select
        string for URL container.
    :param salary_t: BeautifulSoup select
        string for salary container.
    :return: vacancies data dict
    """
    vacancies = {POSITIONS_K: [], URL_K: [], MIN_SALARY_K: [], MAX_SALARY_K: [], CURRENCY_K: []}
    response = requester(1)
    response.raise_for_status()
    max_pages = get_max_pages(response, pages_t)
    pages = max_pages if pages > max_pages else pages
    if pages < 1:
        raise Exception(f'Incorrect pages number, should be greater than 0')
    for page in range(1, pages):
        response = requester(page)
        response.raise_for_status()
        results = vacancy_parser(response, container_t, position_t, url_t, salary_t)
        positions, urls, min_salaries, max_salaries, currencies = results
        vacancies[POSITIONS_K].extend(positions)
        vacancies[URL_K].extend([f'{website_url}{url}' if website_url not in url else url for url in urls])
        vacancies[MIN_SALARY_K].extend(min_salaries)
        vacancies[MAX_SALARY_K].extend(max_salaries)
        vacancies[CURRENCY_K].extend(currencies)
    vacancies[WEBSITE_K] = [website_url for _ in vacancies[POSITIONS_K]]
    return vacancies
