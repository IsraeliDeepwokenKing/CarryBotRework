import discord

from discord.ext import commands

import asyncio
import time

import database

from config import (
    CHANNELS,
    INCIDENT_DELETE_TIME
)





class IncidentModal(discord.ui.Modal):


    def __init__(self, carry_id):

        super().__init__(

            title="Carry Incident Report"

        )

        self.carry_id = carry_id





        self.users = discord.ui.TextInput(

            label="User ID(s)",

            placeholder="Example: 123456789, 987654321",

            required=True

        )



        self.clip = discord.ui.TextInput(

            label="Clip Link",

            placeholder="Paste clip URL",

            required=True

        )



        self.context = discord.ui.TextInput(

            label="What happened?",

            placeholder="Explain the incident",

            style=discord.TextStyle.paragraph,

            required=True

        )



        self.add_item(self.users)

        self.add_item(self.clip)

        self.add_item(self.context)







    async def on_submit(

        self,

        interaction: discord.Interaction

    ):


        carry = await database.get_carry(

            self.carry_id

        )


        if not carry:


            await interaction.response.send_message(

                "Carry no longer exists.",

                ephemeral=True

            )

            return





        players = await database.get_players(

            self.carry_id

        )



        voice = await database.get_voice_logs(

            self.carry_id

        )







        player_list = "\n".join(

            [

                f"<@{x[0]}>"

                for x in players

            ]

        )



        if not player_list:

            player_list = "None"







        voice_list = "\n".join(

            [

                f"<@{x[2]}> - {x[3]}"

                for x in voice

            ]

        )



        if not voice_list:

            voice_list = "No recent voice activity"







        embed = discord.Embed(

            title="Carry Incident Report",

            color=discord.Color.red()

        )



        embed.add_field(

            name="Carry ID",

            value=f"`{self.carry_id}`",

            inline=False

        )



        embed.add_field(

            name="Host",

            value=f"<@{carry[2]}>",

            inline=False

        )



        embed.add_field(

            name="Reported User ID(s)",

            value=self.users.value,

            inline=False

        )



        embed.add_field(

            name="Clip",

            value=self.clip.value,

            inline=False

        )



        embed.add_field(

            name="Context",

            value=self.context.value,

            inline=False

        )



        embed.add_field(

            name="Carry Players",

            value=player_list[:1024],

            inline=False

        )



        embed.add_field(

            name="Voice Logs",

            value=voice_list[:1024],

            inline=False

        )





        channel = discord.utils.get(

            interaction.guild.text_channels,

            name=CHANNELS["incident_reports"]

        )





        if channel is None:


            await interaction.response.send_message(

                "Incident channel missing. Run /setup.",

                ephemeral=True

            )

            return







        message = await channel.send(

            embed=embed,

            view=ResolveView()

        )





        await database.create_incident(

            message.id,

            channel.id,

            int(time.time())

        )





        await interaction.response.send_message(

            "Incident submitted.",

            ephemeral=True

        )









class ResolveView(discord.ui.View):


    def __init__(self):

        super().__init__(

            timeout=None

        )







    @discord.ui.button(

        label="Resolve",

        style=discord.ButtonStyle.success,

        custom_id="resolve_incident"

    )

    async def resolve(

        self,

        interaction: discord.Interaction,

        button: discord.ui.Button

    ):


        if not interaction.user.guild_permissions.manage_messages:


            await interaction.response.send_message(

                "You need moderator permissions.",

                ephemeral=True

            )

            return





        await interaction.response.send_message(

            "Resolved. Deleting in 1 hour.",

            ephemeral=True

        )





        await asyncio.sleep(

            INCIDENT_DELETE_TIME

        )





        try:

            await interaction.message.delete()

        except:

            pass







class Incidents(commands.Cog):


    def __init__(

        self,

        bot

    ):

        self.bot = bot







async def setup(bot):

    await bot.add_cog(

        Incidents(bot)

    )
