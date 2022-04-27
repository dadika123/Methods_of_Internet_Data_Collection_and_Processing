from urllib.parse import urlencode

import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem

PARAMS_BASE = {
    'geo[t][0]': 4
}

URLS_PARAMS = [
    {**PARAMS_BASE, 'keywords': 'python'},
]


class SuperjobSpider(scrapy.Spider):
    name = 'superjob'
    allowed_domains = ['superjob.ru']
    url_base = 'https://superjob.ru/vacancy/search/?'

    def __init__(self, **kwargs):
        super(SuperjobSpider, self).__init__(**kwargs)
        self.start_urls = []
        for params in URLS_PARAMS:
            self.start_urls.append(f'{self.url_base}?{urlencode(params, doseq=True)}')

    def parse(self, response: HtmlResponse, **kwargs):
        next_page = response.xpath('//a[@rel="next"]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath('//div[contains(@class, "f-test-vacancy-item")]'
                               '//a[contains(@class, "f-test-link-") and @target="_blank"]/@href').getall()
        for url in links:
            card = response.xpath(f'//a[contains(@href, "{url}")]')
            position = ''.join(card.xpath(f'text()|span/text()').getall())
            salary = card.xpath('../../span[contains(@class, "f-test-text-company-item-salary")]//text()').getall()
            yield JobparserItem(position=position, salary=salary, url=url)
