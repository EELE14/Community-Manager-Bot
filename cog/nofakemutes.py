import discord
from discord.ext import commands, tasks
from datetime import datetime

MUTE_ROLE_ID = 1358919928912281692

class MuteCheck(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
        self.check_mutes.start()

    def cog_unload(self):
        
        self.check_mutes.cancel()

    @tasks.loop(minutes=1)
    async def check_mutes(self):
        for guild in self.bot.guilds:
            role = guild.get_role(MUTE_ROLE_ID)
            if not role:
                continue
            for member in role.members:

                try:
                    timed_out = member.is_timed_out()
                except AttributeError:
                    t = getattr(member, "communication_disabled_until", None)
                    timed_out = (t is not None and t > datetime.utcnow())
                
                if not timed_out:
                    try:
                        await member.remove_roles(role, reason="Not muted")
                    except Exception as e:
                        print(f"Error removing mute role from {member}: {e}")

    @check_mutes.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
    await bot.add_cog(MuteCheck(bot))
