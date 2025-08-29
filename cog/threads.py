import discord
from discord.ext import commands

class ThreadCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="id")
    async def id_command(self, ctx: commands.Context):
        
        if isinstance(ctx.channel, discord.Thread):
            embed = discord.Embed(
                title="Thread ID",
                description=f"The thread ID is: **{ctx.channel.id}**",
                color=discord.Color.blurple()
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Error <a:fail:1364688207962177588>",
                description="This command must be used inside a thread.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(name="lock")
    async def lock_command(self, ctx: commands.Context):
        
        if isinstance(ctx.channel, discord.Thread):
            try:
                await ctx.channel.edit(locked=True)
                embed = discord.Embed(
                    title="Thread Locked <a:success:1364688189192933436>",
                    description="This thread has been locked.",
                    color=discord.Color.green()
                )
                await ctx.send(embed=embed)
            except Exception as e:
                embed = discord.Embed(
                    title="Error <a:fail:1364688207962177588>",
                    description=f"Failed to lock the thread: {e}",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Error <a:fail:1364688207962177588>",
                description="This command must be used inside a thread.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(name="unlock")
    async def unlock_command(self, ctx: commands.Context):
        
        if isinstance(ctx.channel, discord.Thread):
            try:
                await ctx.channel.edit(locked=False)
                embed = discord.Embed(
                    title="Thread Unlocked <a:success:1364688189192933436>",
                    description="This thread has been unlocked.",
                    color=discord.Color.green()
                )
                await ctx.send(embed=embed)
            except Exception as e:
                embed = discord.Embed(
                    title="Error <a:fail:1364688207962177588>",
                    description=f"Failed to unlock the thread: {e}",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Error <a:fail:1364688207962177588>",
                description="This command must be used inside a thread.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(ThreadCommands(bot))
