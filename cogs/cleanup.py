import discord

from discord.ext import commands

import database

from config import REPORT_CHANNEL_ID





class IncidentModal(discord.ui.Modal):


    def __init__(

        self,

        carry_id

    ):


        super().__init__(

            title="Carry Incident Report"

        )


        self.carry_id = carry_id



        self.reason = discord.ui.TextInput(

            label="Describe the incident",

            style=discord.TextStyle.paragraph,

            placeholder="Explain what happened..."

        )


        self.add_item(

            self.reason

        )






    async def on_submit(

        self,

        interaction: discord.Interaction

    ):


        carry = await database.get_carry(

            self.carry_id

        )



        if not carry:


            await interaction.response.send_message(

                "Carry not found.",

                ephemeral=True

            )

            return





        logs = await database.get_voice_logs(

            carry[7]

        )





        log_text = ""



        for log in logs:


            log_text += (

                f"{log[0]} - "

                f"{log[1]} "

                f"({log[2]})\n"

            )




        await database.add_incident(

            self.carry_id,

            interaction.user.id,

            interaction.user.name,

            self.reason.value,

            log_text

        )





        channel = interaction.guild.get_channel(

            REPORT_CHANNEL_ID

        )





        if channel:


            embed = discord.Embed(

                title="🚨 Carry Incident Report",

                color=discord.Color.red()

            )



            embed.add_field(

                name="Host/Reporter",

                value=interaction.user.mention,

                inline=False

            )



            embed.add_field(

                name="Carry",

                value=f"{carry[3]} #{self.carry_id}",

                inline=False

            )



            embed.add_field(

                name="Reason",

                value=self.reason.value,

                inline=False

            )



            embed.add_field(

                name="Voice Logs",

                value=log_text[:1000] or "No logs",

                inline=False

            )



            await channel.send(

                embed=embed

            )






        await interaction.response.send_message(

            "✅ Incident report sent.",

            ephemeral=True

        )









class Incidents(commands.Cog):


    def __init__(

        self,

        bot

    ):

        self.bot=bot







async def setup(bot):


    await bot.add_cog(

        Incidents(bot)

    )
