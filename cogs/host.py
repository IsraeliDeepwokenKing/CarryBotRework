import discord
from discord.ext import commands
from discord import app_commands

import random
import string

import database

from config import (
    CARRY_LIMITS,
    HOSTER_ROLES,
    CARRY_ROLES,
    CHANNELS,
    CARRY_ID_LENGTH
)





def generate_carry_id():

    chars = string.ascii_uppercase + string.digits

    return "".join(
        random.choice(chars)
        for _ in range(CARRY_ID_LENGTH)
    )







class HostModal(discord.ui.Modal):


    def __init__(self, dungeon):

        super().__init__(
            title=f"{dungeon} Carry"
        )


        self.dungeon = dungeon



        self.slots = discord.ui.TextInput(

            label="Player amount",

            placeholder=f"1-{CARRY_LIMITS[dungeon]}",

            max_length=2

        )


        self.rules = discord.ui.TextInput(

            label="Rules",

            placeholder="Example: No freshies, Take Enforcers",

            required=False,

            style=discord.TextStyle.paragraph

        )



        self.add_item(self.slots)

        self.add_item(self.rules)







    async def on_submit(

        self,

        interaction: discord.Interaction

    ):


        try:

            slots = int(
                self.slots.value
            )

        except:

            await interaction.response.send_message(

                "Invalid number.",

                ephemeral=True

            )

            return





        if slots > CARRY_LIMITS[self.dungeon] or slots < 1:


            await interaction.response.send_message(

                "Invalid player amount.",

                ephemeral=True

            )

            return





        carry_id = generate_carry_id()


        rules = self.rules.value.strip()


        if rules == "":

            rules = "None"







        await database.create_carry(

            carry_id,

            interaction.guild.id,

            interaction.user.id,

            self.dungeon,

            slots,

            rules

        )







        channel = discord.utils.get(

            interaction.guild.text_channels,

            id=(await database.get_settings(

                interaction.guild.id

            ))[2]

        )





        ping_role = discord.utils.get(

            interaction.guild.roles,

            name=CARRY_ROLES[self.dungeon]

        )







        embed = discord.Embed(

            title=f"{self.dungeon} Carry",

            color=discord.Color.blue()

        )


        embed.add_field(

            name="Host",

            value=interaction.user.mention,

            inline=False

        )


        embed.add_field(

            name="Carry ID",

            value=f"`{carry_id}`",

            inline=False

        )


        embed.add_field(

            name="Rules",

            value=rules,

            inline=False

        )


        embed.add_field(

            name=f"Players (1/{slots})",

            value=f"1. {interaction.user.mention}",

            inline=False

        )





        msg = await channel.send(

            content=ping_role.mention,

            embed=embed,

            view=CarryJoinView(carry_id)

        )





        await database.update_carry_resources(

            carry_id,

            message_id=msg.id

        )





        await database.add_player(

            carry_id,

            interaction.user.id,

            str(interaction.user)

        )





        try:

            await interaction.user.send(

                "Your carry control panel:",

                view=HostControlView(

                    carry_id

                )

            )

        except:

            pass






        await interaction.response.send_message(

            f"Carry created: `{carry_id}`",

            ephemeral=True

        )









class DungeonSelect(discord.ui.View):


    def __init__(self):

        super().__init__(

            timeout=60

        )



        for dungeon in CARRY_LIMITS:

            self.add_item(

                DungeonButton(dungeon)

            )









class DungeonButton(discord.ui.Button):


    def __init__(self, dungeon):

        super().__init__(

            label=dungeon,

            style=discord.ButtonStyle.primary

        )

        self.dungeon = dungeon






    async def callback(

        self,

        interaction: discord.Interaction

    ):


        required = HOSTER_ROLES[self.dungeon]


        role = discord.utils.get(

            interaction.guild.roles,

            name=required

        )



        if role not in interaction.user.roles:


            await interaction.response.send_message(

                f"Need role: {required}",

                ephemeral=True

            )

            return





        await interaction.response.send_modal(

            HostModal(

                self.dungeon

            )

        )









class CarryJoinView(discord.ui.View):


    def __init__(self, carry_id):

        super().__init__(

            timeout=None

        )

        self.carry_id = carry_id







    @discord.ui.button(

        label="Join",

        style=discord.ButtonStyle.success

    )

    async def join(

        self,

        interaction: discord.Interaction,

        button

    ):


        if await database.is_blacklisted(

            interaction.user.id

        ):

            await interaction.response.send_message(

                "You are blacklisted.",

                ephemeral=True

            )

            return





        players = await database.get_players(

            self.carry_id

        )



        carry = await database.get_carry(

            self.carry_id

        )



        if len(players) >= carry[4]:


            await interaction.response.send_message(

                "Carry full.",

                ephemeral=True

            )

            return





        await database.add_player(

            self.carry_id,

            interaction.user.id,

            str(interaction.user)

        )



        await interaction.response.send_message(

            "Joined.",

            ephemeral=True

        )








class HostControlView(discord.ui.View):


    def __init__(self, carry_id):

        super().__init__(

            timeout=None

        )

        self.carry_id = carry_id






    @discord.ui.button(

        label="Start Carry",

        style=discord.ButtonStyle.success

    )

    async def start(

        self,

        interaction,

        button

    ):


        await interaction.response.send_message(

            "Starting carry...",

            ephemeral=True

        )







    @discord.ui.button(

        label="Report Incident",

        style=discord.ButtonStyle.danger

    )

    async def report(

        self,

        interaction,

        button

    ):


        from cogs.incidents import IncidentModal


        await interaction.response.send_modal(

            IncidentModal(

                self.carry_id

            )

        )







    @discord.ui.button(

        label="End Carry",

        style=discord.ButtonStyle.secondary

    )

    async def end(

        self,

        interaction,

        button

    ):


        await database.delete_carry(

            self.carry_id

        )


        await interaction.response.send_message(

            "Carry ended.",

            ephemeral=True

        )









class Host(commands.Cog):


    def __init__(self, bot):

        self.bot = bot






    @app_commands.command(

        name="host",

        description="Create a carry"

    )

    async def host(

        self,

        interaction

    ):


        await interaction.response.send_message(

            "Choose dungeon:",

            view=DungeonSelect(),

            ephemeral=True

        )









async def setup(bot):

    await bot.add_cog(

        Host(bot)

    )
