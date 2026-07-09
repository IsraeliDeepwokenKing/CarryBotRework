import discord

from discord.ext import commands

import database

from config import (
    VC_PREFIX,
    MINIMUM_PLAYERS
)





class Carry(commands.Cog):


    def __init__(self, bot):

        self.bot = bot







    async def create_resources(

        self,

        carry_id,

        interaction

    ):


        carry = await database.get_carry(

            carry_id

        )


        if not carry:

            await interaction.response.send_message(

                "Carry does not exist.",

                ephemeral=True

            )

            return





        dungeon = carry[3]


        players = await database.get_players(

            carry_id

        )





        if len(players) < MINIMUM_PLAYERS[dungeon]:


            await interaction.response.send_message(

                f"Need {MINIMUM_PLAYERS[dungeon]} players.",

                ephemeral=True

            )

            return







        guild = interaction.guild





        # temporary role


        role = await guild.create_role(

            name=f"{dungeon} Carry {carry_id}",

            reason="Temporary carry role"

        )







        # category


        category = discord.utils.get(

            guild.categories,

            name="Deepwoken Carry"

        )





        overwrites = {

            guild.default_role:

            discord.PermissionOverwrite(

                view_channel=False

            ),


            role:

            discord.PermissionOverwrite(

                view_channel=True,

                connect=True,

                speak=True

            )

        }







        voice = await guild.create_voice_channel(

            f"{VC_PREFIX[dungeon]}-{carry_id}",

            category=category,

            overwrites=overwrites

        )







        # give roles


        for player in players:


            member = guild.get_member(

                player[0]

            )


            if member:


                await member.add_roles(

                    role

                )







        await database.update_carry_resources(

            carry_id,

            voice_id=voice.id,

            role_id=role.id

        )







        return voice













async def end_carry(

    guild,

    carry_id

):


    carry = await database.get_carry(

        carry_id

    )


    if not carry:

        return





    # delete voice


    if carry[7]:


        channel = guild.get_channel(

            carry[7]

        )


        if channel:

            await channel.delete(

                reason="Carry ended"

            )







    # delete role


    if carry[8]:


        role = guild.get_role(

            carry[8]

        )


        if role:

            await role.delete(

                reason="Carry ended"

            )







    await database.delete_carry(

        carry_id

    )









class Carry(commands.Cog):


    pass









async def setup(bot):

    await bot.add_cog(

        Carry(bot)

    )
