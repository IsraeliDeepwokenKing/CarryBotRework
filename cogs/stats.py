import discord

from discord.ext import commands

import database





class Stats(commands.Cog):


    def __init__(self,bot):

        self.bot = bot





    @discord.app_commands.command(

        name="leaderboard",

        description="Show top carry hosts"

    )
    async def leaderboard(

        self,

        interaction: discord.Interaction

    ):


        data = await database.get_leaderboard()



        embed = discord.Embed(

            title="🏆 Carry Leaderboard",

            color=discord.Color.gold()

        )



        if not data:


            embed.description = (
                "No completed carries yet."
            )


        else:


            text = ""


            for index, player in enumerate(data,1):


                text += (

                    f"**{index}.** "

                    f"{player[0]} "

                    f"- {player[1]} completed\n"

                )


            embed.description = text



        await interaction.response.send_message(

            embed=embed

        )






async def setup(bot):

    await bot.add_cog(
        Stats(bot)
    )
