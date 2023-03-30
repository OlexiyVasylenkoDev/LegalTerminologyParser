from __future__ import annotations

import re

import requests
from bs4 import BeautifulSoup
from exceptions import PageNotAccessible, TermNotFound, TooManyResults
from requests import Response


class Parser:
    """
    The Creator class declares the factory method that is supposed to return an
    object of a Product class. The Creator's subclasses usually provide the
    implementation of this method.
    """

    URL = "https://zakon.rada.gov.ua/laws/term?find=1&text="

    SOUP_FOR_INITIAL_SEARCH = "ul.m-3 li a"
    SOUP_FOR_RETRIEVING_FROM_TERM = "div.card dl"
    SOUP_FOR_COUNTING_NUMBER_OF_RESULTS = "h2.mb-0 b"
    SOUP_FOR_CHECKING_IF_LAW_IS_VALID = "div.doc span"
    SOUP_FOR_CHECKING_IF_LAW_IS_INVALID = "span.invalid"

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
        return " ".join([i.capitalize() for i in self.message.split(" ")]).lower() \
               in list(map(lambda x: x.lower(), self.get_url_links().keys()))

    def law_is_in_force(self, link):
        link = link.split("/ed")
        response = requests.get(link[0])
        soup = BeautifulSoup(response.text, "html.parser")
        try:
            result = soup.find('span', class_=re.compile(r'.*valid\b'))
            return result.text
        except (AttributeError, PageNotAccessible):
            return "DELETED"

        # return link[0]

    def parse(self):
        result = dict()
        soup = BeautifulSoup(self.get_response().text, "html.parser")
        number_of_results = soup.select_one(self.SOUP_FOR_COUNTING_NUMBER_OF_RESULTS)
        if number_of_results is None or int(number_of_results.get_text()) > 10:
            raise TooManyResults(term=self.message)
        for j in list(self.get_url_links().items()):
            response = requests.get(j[1])
            soup = BeautifulSoup(response.text, "html.parser")
            for i in soup.select(self.SOUP_FOR_RETRIEVING_FROM_TERM):
                law_in_force = self.law_is_in_force(i.select_one("div.doc a").get("href"))
                result[re.sub(r"\xa0", "", i.select_one("div.doc a").text)] = [list(j)[0],
                                                                               re.sub("\n", "", i.select_one("p").text),
                                                                               i.select_one("div.doc a").get("href"),
                                                                               law_in_force]
        print(result)
        return result.items()
