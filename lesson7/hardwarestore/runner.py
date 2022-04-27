from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from hardwarestore.spiders.leroymerlin import LeroymerlinSpider
from hardwarestore import settings


def main():
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(LeroymerlinSpider, category='lyustry')

    process.start()


if __name__ == '__main__':
    main()
