import discord
from discord.ext import commands
from discord import app_commands
import os, json, asyncio, re

class ReactionRoleSetupView(discord.ui.View):
    def __init__(self, cog: commands.Cog, interaction: discord.Interaction):
        super().__init__(timeout=300)
        self.cog = cog  
        self.interaction = interaction  
        
        self.message_id = None  
        self.emoji_name = None  
        self.role_id = None     

    def generate_embed(self) -> discord.Embed:
        description = (
            f"- Message: {self.message_id if self.message_id else ''}\n"
            f"- Emoji: {self.emoji_name if self.emoji_name else ''}\n"
            f"- Role: {f'<@&{self.role_id}>' if self.role_id else ''}"
        )
        return discord.Embed(title="Reaction Roles", description=description)

    async def update_message(self):
        try:
            await self.interaction.edit_original_response(embed=self.generate_embed(), view=self)
        except Exception as e:
            print("Error updating message:", e)

    @discord.ui.button(label="Add message", style=discord.ButtonStyle.green, custom_id="add_message")
    async def add_message(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(MessageModal(self))

    @discord.ui.button(label="Add emoji", style=discord.ButtonStyle.green, custom_id="add_emoji")
    async def add_emoji(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EmojiModal(self))

    @discord.ui.button(label="Add Role", style=discord.ButtonStyle.green, custom_id="add_role")
    async def add_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RoleModal(self))

    async def check_and_update_final(self):

        if self.message_id and self.emoji_name and self.role_id:
            self.clear_items()  
            self.add_item(FinalButton(self))
            await self.update_message()

class MessageModal(discord.ui.Modal, title="Add Message"):
    message_input = discord.ui.TextInput(label="Message Link or ID", style=discord.TextStyle.short)

    def __init__(self, view: ReactionRoleSetupView):
        super().__init__()
        self.view_ref = view

    async def on_submit(self, interaction: discord.Interaction):
        content = self.message_input.value.strip()
      
        pattern = r"https?://discord(?:app)?\.com/channels/\d+/\d+/(\d+)"
        match = re.search(pattern, content)
        msg_id = None
        if match:
            try:
                msg_id = int(match.group(1))
            except:
                msg_id = None
        else:
            try:
                msg_id = int(content)
            except ValueError:
                msg_id = None
        if not msg_id:
            await interaction.response.send_message(embed=self.view_ref.cog.error_embed("Invalid message link or ID."), ephemeral=True)
            return
       
        try:
            target = await interaction.channel.fetch_message(msg_id)
        except Exception:
            await interaction.response.send_message(embed=self.view_ref.cog.error_embed("Message not found."), ephemeral=True)
            return
        
        self.view_ref.message_id = msg_id
        for child in self.view_ref.children:
            if isinstance(child, discord.ui.Button) and child.custom_id == "add_message":
                child.disabled = True
        await interaction.response.send_message(embed=self.view_ref.cog.success_embed("Message set successfully."), ephemeral=True)
        await self.view_ref.update_message()
        await self.view_ref.check_and_update_final()

class EmojiModal(discord.ui.Modal, title="Add Emoji"):
    emoji_input = discord.ui.TextInput(label="Emoji Name", style=discord.TextStyle.short)

    def __init__(self, view: ReactionRoleSetupView):
        super().__init__()
        self.view_ref = view

    async def on_submit(self, interaction: discord.Interaction):
        emoji_name = self.emoji_input.value.strip()
        guild = interaction.guild
        found = None
        for emoji in guild.emojis:
            if emoji.name == emoji_name:
                found = emoji
                break
        if not found:
            await interaction.response.send_message(embed=self.view_ref.cog.error_embed("Emoji not found in this guild."), ephemeral=True)
            return
        self.view_ref.emoji_name = emoji_name
        for child in self.view_ref.children:
            if isinstance(child, discord.ui.Button) and child.custom_id == "add_emoji":
                child.disabled = True
        await interaction.response.send_message(embed=self.view_ref.cog.success_embed("Emoji set successfully."), ephemeral=True)
        await self.view_ref.update_message()
        await self.view_ref.check_and_update_final()

class RoleModal(discord.ui.Modal, title="Add Role"):
    role_input = discord.ui.TextInput(label="Role Mention or ID", style=discord.TextStyle.short)

    def __init__(self, view: ReactionRoleSetupView):
        super().__init__()
        self.view_ref = view

    async def on_submit(self, interaction: discord.Interaction):
        content = self.role_input.value.strip()
        role_id = None
       
        match = re.search(r"<@&(\d+)>", content)
        if match:
            try:
                role_id = int(match.group(1))
            except:
                role_id = None
        else:
            try:
                role_id = int(content)
            except:
                role_id = None
        if not role_id:
            await interaction.response.send_message(embed=self.view_ref.cog.error_embed("Invalid role mention or ID."), ephemeral=True)
            return
        role = interaction.guild.get_role(role_id)
        if role is None:
            await interaction.response.send_message(embed=self.view_ref.cog.error_embed("Role not found."), ephemeral=True)
            return
        self.view_ref.role_id = role_id
        for child in self.view_ref.children:
            if isinstance(child, discord.ui.Button) and child.custom_id == "add_role":
                child.disabled = True
        await interaction.response.send_message(embed=self.view_ref.cog.success_embed("Role set successfully."), ephemeral=True)
        await self.view_ref.update_message()
        await self.view_ref.check_and_update_final()

