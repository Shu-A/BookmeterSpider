from bs4 import BeautifulSoup

import requests
import json

class BookmeterSpider:
    LOGIN_PAGE_URL = 'https://bookmeter.com/login'
    DISPLAY_TYPE_PARAM = 'list'

    session = None
    """
    aaa
    """

    def __init__(self, email_address, password):
        self.session = requests.Session()
        payload = {
            'session[email_address]': email_address,
            'session[password]': password
        }

        r = self.session.get(self.LOGIN_PAGE_URL)
        bs_login_page = BeautifulSoup(r.text, "html.parser")
        auth_token = bs_login_page.find(attrs={'name': 'authenticity_token'}).get('value')
        payload['authenticity_token'] = auth_token

        r = self.session.post(self.LOGIN_PAGE_URL, data=payload)
        bs_home_page = BeautifulSoup(r.text, "html.parser")
        user_content = bs_home_page.find(attrs={'name':'current_user'}).get('content')

        j = json.loads(user_content)
        self.user_id = j['user']['id']

    def get_reading_books(self):
        READING_BOOKS_URL = 'https://bookmeter.com/users/' + str(self.user_id) + '/books/reading/?display_type=' + self.DISPLAY_TYPE_PARAM

        return self.__get_books(READING_BOOKS_URL)

    def get_read_books(self):
        READ_BOOKS_URL = 'https://bookmeter.com/users/' + str(self.user_id) + '/books/read/?display_type=' + self.DISPLAY_TYPE_PARAM

        return self.__get_books(READ_BOOKS_URL)

    def get_wish_books(self):
        WISH_BOOKS_URL = 'https://bookmeter.com/users/' + str(self.user_id) + '/books/wish/?display_type=' + self.DISPLAY_TYPE_PARAM

        return self.__get_books(WISH_BOOKS_URL)

    def get_stacked_books(self):
        STACKED_BOOKS_URL = 'https://bookmeter.com/users/' + str(self.user_id) + '/books/stacked/?display_type=' + self.DISPLAY_TYPE_PARAM

        return self.__get_books(STACKED_BOOKS_URL)

    def __get_books(self, url):
        BASE_URL = 'https://bookmeter.com'

        r = self.session.get(url)
        bs_books = BeautifulSoup(r.text, "html.parser")

        content_count = bs_books.find("div", class_="title__content").find("div", class_="content__count").text

        book_details = []
        for i in range(int(content_count)/20 + 1):
            r = self.session.get(url + "&page=" + str(i+1))
            bs_read_books = BeautifulSoup(r.text, "html.parser")
            listtag_books = bs_read_books.find_all("li", class_="group__book")

            for listtag_book in listtag_books:
                book_url = BASE_URL + listtag_book.find("div", class_="book__detail") \
                                                  .find("div", class_="detail__title") \
                                                  .find("a") \
                                                  .attrs["href"]
                book_detail = self.__get_book_detail(book_url)

                book_details.append(book_detail)

        return book_details

    def __get_book_detail(self, book_url):
        r = self.session.get(book_url)
        bs_book = BeautifulSoup(r.text, "html.parser")

        book_detail = {}
        book_detail['bookmeter_url'] = book_url

        header = bs_book.find("header", class_="show__header")
        book_detail['title'] = header.find("h1", class_="inner__title").text
        listtag_authors = header.find("ul", class_="header__authors") \
                                .find_all("li")

        authors = []
        for listtag_author in listtag_authors:
            authors.append(listtag_author.find("a").text)
        book_detail['authors'] = authors

        side_bar_group = bs_book.find("section", class_="sidebar__group")
        book_detail['num_page'] = side_bar_group.find("div", class_="group__detail") \
                                                .find("dd", class_="bm-details-side__item") \
                                                .find("span").text
        book_detail['num_pickup'] = side_bar_group.find("div", class_="group__detail") \
                                                  .find("span", class_="bm-details-side__pickup").text
        book_detail['image_url'] = side_bar_group.find("div", class_="group__image") \
                                                  .find("img").attrs["src"]

        return book_detail

    def print_as_newline_delimited_json(self, books):
        for book in books:
            print json.dumps(book)
