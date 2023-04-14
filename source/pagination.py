from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

NUMBER_OF_KEYBOARD_BUTTONS = 5


class Paginator:
    current_page = 1

    def __init__(self, number_of_pages: int) -> None:
        self.number_of_pages = number_of_pages

    def get_pagination_results(self, data: list) -> list[InlineKeyboardButton]:
        results = list(range(NUMBER_OF_KEYBOARD_BUTTONS * (self.current_page - 1),
                             (NUMBER_OF_KEYBOARD_BUTTONS * self.current_page)))
        return data[results[0]:results[-1] + 1]

    def get_pagination_buttons(self) -> list[InlineKeyboardButton]:
        return [InlineKeyboardButton(f' < ', callback_data=f'page#{self.current_page}-'),
                InlineKeyboardButton(f' {self.current_page}/{self.number_of_pages} ',
                                     callback_data=str(self.current_page)),
                InlineKeyboardButton(f' > ', callback_data=f'page#{self.current_page}+')]

    def pagination_keyboard(self, data: str, buttons: list[InlineKeyboardButton]) -> InlineKeyboardMarkup:
        chars_to_evaluate = data.strip("page#")
        self.current_page = eval(f"{chars_to_evaluate[:-1]} {chars_to_evaluate[-1]} {str(self.current_page)}")
        if self.current_page > int(self.number_of_pages):
            self.current_page = int(self.number_of_pages)
        elif self.current_page < 1:
            self.current_page = 1

        new_keyboard = InlineKeyboardMarkup()

        for j in self.get_pagination_results(buttons):
            new_keyboard.add(j)
        new_keyboard.row(*self.get_pagination_buttons())
        return new_keyboard
