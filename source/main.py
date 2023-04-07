import os

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup
from backend import Backend
from dotenv import load_dotenv
from oop_parser import PageNotAccessible, Parser, TermNotFound, TooManyResults
from sqlalchemy.orm import Session

from source import schema
from source.pagination import Paginator
from source.utils import check_if_term_is_valid

load_dotenv()

bot = Bot(token=os.environ.get("TOKEN"))
dp = Dispatcher(bot=bot)
backend = Backend()


@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    name = message.from_user.full_name
    await message.reply(f"Привіт, {name}")


@dp.message_handler()
async def bot_handler(message: types.Message):
    user_id = message.from_user.id
    keyboard = InlineKeyboardMarkup()
    try:
        parser = Parser(message=message.text)
        parsed_term = parser.parse()
        number_of_results = len(parsed_term)
# 1
        await backend.backend(bot, user_id, parsed_term, number_of_results, keyboard)

        if number_of_results > 1:
            await message.answer(f"Ось, що вдалось знайти за запитом \"{parser.message}\"",
                                 reply_markup=keyboard)
    except (PageNotAccessible, TermNotFound, TooManyResults) as e:
        await bot.send_message(chat_id=user_id, text=str(e))


@dp.message_handler(commands=["end"])
async def end_handler(message: types.Message):
    await message.reply("До зустрічі!")


@dp.callback_query_handler(lambda c: c.data.startswith('page'))
async def pagination_callback(query: types.CallbackQuery = None):
    current_keyboard = query.message.reply_markup.inline_keyboard
    paginator = Paginator(current_keyboard[-1][1]["text"].split("/")[-1])
    await query.message.edit_reply_markup(
        reply_markup=paginator.pagination_keyboard(query.data, backend.buttons))


@dp.callback_query_handler()
async def answer_callback(call):
    with Session(schema.engine) as session:
        term = session.query(schema.Term).filter_by(id=call.data).first()
        await bot.send_message(chat_id=call.message.chat.id,
                               text=f"{check_if_term_is_valid(term)} {term.definition}",
                               parse_mode="HTML")
    await call.answer()


if __name__ == "__main__":
    executor.start_polling(dp)