class FinalButton(discord.ui.Button):
    def __init__(self, view: ReactionRoleSetupView):
        super().__init__(label="Add rroles", style=discord.ButtonStyle.green, custom_id="final_rroles")
        self.view_ref = view

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        try:
            target_message = await interaction.channel.fetch_message(self.view_ref.message_id)
        except Exception:
            await interaction.response.send_message(embed=self.view_ref.cog.error_embed("Message not found during final step."), ephemeral=True)
            return
     
        found = None
        for emoji in guild.emojis:
            if emoji.name == self.view_ref.emoji_name:
                found = emoji
                break
        if not found:
            await interaction.response.send_message(embed=self.view_ref.cog.error_embed("Emoji not found during final step."), ephemeral=True)
            return
        role = guild.get_role(self.view_ref.role_id)
        if role is None:
            await interaction.response.send_message(embed=self.view_ref.cog.error_embed("Role not found during final step."), ephemeral=True)
            return
        try:
            await target_message.add_reaction(found)
        except Exception:
            await interaction.response.send_message(embed=self.view_ref.cog.error_embed("Failed to add reaction during final step."), ephemeral=True)
            return
       
        msg_id_int = target_message.id
        emoji_str = str(found)
        if msg_id_int not in self.view_ref.cog.rrole_mappings:
            self.view_ref.cog.rrole_mappings[msg_id_int] = {}
        self.view_ref.cog.rrole_mappings[msg_id_int][emoji_str] = role.id
        self.view_ref.cog.save_reaction_roles()
        self.disabled = True
        await interaction.response.send_message(embed=self.view_ref.cog.success_embed("Reaction role successfully added."), ephemeral=True)
        self.view_ref.stop()

class ReactionRoles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.rrole_json_file = "reactionroles.json"
        self.rrole_mappings = self.load_reaction_roles()

    def load_blacklist(self):
        if not os.path.exists("blacklist.json"):
            return []
        try:
            with open("blacklist.json", "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def load_reaction_roles(self):
        if not os.path.exists(self.rrole_json_file):
            with open(self.rrole_json_file, "w") as f:
                json.dump({}, f)
            return {}
        try:
            with open(self.rrole_json_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def save_reaction_roles(self):
        with open(self.rrole_json_file, "w") as f:
            json.dump(self.rrole_mappings, f, indent=4)

    def loading_embed(self):
        return discord.Embed(title="Loading...", description="<a:loading:1359934124785143908>")

    def error_embed(self, message: str):
        return discord.Embed(title="Error!", description=message, color=discord.Color.red())

    def success_embed(self, message: str):
        return discord.Embed(title="Success!", description=message, color=discord.Color.green())

    @app_commands.command(name="rroles", description="Add reaction roles.")
    async def rroles_command(self, interaction: discord.Interaction):
        blacklist = self.load_blacklist()
        if interaction.user.id in blacklist or not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(embed=self.error_embed("No permissions"), ephemeral=True)
            return

        initial_embed = discord.Embed(
            title="Reaction Roles",
            description="- Message: \n- Emoji: \n- Role: "
        )
        view = ReactionRoleSetupView(self, interaction)
        await interaction.response.send_message(embed=initial_embed, view=view, ephemeral=False)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.message_id not in self.rrole_mappings:
            return
        emoji_str = str(payload.emoji)
        mapping = self.rrole_mappings[payload.message_id]
        if emoji_str not in mapping:
            return
        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return
        role = guild.get_role(mapping[emoji_str])
        if role is None:
            return
        member = guild.get_member(payload.user_id)
        if member is None or role in member.roles:
            return
        try:
            await member.add_roles(role, reason="Reaction role assignment")
        except Exception as e:
            print(f"Error assigning role: {e}")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.message_id not in self.rrole_mappings:
            return
        emoji_str = str(payload.emoji)
        mapping = self.rrole_mappings[payload.message_id]
        if emoji_str not in mapping:
            return
        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return
        role = guild.get_role(mapping[emoji_str])
        if role is None:
            return
        member = guild.get_member(payload.user_id)
        if member is None or role not in member.roles:
            return
        try:
            await member.remove_roles(role, reason="Reaction role removal")
        except Exception as e:
            print(f"Error removing role: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(ReactionRoles(bot))
