import discord

from discord.ext import commands
from discord import app_commands

import database

from config import CHANNELS, HOSTER_ROLES, CARRY_ROLES





class Setup(commands.Cog):

    def __init__(self, bot):

        self.bot = bot





    @app_commands.command(
        name="setup",
        description="Setup Deepwoken Carry system"
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def setup(
        self,
        interaction: discord.Interaction
    ):

        guild = interaction.guild


        await interaction.response.defer(
            ephemeral=True
        )



        # CATEGORY

        category = discord.utils.find(
            lambda c: c.name == CHANNELS["category"],
            guild.categories
        )


        if category is None:

            category = await guild.create_category(
                CHANNELS["category"]
            )





        # CHANNELS

        created = {}

        for key in [

            "carry_pings",
            "hoster_cmds",
            "incident_reports"

        ]:

            name = CHANNELS[key]


            channel = discord.utils.find(

                lambda c: c.name == name,

                guild.text_channels

            )


            if channel is None:

                channel = await guild.create_text_channel(

                    name,

                    category=category

                )


            created[key] = channel






        # ROLES

        roles = {}


        all_roles = (

            list(HOSTER_ROLES.values())

            +

            list(CARRY_ROLES.values())

        )


        for role_name in all_roles:


            role = discord.utils.find(

                lambda r: r.name == role_name,

                guild.roles

            )


            if role is None:


                role = await guild.create_role(

                    name=role_name,

                    reason="Carry bot setup"

                )


            roles[role_name] = role







        # PERMISSIONS


        bot_member = guild.me



        for channel in created.values():


            await channel.set_permissions(

                guild.default_role,

                view_channel=True,

                send_messages=False

            )


            await channel.set_permissions(

                bot_member,

                view_channel=True,

                send_messages=True,

                embed_links=True

            )






        await database.save_settings(

            guild.id,

            category.id,

            created["carry_pings"].id,

            created["hoster_cmds"].id,

            created["incident_reports"].id

        )





        await interaction.followup.send(

            "Setup complete. Channels and roles created.",

            ephemeral=True

        )









async def setup(bot):

    await bot.add_cog(

        Setup(bot)

    )
