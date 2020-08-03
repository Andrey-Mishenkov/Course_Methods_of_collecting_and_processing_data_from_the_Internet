# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst

def get_comments_count(value):
    value = value.strip()
    if (value.isdigit()):
        return int(value)
    return 0

# информация о статье
class HabrParseItem(scrapy.Item):

    _id         = scrapy.Field()
    collection = scrapy.Field(output_processor=TakeFirst())

    post_url    = scrapy.Field(output_processor=TakeFirst())
    title       = scrapy.Field(output_processor=TakeFirst())
    author_name = scrapy.Field(output_processor=TakeFirst())
    author_url  = scrapy.Field(output_processor=TakeFirst())
    images      = scrapy.Field()
    comments    = scrapy.Field(input_processor=MapCompose(get_comments_count), output_processor=TakeFirst())

# информация об авторе
class HabrAuthorParseItem(scrapy.Item):

    _id             = scrapy.Field()
    collection      = scrapy.Field(output_processor=TakeFirst())

    author_url      = scrapy.Field(output_processor=TakeFirst())
    fullname        = scrapy.Field(output_processor=TakeFirst())
    nickname        = scrapy.Field(output_processor=TakeFirst())
    specialization  = scrapy.Field(output_processor=TakeFirst())

    statistics_labels   = scrapy.Field()
    statistics_values   = scrapy.Field()
    tab_info            = scrapy.Field()
    badges              = scrapy.Field()

    sections_names  = scrapy.Field()
    sections_urls   = scrapy.Field()
    posts           = scrapy.Field()
