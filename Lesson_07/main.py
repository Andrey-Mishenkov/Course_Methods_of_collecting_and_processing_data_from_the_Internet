from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from zillow_parse import settings
from zillow_parse.spiders.zillow import ZillowSpider

if __name__ == '__main__':

    crawl_settings = Settings()
    crawl_settings.setmodule(settings)
    crawl_proc = CrawlerProcess(settings=crawl_settings)
    crawl_proc.crawl(ZillowSpider, '/homes/Detroit/')
    crawl_proc.start()