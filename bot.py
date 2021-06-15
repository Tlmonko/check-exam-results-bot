import asyncio
import os

import requests
from aiogram import Bot, types, executor
from aiogram.dispatcher import Dispatcher
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
TELEGRAM_USER = os.getenv('TELEGRAM_USER_ID')
PARTICIPANT = os.getenv('EXAM_PARTICIPANT')

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply('Bot started')


@dp.message_handler(lambda msg: msg.text == 'ping')
async def ping(msg: types.Message):
    await bot.send_message(msg.from_user.id, 'pong')


async def check_page_update():
    await bot.send_message(chat_id=TELEGRAM_USER, text='Update checking started')
    print('Update checking started')
    old_results = {}
    while True:
        try:
            print('Getting exams results....')
            response = requests.get('http://checkege.rustest.ru/api/exam',
                                    cookies={'Participant': PARTICIPANT})
            results = response.json()['Result']['Exams']
            if old_results and results != old_results:
                await bot.send_message(chat_id=TELEGRAM_USER,
                                       text='Результаты экзаменов изменились!')
                print('Results changed')
            old_results = results
        except Exception as e:
            await bot.send_message(chat_id=TELEGRAM_USER, text='Error: {}'.format(e))
        await asyncio.sleep(60)


async def start_checking_updates(x):
    asyncio.create_task(check_page_update())


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=start_checking_updates)
