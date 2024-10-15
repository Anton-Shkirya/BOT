import asyncio
import logging
import aiosqlite
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import F
from quiz_data import quiz_data
from table_function import get_quiz_index, get_quiz_stats, get_quiz, update_quiz_index_and_stats, create_table

logging.basicConfig(level=logging.INFO)

API_TOKEN = '7262006910:AAHcLyghvZ-HbG1RzLPjkZj1645eG1eYKlw'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
DB_NAME = 'quiz_bot.db'

def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()
    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data=f"right_answer{option}" if option == right_answer else f"wrong_answer{option}")
        )
    builder.adjust(1)
    return builder.as_markup()

@dp.callback_query(F.data.contains ("right_answer"))
async def right_answer(callback: types.CallbackQuery):
    text = callback.data
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    await callback.message.answer (text[12:])
    current_question_index = await get_quiz_index(callback.from_user.id)
    statistic = await get_quiz_stats(callback.from_user.id)
    await callback.message.answer("Верно!")
    current_question_index += 1
    statistic += 1
    await update_quiz_index_and_stats(callback.from_user.id, current_question_index, statistic)
    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")

@dp.callback_query(F.data.contains ("wrong_answer"))
async def wrong_answer(callback: types.CallbackQuery):
    text = callback.data
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    await callback.message.answer (text[12:])
    current_question_index = await get_quiz_index(callback.from_user.id)
    statistic = await get_quiz_stats(callback.from_user.id)
    correct_option = quiz_data[current_question_index]['correct_option']
    await callback.message.answer(f"Неправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}")
    current_question_index += 1
    await update_quiz_index_and_stats(callback.from_user.id, current_question_index, statistic)
    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        current_question_index = 0
        await update_quiz_index_and_stats(callback.from_user.id, current_question_index, statistic)
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Новая игра"))
    builder.add(types.KeyboardButton(text="Продолжить игру"))
    builder.add(types.KeyboardButton(text="Статистика"))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))

async def get_question(message, user_id):
    current_question_index = await get_quiz_index(user_id)
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)

async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    statistic = 0
    await update_quiz_index_and_stats(user_id, current_question_index, statistic)
    await get_question(message, user_id)

async def continue_quiz(message):
    user_id = message.from_user.id
    current_question_index = await get_quiz_index(user_id)
    if current_question_index == len(quiz_data):
        await new_quiz(message)
    else:
        await get_question(message, user_id)

@dp.message(F.text=="Новая игра")
@dp.message(Command("newquiz"))
async def cmd_quiz(message: types.Message):
    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)

@dp.message(F.text=="Продолжить игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    await message.answer(f"Давайте начнем квиз!")
    await continue_quiz(message)

@dp.message(F.text=="Статистика")
@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    await message.answer(f"Статистика по пользователям:")
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT user_id FROM quiz_state', ()) as cursor:
            user_id_list = await cursor.fetchall()
        async with db.execute('SELECT question_index FROM quiz_state', ()) as cursor:
            question_index_list = await cursor.fetchall()
        async with db.execute('SELECT stats FROM quiz_state', ()) as cursor:
            stats_list = await cursor.fetchall()
    for i in range(len(user_id_list)):
        await message.answer(f"{i}:{(await bot.get_chat(user_id_list[i][0])).first_name} - {stats_list[i][0]}/{len(quiz_data) if len(quiz_data)==(question_index_list[i][0]) else question_index_list[i][0]}")

async def main():
    await create_table()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())