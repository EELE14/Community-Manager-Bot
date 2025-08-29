import os
import json
import asyncio
import datetime
import discord
from discord.ext import commands

PANEL2_CHANNEL_ID = 1364206767957082202  
FORWARD2_CHANNEL_ID = 1364698748814622861 

class ForwardActionsView2(discord.ui.View):
    def __init__(self, thread: discord.Thread):
        super().__init__(timeout=None)
        self.thread = thread

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.danger, custom_id="delete_button2")
    async def delete_button2(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await self.thread.delete()
            await interaction.response.send_message("Ticket deleted. <a:success:1364688189192933436>", ephemeral=True)
        except:
            await interaction.response.send_message("Error deleting Ticket. <a:fail:1364688207962177588>", ephemeral=True)

    @discord.ui.button(label="Join", style=discord.ButtonStyle.secondary, custom_id="join_button2")
    async def join_button2(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await self.thread.send(f"{interaction.user.mention}")
            await interaction.response.send_message("You have been added to the ticket. <a:success:1364688189192933436>", ephemeral=True)
        except:
            await interaction.response.send_message("Error sending message in ticket. <a:fail:1364688207962177588>", ephemeral=True)

class RequestView2(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Open Report", style=discord.ButtonStyle.primary, custom_id="request_button2")
    async def request_button2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("<a:loading:1359934124785143908>", ephemeral=True)
        await asyncio.sleep(1)
        ticket_embed = discord.Embed(description="Ticket Created", color=discord.Color.green())
        await interaction.edit_original_response(content=None, embed=ticket_embed)

        channel = interaction.channel
        thread_name = f"report-{interaction.user.name.replace(' ','-').lower()}"
        try:
            thread = await channel.create_thread(name=thread_name, type=discord.ChannelType.private_thread, invitable=False)
        except:
            await interaction.followup.send("Error creating ticket. <a:fail:1364688207962177588>", ephemeral=True)
            return

        try:
            await thread.add_user(interaction.user)
        except:
            pass

        instruction_embed = discord.Embed(
            title="Report Ticket",
            description=(
                "Hello, thank you for opening a report ticket. Please specify your request in a **single message** and attach proof if needed."
            ),
            color=discord.Color.blue()
        )
        await thread.send(content=interaction.user.mention, embed=instruction_embed)

        def check2(m: discord.Message):
            return m.author.id == interaction.user.id and m.channel.id == thread.id

        try:
            user_msg = await interaction.client.wait_for("message", check=check2, timeout=300)
        except asyncio.TimeoutError:
            await thread.send("Timeout. Please repeat the procedure. <a:fail:1364688207962177588>")
            return

        await thread.edit(locked=True)

        forward_embed = discord.Embed(
            title="Moderator Report",
            description=user_msg.content,
            color=discord.Color.green()
        )
        forward_embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)

        view2 = ForwardActionsView2(thread)
        forward_channel = interaction.client.get_channel(FORWARD2_CHANNEL_ID)
        if not forward_channel:
            await thread.send("Forward channel not found. <a:fail:1364688207962177588>")
            return
        await forward_channel.send(embed=forward_embed, view=view2)

        pending_embed = discord.Embed(
            title="Status: Pending",
            description="You submitted your report. The administrative team will contact you soon.",
            color=discord.Color.orange()
        )
        await thread.send(embed=pending_embed)
        await thread.send("Request sent successfully. <a:success:1364688189192933436>")

class Panel2(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name="modticket", description="Send a modsupport ticket.")
    async def panel2(self, interaction: discord.Interaction):
        ALLOWED2_SUPPORT_IDS = {1263756486660587543,724060712120614912}  
        if interaction.user.id not in ALLOWED2_SUPPORT_IDS:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Error <a:fail:1364688207962177588>",
                    description="You cannot use this command.",
                    color=discord.Color.red()
                ), ephemeral=True
            )
            return

        panel_embed = discord.Embed(
            title="Moderator Report Ticket",
            description="You may use this tickets to either request the ban of a member, or report another moderator for abusing moderation powers. This ticket will only be reviewed by administrators.",
            color=discord.Color.blurple()
        )
        view2 = RequestView2()
        panel_channel = self.bot.get_channel(PANEL2_CHANNEL_ID)
        if not panel_channel:
            await interaction.response.send_message("Ticket channel not found. <a:fail:1364688207962177588>", ephemeral=True)
            return

        await panel_channel.send(embed=panel_embed, view=view2)
        await interaction.response.send_message("Ticket Panel sent successfully. <a:success:1364688189192933436>", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Panel2(bot))
