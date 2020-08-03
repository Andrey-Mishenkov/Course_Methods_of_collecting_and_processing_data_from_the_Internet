import scrapy
from scrapy.loader import ItemLoader
from habr_parse.items import HabrParseItem, HabrAuthorParseItem

class HabrSpider(scrapy.Spider):

    name = 'habr'
    allowed_domains = ['habr.com']
    start_urls = ['https://habr.com/ru/all/']

    visited_pages = []
    visited_authors = []
    visited_pages_authors_posts = []
    saved_authors = []

    xpath_sel_page = {
        'pagination'    : '//li[@class="toggle-menu__item toggle-menu__item_pagination"]//@href',
        'posts'         : '//h2/a[@class="post__title_link"]/@href',
        'authors'       : '//div//a[contains(@class, "post__user-info")]/@href',
    }

    xpath_sel_post = {
        'post_url'      : '',
        'title'         : '//div//span[@class="post__title-text"]/text()',
        'author_name'   : '//div//a[contains(@class, "user-info__nickname")]/text()',
        'author_url'    : '//div//a[contains(@class, "post__user-info")]/@href',
        'images'        : '//div[contains(@id, "post-content-body")]//img/@src',
        'comments'      : '//div//span[@id="comments_count"]/text()',
    }

    xpath_sel_author = {
        'author_url'        : '',
        'fullname'          : '//div//a[contains(@class, "user-user-info__fullname")]/text()',
        'nickname'          : '//div//a[contains(@class, "user-info__nickname")]/text()',
        'specialization'    : '//div[contains(@class, "user-info__specialization")]/text()',

        'statistics_labels' : '//div//a//div[contains(@class, "stacked-counter__label")]/text()',
        'statistics_values' : '//div//a//div[contains(@class, "stacked-counter__value")]/text()',
        'tab_info'          : '//div//a//span[contains(@class, "tabs-menu__item-counter_total")]/@title',
        'badges'            : '//ul//li//span[contains(@class, "profile-section__user-badge")]/text()',

        'sections_names'    : '//ul//li//a[contains(@class, "profile-section__user-hub")]/text()',
        'sections_urls'     : '//ul//li//a[contains(@class, "profile-section__user-hub")]/@href',

        'info.labels'       : '//div//ul//span[contains(@class, "defination-list__label")]/text()',
        'info.values'       : '//div//ul//span[contains(@class, "defination-list__label")]/text()',
        'posts'             : '',
    }

    # todo разбор страницы
    def parse(self, response):

        if response.url not in self.visited_pages:
            self.visited_pages.append(response.url)
            print(f'\nСтраница N {len(self.visited_pages)} = ', response.url)

            # пагинация
            list_pagination = response.xpath(self.xpath_sel_page['pagination']).extract()

            for page_url in list_pagination:
                if page_url not in self.visited_pages:
                    yield response.follow(page_url, callback=self.parse)

            # список статей
            list_posts = response.xpath(self.xpath_sel_page['posts']).extract()

            for post_url in list_posts:
                yield response.follow(post_url, callback=self.parse_post)

            # список авторов
            list_authors = response.xpath(self.xpath_sel_page['authors']).extract()

            for author_url in list_authors:
                yield response.follow(author_url, callback=self.parse_author)

    # todo разбор статьи
    def parse_post(self, response):

        item = ItemLoader(HabrParseItem(), response)

        item.add_value('collection',    'habr_posts')

        item.add_value('post_url',      response.url)
        item.add_xpath('title',         self.xpath_sel_post['title'])
        item.add_xpath('author_name',   self.xpath_sel_post['author_name'])
        item.add_xpath('author_url',    self.xpath_sel_post['author_url'])
        item.add_xpath('images',        self.xpath_sel_post['images'])
        item.add_xpath('comments',      self.xpath_sel_post['comments'])

        yield item.load_item()

    # todo разбор страницы автора
    def parse_author(self, response):
        if response.url in self.visited_authors:
            return
        else:
            self.visited_authors.append(response.url)

        item = ItemLoader(HabrAuthorParseItem(), response)

        item.add_value('collection', 'habr_authors')

        item.add_value('author_url', response.url)
        item.add_xpath('fullname', self.xpath_sel_author['fullname'])
        item.add_xpath('nickname', self.xpath_sel_author['nickname'])
        item.add_xpath('specialization', self.xpath_sel_author['specialization'])

        item.add_xpath('statistics_labels', self.xpath_sel_author['statistics_labels'])
        item.add_xpath('statistics_values', self.xpath_sel_author['statistics_values'])
        item.add_xpath('tab_info', self.xpath_sel_author['tab_info'])
        item.add_xpath('badges', self.xpath_sel_author['badges'])

        item.add_xpath('sections_names', self.xpath_sel_author['sections_names'])
        item.add_xpath('sections_urls', self.xpath_sel_author['sections_urls'])

        item.add_value('posts', {})

        # все статьи автора
        url_author_posts = response.url + 'posts/'
        list_urls_authors_posts = []
        is_last_page = False

        yield response.follow(url_author_posts,
                              callback=self.get_author_posts,
                              cb_kwargs={'item': item,
                                         'list_urls_authors_posts': list_urls_authors_posts,
                                         'is_last_page': is_last_page,
                                         'author_url': response.url})

    # todo перебор всех статей автора
    def get_author_posts(self, response, item, list_urls_authors_posts, is_last_page, author_url):

        if response.url in self.visited_pages_authors_posts:
            return
        else:
            self.visited_pages_authors_posts.append(response.url)

        # список статей
        list_posts = response.xpath(self.xpath_sel_page['posts']).extract()

        for url_post in list_posts:
            list_urls_authors_posts.append(url_post)

        # пагинация
        list_pagination = response.xpath(self.xpath_sel_page['pagination']).extract()

        is_last_page = not bool(list_pagination)
        if (not is_last_page):
            for page_url in list_pagination:

                if (page_url.find('https://habr.com') == -1):
                    page_url = f'https://habr.com{page_url}'

                is_last_page = True

                if page_url not in self.visited_pages_authors_posts:
                    is_last_page = False

                    yield response.follow(page_url,
                                          callback=self.get_author_posts,
                                          cb_kwargs={'item': item,
                                                     'list_urls_authors_posts': list_urls_authors_posts,
                                                     'is_last_page': is_last_page,
                                                     'author_url': author_url})

        if (is_last_page):
            if author_url not in self.saved_authors:
                self.saved_authors.append(author_url)
                item.add_value('posts', list_urls_authors_posts)
                yield item.load_item()
