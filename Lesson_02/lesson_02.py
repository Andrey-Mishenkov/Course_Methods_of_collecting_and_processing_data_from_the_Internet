from bs4 import BeautifulSoup as bs
import requests
import re
import json

class BlogParser:

    __domain = 'https://geekbrains.ru'

    def __init__(self):
        self.__post_dict = {}
        self.__page_dict = {}
        self.__page_set = set()

    # todo получение объекта soup по url
    def get_soup(self, url):

        response = requests.get(url)
        soup = bs(response.text, 'lxml')
        return soup

    # todo основная процедура - перебор страниц и статей
    def run_parse_blog(self, url, debug_page_limit = 0, is_debug=False):

        if debug_page_limit and len(self.__page_set) >= debug_page_limit:
            print(f'Тестовый режим; Парсинг остановлен;'
                  f'Задано ограничение количества страниц = {debug_page_limit}')
            return

        print(f'\nСтраница {len(self.__page_set)}; \t{url}')
        soup = self.get_soup(url)

        ul = soup.find('ul', attrs={'class': 'gb__pagination'})
        if ul:
            current_page_dict = {f'{self.__domain}{a.get("href")}': 0 for a in ul.find_all('a') if a.get("href")}
            self.__page_dict.update(current_page_dict)

        # todo разбор статей на странице - получение заголовков и ссылок
        posts = soup.find_all('a', {'class': ['post-item__title']})
        for post in posts:

            post_url = f'{self.__domain}{post.get("href")}'
            post_title = post.text

            if (is_debug):
                print(f'\tСтатья {len(self.__post_dict)}\t{post_title};\t{post_url}')

            if (not post_url in self.__post_dict):
                self.__post_dict[post_url] = {'title': post_title, 'post_url': post_url}

                # todo разбор страницы статьи
                self.parse_post(post_url, is_debug)

        # todo рекурсивный перебор страниц со списком статей
        for url in current_page_dict.keys():
            if (not url in self.__page_set):

                # if debug_page_limit and len(self.__page_set) >= debug_page_limit:
                #     print(f'Тестовый режим; Парсинг остановлен;'
                #           f'Задано ограничение количества страниц = {debug_page_limit}')
                #     return

                self.__page_set.add(url)
                self.run_parse_blog(url, debug_page_limit, is_debug)

    # todo разбор страницы со статьей
    def parse_post(self, url, is_debug=False):
        soup = self.get_soup(url)

        # todo автор
        author = soup.find_all('div', {'itemprop': ['author']})[0].text

        # todo страница автора
        author_page = soup.find_all('a', href = re.compile("/users/"))
        author_page_url = f'{self.__domain}{author_page[0].get("href")}'

        # todo ссылки на теги
        tags_urls = []
        tags = soup.find_all('a', {'class': ['small']})
        for tag in tags:
            tags_urls.append(f'{self.__domain}{tag.get("href")}')

        self.__post_dict[url]['writer_name']   = author
        self.__post_dict[url]['writer_url']    = author_page_url
        self.__post_dict[url]['tags_urls']     = tags_urls

    # todo запись данных в файл
    def save_info_to_file(self, is_debug=False):

        if (is_debug):
            print(f'\nЗапись файла:')
            print('-' * 200)

        post_list = []
        i = 0
        total_count = len(self.__post_dict)
        for post in self.__post_dict.values():

            i += 1
            post_list.append(post)
            if (is_debug):
                print(f'\t{i} из {total_count}; {post}')

        filename = 'geekbrains_posts.json'
        with open(filename, 'w', encoding='UTF-8') as file:
            json.dump(post_list, file, ensure_ascii=False)

    # todo вывод данных
    def print_data(self):
        print('-' * 200)
        for post in self.__post_dict.values():
            print(post)

if __name__ == '__main__':

    # переменные для отладки
    is_debug = True             # вывод данных на экран
    debug_page_limit = 0        # ограничение количества разбираемых страниц, чтобы долго не ждать (0 - разбор всех страниц; 1 и больше - кол-во ограничено

    url_start = 'https://geekbrains.ru/posts'

    blog_parser = BlogParser()
    blog_parser.run_parse_blog(url_start, debug_page_limit, is_debug)
    blog_parser.save_info_to_file(is_debug)

    print('finish')