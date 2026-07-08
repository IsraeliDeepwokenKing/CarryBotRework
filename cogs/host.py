import discord

from discord.ext import commands

from discord import app_commands

import database

from config import CARRY_LIMITS

from cogs.carry import CarryView





class Host(commands.Cog):


    def __init__(self, bot):

        self.bot = bot





    @app_commands.command(

        name="host",

        description="Create a Deepwoken carry"

    )
    async def host(

        self,

        interaction: discord.Interaction

    ):


        await interaction.response.send_message(

            "Choose dungeon:",

            view=DungeonView(),

            ephemeral=True

        )







class DungeonSelect(discord.ui.Select):


    def __init__(self):


        options = []


        for dungeon,limit in CARRY_LIMITS.items():


            options.append(

                discord.SelectOption(

                    label=dungeon,

                    description=f"Maximum {limit} players"

                )

            )



        super().__init__(

            placeholder="Select dungeon",

            options=options

        )





    async def callback(

        self,

        interaction

    ):


        dungeon = self.values[0]



        await interaction.response.send_message(

            "Select player count:",

            view=SlotView(dungeon),

            ephemeral=True

        )








class DungeonView(discord.ui.View):


    def __init__(self):

        super().__init__(

            timeout=60

        )


        self.add_item(

            DungeonSelect()

        )







class SlotView(discord.ui.View):


    def __init__(

        self,

        dungeon

    ):


        super().__init__(

            timeout=60

        )


        self.dungeon=dungeon




        max_players=CARRY_LIMITS[dungeon]



        for i in range(1,max_players+1):


            self.add_item(

                SlotButton(

                    dungeon,

                    i

                )

            )







class SlotButton(discord.ui.Button):


    def __init__(

        self,

        dungeon,

        slots

    ):


        super().__init__(

            label=str(slots),

            style=discord.ButtonStyle.primary

        )


        self.dungeon=dungeon

        self.slots=slots





    async def callback(

        self,

        interaction

    ):


        carry_id = await database.create_carry(

            interaction.user.id,

            interaction.user.name,

            self.dungeon,

            self.slots

        )



        await database.add_player(

            carry_id,

            interaction.user.id,

            interaction.user.name,

            1

        )





        embed = create_embed(

            interaction.user.name,

            self.dungeon,

            self.slots,

            [

                interaction.user.name

            ]

        )





        msg = await interaction.user.send(

            embed=embed,

            view=CarryView(

                carry_id

            )

        )




        await database.save_message(

            carry_id,

            msg.id,

            msg.channel.id

        )





        await interaction.response.send_message(

            "✅ Carry created. Check your DM.",

            ephemeral=True

        )








def create_embed(

    host,

    dungeon,

    slots,

    players

):


    embed = discord.Embed(

        title="🔥 Deepwoken Carry",

        color=discord.Color.blue()

    )



    text = (

        f"**Host:** {host}\n"

        f"**Dungeon:** {dungeon}\n\n"

        "**Players:**\n"

    )




    for i in range(

        1,

        slots+1

    ):


        if i <= len(players):


            text += f"{i}. {players[i-1]}\n"



        else:


            text += f"{i}. 🟢 Empty\n"





    embed.description=text



    return embed






async def setup(bot):


    await bot.add_cog(

        Host(bot)

    )
