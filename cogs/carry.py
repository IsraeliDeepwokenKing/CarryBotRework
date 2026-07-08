import discord

from discord.ext import commands

import database

from config import VC_PREFIX, CARRY_ROLES





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

            return False





        guild = interaction.guild


        dungeon = carry[3]


        host = guild.get_member(

            carry[2]

        )


        players = await database.get_players(

            carry_id

        )







        # =====================
        # Create Role
        # =====================


        role = await guild.create_role(

            name=f"{dungeon} Carry {carry_id}",

            reason="Temporary carry role"

        )





        # =====================
        # Create VC
        # =====================


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

            f"{VC_PREFIX[dungeon]}-{host.name}",

            category=category,

            overwrites=overwrites

        )







        await database.update_carry_resources(

            carry_id,

            voice_id=voice.id,

            role_id=role.id

        )







        # Give role

        for player in players:


            member = guild.get_member(

                player[0]

            )


            if member:


                await member.add_roles(

                    role

                )



        if host:

            await host.add_roles(

                role

            )







        return True











async def end_carry(

    guild,

    carry_id

):


    carry = await database.get_carry(

        carry_id

    )


    if not carry:

        return





    # VC delete


    if carry[7]:


        channel = guild.get_channel(

            carry[7]

        )


        if channel:

            await channel.delete(

                reason="Carry ended"

            )





    # Role delete


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









async def setup(bot):

    await bot.add_cog(

        Carry(bot)

    )
