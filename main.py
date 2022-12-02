import logging
import os
import time

from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv

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

        await bot.send_message(chat_id=user_id, text="Working...")


if __name__ == "__main__":
    executor.start_polling(dp)
