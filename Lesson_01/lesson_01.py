import json
import requests

class Catalog:

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0',
               }

    params = {"records_per_page": 50,
              }

    def __init__(self):
        self.__categories = []

    # Загрузка списка товарных категорий
    def load_categories(self, url, is_debug=False):

        if (is_debug):
            print('-' * 200)
            print('Загрузка списка товарных категорий')

        response = requests.get(url, headers=self.headers, params={})
        self.__categories = response.json()

        if (is_debug):
            print('Категории успешно загружены!')
            print()
            self.print_categories()

    # Вывод списка категорий
    def print_categories(self):

        print('-' * 200)
        print('Список товарных категорий:')
        print('-' * 200)
        i = 0
        total_count = len(self.__categories)
        for category in self.__categories:

            i += 1
            category_code = category['parent_group_code']
            category_name = category['parent_group_name']

            print(f'\t{i} из {total_count}; \tКод = {category_code}; \tНаименование = {category_name}')
        print()

    # Загрузка спец предложений
    def load_spec_offers(self, url, is_debug=False):

        params = {"records_per_page": 50, }
        if (is_debug):
            print('-' * 200)
            print(f'Загрузка спецпредложений по товарной категории:')
            print('-' * 200)

        i = 0
        total_count = len(self.__categories)
        for category in self.__categories:

            i += 1
            category_code = category['parent_group_code']
            category_name = category['parent_group_name']

            params['categories'] = category_code

            response = requests.get(url, headers=self.headers, params=params)
            category_products = response.json()
            category['products'] = category_products
            count_offers = len(category_products['results'])

            if (is_debug):
                print(f'{i} из {total_count}; \tКод = {category_code}; \tНаименование = {category_name}; \tКоличество предложений = {count_offers}')

        if (is_debug):
            print()

    # Запись всех спецпредложений по товарным категориям в отдельные файлы
    def save_spec_offers_to_file(self, is_debug=False):

        bad_symbols = list('\/:*?"<>|') + ["\n", "\t", "\r"]
        if (is_debug):
            print('-' * 200)
            print(f'Запись файла с товарами из товарной категории:')
            print('-' * 200)

        i = 0
        total_count = len(self.__categories)
        for category in self.__categories:

            i += 1
            category_code = category['parent_group_code']
            category_name = category['parent_group_name']
            category_products = category['products']
            count_offers = len(category_products['results'])

            if (is_debug):
                print(f'\t{i} из {total_count}; \tКод = {category_code}; \tНаименование = {category_name}; \tКоличество предложений = {count_offers}')

            # Удаление служебных символов из имени файла
            category_name = ''.join(i for i in category_name if not i in bad_symbols)
            filename = f'{category_code}_{category_name}.json'

            with open(filename, 'w', encoding='UTF-8') as file:
                json.dump(category_products, file, ensure_ascii=False)

        if (is_debug):
            print()

if __name__ == '__main__':

    is_debug = True
    calatog = Catalog()

    calatog.load_categories('https://5ka.ru/api/v2/categories/', is_debug)
    calatog.load_spec_offers('https://5ka.ru/api/v2/special_offers/', is_debug)
    calatog.save_spec_offers_to_file(is_debug)

    print('finish')