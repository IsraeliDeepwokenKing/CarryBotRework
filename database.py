import aiosqlite
from datetime import datetime


DATABASE = "carry.db"



async def setup_database():

    async with aiosqlite.connect(DATABASE) as db:


        await db.execute("""
        CREATE TABLE IF NOT EXISTS carries(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            host_id INTEGER,
            host_name TEXT,

            dungeon TEXT,

            slots INTEGER,

            status TEXT DEFAULT 'waiting',

            role_id INTEGER DEFAULT 0,

            vc_id INTEGER DEFAULT 0,

            lobby_message_id INTEGER DEFAULT 0,

            created TEXT

        )
        """)



        await db.execute("""
        CREATE TABLE IF NOT EXISTS players(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            carry_id INTEGER,

            user_id INTEGER,

            username TEXT,

            position INTEGER

        )
        """)



        await db.execute("""
        CREATE TABLE IF NOT EXISTS voice_logs(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER,

            username TEXT,

            event TEXT,

            channel_id INTEGER,

            time TEXT

        )
        """)



        await db.execute("""
        CREATE TABLE IF NOT EXISTS incidents(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            carry_id INTEGER,

            host_id INTEGER,

            username TEXT,

            reason TEXT,

            logs TEXT,

            created TEXT

        )
        """)



        await db.execute("""
        CREATE TABLE IF NOT EXISTS carry_messages(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            carry_id INTEGER,

            message_id INTEGER,

            channel_id INTEGER

        )
        """)



        await db.execute("""
        CREATE TABLE IF NOT EXISTS statistics(

            user_id INTEGER PRIMARY KEY,

            username TEXT,

            completed INTEGER DEFAULT 0,

            hosted INTEGER DEFAULT 0

        )
        """)



        await db.commit()






# ======================
# CARRY
# ======================


async def create_carry(
    host_id,
    host_name,
    dungeon,
    slots
):

    async with aiosqlite.connect(DATABASE) as db:


        cur = await db.execute(
        """
        INSERT INTO carries

        (
        host_id,
        host_name,
        dungeon,
        slots,
        created

        )

        VALUES(?,?,?,?,?)

        """,

        (
        host_id,
        host_name,
        dungeon,
        slots,
        datetime.now().isoformat()

        ))


        await db.commit()


        return cur.lastrowid





async def get_carry(
    carry_id
):

    async with aiosqlite.connect(DATABASE) as db:


        cur = await db.execute(
        """
        SELECT *

        FROM carries

        WHERE id=?

        """,

        (
        carry_id,
        ))


        return await cur.fetchone()





async def update_carry(
    carry_id,
    role_id,
    vc_id
):

    async with aiosqlite.connect(DATABASE) as db:


        await db.execute(
        """
        UPDATE carries

        SET

        role_id=?,
        vc_id=?,
        status='running'

        WHERE id=?

        """,

        (
        role_id,
        vc_id,
        carry_id

        ))


        await db.commit()





async def end_carry(
    carry_id
):

    async with aiosqlite.connect(DATABASE) as db:


        await db.execute(
        """
        UPDATE carries

        SET status='ended'

        WHERE id=?

        """,

        (
        carry_id,
        ))


        await db.commit()





# ======================
# PLAYERS
# ======================


async def add_player(
    carry_id,
    user_id,
    username,
    position
):

    async with aiosqlite.connect(DATABASE) as db:


        await db.execute(
        """
        INSERT INTO players

        (
        carry_id,
        user_id,
        username,
        position

        )

        VALUES(?,?,?,?)

        """,

        (
        carry_id,
        user_id,
        username,
        position

        ))


        await db.commit()






async def get_players(
    carry_id
):

    async with aiosqlite.connect(DATABASE) as db:


        cur = await db.execute(
        """
        SELECT username

        FROM players

        WHERE carry_id=?

        ORDER BY position

        """,

        (
        carry_id,
        ))


        return await cur.fetchall()





async def player_exists(
    carry_id,
    user_id
):

    async with aiosqlite.connect(DATABASE) as db:


        cur = await db.execute(
        """
        SELECT *

        FROM players

        WHERE carry_id=?
        AND user_id=?

        """,

        (
        carry_id,
        user_id

        ))


        return await cur.fetchone()





async def player_count(
    carry_id
):

    async with aiosqlite.connect(DATABASE) as db:


        cur = await db.execute(
        """
        SELECT COUNT(*)

        FROM players

        WHERE carry_id=?

        """,

        (
        carry_id,
        ))


        result = await cur.fetchone()


        return result[0]






# ======================
# VOICE LOGS
# ======================


async def add_voice_log(
    user_id,
    username,
    event,
    channel_id
):

    async with aiosqlite.connect(DATABASE) as db:


        await db.execute(
        """
        INSERT INTO voice_logs

        VALUES(NULL,?,?,?,?,?)

        """,

        (
        user_id,
        username,
        event,
        channel_id,
        datetime.now().strftime("%H:%M:%S")

        ))


        await db.commit()






async def get_voice_logs(
    channel_id
):

    async with aiosqlite.connect(DATABASE) as db:


        cur = await db.execute(
        """
        SELECT username,event,time

        FROM voice_logs

        WHERE channel_id=?

        ORDER BY id DESC

        LIMIT 50

        """,

        (
        channel_id,
        ))


        return await cur.fetchall()






# ======================
# MESSAGES
# ======================


async def save_message(
    carry_id,
    message_id,
    channel_id
):

    async with aiosqlite.connect(DATABASE) as db:


        await db.execute(
        """
        INSERT INTO carry_messages

        VALUES(NULL,?,?,?)

        """,

        (
        carry_id,
        message_id,
        channel_id

        ))


        await db.commit()





async def get_messages(
    carry_id
):

    async with aiosqlite.connect(DATABASE) as db:


        cur = await db.execute(
        """
        SELECT message_id,channel_id

        FROM carry_messages

        WHERE carry_id=?

        """,

        (
        carry_id,
        ))


        return await cur.fetchall()





# ======================
# STATS
# ======================


async def add_stat(
    user_id,
    username
):

    async with aiosqlite.connect(DATABASE) as db:


        await db.execute(
        """
        INSERT INTO statistics

        (
        user_id,
        username,
        completed,
        hosted

        )

        VALUES(?,?,1,1)

        ON CONFLICT(user_id)

        DO UPDATE SET

        completed=completed+1,
        hosted=hosted+1

        """,

        (
        user_id,
        username

        ))


        await db.commit()
