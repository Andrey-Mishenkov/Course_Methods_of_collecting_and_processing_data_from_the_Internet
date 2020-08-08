# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from unicodedata import normalize

# todo преобразование цены в число
def get_clean_price(value):
    value = value.strip().replace('$', '').replace(',', '')
    if (value.isdigit()):
        return int(value)
    return 0

# todo удаление служебных символов из элементов адреса
def get_clean_address(value):
    value = normalize('NFKD', ''.join(value).strip()).replace('  ', ' ')
    return value

class ZillowParseItem(scrapy.Item):

    _id         = scrapy.Field()
    adv_url     = scrapy.Field(output_processor=TakeFirst())
    price       = scrapy.Field(input_processor=MapCompose(get_clean_price),     output_processor=TakeFirst())
    address     = scrapy.Field(input_processor=MapCompose(get_clean_address),   output_processor=Join())
    photos      = scrapy.Field()

