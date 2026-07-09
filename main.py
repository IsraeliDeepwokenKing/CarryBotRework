import discord

from discord.ext import commands

import database

import os


from keep_alive import keep_alive





TOKEN = os.getenv("TOKEN")







class CarryBot(commands.Bot):


    def __init__(self):

        intents = discord.Intents.default()

        intents.members = True

        intents.message_content = True


        super().__init__(

            command_prefix="!",

            intents=intents

        )







    async def setup_hook(self):


        await database.init_db()



        extensions = [

            "cogs.setup",

            "cogs.host",

            "cogs.carry",

            "cogs.incidents",

            "cogs.blacklist",

        ]



        for ext in extensions:

            try:

                await self.load_extension(ext)

                print(

                    f"Loaded {ext}"

                )

            except Exception as e:

                print(

                    f"FAILED {ext}: {e}"

                )






        try:

            synced = await self.tree.sync()

            print(

                f"Synced {len(synced)} commands"

            )

        except Exception as e:

            print(

                f"Sync error: {e}"

            )









bot = CarryBot()







keep_alive()





bot.run(TOKEN)
