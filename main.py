import logging
import os
import time

from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.markdown import hlink
from dotenv import load_dotenv

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

    for i in range(5):
        time.sleep(2)

        await bot.send_message(chat_id=user_id, text=f"Working... {i}")


@dp.message_handler(commands=["end"])
async def end_handler(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.full_name
    logging.info(f"{user_id} {name} {time.asctime()}")

    await message.reply("Goodbye!")


@dp.message_handler()
async def handler(message: types.Message):
    user_id = message.from_user.id
    try:
        parser = Parser(message=message.text).router()
        print(parser.__class__.__name__)
        for i in parser.parse():
            await bot.send_message(chat_id=user_id,
                                   text=f"{i[1][0]}\n<i>{hlink(i[0], i[1][1])}</i>",
                                   parse_mode="HTML")
    except (PageNotAccessible, TermNotFound, TooManyResults) as e:
        await bot.send_message(chat_id=user_id, text=str(e))


if __name__ == "__main__":
    executor.start_polling(dp)
