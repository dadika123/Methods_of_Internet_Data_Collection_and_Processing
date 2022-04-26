"""
Collect vacancies information from hh.ru and superjob.ru.
"""
import re

import requests

from lesson2.generic import get_vacancies_from_pages

HH_URL = 'hh.ru'
SJ_URL = 'superjob.ru'
PROT = 'https://'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0'
}
MAX_PAGES = 1_000_000


def get_hh_vacancies(position: str, pages: int) -> dict:
    """
    Gets certain positions from hh.ru from a number
    of pages and returns them as a DataFrame.

    :param position: name of a vacancy to search.
    :param pages: amount of pages to cover.
    :return: vacancies data dict.
    """
    pages_t = 'a.bloko-button[data-qa=pager-page] span'
    container_t = 'div.vacancy-serp-item'
    position_t = 'a[data-qa=vacancy-serp__vacancy-title]'
    url_t = 'a[data-qa=vacancy-serp__vacancy-title]'
    salary_t = 'span.bloko-header-section-3[data-qa=vacancy-serp__vacancy-compensation]'
    requester = lambda page: requests.get(f'{PROT}{HH_URL}/search/vacancy',
                                          params={'text': position, 'page': page},
                                          headers=HEADERS)
    vac_data = get_vacancies_from_pages(HH_URL, pages, requester, pages_t, container_t, position_t, url_t, salary_t)
    return vac_data


def get_superjob_vacancies(position: str, pages: int) -> dict:
    """
    Gets certain positions from superjob.ru from a number
    of pages and returns them as a DataFrame.

    :param position: name of a position to search.
    :param pages: amount of pages to cover.
    :return: vacancies data dict.
    """
    pages_t = ('a', {'class': re.compile(r'f-test-button-\d+')})
    container_t = 'div.f-test-vacancy-item'
    position_t = (('a', {'class': re.compile(r'f-test-link-\w+')}), 0)
    url_t = (('a', {'class': re.compile(r'f-test-link-\w+')}), 0)
    salary_t = ('span.f-test-text-company-item-salary span', 0)
    requester = lambda page: requests.get(f'{PROT}{SJ_URL}/vacancy/search/',
                                          params={'keywords': position, 'page': page},
                                          headers=HEADERS)
    vac_data = get_vacancies_from_pages(SJ_URL, pages, requester, pages_t, container_t, position_t, url_t, salary_t)
    return vac_data


def main():
    position = 'Разработчик'
    hh_df = get_hh_vacancies(position, 2)
    sj_df = get_superjob_vacancies(position, 2)
    # websites_df = pd.concat([hh_df, sj_df])
    # websites_df.to_csv('collected_data.csv', index=False)


if __name__ == '__main__':
    main()
