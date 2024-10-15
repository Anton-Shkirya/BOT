import aiosqlite
DB_NAME = 'quiz_bot.db'
async def get_quiz_index(user_id):
     async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0

async def get_quiz_stats(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT stats FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            results1 = await cursor.fetchone()
            if results1 is not None:
                return results1[0]
            else:
                return 0

async def get_quiz(message):
    user_id = message.from_user.id
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT stats FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0

async def update_quiz_index_and_stats(user_id, index, statistic):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index, stats) VALUES (?, ?, ?)', (user_id, index, statistic))
        await db.commit()

async def create_table():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY, question_index INTEGER, stats INTEGER)''')
        await db.commit()