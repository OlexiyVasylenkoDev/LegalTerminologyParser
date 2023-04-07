import schema
from aiogram.types import InlineKeyboardButton
from aiogram.utils.markdown import hlink
from sqlalchemy.orm import Session

from source.utils import check_if_term_is_valid
from source.pagination import NUMBER_OF_KEYBOARD_BUTTONS, Paginator


class Backend:
    buttons = []

    async def backend(self, bot, user_id, parsed_term, number_of_results, keyboard):
        self.buttons.clear()
        for i in parsed_term:
            definition = i.definition
            term_name = i.name
            law_name = i.law_name
            link_to_law = i.link_to_law
            law_number = i.law_number
            is_valid = i.law_is_valid
            definition = f"{definition}\n<i>{hlink(law_name, link_to_law)}</i>"

            with Session(schema.engine) as session:
                law = session.query(schema.Law).filter_by(law_number=law_number).first()
                if law:
                    current_law = session.query(schema.Law).filter_by(law_name=law_name).first()
                    current_law.number_of_mentions += 1
                else:
                    new_law = schema.Law(law_name=law_name,
                                         law_number=law_number,
                                         is_valid=is_valid)
                    session.add(new_law)
                session.commit()

                term = session.query(schema.Term).filter_by(definition=definition).first()
                if not term:
                    term = schema.Term(term_name=term_name,
                                       definition=definition,
                                       law_name=law_name,
                                       law=session.query(schema.Law).filter_by(law_name=law_name).first())
                    session.add(term)
                    session.commit()

                if number_of_results > 1:
                    self.buttons.append(
                        InlineKeyboardButton(
                            text=f"{check_if_term_is_valid(term)} {term_name} ({law_name})",
                            callback_data=term.id))
                else:
                    await bot.send_message(chat_id=user_id,
                                           text=f"{check_if_term_is_valid(term)} "
                                                f"{session.query(schema.Term).filter_by(id=term.id).first().definition}",
                                           parse_mode="HTML")

        number_of_pages = round(number_of_results / NUMBER_OF_KEYBOARD_BUTTONS)
        paginator = Paginator(number_of_pages)

        self.buttons = sorted(self.buttons, key=lambda x: x.text)

        for j in paginator.get_pagination_results(self.buttons):
            keyboard.add(j)

        if number_of_pages > 1:
            keyboard.row(*paginator.get_pagination_buttons())
