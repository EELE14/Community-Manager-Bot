import discord
from discord.ext import commands
from discord import app_commands
import os, json, asyncio

class ActiveStaff(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.enabled = True
        self.active_role_id = 1359892231452102740
        self.excluded_role_id = 1359893175459643617

    def load_moderators(self):
        
        if not os.path.exists("moderators.json"):
            return []
        try:
            with open("moderators.json", "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def save_moderators(self, mods):
        
        with open("moderators.json", "w") as f:
            json.dump(mods, f, indent=4)

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

    def error_embed(self, message):
        return discord.Embed(title="Error!", description=message, color=discord.Color.red())

    def success_embed(self, message):
        return discord.Embed(title="Success!", description=message, color=discord.Color.green())

    @app_commands.command(name="modadd", description="Add a user as a moderator with an alwaysping flag.")
    async def modadd(self, interaction: discord.Interaction, member: discord.Member, alwaysping: bool):
        
        blacklist = self.load_blacklist()
        if interaction.user.id in blacklist:
            await interaction.response.send_message(embed=self.loading_embed(), ephemeral=False)
            await asyncio.sleep(1)
            return await interaction.edit_original_response(embed=self.error_embed("No permissions"))
        
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(embed=self.loading_embed(), ephemeral=False)
            await asyncio.sleep(1)
            return await interaction.edit_original_response(embed=self.error_embed("No permissions"))

        if member.id in blacklist:
            await interaction.response.send_message(embed=self.loading_embed(), ephemeral=False)
            await asyncio.sleep(1)
            return await interaction.edit_original_response(embed=self.error_embed("Cannot add blacklisted user."))

        mods = self.load_moderators()
       
        entry = next((m for m in mods if m["id"] == member.id), None)
        if entry:
           
            entry["alwaysping"] = alwaysping
            message_text = f"{member.name} is already a moderator. Updated alwaysping to **{alwaysping}**."
        else:
            mods.append({"id": member.id, "alwaysping": alwaysping})
            message_text = f"{member.name} has been added as a moderator with alwaysping = **{alwaysping}**."
        
        self.save_moderators(mods)
        await interaction.response.send_message(embed=self.loading_embed(), ephemeral=False)
        await asyncio.sleep(1)
        await interaction.edit_original_response(embed=self.success_embed(message_text))

    @app_commands.command(name="modremove", description="Remove a user from the moderator list")
    async def modremove(self, interaction: discord.Interaction, member: discord.Member):
        
        blacklist = self.load_blacklist()
        if interaction.user.id in blacklist:
            await interaction.response.send_message(embed=self.loading_embed(), ephemeral=False)
            await asyncio.sleep(1)
            return await interaction.edit_original_response(embed=self.error_embed("No permissions"))
        
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(embed=self.loading_embed(), ephemeral=False)
            await asyncio.sleep(1)
            return await interaction.edit_original_response(embed=self.error_embed("No permissions"))
        
        mods = self.load_moderators()
        
        entry = next((m for m in mods if m["id"] == member.id), None)
        if not entry:
            await interaction.response.send_message(embed=self.loading_embed(), ephemeral=False)
            await asyncio.sleep(1)
            return await interaction.edit_original_response(embed=self.error_embed(f"{member.name} is not a moderator."))
        
        mods.remove(entry)
        self.save_moderators(mods)
        await interaction.response.send_message(embed=self.loading_embed(), ephemeral=False)
        await asyncio.sleep(1)
        await interaction.edit_original_response(embed=self.success_embed(f"{member.name} has been removed as a moderator."))

    @commands.command(name="enable")
    @commands.has_permissions(administrator=True)
    async def enable(self, ctx: commands.Context):
        
        blacklist = self.load_blacklist()
        if ctx.author.id in blacklist:
            msg = await ctx.send(embed=self.loading_embed())
            await asyncio.sleep(1)
            return await msg.edit(embed=self.error_embed("No permissions"))
        
        msg = await ctx.send(embed=self.loading_embed())
        await asyncio.sleep(1)
        self.enabled = True
        await self.update_all_moderators(ctx.guild)
        await self.update_bot_presence(ctx.guild)
        await msg.edit(embed=self.success_embed("Active staff monitoring enabled."))

    @commands.command(name="disable")
    @commands.has_permissions(administrator=True)
    async def disable(self, ctx: commands.Context):
        
        blacklist = self.load_blacklist()
        if ctx.author.id in blacklist:
            msg = await ctx.send(embed=self.loading_embed())
            await asyncio.sleep(1)
            return await msg.edit(embed=self.error_embed("No permissions"))
        
        msg = await ctx.send(embed=self.loading_embed())
        await asyncio.sleep(1)
        self.enabled = False
        await self.remove_active_role_from_all(ctx.guild)
        await self.bot.change_presence(activity=None)
        await msg.edit(embed=self.success_embed("Active staff monitoring disabled."))

    async def update_all_moderators(self, guild: discord.Guild):
        mods = self.load_moderators()
        for mod_entry in mods:
            member = guild.get_member(mod_entry["id"])
            if member:
                await self.update_member_role(member, mod_entry)

    async def remove_active_role_from_all(self, guild: discord.Guild):
        mods = self.load_moderators()
        role = guild.get_role(self.active_role_id)
        if role is None:
            return
        for mod_entry in mods:
            member = guild.get_member(mod_entry["id"])
            if member and role in member.roles:
                try:
                    await member.remove_roles(role)
                except Exception as e:
                    print(f"Error removing active role from {member}: {e}")

    async def update_member_role(self, member: discord.Member, mod_entry: dict):
        
        active_role = member.guild.get_role(self.active_role_id)
        if active_role is None:
            return
        
        alwaysping = mod_entry.get("alwaysping", False)
        
        if alwaysping:
            if active_role not in member.roles:
                try:
                    await member.add_roles(active_role)
                except Exception as e:
                    print(f"Error adding active role to {member}: {e}")
            return

        if member.status in (discord.Status.online, discord.Status.idle, discord.Status.dnd) and not any(r.id == self.excluded_role_id for r in member.roles):
            if active_role not in member.roles:
                try:
                    await member.add_roles(active_role)
                except Exception as e:
                    print(f"Error adding active role to {member}: {e}")
        else:
            if active_role in member.roles:
                try:
                    await member.remove_roles(active_role)
                except Exception as e:
                    print(f"Error removing active role from {member}: {e}")

    async def update_bot_presence(self, guild: discord.Guild):
        
        mods = self.load_moderators()
        count = 0
        for mod_entry in mods:
            member = guild.get_member(mod_entry["id"])
            if not member:
                continue
            if mod_entry.get("alwaysping", False) or member.status in (discord.Status.online, discord.Status.idle, discord.Status.dnd):
                count += 1
        watching_activity = discord.Activity(type=discord.ActivityType.watching, name=f"Active moderators: {count}")
        await self.bot.change_presence(status=discord.Status.dnd, activity=watching_activity)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if not self.enabled:
            return
        mods = self.load_moderators()
        if not any(mod["id"] == after.id for mod in mods):
            return
        
        entry = next((m for m in mods if m["id"] == after.id), None)
        if entry and (before.status != after.status or set(before.roles) != set(after.roles)):
            await self.update_member_role(after, entry)
            await self.update_bot_presence(after.guild)

    @commands.Cog.listener()
    async def on_presence_update(self, before: discord.Member, after: discord.Member):
        if not self.enabled:
            return
        mods = self.load_moderators()
        if not any(mod["id"] == after.id for mod in mods):
            return
        entry = next((m for m in mods if m["id"] == after.id), None)
        if entry:
            await self.update_member_role(after, entry)
            await self.update_bot_presence(after.guild)

async def setup(bot: commands.Bot):
    await bot.add_cog(ActiveStaff(bot))
