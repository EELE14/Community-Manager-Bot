import discord
from discord.ext import commands
from discord import app_commands
import os, json, asyncio, re
from datetime import timedelta

class AutomodBypassView(discord.ui.View):
    def __init__(self, original_message: str, moderator: discord.Member, cog: commands.Cog):
        super().__init__(timeout=300)
        self.original_message = original_message  
        self.moderator = moderator                
        self.cog = cog                            

    def generate_report_embed(self) -> discord.Embed:
        desc = f"Please add one of the words, or the whole message to automod:\n> - {self.original_message}"
        return discord.Embed(title="Automod bypass report", description=desc)

    async def update_message(self, interaction: discord.Interaction, message_obj: discord.Message):
        try:
            await message_obj.edit(embed=self.generate_report_embed(), view=self)
        except Exception as e:
            print("Error updating report message:", e)

    @discord.ui.button(label="Add word", style=discord.ButtonStyle.green, custom_id="add_word")
    async def add_word(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AddWordModal(self))

    @discord.ui.button(label="Add message", style=discord.ButtonStyle.green, custom_id="add_message")
    async def add_message_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if len(self.original_message) > 30:
            await interaction.response.send_message(embed=self.cog.error_embed("Message is longer than 30 characters. Not saved."), ephemeral=True)
            return
        words = self.original_message.split()
        if "words" not in self.cog.automod_data:
            self.cog.automod_data["words"] = []
        for word in words:
            lw = word.lower()
            if lw not in self.cog.automod_data["words"]:
                self.cog.automod_data["words"].append(lw)
        self.cog.save_automod_data()
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
        await interaction.response.send_message(embed=self.cog.success_embed("Words successfully added."), ephemeral=True)
        self.stop()

class AddWordModal(discord.ui.Modal, title="Add Word"):
    word_input = discord.ui.TextInput(label="Enter a word from the message", style=discord.TextStyle.short)

    def __init__(self, view: AutomodBypassView):
        super().__init__()
        self.view_ref = view

    async def on_submit(self, interaction: discord.Interaction):
        word = self.word_input.value.strip().lower()
        if "words" not in self.view_ref.cog.automod_data:
            self.view_ref.cog.automod_data["words"] = []
        if word not in self.view_ref.original_message.lower().split():
            await interaction.response.send_message(embed=self.view_ref.cog.error_embed("Word not found in the original message."), ephemeral=True)
            return
        if word not in self.view_ref.cog.automod_data["words"]:
            self.view_ref.cog.automod_data["words"].append(word)
            self.view_ref.cog.save_automod_data()
        for child in self.view_ref.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
        await interaction.response.send_message(embed=self.view_ref.cog.success_embed("Word successfully added."), ephemeral=True)
        self.view_ref.stop()

