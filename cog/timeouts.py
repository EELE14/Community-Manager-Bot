import discord, os, json, re, time, datetime, sys, asyncio, importlib
from discord.ext import commands, tasks
from discord import app_commands
from operator import itemgetter
sys.dont_write_bytecode = True

class Muted(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.AutoShardedBot = bot  

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):

        muted = self.bot.get_guild(1358919712473481507).get_role(1358919928912281692)

        async for entry in after.guild.audit_logs(action=discord.AuditLogAction.member_role_update, limit=1):
            if entry.target == after and entry.user != self.bot.user:
                if muted not in before.roles and muted in after.roles:
                    await after.timeout(datetime.timedelta(minutes=15), reason="Role assignment timeout")
                    return

                elif muted in before.roles and muted not in after.roles:
                    await after.timeout(None, reason=f"Role removed by {entry.user.top_role.name}") 
                    return

        if before.is_timed_out() == True and after.is_timed_out() == False:
            
            await before.remove_roles(muted)  
            return    

        elif before.is_timed_out() == False and after.is_timed_out() == True:
            
            await before.add_roles(muted)
            return

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        
        if message.guild is None:
            return
        muted = message.guild.get_role(1358919928912281692)
        member = message.guild.get_member(message.author.id)
        if member is None:
            return
        if muted in member.roles:
            await message.author.remove_roles(muted)

    async def cog_load(self):
        print(f"{self.bot.user.name}: {self.__class__.__name__} loaded!")

    async def cog_unload(self):
        print(f"{self.bot.user.name}: {self.__class__.__name__} unloaded!")

async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(Muted(bot=bot))
