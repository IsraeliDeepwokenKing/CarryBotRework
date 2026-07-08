from discord.ext import commands, tasks

import time

import database

from config import VOICE_LOG_SECONDS





class Cleanup(commands.Cog):


    def __init__(self, bot):

        self.bot = bot

        self.cleanup.start()







    def cog_unload(self):

        self.cleanup.cancel()







    @tasks.loop(

        minutes=5

    )

    async def cleanup(self):


        cutoff = int(time.time()) - VOICE_LOG_SECONDS


        await database.clean_voice_logs(

            cutoff

        )









async def setup(bot):

    await bot.add_cog(

        Cleanup(bot)

    )
