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

        carry_id

    ):


        carry = await database.get_carry(

            carry_id

        )


        if not carry:

            return False, "Carry not found."





        guild = self.bot.get_guild(

            carry[1]

        )


        if guild is None:

            return False, "Guild not found."







        players = await database.get_players(

            carry_id

        )


        dungeon = carry[3]







        if len(players) < MINIMUM_PLAYERS[dungeon]:

            return False, (

                f"Need {MINIMUM_PLAYERS[dungeon]} players."

            )








        # create temporary role


        role = await guild.create_role(

            name=f"{dungeon} Carry {carry_id}",

            reason="Temporary carry"

        )







        category = discord.utils.find(

            lambda c: c.name == "Deepwoken Carry",

            guild.categories

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

            name=f"{VC_PREFIX[dungeon]}-{carry_id}",

            category=category,

            overwrites=overwrites

        )







        # give role


        for player in players:


            member = guild.get_member(

                player[1]

            )


            if member:


                await member.add_roles(

                    role

                )







        await database.update_carry_resources(

            carry_id,

            voice_id=voice.id,

            role_id=role.id,

            status="RUNNING"

        )







        return True, voice










async def end_carry(

    bot,

    carry_id

):


    carry = await database.get_carry(

        carry_id

    )


    if not carry:

        return False





    guild = bot.get_guild(

        carry[1]

    )


    if guild is None:

        return False







    # remove voice


    if carry[7]:


        voice = guild.get_channel(

            carry[7]

        )


        if voice:

            await voice.delete(

                reason="Carry finished"

            )







    # remove role


    if carry[8]:


        role = guild.get_role(

            carry[8]

        )


        if role:

            await role.delete(

                reason="Carry finished"

            )







    await database.delete_carry(

        carry_id

    )


    return True











async def setup(bot):

    await bot.add_cog(

        Carry(bot)

    )
