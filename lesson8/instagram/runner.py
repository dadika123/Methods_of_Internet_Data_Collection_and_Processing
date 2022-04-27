from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from instagram.spiders.profiles import ProfilesSpider
from instagram import settings


def main():
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(ProfilesSpider, profiles=['kaenmuenchen', 'odessa_feinkost'])

    process.start()


if __name__ == '__main__':
    main()
