import discord

from discord.ext import commands, tasks

import time

import database

from config import VOICE_LOG_SECONDS





class VoiceLogs(commands.Cog):


    def __init__(self, bot):

        self.bot = bot

        self.cleanup_logs.start()







    def cog_unload(self):

        self.cleanup_logs.cancel()







    @commands.Cog.listener()

    async def on_voice_state_update(

        self,

        member: discord.Member,

        before: discord.VoiceState,

        after: discord.VoiceState

    ):


        # JOIN

        if before.channel is None and after.channel:


            await self.log_voice(

                member,

                after.channel,

                "JOIN"

            )







        # LEAVE

        elif before.channel and after.channel is None:


            await self.log_voice(

                member,

                before.channel,

                "LEAVE"

            )







        # MOVE

        elif before.channel != after.channel:


            if before.channel:


                await self.log_voice(

                    member,

                    before.channel,

                    "LEAVE"

                )



            if after.channel:


                await self.log_voice(

                    member,

                    after.channel,

                    "JOIN"

                )









    async def log_voice(

        self,

        member,

        channel,

        action

    ):


        # traži carry sa ovim VC ID-em


        db = await database.get_db()


        cursor = await db.execute(

            """

            SELECT carry_id

            FROM carries

            WHERE voice_id=?

            """,

            (

                channel.id,

            )

        )


        carry = await cursor.fetchone()


        await db.close()





        if not carry:

            return





        await database.add_voice_log(

            carry[0],

            member.id,

            action,

            int(time.time())

        )









    @tasks.loop(

        seconds=60

    )

    async def cleanup_logs(self):


        cutoff = int(time.time()) - VOICE_LOG_SECONDS


        await database.clean_voice_logs(

            cutoff

        )









async def setup(bot):

    await bot.add_cog(

        VoiceLogs(bot)

    )
