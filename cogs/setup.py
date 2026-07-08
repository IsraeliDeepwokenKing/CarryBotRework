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

        description="Setup Deepwoken carry system"

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





        # ==========================
        # Category
        # ==========================


        category = discord.utils.get(

            guild.categories,

            name=CHANNELS["category"]

        )


        if not category:


            category = await guild.create_category(

                CHANNELS["category"]

            )







        # ==========================
        # Channels
        # ==========================


        created_channels = {}



        for key in [

            "carry_pings",

            "hoster_cmds",

            "incident_reports"

        ]:


            channel_name = CHANNELS[key]



            channel = discord.utils.get(

                guild.text_channels,

                name=channel_name

            )



            if not channel:


                channel = await guild.create_text_channel(

                    channel_name,

                    category=category

                )



            created_channels[key] = channel







        # ==========================
        # Roles
        # ==========================


        roles_to_create = list(

            HOSTER_ROLES.values()

        ) + list(

            CARRY_ROLES.values()

        )





        created_roles = {}



        for role_name in roles_to_create:


            role = discord.utils.get(

                guild.roles,

                name=role_name

            )


            if not role:


                role = await guild.create_role(

                    name=role_name

                )


            created_roles[role_name] = role







        # ==========================
        # Permissions
        # ==========================


        bot_member = guild.me



        for channel in created_channels.values():


            await channel.set_permissions(

                guild.default_role,

                send_messages=False

            )


            await channel.set_permissions(

                bot_member,

                send_messages=True,

                view_channel=True

            )






        # Hoster commands channel

        hoster_channel = created_channels["hoster_cmds"]


        await hoster_channel.set_permissions(

            guild.default_role,

            send_messages=False

        )







        # ==========================
        # Save IDs
        # ==========================


        db = await database.get_db()


        await db.execute(

            """

            INSERT OR REPLACE INTO settings

            VALUES (?, ?, ?, ?, ?)

            """,

            (

                guild.id,

                category.id,

                created_channels["carry_pings"].id,

                created_channels["hoster_cmds"].id,

                created_channels["incident_reports"].id

            )

        )


        await db.commit()

        await db.close()







        await interaction.followup.send(

            "✅ Deepwoken carry system setup complete.",

            ephemeral=True

        )









async def setup(bot):

    await bot.add_cog(

        Setup(bot)

    )
