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


async def get_last_commit_hash():
    try:
        with open(r'.git/refs/heads/main', 'r') as file:
            commit_hash = file.read()
    except Exception as e:
        await bot.send_message('Error if function get_last_commit_hash: {}'.format(e))
        commit_hash = 'HASH NOT FOUND'
    return commit_hash


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply('Bot started')


@dp.message_handler(lambda msg: msg.text == 'ping')
async def ping(msg: types.Message):
    await bot.send_message(msg.from_user.id, 'pong')


@dp.message_handler(commands=['status'])
async def get_status(message: types.Message):
    last_commit_hash = await get_last_commit_hash()
    tasks = asyncio.all_tasks()
    await bot.send_message(message.from_user.id,
                           'Bot is now running. \n\nCoroutine objects:\n`{}` \n\nVersion: {}'.format(
                               [task.get_coro() for task in tasks], last_commit_hash),
                           parse_mode='Markdown')


async def check_page_update():
    last_commit_hash = await get_last_commit_hash()
    await bot.send_message(chat_id=TELEGRAM_USER,
                           text='Update checking started on version {}'.format(last_commit_hash))
    print('Update checking started')
    old_results = {}
    while True:
        try:
            print('Getting exams results....')
            response = requests.get('https://checkege.rustest.ru/api/exam',
                                    cookies={'Participant': PARTICIPANT})
            results = response.json()['Result']['Exams']
            changed_results = []
            for result in results:
                exam_id = result['ExamId']
                old_exam = next(filter(lambda exam: exam['ExamId'] == exam_id, old_results), None)
                if old_exam and old_exam != result:
                    if old_exam['StatusName'] != result['StatusName']:
                        changed_results.append(result['Subject'])
            if old_results and results != old_results and changed_results:
                await bot.send_message(chat_id=TELEGRAM_USER,
                                       text='Изменились результаты по предметам: {}. Новый статус '
                                            'результата: {}'.format(', '.join(changed_results),
                                                                    results['StatusName']))
                print('Results changed', changed_results)
            old_results = results
        except Exception as e:
            await bot.send_message(chat_id=TELEGRAM_USER,
                                   text='Error in update exam results loop: {}'.format(e))
        await asyncio.sleep(60)


async def start_checking_updates(x):
    asyncio.create_task(check_page_update())


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=start_checking_updates)
