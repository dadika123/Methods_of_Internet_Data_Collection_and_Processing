import os
import abc
import random
import time
import re
import json
import locale
import dateutil.parser

from threading import Thread, Lock
from typing import Type, List
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver as WebDriverBase
from selenium.webdriver.common.service import Service as ServiceBase
from selenium.webdriver.common.options import ArgOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as exc
from selenium.webdriver.common.action_chains import ActionChains
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv('EMAIL')
PASS = os.getenv('PASS')

TITLE_K = 'title'
SENDER_K = 'from'
DATE_K = 'when'
BODY_K = 'body'

DATE_FORMAT = '%d.%m.%Y %H:%M:%S'

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')


class GenericItemParser:

    def __init__(self, webdriver_cls: Type[WebDriverBase], service: Type[ServiceBase],
                 executable_path: str, options_cls: Type[ArgOptions],
                 options_args: List[str] = None):
        self._wd_cls = webdriver_cls
        self._service_cls = service
        self._exc_path = executable_path
        self._options_cls = options_cls
        self._options_args = options_args

    def run(self):
        options = None
        if self._options_args:
            options = self._options_cls()
            for arg in self._options_args:
                options.add_argument(arg)
        service = self._service_cls(executable_path=self._exc_path)
        with self._wd_cls(service=service, options=options) as driver:
            self._main_worker(driver)
            print('Exiting main worker')

    @abc.abstractmethod
    def _main_worker(self, driver: WebDriverBase):
        pass

    @abc.abstractmethod
    def _side_worker(self, *args, **kwargs):
        pass


