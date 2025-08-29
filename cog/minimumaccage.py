import discord
from discord.ext import commands
import datetime
import json

MIN_ACCOUNT_AGE_SECONDS = 5 * 24 * 60 * 60

FLAGGED_FILE = "flagged.json"

LOG_CHANNEL_ID = 123456789012345678  

def load_flagged():
    
    try:
        with open(FLAGGED_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_flagged(data):
    
    with open(FLAGGED_FILE, "w") as f:
        json.dump(data, f)

class MinimumAccountAgeCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        
        now = datetime.datetime.now(datetime.timezone.utc)
        created_at = member.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=datetime.timezone.utc)
        account_age_seconds = (now - created_at).total_seconds()

        flagged = load_flagged()

        if account_age_seconds < MIN_ACCOUNT_AGE_SECONDS:
            dm_success = False
            try:
                
                dm_embed = discord.Embed(
                    title="You got kicked!",
                    description=(
                        "You have been kicked for having a too young account. "
                        f"The minimum account age is `{MIN_ACCOUNT_AGE_SECONDS // 86400} days`."
                    ),
                    color=discord.Color.red()
                )
                await member.send(embed=dm_embed)
                dm_success = True
            except Exception:
                
                pass

            await member.kick(reason="Account too new")

            log_channel = member.guild.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                log_embed = discord.Embed(
                    title="Flagged join!",
                    description=(
                        f"Member **{member}** (`{member.id}`) "
                        f"joined with account age "
                        f"{account_age_seconds / 3600:.2f} hours."
                    ),
                    color=discord.Color.orange()
                )
                log_embed.add_field(name="DM successful?", value=str(dm_success))
                await log_channel.send(embed=log_embed)

            flagged.append(member.id)
            save_flagged(flagged)

async def setup(bot: commands.Bot):
    await bot.add_cog(MinimumAccountAgeCog(bot))