class AutomodBypass(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.automod_file = "automod.json"
        self.automod_data = self.load_automod_data()  
    
    def load_automod_data(self):
        if not os.path.exists(self.automod_file):
            with open(self.automod_file, "w") as f:
                json.dump({"words": []}, f)
            return {"words": []}
        try:
            with open(self.automod_file, "r") as f:
                data = json.load(f)
            if "words" not in data:
                data["words"] = []
            return data
        except json.JSONDecodeError:
            return {"words": []}

    def save_automod_data(self):
        with open(self.automod_file, "w") as f:
            json.dump(self.automod_data, f, indent=4)

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

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        
        if payload.emoji.id != 1361808255290179857:
            return
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
        member = guild.get_member(payload.user_id)
        if not member:
            return
        if not member.guild_permissions.moderate_members:
            return
        blacklist = self.load_blacklist()
        if member.id in blacklist:
            return
        channel = guild.get_channel(payload.channel_id)
        if not channel:
            return
        try:
            msg = await channel.fetch_message(payload.message_id)
        except Exception as e:
            print("Error fetching message:", e)
            return
        original_content = msg.content
        try:
            await msg.remove_reaction(payload.emoji, member)
        except Exception as e:
            print("Error removing reaction:", e)
        loading_emoji = discord.PartialEmoji.from_str("<a:loading:1359934124785143908>")
        tick_emoji = discord.PartialEmoji.from_str("<:tick:1359934081584075043>")
        try:
            await msg.add_reaction(loading_emoji)
            await asyncio.sleep(1)
            await msg.remove_reaction(loading_emoji, self.bot.user)
            await msg.add_reaction(tick_emoji)
        except Exception as e:
            print("Error with reaction sequence:", e)
        report_channel = guild.get_channel(1360002237971173486)
        if not report_channel:
            return
        report_embed = discord.Embed(
            title="Automod bypass report",
            description=f"Please add one of the words, or the whole message to automod:\n> - {original_content}"
        )
        view = AutomodBypassView(original_message=original_content, moderator=member, cog=self)
        try:
            await report_channel.send(content=member.mention, embed=report_embed, view=view)
        except Exception as e:
            print("Error sending automod bypass report:", e)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild or message.author.bot:
            return
        if message.author.guild_permissions.administrator:
            return
        content_lower = message.content.lower()
        for word in self.automod_data.get("words", []):
            if word.lower() in content_lower:
                try:
                    await message.delete()
                except Exception as e:
                    print("Error deleting message:", e)
                try:
                    await message.author.timeout(timedelta(minutes=5), reason="Automod bypass timeout")
                except Exception as e:
                    print("Error timing out user:", e)
                try:
                    report = discord.Embed(
                        title="Automod bypass!",
                        description="Please do not attempt to bypass automod. You are now muted.",
                        color=discord.Color.red()
                    )
                    await message.channel.send(embed=report)
                except Exception as e:
                    print("Error sending automod report:", e)
                return

    @commands.command(name="bypassreport")
    async def bypassreport(self, ctx: commands.Context):
        if not ctx.message.reference:
            await ctx.send(embed=self.error_embed("You must reply to a message to report bypass."), delete_after=5)
            return
        try:
            ref_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        except Exception as e:
            await ctx.send(embed=self.error_embed("Referenced message not found."), delete_after=5)
            return
        await self.process_bypass_report(ref_msg, ctx.author)

    async def process_bypass_report(self, message: discord.Message, moderator: discord.Member):
        original_content = message.content
        try:
            await message.add_reaction(discord.PartialEmoji.from_str("<a:loading:1359934124785143908>"))
            await asyncio.sleep(1)
            await message.remove_reaction(discord.PartialEmoji.from_str("<a:loading:1359934124785143908>"), self.bot.user)
            await message.add_reaction(discord.PartialEmoji.from_str("<:tick:1359934081584075043>"))
        except Exception as e:
            print("Error during reaction sequence in bypass report:", e)
        report_channel = message.guild.get_channel(1360002237971173486)
        if not report_channel:
            return
        report_embed = discord.Embed(
            title="Automod bypass report",
            description=f"Please add one of the words, or the whole message to automod:\n> - {original_content}"
        )
        view = AutomodBypassView(original_message=original_content, moderator=moderator, cog=self)
        try:
            await report_channel.send(content=moderator.mention, embed=report_embed, view=view)
        except Exception as e:
            print("Error sending bypass report via command:", e)

async def setup(bot: commands.Bot):
    await bot.add_cog(AutomodBypass(bot))
    
    bot.tree.add_command(report_bypass_context)

@app_commands.context_menu(name="Report Bypass")
async def report_bypass_context(interaction: discord.Interaction, message: discord.Message):
    if not message.guild:
        return
    member = message.guild.get_member(interaction.user.id)
    if not member or not member.guild_permissions.moderate_members:
        await interaction.response.send_message(embed=discord.Embed(title="Error!", description="No permissions.", color=discord.Color.red()), ephemeral=True)
        return
    automod_cog = interaction.client.get_cog("Automod")
    if automod_cog is None:
        await interaction.response.send_message("Automod cog not loaded.", ephemeral=True)
        return
    blacklist = automod_cog.load_blacklist()
    if member.id in blacklist:
        await interaction.response.send_message(embed=automod_cog.error_embed("No permissions."), ephemeral=True)
        return
    await interaction.response.defer(ephemeral=False)
    await automod_cog.process_bypass_report(message, interaction.user)
