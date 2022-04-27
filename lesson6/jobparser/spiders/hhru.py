from urllib.parse import urlencode

import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem

PARAMS_BASE = {
    'area': 1,
    'search_field': [
        'name',
        'company_name',
        'description'
    ],
    'items_on_page': 20
}

URLS_PARAMS = [
    {**PARAMS_BASE, 'text': 'python'},
]


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    url_base = 'https://hh.ru/search/vacancy'

    def __init__(self, **kwargs):
        super(HhruSpider, self).__init__(**kwargs)
        self.start_urls = []
        for params in URLS_PARAMS:
            self.start_urls.append(f'{self.url_base}?{urlencode(params, doseq=True)}')

    def parse(self, response: HtmlResponse, **kwargs):
        next_page = response.xpath('//a[@data-qa="pager-next"]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links_xpaths = response.xpath('//a[@data-qa="vacancy-serp__vacancy-title"]/@href')
        for l_xpath in links_xpaths:
            link = l_xpath.get()
            yield response.follow(link, callback=self.vacancy_parse)

    @staticmethod
    def vacancy_parse(response: HtmlResponse):
        position = response.xpath('//h1//text()').get()
        salary = response.xpath('//div[@data-qa="vacancy-salary"]//text()').getall()
        url = response.url
        yield JobparserItem(position=position, salary=salary, url=url)

