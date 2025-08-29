import os
import json
import asyncio
import datetime
import discord
from discord.ext import commands

PANEL_CHANNEL_ID = 1364693136936538193       
FORWARD_CHANNEL_ID = 1364698748814622861      

class ForwardActionsView(discord.ui.View):
    def __init__(self, thread: discord.Thread):
        super().__init__(timeout=None)
        self.thread = thread

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.danger, custom_id="delete_button")
    async def delete_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await self.thread.delete()
            await interaction.response.send_message("Thread deleted. <a:success:1364688189192933436>", ephemeral=True)
        except Exception:
            await interaction.response.send_message("Error deleting thread. <a:fail:1364688207962177588>", ephemeral=True)

    @discord.ui.button(label="Join", style=discord.ButtonStyle.secondary, custom_id="join_button")
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            
            await self.thread.send(f"{interaction.user.mention}")
            await interaction.response.send_message("You have been added to the ticket. <a:success:1364688189192933436>", ephemeral=True)
        except Exception:
            await interaction.response.send_message("Error sending message in thread. <a:fail:1364688207962177588>", ephemeral=True)

class RequestView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  

    @discord.ui.button(label="Request", style=discord.ButtonStyle.primary, custom_id="request_button")
    async def request_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        await interaction.response.send_message("<a:loading:1359934124785143908>", ephemeral=True)
        await asyncio.sleep(1)
        
        ticket_embed = discord.Embed(
            description="Ticket Created",
            color=discord.Color.green()
        )
        await interaction.edit_original_response(content=None, embed=ticket_embed)

        channel = interaction.channel
        thread_name = f"sponsorship-{interaction.user.name.replace(' ', '-').lower()}"
        try:
            thread = await channel.create_thread(
                name=thread_name,
                type=discord.ChannelType.private_thread,  
                invitable=False  
            )
        except Exception:
            await interaction.followup.send("Error creating ticket. <a:fail:1364688207962177588>", ephemeral=True)
            return

        try:
            await thread.add_user(interaction.user)
        except Exception:
            pass  

        instruction_embed = discord.Embed(
            title="Sponsorship Ticket",
            description=(
                "Hello, thank you for opening a ticket. Please make sure to tell your specified type of sponsorship and if you purchased it already. If so please provide proof (screenshot). Our staff team assists you soon.\n"
                "**(Make sure to write it in one message!)**"
            ),
            color=discord.Color.blue()
        )
        await thread.send(content=interaction.user.mention, embed=instruction_embed)

        def check(m: discord.Message):
            return m.author.id == interaction.user.id and m.channel.id == thread.id

        try:
            user_msg = await interaction.client.wait_for("message", check=check, timeout=300)  
        except asyncio.TimeoutError:
            await thread.send("Timeout. Please restart the process if you wish to submit a request. <a:fail:1364688207962177588>")
            return

        await thread.edit(locked=True)

        forward_embed = discord.Embed(
            title="New Sponsorship Request",
            description=user_msg.content,
            color=discord.Color.green()
        )
        forward_embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.display_avatar.url
        )

        view = ForwardActionsView(thread)
        forward_channel = interaction.client.get_channel(FORWARD_CHANNEL_ID)
        if forward_channel is None:
            await thread.send("Forward channel not found. <a:fail:1364688207962177588>")
            return

        await forward_channel.send(embed=forward_embed, view=view)

        pending_embed = discord.Embed(
            title="Status: Pending",
            description="You submitted a ticket request. Server staff will contact you soon.",
            color=discord.Color.orange()
        )
        await thread.send(embed=pending_embed)

        await thread.send("Request sent successfully. <a:success:1364688189192933436>")

class Panel(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name="panel", description="Send the support panel.")
    async def panel(self, interaction: discord.Interaction):
        
        ALLOWED_SUPPORT_IDS = {1263756486660587543, 724060712120614912}
        if interaction.user.id not in ALLOWED_SUPPORT_IDS:
            error_embed = discord.Embed(title="Error <a:fail:1364688207962177588>", description="You are not allowed to use this command.", color=discord.Color.red())
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return

        panel_embed = discord.Embed(
            title="Request Sponsorship",
            description="Thank you for choosing one of our sponsorship programms! Please click the button below and get started. **Make sure to follow all instructions given in the ticket!**",
            color=discord.Color.blurple()
        )
        view = RequestView()
        panel_channel = self.bot.get_channel(PANEL_CHANNEL_ID)
        if panel_channel is None:
            await interaction.response.send_message("Panel channel not found. <a:fail:1364688207962177588>", ephemeral=True)
            return
        
        await panel_channel.send(embed=panel_embed, view=view)
        await interaction.response.send_message("Panel sent successfully. <a:success:1364688189192933436>", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Panel(bot))
