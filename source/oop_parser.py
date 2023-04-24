from __future__ import annotations

import re

import requests
from bs4 import BeautifulSoup
from exceptions import PageNotAccessible, TermNotFound, TooManyResults
from requests import Response


class Term:
    def __init__(self, definition, term_name, law_name, link_to_law, law_number, law_is_valid):
        self.definition = definition
        self.term_name = term_name
        self.law_name = law_name
        self.link_to_law = link_to_law
        self.law_number = law_number
        self.law_is_valid = law_is_valid

    def __str__(self):
        return self.term_name


class Parser:
    URL = "https://zakon.rada.gov.ua/laws/term?find=1&text="

    SOUP_FOR_INITIAL_SEARCH = "ul.m-3 li a"
    SOUP_FOR_RETRIEVING_FROM_TERM = "div.card dl"
    SOUP_FOR_COUNTING_NUMBER_OF_RESULTS = "h2.mb-0 b"

    def __init__(self, message: str) -> None:
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

    def get_law_info(self, link: str):
        link = link.split("/ed")
        response = requests.get(link[0])
        soup = BeautifulSoup(response.text, "html.parser")
        law_info = {"number": None,
                    "is_valid": None}
        if not response.status_code <= 400:
            law_info["number"] = law_info["is_valid"] = "сторінку не знайдено"

        try:
            law_number = soup.select_one("abbr").text
            law_info["number"] = law_number
        except AttributeError:
            law_info["number"] = "невідомо"

        try:
            law_is_valid = soup.find('span', class_=re.compile(r'.*valid\b')).text
            law_info["is_valid"] = law_is_valid

        except AttributeError:
            law_info["is_valid"] = "невідомо"

        return law_info

    def get_term_definition(self, term):
        try:
            return re.sub("\n", "", term.select_one("p").text)
        except AttributeError:
            return ""

    def parse(self) -> list[Term]:
        result = list()
        soup = BeautifulSoup(self.get_response().text, "html.parser")
        number_of_results = soup.select_one(self.SOUP_FOR_COUNTING_NUMBER_OF_RESULTS)
        if number_of_results is None or int(number_of_results.get_text()) > 100:
            raise TooManyResults(term=self.message)
        for j in list(self.get_url_links().items()):
            print(j)
            response = requests.get(j[1])
            soup = BeautifulSoup(response.text, "html.parser")
            for i in soup.select(self.SOUP_FOR_RETRIEVING_FROM_TERM):
                definition = self.get_term_definition(i)
                term_name = list(j)[0]
                law_name = re.sub(r"\xa0", "", i.select_one("div.doc a").text)
                link_to_law = i.select_one("div.doc a").get("href")
                law_info = self.get_law_info(link_to_law)

                parsed_term = Term(definition=definition,
                                   term_name=term_name,
                                   law_name=law_name,
                                   link_to_law=link_to_law,
                                   law_number=law_info["number"],
                                   law_is_valid=law_info["is_valid"], )

                result.append(parsed_term)

            if self.is_exact_match():
                break
        return result
