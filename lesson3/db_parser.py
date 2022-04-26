"""
Collect vacancies information from hh.ru and superjob.ru.
"""
from pprint import pprint
from typing import Callable, List

from pymongo import MongoClient

from lesson2.generic import URL_K, POSITIONS_K, MIN_SALARY_K, MAX_SALARY_K, CURRENCY_K, WEBSITE_K
from lesson2.parser import get_hh_vacancies, get_superjob_vacancies, MAX_PAGES

MONGODB_URI = '127.0.0.1:27017'
DB_NAME = 'vacancy_db'
COLLECTION_NAME = 'vacancy'


class VacancyParser:
    def __init__(self, uri: str = MONGODB_URI, db_name: str = DB_NAME,
                 collection: str = COLLECTION_NAME):
        self.mongodb = MongoClient(uri)
        self.db = self.mongodb[db_name]
        self.vacancies = self.db[collection]
        self.vacancies.create_index(URL_K, name='search_index', unique=True)

    def update_vacancies(self, position: str):
        self._update_vacancies(get_hh_vacancies, position)
        self._update_vacancies(get_superjob_vacancies, position)

    def get_currencies(self) -> List[str]:
        currency_list = []
        for currency in self.vacancies.find().distinct(CURRENCY_K):
            if currency:
                currency_list.append(currency)
        return currency_list

    def get_vacancies(self, threshold: int, currency: str) -> list:
        query_params = {'$or': [
            {MIN_SALARY_K: {'$gte': threshold}},
            {MAX_SALARY_K: {'$gte': threshold}}
        ]}
        if currency:
            if currency not in (currencies := self.get_currencies()):
                raise Exception(f'Currency {currency} is not one of {", ".join(currencies)}')
            query_params = {'$and': [{CURRENCY_K: currency}, query_params]}
        query_set = self.vacancies.find(query_params)
        return [query for query in query_set]

    def _update_vacancies(self, getter: Callable, position: str):
        vacancies_data = getter(position, MAX_PAGES)
        for idx, vacancy_url in enumerate(vacancies_data[URL_K]):
            data = {
                POSITIONS_K: vacancies_data[POSITIONS_K][idx],
                URL_K: vacancy_url,
                MIN_SALARY_K: vacancies_data[MIN_SALARY_K][idx],
                MAX_SALARY_K: vacancies_data[MAX_SALARY_K][idx],
                CURRENCY_K: vacancies_data[CURRENCY_K][idx],
                WEBSITE_K: vacancies_data[WEBSITE_K][idx]
            }
            self.vacancies.replace_one({URL_K: vacancy_url}, data, upsert=True)


def main():
    vac_parser = VacancyParser()
    # vac_parser.update_vacancies('Python')
    currencies = vac_parser.get_currencies()
    correct = False
    currency = ''
    while not correct:
        currency = input(f'Enter a currency. Possible currencies '
                         f'are {", ".join(currencies)} or skip for any: ')
        if currency not in currencies:
            print(f'Incorrect currency {currency}! Try again...')
            continue
        correct = True

    correct = False
    while not correct:
        salary = input(f'Enter a minimal salary for search: ')
        try:
            salary = int(salary)
            if salary < 0:
                raise ValueError
        except ValueError:
            print(f'Salary must be a positive integer, not {salary}! Try again...')
            continue
        vacancies = vac_parser.get_vacancies(salary, currency)
        pprint(vacancies)
        correct = True


if __name__ == '__main__':
    main()
