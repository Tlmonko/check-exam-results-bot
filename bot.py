import asyncio
import os

from aiogram import Bot, types, executor
from aiogram.dispatcher import Dispatcher
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply('To add participant, use /add command')


@dp.message_handler(commands=['add'])
async def add_participant(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text='Send your participant id (you can find it in '
                                'https://checkege.rustest.ru/exams cookies)')


@dp.message_handler(lambda msg: msg.text == 'ping')
async def ping(message: types.Message):
    await bot.send_message(message.from_user.id, 'pong')


async def check_page_update():
    pass


async def start_checking_updates(x):
    asyncio.create_task(check_page_update())


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=start_checking_updates)
