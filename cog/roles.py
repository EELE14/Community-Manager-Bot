import discord
from discord.ext import commands
from discord import app_commands
import os, json, asyncio

ALLOWED_IDS = {1263756486660587543, 1124836200482615296, 724060712120614912}

class RoleManager(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.roles_file = "roles.json"
        self.saved_roles = self.load_roles()  

    def load_roles(self):
        if not os.path.exists(self.roles_file):
            with open(self.roles_file, "w") as f:
                json.dump({}, f)
            return {}
        try:
            with open(self.roles_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def save_roles(self):
        with open(self.roles_file, "w") as f:
            json.dump(self.saved_roles, f, indent=4)

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

    @app_commands.command(name="saveroles", description="Save all roles of a user to roles.json")
    async def saveroles(self, interaction: discord.Interaction, member: discord.Member):
        
        blacklist = self.load_blacklist()
        if interaction.user.id in blacklist or interaction.user.id not in ALLOWED_IDS:
            await interaction.response.send_message(embed=self.error_embed("No permissions."), ephemeral=True)
            return
        
        roles_ids = [role.id for role in member.roles if role.id != member.guild.default_role.id]
        self.saved_roles[str(member.id)] = roles_ids
        self.save_roles()
        await interaction.response.send_message(embed=self.success_embed(f"Roles for {member.mention} saved."), ephemeral=True)

    @app_commands.command(name="recover", description="Recover saved roles for a user")
    async def recover(self, interaction: discord.Interaction, member: discord.Member):
        
        blacklist = self.load_blacklist()
        if interaction.user.id in blacklist or interaction.user.id not in ALLOWED_IDS:
            await interaction.response.send_message(embed=self.error_embed("No permissions."), ephemeral=True)
            return
        if str(member.id) not in self.saved_roles:
            await interaction.response.send_message(embed=self.error_embed("No saved roles for this user."), ephemeral=True)
            return
        role_ids = self.saved_roles[str(member.id)]
        roles_to_add = []
        for rid in role_ids:
            role = member.guild.get_role(rid)
            if role:
                roles_to_add.append(role)
        if roles_to_add:
            try:
                
                current_roles = set(member.roles)
                new_roles = current_roles.union(set(roles_to_add))
                await member.edit(roles=list(new_roles), reason="Role recovery command")
            except Exception as e:
                await interaction.response.send_message(embed=self.error_embed(f"Failed to recover roles: {e}"), ephemeral=True)
                return
        await interaction.response.send_message(embed=self.success_embed(f"Roles recovered for {member.mention}."), ephemeral=True)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        
        user_key = str(after.id)
        if user_key not in self.saved_roles:
            return
        saved_ids = set(self.saved_roles[user_key])
        
        before_ids = {role.id for role in before.roles}
        after_ids = {role.id for role in after.roles}
        new_role_ids = after_ids - before_ids
        if not new_role_ids:
            return
        guild = after.guild

        max_saved_position = 0
        for rid in saved_ids:
            role = guild.get_role(rid)
            if role and role.position > max_saved_position:
                max_saved_position = role.position

        for new_role_id in new_role_ids:
            new_role = guild.get_role(new_role_id)
            if not new_role:
                continue
            
            if new_role.position > max_saved_position:
                
                adder = None
                try:
                    async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.member_role_update):
                        if entry.target.id == after.id:
                            changes = entry.changes
                            if "roles" in changes:
                                old_value = changes["roles"].get("old_value", [])
                                new_value = changes["roles"].get("new_value", [])
                                old_ids = [r.id for r in old_value] if isinstance(old_value, list) else []
                                new_ids = [r.id for r in new_value] if isinstance(new_value, list) else []
                                if new_role_id in new_ids and new_role_id not in old_ids:
                                    adder = entry.user
                                    break
                except Exception as e:
                    print("Error fetching audit logs:", e)
                
                if adder and adder.id in ALLOWED_IDS:
                    if new_role_id not in saved_ids:
                        self.saved_roles[user_key].append(new_role_id)
                        self.save_roles()
                    continue
                
                try:
                    await after.remove_roles(new_role, reason="Unauthorized higher role addition")
                except Exception as e:
                    print(f"Error removing higher role {new_role.name} from {after}: {e}")
                
                roles_to_remove = [role for role in after.roles if role.permissions.administrator or role.permissions.manage_roles]
                if roles_to_remove:
                    try:
                        await after.remove_roles(*roles_to_remove, reason="Unauthorized role addition")
                    except Exception as e:
                        print(f"Error removing privileged roles from {after}: {e}")
                
                if adder and adder.bot:
                    bot_member = guild.get_member(adder.id)
                    if bot_member:
                        bot_roles_to_remove = [r for r in bot_member.roles if r.permissions.administrator or r.permissions.manage_roles]
                        if bot_roles_to_remove:
                            try:
                                await bot_member.remove_roles(*bot_roles_to_remove, reason="Unauthorized privileged role addition by bot")
                            except Exception as e:
                                print(f"Error removing privileged roles from bot {adder}: {e}")

    async def cog_load(self):
        print(f"{self.bot.user.name}: RoleManager loaded!")

    async def cog_unload(self):
        print(f"{self.bot.user.name}: RoleManager unloaded!")

async def setup(bot: commands.Bot):
    await bot.add_cog(RoleManager(bot))
