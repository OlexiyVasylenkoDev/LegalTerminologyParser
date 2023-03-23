import logging
import os
import time

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.markdown import hlink
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from message_translator import translate_message
from oop_parser import PageNotAccessible, Parser, TermNotFound, TooManyResults
from schema import Term, engine, Law

load_dotenv()

bot = Bot(token=os.environ.get("TOKEN"))
dp = Dispatcher(bot=bot)


@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.full_name
    logging.info(f"{user_id} {name} {time.asctime()}")
    await message.reply(f"Hello, {name}")


@dp.message_handler(commands=["end"])
async def end_handler(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.full_name
    logging.info(f"{user_id} {name} {time.asctime()}")
    await message.reply("Goodbye!")


@dp.message_handler()
async def handler(message: types.Message):
    user_id = message.from_user.id
    keyboard = InlineKeyboardMarkup()
    try:
        parser = Parser(message=translate_message(message.text)).router()
        print(parser.__class__.__name__)
        print(translate_message(message.text))
        if parser.__class__.__name__ == "PartialMatch":
            for i in parser.parse():
                definition = f"{i[1][0]}\n<i>{hlink(i[0], i[1][1])}</i>"
                law_name = i[0]
                with Session(engine) as session:
                    term = session.query(Term).filter_by(content=definition).first()
                    law = session.query(Law).filter_by(name=law_name).first()
                    if law:
                        current_law = session.query(Law).filter_by(name=law_name).first()
                        current_law.number_of_mentions += 1
                        session.commit()
                    else:
                        new_law = Law(name=law_name)
                        session.add(new_law)
                    session.commit()
                    if term:
                        keyboard.add(InlineKeyboardButton(text=i[0],
                                                          callback_data=term.id))
                    else:
                        new_term = Term(content=definition, law=session.query(Law).filter_by(name=i[0]).first())
                        session.add(new_term)
                        session.commit()
                        keyboard.add(InlineKeyboardButton(text=i[0],
                                                          callback_data=new_term.id))
            await message.answer(f"Here are the results:", reply_markup=keyboard)
        else:
            for i in parser.parse():
                definition = f"{i[1][0]}\n<i>{hlink(i[0], i[1][1])}</i>"
                law_name = i[0]
                with Session(engine) as session:
                    term = session.query(Term).filter_by(content=definition).first()
                    law = session.query(Law).filter_by(name=law_name).first()
                    if law:
                        current_law = session.query(Law).filter_by(name=law_name).first()
                        current_law.number_of_mentions += 1
                        session.commit()
                    else:
                        new_law = Law(name=law_name)
                        session.add(new_law)
                    session.commit()
                    if term:
                        keyboard.add(InlineKeyboardButton(text=i[0],
                                                          callback_data=term.id))
                    else:
                        new_term = Term(content=definition, law=session.query(Law).filter_by(name=i[0]).first())
                        session.add(new_term)
                        session.commit()
                        keyboard.add(InlineKeyboardButton(text=i[0],
                                                          callback_data=new_term.id))
            await message.answer(f"Here are the results:", reply_markup=keyboard)

    except (PageNotAccessible, TermNotFound, TooManyResults) as e:
        await bot.send_message(chat_id=user_id, text=str(e))


@dp.callback_query_handler()
async def answer(call):
    with Session(engine) as session:
        await bot.send_message(chat_id=call.message.chat.id,
                               text=session.query(Term).filter_by(id=call.data).first().content,
                               parse_mode="HTML")
    await call.answer()


if __name__ == "__main__":
    executor.start_polling(dp)
