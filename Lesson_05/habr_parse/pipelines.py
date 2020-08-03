# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient

class HabrParsePipeline:

    def __init__(self):

        db_client = MongoClient('localhost', 27017)
        self.db = db_client['habr']

        collection = self.db['habr_posts']
        if (collection.estimated_document_count() > 0):
            collection.delete_many({})

        collection = self.db['habr_authors']
        if (collection.estimated_document_count() > 0):
            collection.delete_many({})

    def process_item(self, item, spider):

        collection = self.db[item['collection']]
        collection.insert_one(item)

        return item
