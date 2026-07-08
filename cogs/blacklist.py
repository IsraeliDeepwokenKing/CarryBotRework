import discord

from discord.ext import commands

from discord import app_commands

import time

import database





class Blacklist(commands.Cog):


    def __init__(self, bot):

        self.bot = bot







    @app_commands.command(

        name="blacklist",

        description="Blacklist user from carries"

    )

    @app_commands.checks.has_permissions(

        manage_messages=True

    )

    async def blacklist(

        self,

        interaction: discord.Interaction,

        user: discord.Member,

        reason: str

    ):


        await database.add_blacklist(

            user.id,

            reason,

            interaction.user.id,

            int(time.time())

        )





        await interaction.response.send_message(

            f"Blacklisted {user.mention}\nReason: {reason}",

            ephemeral=True

        )









    @app_commands.command(

        name="unblacklist",

        description="Remove user from blacklist"

    )

    @app_commands.checks.has_permissions(

        manage_messages=True

    )

    async def unblacklist(

        self,

        interaction: discord.Interaction,

        user: discord.Member

    ):


        await database.remove_blacklist(

            user.id

        )





        await interaction.response.send_message(

            f"Removed {user.mention} from blacklist.",

            ephemeral=True

        )









    @app_commands.command(

        name="blacklist_check",

        description="Check blacklist status"

    )

    @app_commands.checks.has_permissions(

        manage_messages=True

    )

    async def blacklist_check(

        self,

        interaction: discord.Interaction,

        user: discord.Member

    ):


        result = await database.is_blacklisted(

            user.id

        )





        if result:


            await interaction.response.send_message(

                f"{user.mention} is blacklisted.",

                ephemeral=True

            )


        else:


            await interaction.response.send_message(

                f"{user.mention} is not blacklisted.",

                ephemeral=True

            )









async def setup(bot):

    await bot.add_cog(

        Blacklist(bot)

    )
