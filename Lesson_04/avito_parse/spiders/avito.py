import scrapy
from pymongo import MongoClient

class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['avito.ru']
    # start_urls = ['https://avito.ru/himki/kvartiry/prodam-ASgBAgICAUSSA8YQ']
    # start_urls = ['https://avito.ru/ramenskoe/kvartiry/prodam-ASgBAgICAUSSA8YQ']
    start_urls = ['https://www.avito.ru/bronnitsy/kvartiry/prodam-ASgBAgICAUSSA8YQ']

    __visited_pages = []
    __list_adv = []

    xpath_sel = {
        'pagination': '//span[@class="pagination-item-1WyVp"]/text()',
        'catalog': '//div[contains(@class, "js-catalog-list")]',
        'adv_url': '//div[contains(@class, "id")]//a[contains(@class, "snippet-link")]/@href'
    }

    adv_page_data = {
        'title': '//span[contains(@class, "title-info-title-text")]/text()',
        'price':    '//span[contains(@itemprop, "price")]/@content',
        'param_name':   '//span[contains(@class, "item-params-label")]/text()',
        'param_value':  '//li[@class="item-params-list-item"]/text()',
    }

    def __init__(self):
        db_client = MongoClient('localhost', 27017)
        db = db_client['avito']
        self.collection = db['avito_apartments']

    # todo получение индекса страницы (...)
    def get_index_last_page(list_pages):
        try:
            result = list_pages.index('page(...)')
        except Exception:
            result = -1
        return result

    # todo получение списка url страниц ленты
    def get_list_urls_pages(self, response, list_pagination):
        result = []

        # удаление нечисловых элементов
        for item in list_pagination:
            if not item.isdigit():
                list_pagination.remove(item)

        # формирование списка url страниц объявлений
        for item in list_pagination:
            url = f'{self.start_urls[0]}?p={item}'

            if (url not in self.__visited_pages):
                result.append(url)

        return result

    # todo проверка на пустую страницу
    def is_empty_page(self, response):
        result = not bool(response.xpath(self.xpath_sel['catalog']))
        return result

    # todo
    def parse(self, response):
        if response.url not in self.__visited_pages:

            self.__visited_pages.append(response.url)
            print()
            print(f'Страница N {len(self.__visited_pages)} = ', response.url)

            # проверка на пустую страницу
            is_empty_page = self.is_empty_page(response)
            if (is_empty_page):
                print('Пустая страница = ', response.url)
                return

            # пагинация
            list = response.xpath(self.xpath_sel['pagination']).extract()
            list_pagination = self.get_list_urls_pages(response, list)
            # print(list_pagination)

            for page_url in list_pagination:
                if page_url not in self.__visited_pages:
                    yield response.follow(page_url, callback=self.parse)

            # список объявлений
            list_adv_urls = response.xpath(self.xpath_sel['adv_url']).extract()
            for adv_url in list_adv_urls:
                yield response.follow(adv_url, callback=self.adv_parse)

    # объявление
    def adv_parse(self, response):
        adv_item = {}

        # заголовок, url, цена
        adv_item['title'] = response.xpath(self.adv_page_data['title']).extract_first()
        adv_item['url'] = response.url
        adv_item['price'] = response.xpath(self.adv_page_data['price']).extract_first()

        # наименования параметров объявления
        list_params = response.xpath(self.adv_page_data['param_name']).extract()
        for i in range(len(list_params)):
            list_params[i] = list_params[i].replace(u'\xa0', u' ').strip()

        # значения параметров объявления
        list_values = response.xpath(self.adv_page_data['param_value']).extract()
        for i, item in reversed(list(enumerate(list_values))):
            item = item.replace(u'\xa0', u' ').strip()
            if item == '':
                del list_values[i]
            else:
                list_values[i] = item

        dict_params = {}
        for i, item in enumerate(list_params):
            if (i <= len(list_values)):
                dict_params[item] = list_values[i]

        # параметры объявления
        adv_item['params'] = dict_params

        # запись в базу
        self.collection.insert_one(adv_item)
        self.__list_adv.append(adv_item)

        print()
        print(f'Квартира N {len(self.__list_adv) + 1} = {adv_item}')

