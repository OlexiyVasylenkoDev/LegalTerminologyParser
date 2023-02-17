from __future__ import annotations

import re
from abc import ABC

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
        return f"Sorry, {self._term} wasn`t found!"

    @property
    def term(self) -> str:
        return self._term


class TooManyResults(Exception):
    def __init__(self, term: str):
        self._term = term

    def __str__(self) -> str:
        return f"Sorry, there are too many results for {self._term} found!"

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
    SOUP_FOR_COUNTING_NUMBER_OF_RESULTS = "h2 small b"

    def __init__(self, message: str):
        self.message = message

    def get_url(self) -> str:
        return self.URL + self.message

    def get_response(self) -> Response:
        response = requests.get(self.get_url())
        if response.status_code >= 400:
            raise PageNotAccessible(status_code=response.status_code, response=response)
        return response

    def get_url_links(self) -> dict:
        soup = BeautifulSoup(self.get_response().text, "html.parser")
        links = dict()
        if not soup.select(self.SOUP_FOR_INITIAL_SEARCH):
            raise TermNotFound(term=self.message)
        for i in soup.select(self.SOUP_FOR_INITIAL_SEARCH):
            links[i.text] = i.get("href")
        return links

    def is_exact_match(self) -> bool:
        print(list(map(lambda x: x.lower(), self.get_url_links().keys())))
        return " ".join([i.capitalize() for i in self.message.split(" ")]).lower() \
               in list(map(lambda x: x.lower(), self.get_url_links().keys()))

    def parse(self):
        pass

    def router(self):
        if self.is_exact_match():
            return ExactMatch(self.message)
        return PartialMatch(self.message)


class ExactMatch(Parser):
    def parse(self):
        result = dict()
        response = requests.get(list(self.get_url_links().items())[0][1])
        soup = BeautifulSoup(response.text, "html.parser")
        for i in soup.select(self.SOUP_FOR_RETRIEVING_FROM_TERM):
            result[re.sub(r"\xa0", "", i.select_one("div.doc a").text)] = [re.sub("\n", "", i.select_one("p").text),
                                                                           i.select_one("div.doc a").get("href")]
        print(result.items())
        return result.items()


class PartialMatch(Parser):
    def parse(self):
        result = dict()
        soup = BeautifulSoup(self.get_response().text, "html.parser")
        if int([i.text for i in soup.select(self.SOUP_FOR_COUNTING_NUMBER_OF_RESULTS)][0]) > 10:
            raise TooManyResults(term=self.message)
        for j in list(self.get_url_links().items()):
            response = requests.get(j[1])
            soup = BeautifulSoup(response.text, "html.parser")
            for i in soup.select(self.SOUP_FOR_RETRIEVING_FROM_TERM):
                result[re.sub(r"\xa0", "", i.select_one("div.doc a").text)] = [re.sub("\n", "", i.select_one("p").text),
                                                                               i.select_one("div.doc a").get("href")]
        # print(result.items())
        return result.items()
