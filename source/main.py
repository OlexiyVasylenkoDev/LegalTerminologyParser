import logging
import os
import time

import schema
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup
from db_connector import connector
from dotenv import load_dotenv
from message_translator import translate_message
from oop_parser import PageNotAccessible, Parser, TermNotFound, TooManyResults
from sqlalchemy.orm import Session

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
        # TODO: Fix bug with A1
        number_of_results = len(parsed_term)

        await connector(message.text, bot, user_id, parsed_term, number_of_results, keyboard)

        if number_of_results > 1:
            await message.answer(f"Ось, що вдалось знайти за запитом \"{parser.message}\"", reply_markup=keyboard)

    except (PageNotAccessible, TermNotFound, TooManyResults) as e:
        await bot.send_message(chat_id=user_id, text=str(e))


@dp.callback_query_handler()
async def answer(call):
    with Session(schema.engine) as session:
        await bot.send_message(chat_id=call.message.chat.id,
                               text=session.query(schema.Term).filter_by(id=call.data).first().definition,
                               parse_mode="HTML")
    await call.answer()


if __name__ == "__main__":
    executor.start_polling(dp)

# TODO: Fix bug with translation in error representation and pagination
