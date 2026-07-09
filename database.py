import aiosqlite

from config import DATABASE_FILE





async def get_db():

    return await aiosqlite.connect(
        DATABASE_FILE
    )







async def init_db():

    db = await get_db()



    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (

            guild_id INTEGER PRIMARY KEY,

            category_id INTEGER,

            carry_ping_id INTEGER,

            hoster_cmd_id INTEGER,

            incident_id INTEGER

        )
        """
    )





    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS carries (

            carry_id TEXT PRIMARY KEY,

            guild_id INTEGER,

            host_id INTEGER,

            dungeon TEXT,

            slots INTEGER,

            rules TEXT,

            message_id INTEGER,

            voice_id INTEGER,

            role_id INTEGER,

            status TEXT DEFAULT 'WAITING'

        )
        """
    )






    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS players (

            carry_id TEXT,

            user_id INTEGER,

            username TEXT

        )
        """
    )







    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS voice_logs (

            carry_id TEXT,

            user_id INTEGER,

            action TEXT,

            timestamp INTEGER

        )
        """
    )







    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS blacklist (

            user_id INTEGER PRIMARY KEY,

            reason TEXT,

            moderator INTEGER,

            timestamp INTEGER

        )
        """
    )







    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS incidents (

            message_id INTEGER PRIMARY KEY,

            channel_id INTEGER,

            delete_time INTEGER

        )
        """
    )





    await db.commit()

    await db.close()







# -------------------------
# SETTINGS
# -------------------------



async def save_settings(

    guild_id,

    category_id,

    carry_ping_id,

    hoster_cmd_id,

    incident_id

):


    db = await get_db()



    await db.execute(

        """

        INSERT OR REPLACE INTO settings

        VALUES (?,?,?,?,?)

        """,

        (

            guild_id,

            category_id,

            carry_ping_id,

            hoster_cmd_id,

            incident_id

        )

    )



    await db.commit()

    await db.close()







async def get_settings(

    guild_id

):


    db = await get_db()



    cursor = await db.execute(

        """

        SELECT *

        FROM settings

        WHERE guild_id=?

        """,

        (

            guild_id,

        )

    )


    data = await cursor.fetchone()


    await db.close()


    return data







# -------------------------
# CARRY
# -------------------------



async def create_carry(

    carry_id,

    guild_id,

    host_id,

    dungeon,

    slots,

    rules

):


    db = await get_db()



    await db.execute(

        """

        INSERT INTO carries

        (

        carry_id,

        guild_id,

        host_id,

        dungeon,

        slots,

        rules

        )

        VALUES (?,?,?,?,?,?)

        """,

        (

            carry_id,

            guild_id,

            host_id,

            dungeon,

            slots,

            rules

        )

    )



    await db.commit()

    await db.close()







async def get_carry(

    carry_id

):


    db = await get_db()



    cursor = await db.execute(

        """

        SELECT *

        FROM carries

        WHERE carry_id=?

        """,

        (

            carry_id,

        )

    )


    data = await cursor.fetchone()


    await db.close()



    return data







async def update_carry_resources(

    carry_id,

    message_id=None,

    voice_id=None,

    role_id=None,

    status=None

):


    db = await get_db()



    if message_id:

        await db.execute(

            """

            UPDATE carries

            SET message_id=?

            WHERE carry_id=?

            """,

            (

                message_id,

                carry_id

            )

        )



    if voice_id:

        await db.execute(

            """

            UPDATE carries

            SET voice_id=?

            WHERE carry_id=?

            """,

            (

                voice_id,

                carry_id

            )

        )



    if role_id:

        await db.execute(

            """

            UPDATE carries

            SET role_id=?

            WHERE carry_id=?

            """,

            (

                role_id,

                carry_id

            )

        )



    if status:

        await db.execute(

            """

            UPDATE carries

            SET status=?

            WHERE carry_id=?

            """,

            (

                status,

                carry_id

            )

        )




    await db.commit()

    await db.close()







async def delete_carry(

    carry_id

):


    db = await get_db()



    await db.execute(

        "DELETE FROM players WHERE carry_id=?",

        (

            carry_id,

        )

    )



    await db.execute(

        "DELETE FROM voice_logs WHERE carry_id=?",

        (

            carry_id,

        )

    )



    await db.execute(

        "DELETE FROM carries WHERE carry_id=?",

        (

            carry_id,

        )

    )



    await db.commit()

    await db.close()







# -------------------------
# PLAYERS
# -------------------------



async def add_player(

    carry_id,

    user_id,

    username

):


    db = await get_db()



    await db.execute(

        """

        INSERT INTO players

        VALUES (?,?,?)

        """,

        (

            carry_id,

            user_id,

            username

        )

    )



    await db.commit()

    await db.close()







async def get_players(

    carry_id

):


    db = await get_db()



    cursor = await db.execute(

        """

        SELECT *

        FROM players

        WHERE carry_id=?

        """,

        (

            carry_id,

        )

    )



    data = await cursor.fetchall()


    await db.close()


    return data







# -------------------------
# BLACKLIST
# -------------------------



async def add_blacklist(

    user_id,

    reason,

    moderator,

    timestamp

):


    db = await get_db()



    await db.execute(

        """

        INSERT OR REPLACE INTO blacklist

        VALUES (?,?,?,?)

        """,

        (

            user_id,

            reason,

            moderator,

            timestamp

        )

    )



    await db.commit()

    await db.close()







async def remove_blacklist(

    user_id

):


    db = await get_db()



    await db.execute(

        "DELETE FROM blacklist WHERE user_id=?",

        (

            user_id,

        )

    )



    await db.commit()

    await db.close()







async def is_blacklisted(

    user_id

):


    db = await get_db()



    cursor = await db.execute(

        """

        SELECT user_id

        FROM blacklist

        WHERE user_id=?

        """,

        (

            user_id,

        )

    )


    result = await cursor.fetchone()


    await db.close()



    return result is not None
