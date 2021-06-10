import os

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
PARTICIPANT = os.getenv('CHECKEGE_PARTICIPANT')

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply('Bot started')

