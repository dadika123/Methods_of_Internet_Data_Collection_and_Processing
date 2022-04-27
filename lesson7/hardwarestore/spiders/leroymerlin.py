import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader

from hardwarestore.items import HardwarestoreItem


class LeroymerlinSpider(scrapy.Spider):
    name = 'leroymerlin'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, category, **kwargs):
        super(LeroymerlinSpider, self).__init__(*kwargs)
        self.cat = category
        self.start_urls = [f'https://leroymerlin.ru/catalogue/{category}/']

    def parse(self, response: HtmlResponse, **kwargs):
        next_page = response.xpath('//a[@data-qa-pagination-item="right"]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath('//div[contains(@class, "largeCard")]/a[@data-qa="product-name"]/@href')
        for link in links:
            yield response.follow(link, callback=self.parse_product)

    @staticmethod
    def parse_product(response: HtmlResponse):
        loader = ItemLoader(item=HardwarestoreItem(), response=response)
        loader.add_xpath('name', '//h1/text()')
        loader.add_xpath('price', '//span[@slot="price"]/text()')
        loader.add_value('url', response.url)
        loader.add_xpath('photos', '//img[@alt="product image"]/@src')
        loader.add_xpath('properties', '//div[contains(@class, "def-list__group")]'
                                       '/*[self::dt or self::dd]/text()')
        yield loader.load_item()
