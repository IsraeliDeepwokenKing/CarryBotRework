import discord
from discord.ext import commands
from discord import app_commands

import random
import string
import traceback

import database

from config import (
    CARRY_LIMITS,
    MINIMUM_PLAYERS,
    HOSTER_ROLES,
    CARRY_ROLES,
    CARRY_ID_LENGTH
)





def generate_carry_id():

    return "".join(
        random.choice(
            string.ascii_uppercase + string.digits
        )
        for _ in range(CARRY_ID_LENGTH)
    )







def build_carry_embed(carry, players):

    carry_id = carry[0]
    host_id = carry[2]
    dungeon = carry[3]
    slots = carry[4]
    rules = carry[5]


    embed = discord.Embed(

        title=f"{dungeon} Carry",

        description="Open carry queue",

        color=discord.Color.blurple()

    )


    embed.add_field(

        name="Host",

        value=f"<@{host_id}>",

        inline=True

    )


    embed.add_field(

        name="Players",

        value=f"{len(players)}/{slots}",

        inline=True

    )


    embed.add_field(

        name="Carry ID",

        value=f"`{carry_id}`",

        inline=True

    )


    embed.add_field(

        name="Rules",

        value=rules,

        inline=False

    )


    if len(players) < MINIMUM_PLAYERS[dungeon]:

        embed.set_footer(

            text=f"Needs {MINIMUM_PLAYERS[dungeon]} players before starting"

        )

    else:

        embed.set_footer(

            text="Ready to start"

        )


    return embed







class HostModal(discord.ui.Modal):


    def __init__(self, dungeon):

        super().__init__(

            title=f"{dungeon} Carry"

        )

        self.dungeon = dungeon



        self.slots = discord.ui.TextInput(

            label="Maximum players",

            placeholder=str(

                CARRY_LIMITS[dungeon]

            ),

            max_length=2

        )


        self.rules = discord.ui.TextInput(

            label="Rules",

            placeholder="Example: Take Enforcers, No freshies",

            required=False,

            style=discord.TextStyle.paragraph

        )


        self.add_item(self.slots)

        self.add_item(self.rules)







    async def on_submit(self, interaction):

        try:


            slots = int(

                self.slots.value

            )


            if slots < MINIMUM_PLAYERS[self.dungeon]:

                await interaction.response.send_message(

                    f"Minimum for {self.dungeon} is {MINIMUM_PLAYERS[self.dungeon]}.",

                    ephemeral=True

                )

                return



            if slots > CARRY_LIMITS[self.dungeon]:

                await interaction.response.send_message(

                    "Too many players.",

                    ephemeral=True

                )

                return





            settings = await database.get_settings(

                interaction.guild.id

            )


            if not settings:


                await interaction.response.send_message(

                    "Run /setup first.",

                    ephemeral=True

                )

                return






            carry_id = generate_carry_id()



            rules = self.rules.value or "No rules"





            await database.create_carry(

                carry_id,

                interaction.guild.id,

                interaction.user.id,

                self.dungeon,

                slots,

                rules

            )




            await database.add_player(

                carry_id,

                interaction.user.id,

                str(interaction.user)

            )





            carry = await database.get_carry(

                carry_id

            )


            players = await database.get_players(

                carry_id

            )





            channel = interaction.guild.get_channel(

                settings[2]

            )



            role = discord.utils.get(

                interaction.guild.roles,

                name=CARRY_ROLES[self.dungeon]

            )


            if not channel or not role:


                await interaction.response.send_message(

                    "Setup incomplete. Run /setup again.",

                    ephemeral=True

                )

                return






            msg = await channel.send(

                content=role.mention,

                embed=build_carry_embed(

                    carry,

                    players

                ),

                view=JoinView(

                    carry_id

                )

            )





            await database.update_carry_resources(

                carry_id,

                message_id=msg.id

            )






            await interaction.user.send(

                "Carry control panel",

                view=HostPanel(

                    carry_id

                )

            )





            await interaction.response.send_message(

                f"Created `{carry_id}`",

                ephemeral=True

            )



        except Exception:

            traceback.print_exc()

            await interaction.response.send_message(

                "Host creation failed. Check console.",

                ephemeral=True

            )









class DungeonView(discord.ui.View):


    def __init__(self):

        super().__init__(

            timeout=60

        )


        for dungeon in CARRY_LIMITS:

            self.add_item(

                DungeonButton(

                    dungeon

                )

            )









class DungeonButton(discord.ui.Button):


    def __init__(self, dungeon):

        super().__init__(

            label=dungeon,

            style=discord.ButtonStyle.primary

        )

        self.dungeon=dungeon







    async def callback(self, interaction):


        role = discord.utils.get(

            interaction.guild.roles,

            name=HOSTER_ROLES[self.dungeon]

        )


        if role not in interaction.user.roles:

            await interaction.response.send_message(

                "Missing hoster role.",

                ephemeral=True

            )

            return





        await interaction.response.send_modal(

            HostModal(

                self.dungeon

            )

        )









class JoinView(discord.ui.View):


    def __init__(self, carry_id):

        super().__init__(

            timeout=None

        )

        self.carry_id=carry_id







    @discord.ui.button(

        label="Join Carry",

        style=discord.ButtonStyle.success

    )

    async def join(self, interaction, button):


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

            "Joined carry.",

            ephemeral=True

        )









class HostPanel(discord.ui.View):


    def __init__(self, carry_id):

        super().__init__(

            timeout=None

        )

        self.carry_id=carry_id







    @discord.ui.button(

        label="Start Carry",

        style=discord.ButtonStyle.success

    )

    async def start(self, interaction, button):


        players = await database.get_players(

            self.carry_id

        )


        carry = await database.get_carry(

            self.carry_id

        )


        if len(players) < MINIMUM_PLAYERS[carry[3]]:

            await interaction.response.send_message(

                "Not enough players.",

                ephemeral=True

            )

            return





        await interaction.response.send_message(

            "Starting carry...",

            ephemeral=True

        )







    @discord.ui.button(

        label="Report Incident",

        style=discord.ButtonStyle.danger

    )

    async def report(self, interaction, button):


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

    async def end(self, interaction, button):


        from cogs.carry import end_carry


        await end_carry(

            interaction.guild,

            self.carry_id

        )


        await interaction.response.send_message(

            "Carry ended.",

            ephemeral=True

        )









class Host(commands.Cog):


    def __init__(self, bot):

        self.bot=bot







    @app_commands.command(

        name="host",

        description="Create carry"

    )

    async def host(self, interaction):


        await interaction.response.send_message(

            "Select dungeon",

            view=DungeonView(),

            ephemeral=True

        )









async def setup(bot):

    await bot.add_cog(

        Host(bot)

    )
