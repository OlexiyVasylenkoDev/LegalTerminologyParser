from requests import Response


class PageNotAccessible(Exception):
    def __init__(self, status_code: int, response: Response):
        self._status_code = status_code
        self._response = response

    def __str__(self):
        return "Сторінка недоступна"

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
        return f"Не вдалось знайти термін \"{self._term}\" в законодавстві"

    @property
    def term(self) -> str:
        return self._term


class TooManyResults(Exception):
    def __init__(self, term: str):
        self._term = term

    def __str__(self) -> str:
        return f"Знайдено занадто багато результатів для \"{self._term}\". Спробуйте уточнити Ваш пошук"

    @property
    def term(self) -> str:
        return self._term
