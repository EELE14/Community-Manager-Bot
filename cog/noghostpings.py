import discord
from discord.ext import commands
from discord import app_commands
import os, json, asyncio
import re

class NoGhostPing(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.enabled = True  

    def load_blacklist(self):
        
        if not os.path.exists("blacklist.json"):
            return []
        try:
            with open("blacklist.json", "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def loading_embed(self):
        return discord.Embed(title="Loading...", description="<a:loading:1359934124785143908>")

    def error_embed(self, message: str):
        return discord.Embed(title="Error!", description=message, color=discord.Color.red())

    def success_embed(self, message: str):
        return discord.Embed(title="Success!", description=message, color=discord.Color.green())

    @app_commands.command(name="enable", description="Enable ghostping detection")
    async def enable(self, interaction: discord.Interaction):

        blacklist = self.load_blacklist()
        if interaction.user.id in blacklist:
            await interaction.response.send_message(embed=self.loading_embed(), ephemeral=False)
            await asyncio.sleep(1)
            return await interaction.edit_original_response(embed=self.error_embed("No permissions"))
        
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(embed=self.loading_embed(), ephemeral=False)
            await asyncio.sleep(1)
            return await interaction.edit_original_response(embed=self.error_embed("No permissions"))
        
        await interaction.response.send_message(embed=self.loading_embed(), ephemeral=False)
        await asyncio.sleep(1)
        self.enabled = True
        await interaction.edit_original_response(embed=self.success_embed("Ghostping detection enabled."))

    @app_commands.command(name="disable", description="Disable ghostping detection")
    async def disable(self, interaction: discord.Interaction):

        blacklist = self.load_blacklist()
        if interaction.user.id in blacklist:
            await interaction.response.send_message(embed=self.loading_embed(), ephemeral=False)
            await asyncio.sleep(1)
            return await interaction.edit_original_response(embed=self.error_embed("No permissions"))
        
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(embed=self.loading_embed(), ephemeral=False)
            await asyncio.sleep(1)
            return await interaction.edit_original_response(embed=self.error_embed("No permissions"))
        
        await interaction.response.send_message(embed=self.loading_embed(), ephemeral=False)
        await asyncio.sleep(1)
        self.enabled = False
        await interaction.edit_original_response(embed=self.success_embed("Ghostping detection disabled."))

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):

        if message.author.bot:
            return

        if not self.enabled:
            return

        content = message.content.strip()
        if content.startswith('-') or content.startswith('s!') or content.startswith('s?'):
            return

        pattern = r"<@!?(\d+)>"
        matches = re.findall(pattern, message.content)
        if not matches:
            return  

        target_id = int(matches[0])
        target_member = message.guild.get_member(target_id) if message.guild else None
        if not target_member:
            target_member = self.bot.get_user(target_id)

        embed = discord.Embed(
            title="Ghostping detected!",
            description=f"- {message.author.mention} tried to ghostping {target_member.mention if target_member else f'<@{target_id}>'}.\n- Message: {message.content}",
            color=discord.Color.red()
        )
        embed.set_footer(text=f"Ghostping detected by {message.author.display_name}")

        try:
            await message.channel.send(embed=embed)
        except Exception as e:
            print(f"Error sending ghostping alert: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(NoGhostPing(bot))
