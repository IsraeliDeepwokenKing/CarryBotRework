import discord

from discord.ext import commands

import database

from cogs.cleanup import cleanup_carry





async def create_carry_room(

    guild,

    host,

    dungeon

):


    role = await guild.create_role(

        name=f"Carry-{host.name}"

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

        ),



        host:

        discord.PermissionOverwrite(

            view_channel=True,

            connect=True,

            manage_channels=True

        )

    }




    vc = await guild.create_voice_channel(

        name=f"{dungeon.lower()}-vc-{host.name.lower()}",

        overwrites=overwrites

    )



    return role, vc







class JoinButton(discord.ui.Button):


    def __init__(

        self,

        carry_id

    ):


        super().__init__(

            label="JOIN CARRY",

            style=discord.ButtonStyle.blurple

        )


        self.carry_id=carry_id





    async def callback(

        self,

        interaction

    ):


        carry = await database.get_carry(

            self.carry_id

        )



        if not carry:


            await interaction.response.send_message(

                "Carry does not exist.",

                ephemeral=True

            )

            return





        if await database.player_exists(

            self.carry_id,

            interaction.user.id

        ):


            await interaction.response.send_message(

                "You are already in this carry.",

                ephemeral=True

            )

            return





        count = await database.player_count(

            self.carry_id

        )



        if count >= carry[4]:


            await interaction.response.send_message(

                "Carry is full.",

                ephemeral=True

            )

            return





        await database.add_player(

            self.carry_id,

            interaction.user.id,

            interaction.user.name,

            count+1

        )





        await interaction.response.send_message(

            "✅ Joined carry.",

            ephemeral=True

        )









class StartButton(discord.ui.Button):


    def __init__(

        self,

        carry_id

    ):


        super().__init__(

            label="START CARRY",

            style=discord.ButtonStyle.green

        )


        self.carry_id=carry_id





    async def callback(

        self,

        interaction

    ):


        carry = await database.get_carry(

            self.carry_id

        )



        if not carry:


            await interaction.response.send_message(

                "Carry missing.",

                ephemeral=True

            )

            return





        role,vc = await create_carry_room(

            interaction.guild,

            interaction.user,

            carry[3]

        )





        await interaction.user.add_roles(

            role

        )





        await database.update_carry(

            self.carry_id,

            role.id,

            vc.id

        )





        await interaction.response.send_message(

            f"✅ Carry started\n{vc.mention}",

            ephemeral=True

        )









class EndButton(discord.ui.Button):


    def __init__(

        self,

        carry_id

    ):


        super().__init__(

            label="END CARRY",

            style=discord.ButtonStyle.gray

        )


        self.carry_id=carry_id





    async def callback(

        self,

        interaction

    ):


        carry = await database.get_carry(

            self.carry_id

        )



        if carry:


            await cleanup_carry(

                interaction.guild,

                carry[6],

                carry[7]

            )



            await database.end_carry(

                self.carry_id

            )





        await interaction.response.send_message(

            "✅ Carry ended.",

            ephemeral=True

        )









class ReportButton(discord.ui.Button):


    def __init__(

        self,

        carry_id

    ):


        super().__init__(

            label="REPORT INCIDENT",

            style=discord.ButtonStyle.red

        )


        self.carry_id=carry_id





    async def callback(

        self,

        interaction

    ):


        from cogs.incidents import IncidentModal



        await interaction.response.send_modal(

            IncidentModal(

                self.carry_id

            )

        )








class CarryView(discord.ui.View):


    def __init__(

        self,

        carry_id

    ):


        super().__init__(

            timeout=None

        )


        self.add_item(

            JoinButton(carry_id)

        )


        self.add_item(

            StartButton(carry_id)

        )


        self.add_item(

            ReportButton(carry_id)

        )


        self.add_item(

            EndButton(carry_id)

        )








class Carry(commands.Cog):


    def __init__(

        self,

        bot

    ):

        self.bot=bot






async def setup(bot):


    await bot.add_cog(

        Carry(bot)

    )
