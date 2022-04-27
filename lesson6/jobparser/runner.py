from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from jobparser import settings
from jobparser.spiders.hhru import HhruSpider
from jobparser.spiders.superjob import SuperjobSpider


def start_hh_crawler(crawler_settings=None):
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(HhruSpider)

    process.start()


def start_superjob_crawler(crawler_settings=None):
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(SuperjobSpider)

    process.start()


def main():
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    # start_hh_crawler(crawler_settings)
    start_superjob_crawler(crawler_settings)


if __name__ == '__main__':
    main()
