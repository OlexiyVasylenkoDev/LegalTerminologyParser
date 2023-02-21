import os

from aiogram import Bot, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.utils.callback_data import CallbackData
from dotenv import load_dotenv

load_dotenv()

# Define your callback data
button_callback = CallbackData("button", "param1", "param2")

bot = Bot(token=os.environ.get("TOKEN"))
dp = Dispatcher(bot=bot)

# Define a function to generate the keyboard markup
def generate_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    for i in range(1, 5):
        # Add a button to the keyboard for each iteration
        print(i)
        button_text = f"Button {i}"
        button_data = button_callback.new(param1=i, param2="some_value")
        button = InlineKeyboardButton(button_text, callback_data=button_data)
        keyboard.add(button)
    return keyboard

# Define the callback query handler for the generated buttons
@dp.callback_query_handler()
async def handle_button_callback(query):
    # Extract the parameters from the callback data
    print(query["message"])
    params = button_callback.parse(query.data)
    param1 = params["param1"]
    param2 = params["param2"]
    # Do something with the parameters, such as updating a database
    await bot.send_message(chat_id=query["message"]["chat"]["id"], text=param1)

# Use the generated keyboard markup in your bot's message handler
@dp.message_handler()
async def handle_message(message):
    keyboard = generate_keyboard()
    await bot.send_message(message.chat.id, "Press a button:", reply_markup=keyboard)

if __name__ == "__main__":
    executor.start_polling(dp)
