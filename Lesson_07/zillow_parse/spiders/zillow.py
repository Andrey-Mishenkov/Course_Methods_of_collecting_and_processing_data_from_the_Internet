from time import sleep
import scrapy
from scrapy.loader import ItemLoader
from zillow_parse.items import ZillowParseItem
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class ZillowSpider(scrapy.Spider):

    name = 'zillow'
    allowed_domains = ['www.zillow.com']
    start_urls = ['https://www.zillow.com']

    browser = webdriver.Firefox()

    xpath_sel_page = {
        'pagination': '//div//nav//ul//a[contains(@class, "PaginationButton")]/@href',
        'adv':    '//div//ul//li//div//a[contains(@class, "list-card-link")]/@href'
    }

    xpath_sel_adv = {
        'price':        '//div[@class="ds-chip"]//h3//span/span[@class="ds-value"]/text()',
        'address':      '//div[@class="ds-chip"]//h1[@class="ds-address-container"]//span/text()',
        'media_col':    '//div[contains(@class, "ds-media-col")]',
        'media_stream': '//ul[@class="media-stream"]/li//picture/source[@type="image/jpeg"]',
        'photo_set':    '//div//ul//li//picture[contains(@class, "media-stream-photo")]/img',
        'photo_url':    '//div//ul//li//picture[contains(@class, "media-stream-photo")]/img/@src',
    }

    def __init__(self, search_location: str, *args, **kwargs):

        self.start_urls[0] = f'{self.start_urls[0]}{search_location}'
        super().__init__(*args, **kwargs)

    # todo разбор страниц
    def parse(self, response):
        print('\nСтраница =', response.url)

        list_pagination = response.xpath(self.xpath_sel_page['pagination']).extract()
        for page_url in list_pagination:
            yield response.follow(page_url, callback=self.parse)

        # список объявлений
        list_adv = response.xpath(self.xpath_sel_page['adv']).extract()
        for adv_url in list_adv:
            yield response.follow(adv_url, callback=self.parse_adv)

    # todo скроллинг ленты фото
    def scroll_and_sleep(self, time_sleep):
        media_col = self.browser.find_element_by_xpath(self.xpath_sel_adv['media_col'])
        len_images = len(self.browser.find_elements_by_xpath(self.xpath_sel_adv['media_stream']))

        while True:
            media_col.send_keys(Keys.PAGE_DOWN)
            media_col.send_keys(Keys.PAGE_DOWN)
            media_col.send_keys(Keys.PAGE_DOWN)
            media_col.send_keys(Keys.PAGE_DOWN)

            sleep(time_sleep)

            len_tmp = len(self.browser.find_elements_by_xpath(self.xpath_sel_adv['media_stream']))
            if (len_tmp == len_images):
                break
            len_images = len_tmp

    # todo разбор объявления
    def parse_adv(self, response):
        print('\nОбъявление =', response.url)

        self.browser.get(response.url)

        # скроллинг ленты фото
        self.scroll_and_sleep(1)

        # todo формирование списка url всех фото
        list_photo_url = []
        list_obj = self.browser.find_elements_by_xpath(self.xpath_sel_adv['photo_set'])
        for itm in list_obj:
            list_photo_url.append(itm.get_attribute('src'))

        # todo заполнение Item
        item = ItemLoader(ZillowParseItem(), response)

        item.add_value('adv_url',  response.url)
        item.add_xpath('address',  self.xpath_sel_adv['address'])
        item.add_xpath('price',    self.xpath_sel_adv['price'])
        item.add_value('photos',   list_photo_url)

        yield item.load_item()