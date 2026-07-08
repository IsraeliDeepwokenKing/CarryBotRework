import discord

from discord.ext import commands

from discord import app_commands

import database

from config import CARRY_LIMITS, CARRY_ROLES

from cogs.carry import CarryView





class Host(commands.Cog):


    def __init__(self,bot):

        self.bot=bot







    @app_commands.command(

        name="host",

        description="Create a Deepwoken carry"

    )
    async def host(

        self,

        interaction: discord.Interaction

    ):


        await interaction.response.send_message(

            "Choose carry:",

            view=DungeonView(),

            ephemeral=True

        )









class DungeonSelect(discord.ui.Select):


    def __init__(self):


        options=[]



        for dungeon in CARRY_LIMITS:


            options.append(

                discord.SelectOption(

                    label=dungeon

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


        await interaction.response.send_message(

            "Choose slots:",

            view=SlotView(

                self.values[0]

            ),

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


        for i in range(

            1,

            CARRY_LIMITS[dungeon]+1

        ):


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





        role_name=CARRY_ROLES[self.dungeon]



        role=discord.utils.get(

            interaction.guild.roles,

            name=role_name

        )





        ping = role.mention if role else ""






        embed=discord.Embed(

            title="🔥 Deepwoken Carry",

            description=(

                f"Host: {interaction.user.mention}\n\n"

                f"Dungeon: **{self.dungeon}**\n\n"

                "Players:\n"

                +

                "\n".join(

                    [

                    f"{i}. 🟢 Empty"

                    for i in range(1,self.slots+1)

                    ]

                )

            )

        )







        await interaction.user.send(

            embed=embed,

            view=CarryView(

                carry_id

            )

        )





        await interaction.response.send_message(

            f"✅ Carry created.\n{ping}",

            ephemeral=True

        )







async def setup(bot):

    await bot.add_cog(

        Host(bot)

    )
