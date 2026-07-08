import aiosqlite

from config import DATABASE_FILE





async def get_db():

    return await aiosqlite.connect(
        DATABASE_FILE
    )





async def setup_database():

    db = await get_db()


    await db.executescript("""

    CREATE TABLE IF NOT EXISTS settings (

        guild_id INTEGER PRIMARY KEY,

        category_id INTEGER,

        carry_pings_id INTEGER,

        hoster_cmds_id INTEGER,

        incident_reports_id INTEGER

    );





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

        active INTEGER DEFAULT 1

    );





    CREATE TABLE IF NOT EXISTS carry_players (

        carry_id TEXT,

        user_id INTEGER,

        username TEXT,

        joined_at INTEGER

    );





    CREATE TABLE IF NOT EXISTS voice_logs (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        carry_id TEXT,

        user_id INTEGER,

        action TEXT,

        timestamp INTEGER

    );





    CREATE TABLE IF NOT EXISTS blacklist (

        user_id INTEGER PRIMARY KEY,

        reason TEXT,

        moderator_id INTEGER,

        created_at INTEGER

    );





    CREATE TABLE IF NOT EXISTS incidents (

        message_id INTEGER PRIMARY KEY,

        channel_id INTEGER,

        delete_time INTEGER

    );

    """)


    await db.commit()

    await db.close()







# =========================
# SETTINGS
# =========================


async def save_settings(

    guild_id,

    category_id,

    carry_pings_id,

    hoster_cmds_id,

    incident_reports_id

):

    db = await get_db()


    await db.execute(

        """

        INSERT OR REPLACE INTO settings

        VALUES (?, ?, ?, ?, ?)

        """,

        (

            guild_id,

            category_id,

            carry_pings_id,

            hoster_cmds_id,

            incident_reports_id

        )

    )


    await db.commit()

    await db.close()





async def get_settings(guild_id):

    db = await get_db()


    cursor = await db.execute(

        """

        SELECT *

        FROM settings

        WHERE guild_id=?

        """,

        (guild_id,)

    )


    result = await cursor.fetchone()


    await db.close()


    return result







# =========================
# CARRY
# =========================


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

        VALUES (?, ?, ?, ?, ?, ?, NULL, NULL, NULL, 1)

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







async def get_carry(carry_id):

    db = await get_db()


    cursor = await db.execute(

        """

        SELECT *

        FROM carries

        WHERE carry_id=?

        """,

        (carry_id,)

    )


    result = await cursor.fetchone()


    await db.close()


    return result







async def update_carry_resources(

    carry_id,

    message_id=None,

    voice_id=None,

    role_id=None

):

    db = await get_db()


    await db.execute(

        """

        UPDATE carries

        SET

        message_id = COALESCE(?, message_id),

        voice_id = COALESCE(?, voice_id),

        role_id = COALESCE(?, role_id)

        WHERE carry_id=?

        """,

        (

            message_id,

            voice_id,

            role_id,

            carry_id

        )

    )


    await db.commit()

    await db.close()







async def delete_carry(carry_id):


    db = await get_db()


    await db.execute(

        "DELETE FROM carry_players WHERE carry_id=?",

        (carry_id,)

    )


    await db.execute(

        "DELETE FROM voice_logs WHERE carry_id=?",

        (carry_id,)

    )


    await db.execute(

        "DELETE FROM carries WHERE carry_id=?",

        (carry_id,)

    )


    await db.commit()

    await db.close()







# =========================
# PLAYERS
# =========================


async def add_player(

    carry_id,

    user_id,

    username

):

    db = await get_db()


    await db.execute(

        """

        INSERT INTO carry_players

        VALUES (?, ?, ?, ?)

        """,

        (

            carry_id,

            user_id,

            username,

            0

        )

    )


    await db.commit()

    await db.close()







async def remove_player(

    carry_id,

    user_id

):

    db = await get_db()


    await db.execute(

        """

        DELETE FROM carry_players

        WHERE carry_id=? AND user_id=?

        """,

        (

            carry_id,

            user_id

        )

    )


    await db.commit()

    await db.close()







async def get_players(carry_id):

    db = await get_db()


    cursor = await db.execute(

        """

        SELECT user_id, username

        FROM carry_players

        WHERE carry_id=?

        """,

        (carry_id,)

    )


    result = await cursor.fetchall()


    await db.close()


    return result







# =========================
# VOICE LOGS
# =========================


async def add_voice_log(

    carry_id,

    user_id,

    action,

    timestamp

):

    db = await get_db()


    await db.execute(

        """

        INSERT INTO voice_logs

        VALUES (NULL, ?, ?, ?, ?)

        """,

        (

            carry_id,

            user_id,

            action,

            timestamp

        )

    )


    await db.commit()

    await db.close()







async def get_voice_logs(carry_id):

    db = await get_db()


    cursor = await db.execute(

        """

        SELECT *

        FROM voice_logs

        WHERE carry_id=?

        ORDER BY timestamp ASC

        """,

        (carry_id,)

    )


    result = await cursor.fetchall()


    await db.close()


    return result







async def clean_voice_logs(timestamp):

    db = await get_db()


    await db.execute(

        """

        DELETE FROM voice_logs

        WHERE timestamp < ?

        """,

        (timestamp,)

    )


    await db.commit()

    await db.close()







# =========================
# BLACKLIST
# =========================


async def add_blacklist(

    user_id,

    reason,

    moderator_id,

    created_at

):

    db = await get_db()


    await db.execute(

        """

        INSERT OR REPLACE INTO blacklist

        VALUES (?, ?, ?, ?)

        """,

        (

            user_id,

            reason,

            moderator_id,

            created_at

        )

    )


    await db.commit()

    await db.close()







async def remove_blacklist(user_id):

    db = await get_db()


    await db.execute(

        """

        DELETE FROM blacklist

        WHERE user_id=?

        """,

        (user_id,)

    )


    await db.commit()

    await db.close()







async def is_blacklisted(user_id):

    db = await get_db()


    cursor = await db.execute(

        """

        SELECT user_id

        FROM blacklist

        WHERE user_id=?

        """,

        (user_id,)

    )


    result = await cursor.fetchone()


    await db.close()


    return result is not None







# =========================
# INCIDENTS
# =========================


async def create_incident(

    message_id,

    channel_id,

    delete_time

):

    db = await get_db()


    await db.execute(

        """

        INSERT OR REPLACE INTO incidents

        VALUES (?, ?, ?)

        """,

        (

            message_id,

            channel_id,

            delete_time

        )

    )


    await db.commit()

    await db.close()
