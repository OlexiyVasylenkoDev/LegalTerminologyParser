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
import schema

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
        parser = Parser(message=translate_message(message.text))
        parsed_term = parser.parse()
        print(translate_message(message.text))
        if len(parsed_term) > 1:
            for i in parsed_term:
                definition = f"{i[1][0]}\n<i>{hlink(i[0], i[1][1])}</i>"
                law_name = i[0]
                with Session(schema.engine) as session:
                    law = session.query(schema.Law).filter_by(name=law_name).first()
                    if law:
                        current_law = session.query(schema.Law).filter_by(name=law_name).first()
                        current_law.number_of_mentions += 1
                    else:
                        new_law = schema.Law(name=law_name)
                        session.add(new_law)
                    session.commit()

                    term = session.query(schema.Term).filter_by(content=definition).first()
                    if term:
                        keyboard.add(InlineKeyboardButton(text=i[0],
                                                          callback_data=term.id))
                    else:
                        new_term = schema.Term(content=definition,
                                               law=session.query(schema.Law).filter_by(name=i[0]).first())
                        session.add(new_term)
                        session.commit()
                        keyboard.add(InlineKeyboardButton(text=i[0],
                                                          callback_data=new_term.id))
            await message.answer(f"Here are the results:", reply_markup=keyboard)
        else:
            for i in parsed_term:
                definition = f"{i[1][0]}\n<i>{hlink(i[0], i[1][1])}</i>"
                law_name = i[0]
                with Session(schema.engine) as session:
                    law = session.query(schema.Law).filter_by(name=law_name).first()
                    if law:
                        current_law = session.query(schema.Law).filter_by(name=law_name).first()
                        current_law.number_of_mentions += 1
                    else:
                        new_law = schema.Law(name=law_name)
                        session.add(new_law)
                    session.commit()

                    term = session.query(schema.Term).filter_by(content=definition).first()
                    if term:
                        pass
                    else:
                        new_term = schema.Term(content=definition,
                                               law=session.query(schema.Law).filter_by(name=i[0]).first())
                        session.add(new_term)
                        session.commit()
                await bot.send_message(chat_id=user_id,
                                       text=f"{i[1][0]}\n<i>{hlink(i[0], i[1][1])}</i>",
                                       parse_mode="HTML")
    except (PageNotAccessible, TermNotFound, TooManyResults) as e:
        await bot.send_message(chat_id=user_id, text=str(e))


@dp.callback_query_handler()
async def answer(call):
    with Session(schema.engine) as session:
        await bot.send_message(chat_id=call.message.chat.id,
                               text=session.query(schema.Term).filter_by(id=call.data).first().content,
                               parse_mode="HTML")
    await call.answer()


if __name__ == "__main__":
    executor.start_polling(dp)

# TODO: Fix bug with translation in error representation and add functionality for checking if law is in force
