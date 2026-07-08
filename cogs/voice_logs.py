import discord

from discord.ext import commands

from datetime import datetime

import database





class VoiceLogs(commands.Cog):


    def __init__(self,bot):

        self.bot=bot





    @commands.Cog.listener()
    async def on_voice_state_update(

        self,
        member,
        before,
        after

    ):


        now=datetime.now().strftime(
            "%H:%M:%S"
        )



        # JOIN VC

        if before.channel is None and after.channel is not None:


            await database.add_voice_log(

                member.id,

                member.name,

                "JOIN",

                after.channel.id,

                now

            )


            print(
                f"{member} joined {after.channel.name}"
            )





        # LEAVE VC

        elif before.channel is not None and after.channel is None:


            await database.add_voice_log(

                member.id,

                member.name,

                "LEAVE",

                before.channel.id,

                now

            )


            print(
                f"{member} left {before.channel.name}"
            )






        # MOVE VC

        elif before.channel != after.channel:


            await database.add_voice_log(

                member.id,

                member.name,

                "MOVE_FROM",

                before.channel.id,

                now

            )


            await database.add_voice_log(

                member.id,

                member.name,

                "MOVE_TO",

                after.channel.id,

                now

            )





async def setup(bot):

    await bot.add_cog(
        VoiceLogs(bot)
    )
