# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
import os
from urllib.parse import urlparse

class ZillowParsePipeline:

    def __init__(self):

        db_client = MongoClient('localhost', 27017)
        self.db = db_client['zillow']

        collection = self.db['zillow_apparts']
        if (collection.estimated_document_count() > 0):
            collection.delete_many({})

    def process_item(self, item, spider):

        collection = self.db['zillow_apparts']
        collection.insert_one(item)

        return item

# работа с фото
class ImgPipeline(ImagesPipeline):

    # id объявления
    adv_id = ''

    # изменение имени файла = id абъявления + имя файла из url
    def file_path(self, request, response=None, info=None):
        file_name = f'image_files/{self.adv_id}_{os.path.basename(urlparse(request.url).path)}'
        return file_name

    def get_media_requests(self, item, info):

        # получение id объявления; используется для нового имени файла
        local_id = ''
        try:
             local_id = item['adv_url'].split('/')[-2]
        except Exception as e:
            print(e)

        if self.adv_id != local_id:
            self.adv_id = local_id

        for url in item.get('photos', []):
            try:
                yield Request(url)
            except ValueError as e:
                print(e)

    def item_completed(self, results, item, info):
        item['photos'] = [itm[1] for itm in results]
        return item
