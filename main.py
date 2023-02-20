import logging
import os
import random
import time

from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.markdown import hlink
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

from message_translator import translate_message
from oop_parser import Parser, PageNotAccessible, TermNotFound, TooManyResults

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
                keyboard.add(InlineKeyboardButton(text=i[0],
                                                  callback_data="answer",
                                                  kwargs={"text": i[1][0],
                                                          "link": hlink(i[0], i[1][1])}))
                print(keyboard)
            await message.answer("Here are the results:", reply_markup=keyboard)
        else:
            for i in parser.parse():
                await bot.send_message(chat_id=user_id,
                                       text=f"{i[1][0]}\n<i>{hlink(i[0], i[1][1])}</i>",
                                       parse_mode="HTML")
    except (PageNotAccessible, TermNotFound, TooManyResults) as e:
        await bot.send_message(chat_id=user_id, text=str(e))


@dp.callback_query_handler(text=["answer"])
async def answer(call, text, link):
    await call.message.answer(f"{text}\n<i>{link}</i>")
    await call.answer(call)


if __name__ == "__main__":
    executor.start_polling(dp)
