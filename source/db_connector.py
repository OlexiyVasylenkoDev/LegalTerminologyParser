import schema
from aiogram.types import InlineKeyboardButton
from aiogram.utils.markdown import hlink
from sqlalchemy.orm import Session


async def connector(bot, user_id, parsed_term, number_of_results, keyboard):
    for i in parsed_term:
        term_name = i[1][0]
        definition = f"{i[1][1]}\n<i>{hlink(i[0], i[1][2])}</i>"
        law_name = i[0]
        print(i)
        with Session(schema.engine) as session:
            law = session.query(schema.Law).filter_by(name=law_name).first()
            if law:
                current_law = session.query(schema.Law).filter_by(name=law_name).first()
                current_law.number_of_mentions += 1
            else:
                new_law = schema.Law(name=law_name)
                session.add(new_law)
            session.commit()

            term = session.query(schema.Term).filter_by(definition=definition).first()
            if term:
                pass
            else:
                term = schema.Term(name=term_name,
                                   definition=definition,
                                   law_name=law_name,
                                   law=session.query(schema.Law).filter_by(name=i[0]).first())
                session.add(term)
                session.commit()
            if number_of_results > 1:
                keyboard.add(InlineKeyboardButton(text=f"{i[1][0]} ({i[0]})",
                                                  callback_data=term.id))
            else:
                await bot.send_message(chat_id=user_id,
                                       text=f"{i[1][1]}\n<i>{hlink(i[0], i[1][2])}</i>",
                                       parse_mode="HTML")
