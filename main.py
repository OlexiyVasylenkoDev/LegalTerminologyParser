import logging
import os
import time

import kb as kb
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.markdown import hlink, link
from dotenv import load_dotenv

from oop_parser import Parser, SingleExactMatch, PageNotAccessible, TermNotFound

load_dotenv()

bot = Bot(token=os.environ.get("TOKEN"))
dp = Dispatcher(bot=bot)

LANGUAGES_KEYBOARD = ReplyKeyboardMarkup(resize_keyboard=True)

LANGUAGES_KEYBOARD.add(KeyboardButton("English 🏴󠁧󠁢󠁥󠁮󠁧󠁿"))
LANGUAGES_KEYBOARD.add(KeyboardButton("Ukrainian 🇺🇦"))
LANGUAGES_KEYBOARD.add(KeyboardButton("German 🇩🇪"))
LANGUAGES_KEYBOARD.add(KeyboardButton("French 🇫🇷"))
LANGUAGES_KEYBOARD.add(KeyboardButton("Italian 🇮🇹"))


@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.full_name
    logging.info(f"{user_id} {name} {time.asctime()}")

    await message.reply(f"Hello, {name}")

    for i in range(5):
        time.sleep(2)

        await bot.send_message(chat_id=user_id, text=f"Working... {i}")


# @dp.message_handler(commands=['hi1'])
# async def process_hi1_command(message: types.Message):
#     await message.reply("Клавиатура1", reply_markup=LANGUAGES_KEYBOARD)


@dp.message_handler(commands=["end"])
async def end_handler(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.full_name
    logging.info(f"{user_id} {name} {time.asctime()}")

    await message.reply(f"Goodbye!")


@dp.message_handler()
async def handler(message: types.Message):
    user_id = message.from_user.id
    try:
        parser = SingleExactMatch(message=message.text)
        for i in parser.parse():
            await bot.send_message(chat_id=user_id, text=hlink(i[1][0], i[1][1]), parse_mode="HTML")
    except (PageNotAccessible, TermNotFound) as e:
        await bot.send_message(chat_id=user_id, text=str(e))

if __name__ == "__main__":
    executor.start_polling(dp)
