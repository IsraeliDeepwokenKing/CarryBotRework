import os
import asyncio

import discord
from discord.ext import commands

import database
from keep_alive import keep_alive



TOKEN = os.getenv("TOKEN")





class CarryBot(commands.Bot):

    def __init__(self):

        intents = discord.Intents.default()

        intents.members = True
        intents.message_content = True
        intents.voice_states = True


        super().__init__(
            command_prefix="!",
            intents=intents
        )





    async def setup_hook(self):

        await database.setup_database()


        extensions = [

            "cogs.setup",
            "cogs.host",
            "cogs.carry",
            "cogs.voice_logs",
            "cogs.incidents",
            "cogs.blacklist",
            "cogs.cleanup"

        ]


        for extension in extensions:

            try:

                await self.load_extension(extension)

                print(
                    f"Loaded: {extension}"
                )


            except Exception as error:

                print(
                    f"Failed loading {extension}: {error}"
                )



        synced = await self.tree.sync()


        print(
            f"Synced {len(synced)} slash commands"
        )







    async def on_ready(self):

        print("======================")

        print(
            f"Logged in as {self.user}"
        )

        print(
            f"Servers: {len(self.guilds)}"
        )

        print("======================")









bot = CarryBot()







async def main():

    if not TOKEN:

        print(
            "ERROR: TOKEN environment variable missing"
        )

        return



    keep_alive()


    await bot.start(
        TOKEN
    )








if __name__ == "__main__":

    asyncio.run(
        main()
    )
