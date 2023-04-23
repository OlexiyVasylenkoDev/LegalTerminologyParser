import schema
from aiogram.types import InlineKeyboardButton
from aiogram.utils.markdown import hlink
from sqlalchemy.orm import Session

from utils import check_if_term_is_valid
from pagination import NUMBER_OF_KEYBOARD_BUTTONS, Paginator


class Backend:
    buttons = []

    async def connector(self, bot, user_id, parsed_term, number_of_results, keyboard):
        self.buttons.clear()
        for term in parsed_term:
            definition = f"{term.definition}\n<i>{hlink(term.law_name, term.link_to_law)}</i>"

            with Session(schema.engine) as session:
                law = session.get(schema.Law, term.law_number)
                if law:
                    current_law = session.get(schema.Law, term.law_number)
                    current_law.number_of_mentions += 1
                else:
                    new_law = schema.Law(law_name=term.law_name,
                                         law_number=term.law_number,
                                         is_valid=term.law_is_valid)
                    session.add(new_law)
                session.commit()

                current_term = session.query(schema.Term).filter_by(definition=definition).first()
                if not current_term:
                    current_term = schema.Term(term_name=term.term_name,
                                               definition=definition,
                                               law_name=term.law_name,
                                               law=session.query(schema.Law).filter_by(law_name=term.law_name).first())
                    session.add(current_term)
                    session.commit()

                if number_of_results > 1:
                    self.buttons.append(
                        InlineKeyboardButton(
                            text=f"{check_if_term_is_valid(current_term)} {term.term_name} ({term.law_name})",
                            callback_data=current_term.id))
                else:
                    await bot.send_message(chat_id=user_id,
                                           text=f"{check_if_term_is_valid(current_term)} "
                                                f"{session.get(schema.Term, current_term.id).definition}",
                                           parse_mode="HTML")

        number_of_pages = round(number_of_results / NUMBER_OF_KEYBOARD_BUTTONS)
        paginator = Paginator(number_of_pages)

        self.buttons = sorted(self.buttons, key=lambda x: x.text)

        for j in paginator.get_pagination_results(self.buttons):
            keyboard.add(j)

        if number_of_pages > 1:
            keyboard.row(*paginator.get_pagination_buttons())