class MailRuParser(GenericItemParser):

    def __init__(self, *args, url: str, num_of_threads: int = 10, **kwargs):
        super(MailRuParser, self).__init__(*args, **kwargs)
        self.url = url
        self.email_data = []
        self._urls_pool = []
        self._thread_pool = []
        self._data_lock = Lock()
        self._urls_lock = Lock()
        self._threads_lock = Lock()
        self._max_threads = num_of_threads

    def _main_worker(self, driver: WebDriverBase):
        """Starts thread manager, logins, and scrolls the emails page"""
        thread_manager = Thread(target=self._thread_manager, daemon=True)
        thread_manager.start()

        driver.get(self.url)
        self._login(driver)
        self._accept_cookies(driver)

        # Wait for complete page load
        exc.presence_of_element_located((By.XPATH, '//a[contains(@class, "js-letter-list-item")]'))

        # Scroll until the end
        self._scroll(driver)

        # Wait for all data to be gathered
        while self._threads_alive():
            time.sleep(1)

        # Sort by date and save to file
        self.email_data = sorted(self.email_data, key=lambda d: [DATE_K], reverse=True)
        with open('emails.json', 'w') as f:
            json.dump(self.email_data, f, indent=2, ensure_ascii=False)

    def _scroll(self, driver: WebDriverBase):
        """Scrolls the emails page"""
        prev_element = None
        extracted_urls = []
        while True:
            emails = driver.find_elements(By.XPATH, '//a[contains(@class, "js-letter-list-item")]')
            last_element = emails[-1]
            if last_element == prev_element:
                break
            print('Scrolling...')
            urls = [email.get_attribute('href') for email in emails]
            urls = [url for url in urls if url not in extracted_urls]
            extracted_urls.extend(urls)
            with self._urls_lock:
                self._urls_pool.extend(urls)
            ActionChains(driver).move_to_element(emails[-1]).perform()
            time.sleep(3)
            prev_element = last_element

    def _thread_manager(self):
        """Manages creation and deletion of threads according to URL pool"""
        prev_count = len(self._urls_pool)
        while True:
            with self._urls_lock:
                urls_idx = []
                for idx, url in enumerate(self._urls_pool):
                    if len(self._thread_pool) >= self._max_threads:
                        break
                    print(f'Creating a new thread for {url}')
                    thread = Thread(target=self._side_worker, args=(url,), daemon=True)
                    self._thread_pool.append(thread)
                    thread.start()
                    urls_idx.append(idx)
                for idx in reversed(urls_idx):
                    self._urls_pool.pop(idx)
                if (cur_count := len(self._urls_pool)) != prev_count:
                    prev_count = cur_count
                    print(f'Messages left to cover: {cur_count}')
            dead_idx = []
            with self._threads_lock:
                for idx, thread in enumerate(self._thread_pool):
                    if not thread.is_alive():
                        dead_idx.append(idx)
                for idx in reversed(dead_idx):
                    self._thread_pool.pop(idx)
            time.sleep(0.01)

    def _threads_alive(self):
        """Checks whether any threads are running"""
        with self._threads_lock:
            status = any([thr for thr in self._thread_pool])
        return status

    def _side_worker(self, url):
        """Thread wrapper for parsing specific emails"""
        try:
            self._side_worker_job(url)
        except NoSuchElementException:
            time.sleep(60)
            self._side_worker_job(url)

    def _side_worker_job(self, url):
        """Parses specific email"""
        time.sleep(random.uniform(1, 5))
        options = self._options_cls()
        # options.add_argument('--headless')
        service = self._service_cls(executable_path=self._exc_path)
        with self._wd_cls(service=service, options=options) as driver:
            driver.get(url)
            self._login(driver)
            self._extract_email_data(driver)

    def _extract_email_data(self, driver: WebDriverBase):
        """Extracts email data"""
        wait = WebDriverWait(driver, 60, ignored_exceptions=(StaleElementReferenceException,))
        title = wait.until(
            exc.presence_of_element_located((By.XPATH, '//div[contains(@class, "head__subj__text")]'))).text
        sender = driver.find_element(By.XPATH, '//span[contains(@class, "js-contact-informer")]/span').text
        date = driver.find_element(By.XPATH, '//div[contains(@class, "head__date")]').text
        body = driver.find_element(By.XPATH, '//div[contains(@id, "_BODY")]').text
        print(f'Found email {title}')
        with self._data_lock:
            self.email_data.append({
                TITLE_K: title,
                SENDER_K: sender,
                DATE_K: self._convert_date(date),
                BODY_K: body
            })

    @staticmethod
    def _accept_cookies(driver: WebDriverBase):
        """Accepts cookies if present"""
        wait = WebDriverWait(driver, 10, ignored_exceptions=(StaleElementReferenceException,))
        try:
            cookies_btn = wait.until(
                exc.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Accept')]/../..")))
            cookies_btn.click()
        except TimeoutException:
            pass

    @staticmethod
    def _login(driver: WebDriverBase):
        """Logins to mail.ru"""
        email_xpath = '//input[contains(@class, "email-input") or contains(@name, "username")]'
        pass_xpath = '//input[contains(@class, "password-input") or contains(@name, "password")]'

        wait = WebDriverWait(driver, 60, ignored_exceptions=(StaleElementReferenceException,))
        email = wait.until(exc.element_to_be_clickable((By.XPATH, email_xpath)))
        email.send_keys(EMAIL)
        email.send_keys(Keys.ENTER)

        password = wait.until(exc.visibility_of_element_located((By.XPATH, pass_xpath)))
        password.send_keys(PASS)
        time.sleep(random.uniform(0.5, 1))
        password.send_keys(Keys.ENTER)

    @staticmethod
    def _convert_date(date):
        """Converts given date to a common standard"""
        try:
            date_extracted = dateutil.parser.parse(date)
            output = date_extracted.strftime(DATE_FORMAT)
        except ValueError:
            try:
                date_extracted = datetime.strptime(date, '%d %B, %H:%M')
                now = datetime.now()
                date_extracted.replace(year=now.year)
                output = date_extracted.strftime(DATE_FORMAT)
            except ValueError:
                try:
                    date_extracted = datetime.strptime(date, '%d %B %Y, %H:%M')
                    output = date_extracted.strftime(DATE_FORMAT)
                except ValueError:
                    res = re.search(r'(вчера|сегодня)[^\d]+(\d+):(\d+)', date.lower())
                    if res and (when := res.group(1)) and (hours := res.group(2)) and (minutes := res.group(2)):
                        date_extracted = datetime.now()
                        if when == 'вчера':
                            date_extracted = date_extracted.replace(day=date_extracted.day - 1)
                        date_extracted = date_extracted.replace(hour=int(hours), minute=int(minutes), second=0,
                                                                microsecond=0)
                        output = date_extracted.strftime(DATE_FORMAT)
                    else:
                        raise ValueError
        return output


def main():
    mailru_parser = MailRuParser(webdriver_cls=webdriver.Chrome, service=Service,
                                 executable_path='./chromedriver', options_cls=Options,
                                 url='https://mail.ru/')
    mailru_parser.run()


if __name__ == '__main__':
    main()
