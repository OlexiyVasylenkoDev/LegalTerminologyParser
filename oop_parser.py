from __future__ import annotations

import pprint
import re
from abc import ABC, abstractmethod

import requests
from bs4 import BeautifulSoup
from requests import Response


class PageNotAccessible(Exception):
    def __init__(self, status_code: int, response: Response):
        self._status_code = status_code
        self._response = response

    def __str__(self):
        return "Sorry, page is not accessible!"

    @property
    def status_code(self) -> int:
        return self._status_code

    @property
    def response(self) -> Response:
        return self._response


class TermNotFound(Exception):
    def __init__(self, term: str):
        self._term = term

    def __str__(self) -> str:
        return "Sorry, term wasn`t found!"

    @property
    def term(self) -> str:
        return self._term


class Parser(ABC):
    """
    The Creator class declares the factory method that is supposed to return an
    object of a Product class. The Creator's subclasses usually provide the
    implementation of this method.
    """

    URL = "https://zakon.rada.gov.ua/laws/term?find=1&text="

    SOUP_FOR_INITIAL_SEARCH = "ul.m-3 li a"
    SOUP_FOR_RETRIEVING_FROM_TERM = "div.card dl"

    def __init__(self, message: str):
        self.message = message

    def get_url(self):
        return self.URL + self.message

    def get_response(self):
        response = requests.get(self.get_url())
        if response.status_code >= 400:
            raise PageNotAccessible(status_code=response.status_code, response=response)
        return response

    def get_url_links(self):
        soup = BeautifulSoup(self.get_response().text, "html.parser")
        links = dict()
        if not soup.select(self.SOUP_FOR_INITIAL_SEARCH):
            raise TermNotFound(term=self.message)
        for i in soup.select(self.SOUP_FOR_INITIAL_SEARCH):
            links[i.text] = i.get("href")
        return links

    def exact_match(self):
        return " ".join([i.capitalize() for i in self.message.split(" ")]) in self.get_url_links().keys()

    @abstractmethod
    def parse(self):
        pass

        # def get_url(self):
        #     return self.URL + self.message
        #
        # def get_url_response(self) -> Response:
        #     return requests.get(self.get_url())
        #
        # def get_url_soup(self) -> BeautifulSoup:
        #     return BeautifulSoup(self.get_url_response().text, "html.parser")
        #
        # def get_url_links(self):
        #     return [i.text for i in self.get_url_soup().select("ul.m-3 li a")]
        #
        # def exact_match(self):
        #     return " ".join([i.capitalize() for i in self.message.split(" ")]) in self.get_url_links()

        # def router(self):
        #     if self.exact_match():
        #         return CLASS_FOR_EXACT_MATCH
        #     return CLASS_FOR_MANY_MATCHES

        # @abstractmethod
        # def factory_method(self):
        #     """
        #     Note that the Creator may also provide some default implementation of
        #     the factory method.
        #     """
        #     pass
        #
        # def some_operation(self) -> str:
        #     """
        #     Also note that, despite its name, the Creator's primary responsibility
        #     is not creating products. Usually, it contains some core business logic
        #     that relies on Product objects, returned by the factory method.
        #     Subclasses can indirectly change that business logic by overriding the
        #     factory method and returning a different type of product from it.
        #     """

        # Call the factory method to create a Product object.
        parser = self.parse()

        # Now, use the product.
        # result = f"Creator: The same creator's code has just worked with {product.operation()}"

        # return result


class SingleExactMatch(Parser):
    def parse(self):
        result = dict()
        for j in list(self.get_url_links().items()):
            response = requests.get(j[1])
            soup = BeautifulSoup(response.text, "html.parser")
            for i in soup.select(self.SOUP_FOR_RETRIEVING_FROM_TERM):
                result[re.sub(r"\xa0", "", i.select_one("div.doc a").text)] = [re.sub("\n", "", i.select_one("p").text),
                                                                               i.select_one("div.doc a").get("href")]
        return result.items()


class MultipleExactMatch(Parser):
    def parse(self):
        pass


"""
Concrete Creators override the factory method in order to change the resulting
product's type.
"""


class ConcreteCreator1(Parser):
    """
    Note that the signature of the method still uses the abstract product type,
    even though the concrete product is actually returned from the method. This
    way the Creator can stay independent of concrete product classes.
    """

    def factory_method(self) -> Term:
        return ConcreteProduct1()


class ConcreteCreator2(Parser):
    def factory_method(self) -> Term:
        return ConcreteProduct2()


class Term(ABC):
    """
    The Product interface declares the operations that all concrete products
    must implement.
    """

    @abstractmethod
    def operation(self) -> str:
        pass


"""
Concrete Products provide various implementations of the Product interface.
"""


class ConcreteProduct1(Term):
    def operation(self) -> str:
        return "{Result of the ConcreteProduct1}"


class ConcreteProduct2(Term):
    def operation(self) -> str:
        return "{Result of the ConcreteProduct2}"


def client_code(creator: Parser) -> None:
    """
    The client code works with an instance of a concrete creator, albeit through
    its base interface. As long as the client keeps working with the creator via
    the base interface, you can pass it any creator's subclass.
    """

    print(f"Client: I'm not aware of the creator's class, but it still works.\n"
          f"{creator.some_operation()}", end="")


if __name__ == "__main__":
    # print("App: Launched with the ConcreteCreator1.")
    # test = ConcreteCreator1("посадка")
    # pprint.pprint(test.get_url_links())
    # print(test.exact_match())
    # # print(test.router())
    # print("\n")
    #
    # print("App: Launched with the ConcreteCreator2.")
    # ConcreteCreator1("Ліонель Мессі").get_url()
    # test = SingleExactMatch("тривога")
    # test.parse()
    test = SingleExactMatch()
    test.parse()
