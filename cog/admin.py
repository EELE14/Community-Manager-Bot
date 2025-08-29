import discord,os,json,time,datetime,sys,asyncio
from discord.ext import commands,tasks
from discord import app_commands
from helpers import *
sys.dont_write_bytecode = True

class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.AutoShardedBot = bot 

    @commands.command(name="reload")
    async def reloadcmd(self,ctx:commands.Context):
        
        try:
            if ctx.guild.id != 1358919712473481507:
                return
        except:
            ...

        if ctx.author.id not in [1263756486660587543]:

            response = await ctx.reply(embed=loading_embed())
            await asyncio.sleep(1)
            await response.edit(embed=error_embed("Missing permissions"))
            return

        content = '```diff\n'
        suffix = '```'
        response = await ctx.reply(embed=loading_embed())

        for fp in os.listdir('cog'):
            if "admin_commands.py" != fp and fp.endswith('.py'):
                fp = fp.removesuffix(".py")

                try:
                    await self.bot.unload_extension(name="cog." + fp)
                    content = content + f"- {fp}\n"
                    await response.edit(embed=loading_embed(content+suffix))
                except:
                    ...

                time.sleep(0.2)

                try:
                    await self.bot.load_extension(name="cog." + fp)
                    content = content + f"+ {fp}\n"
                    await response.edit(embed=loading_embed(content+suffix))
                except Exception as e:
                    content = content + f"- Error loading {fp}: {e}\n"
                    await response.edit(embed=loading_embed(content+suffix))

        await self.bot.tree.sync()
        await response.edit(embed=success_embed(content+suffix))

    @commands.command(name="upload")
    async def upload(self,ctx:commands.Context):

        try:
            if ctx.guild.id != 1358919712473481507:
                return
        except:
            ...

        if ctx.author.id not in [1263756486660587543]:

            response = await ctx.reply(embed=loading_embed())
            await asyncio.sleep(1)
            await response.edit(embed=error_embed("Missing permissions"))
            return

        response = await ctx.reply(embed=loading_embed())

        for attatchment in ctx.message.attachments:
            if attatchment.filename == "helpers.py":
                await attatchment.save("helpers.py")
            else:
                await attatchment.save(f"cog/{attatchment.filename}")
        
        await response.edit(embed=success_embed("Files uploaded sucessfully (,reload to update)"))

    @commands.command(name="download")
    async def download(self,ctx:commands.Context,name:str):

        try:
            if ctx.guild.id != 1358919712473481507:
                return
        except:
            ...

        if ctx.author.id not in [1263756486660587543]:

            response = await ctx.reply(embed=loading_embed())
            await asyncio.sleep(1)
            await response.edit(embed=error_embed("Missing permissions"))
            return

        response = await ctx.reply(embed=loading_embed())

        if name == "*" or name == ".":
            for fp in os.listdir('cog'):
                if fp.endswith(".py"):
                    await ctx.channel.send(file=discord.File(f'cog/{fp}'))
            await ctx.channel.send(file=discord.File("helpers.py"))

        elif name.removeprefix(".py") == "helpers":
            await ctx.channel.send(file=discord.File(f"{name.removesuffix(".py")}.py"))

        else:
            await ctx.channel.send(file=discord.File(f"cog/{name.removesuffix(".py")}.py"))
        
        await response.edit(embed=success_embed("Downloaded completed sucessfully"))

    @commands.command(name="list")
    async def coglist(self,ctx:commands.Context):

        try:
            if ctx.guild.id != 1358919712473481507:
                return
        except:
            ...

        if ctx.author.id not in [1263756486660587543]:

            response = await ctx.reply(embed=loading_embed())
            await asyncio.sleep(1)
            await response.edit(embed=error_embed("Missing permissions"))
            return

        response = await ctx.reply(embed=loading_embed())

        content = "```ansi\n*/. (all)\nhelpers.py"

        for file in os.listdir("cog"):
            if file.endswith(".py"):
                content = content + f'\n{file}'

        content = content + "\n```"

        await response.edit(embed=success_embed(content))

    @commands.command(name="load")
    async def loadext(self,ctx:commands.Context,ext:str):

        try:
            if ctx.guild.id != 1358919712473481507:
                return
        except:
            ...

        if ctx.author.id not in [1263756486660587543]:

            response = await ctx.reply(embed=loading_embed())
            await asyncio.sleep(1)
            await response.edit(embed=error_embed("Missing permissions"))
            return

        resp = await ctx.reply(embed=loading_embed())
        try:
            await self.bot.load_extension("cog." + ext.removesuffix(".py"))
            await resp.edit(embed=success_embed(f"Loaded {ext}"))
        except Exception as e:
            await resp.edit(embed=error_embed(e))

    @commands.command(name="unload")
    async def unloadext(self,ctx:commands.Context,ext:str):

        try:
            if ctx.guild.id != 1358919712473481507:
                return
        except:
            ...

        if ctx.author.id not in [1263756486660587543]:

            response = await ctx.reply(embed=loading_embed())
            await asyncio.sleep(1)
            await response.edit(embed=error_embed("Missing permissions"))
            return

        resp = await ctx.reply(embed=loading_embed())
        try:
            await self.bot.unload_extension("cog." + ext.removesuffix(".py"))
            await resp.edit(embed=success_embed(f"Unloaded {ext}"))
        except Exception as e:
            await resp.edit(embed=error_embed(e))

    async def cog_load(self):
        print(f"{self.__class__.__name__} loaded!")

    async def cog_unload(self):
        print(f"{self.__class__.__name__} unloaded!")

async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(AdminCog(bot=bot))
    
    