import discord

from discord.ext import commands

import os
import asyncio

import database

from keep_alive import keep_alive





TOKEN = os.getenv("TOKEN")





intents = discord.Intents.default()

intents.members = True

intents.message_content = True

intents.voice_states = True





bot = commands.Bot(

    command_prefix="!",

    intents=intents

)







@bot.event
async def on_ready():


    print("===================")

    print(
        f"ONLINE: {bot.user}"
    )

    print("===================")



    await database.setup_database()



    try:


        synced = await bot.tree.sync()



        print(

            f"Synced {len(synced)} commands"

        )


    except Exception as e:


        print(
            f"Sync error: {e}"
        )









async def load_extensions():


    extensions = [


        "cogs.host",

        "cogs.carry",

        "cogs.voice_logs",

        "cogs.incidents",

        "cogs.stats"


    ]





    for extension in extensions:


        try:


            await bot.load_extension(
                extension
            )


            print(
                f"Loaded: {extension}"
            )



        except Exception as e:


            print(
                f"Failed {extension}: {e}"
            )









async def main():


    keep_alive()



    await load_extensions()



    await bot.start(
        TOKEN
    )








asyncio.run(main())
