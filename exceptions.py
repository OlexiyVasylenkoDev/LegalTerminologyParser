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
