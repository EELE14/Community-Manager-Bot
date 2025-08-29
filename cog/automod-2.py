import json
import re
import datetime
import os
import discord
from discord.ext import commands

class Automod(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.file_path = os.path.join(os.path.dirname(__file__), 'badwords.json')
        self.blacklist_path = os.path.join(os.path.dirname(__file__), 'blacklist.json')
        self.load_badwords()
        self.load_blacklist()

    def load_badwords(self):
        
        with open(self.file_path, 'r', encoding='utf-8') as f:
            self.badwords = json.load(f)
        self.word_map = {}
        for category, words in self.badwords.items():
            for word in words:
                self.word_map[word.lower()] = category
        self.sorted_words = sorted(self.word_map.keys(), key=lambda w: len(w), reverse=True)

    def load_blacklist(self):
        
        try:
            with open(self.blacklist_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict) and 'blacklist' in data:
                ids = data['blacklist']
            elif isinstance(data, list):
                ids = data
            else:
                ids = []
            self.blacklist = {str(x) for x in ids}
        except FileNotFoundError:
            self.blacklist = set()

    def save_badwords(self):
        
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.badwords, f, indent=2, ensure_ascii=False)
        self.load_badwords()

    @commands.Cog.listener()
    async def on_message(self, message):
        
        if message.author.bot or not message.guild:
            return
        if message.author.guild_permissions.administrator:
            return

        content = message.content.lower()
        triggered_word = None
        triggered_category = None

        for word in self.sorted_words:
            pattern = rf'\b{re.escape(word)}\b'
            if re.search(pattern, content):
                triggered_word = word
                triggered_category = self.word_map[word]
                break

        if not triggered_word:
            return

        try:
            await message.delete()
        except discord.errors.Forbidden:
            pass

        if triggered_category in ['general_insults', 'profanity']:
            embed = discord.Embed(
                title='<:Automod:1364672691214483486> Automod',
                description='You triggered the automod! Please refrain from using insults or profanity.',
                color=discord.Color.red()
            )
            embed.set_footer(text='Repeated offenses may get you timed out.')
            await message.channel.send(embed=embed)
            return

        embed = discord.Embed(
            title='<:Automod:1364672691214483486> Automod',
            description='You have been timed out! Repeated offenses may lead to further action.',
            color=discord.Color.orange()
        )
        embed.set_footer(text='Duration: 1m')
        await message.channel.send(embed=embed)

        try:
            await message.author.timeout(
                datetime.timedelta(minutes=1),
                reason=f'Triggered automod: {triggered_word}'
            )
        except Exception:
            pass

    @commands.command(name='amremove')
    async def amremove(self, ctx, word: str):
        
        author_id = str(ctx.author.id)
        
        if author_id in self.blacklist:
            await ctx.send('You are not allowed to use this command.')
            return
        
        if not ctx.author.guild_permissions.administrator:
            await ctx.send('You need Administrator permissions to use this command.')
            return

        word_lower = word.lower()
        found = False
        for category, words in self.badwords.items():
            if word_lower in [w.lower() for w in words]:
                self.badwords[category] = [w for w in words if w.lower() != word_lower]
                found = True
                break

        if not found:
            await ctx.send(f'`{word}` is not in the badwords list.')
            return

        self.save_badwords()
        await ctx.send(f'Removed `{word}` from category `{category}`.')

    @commands.command(name='amadd')
    async def amadd(self, ctx, word: str, category: str):
        
        author_id = str(ctx.author.id)
        
        if author_id in self.blacklist:
            await ctx.send('You are not allowed to use this command.')
            return
        
        if not ctx.author.guild_permissions.administrator:
            await ctx.send('You need Administrator permissions to use this command.')
            return

        category = category.lower()
        if category not in self.badwords:
            available = ', '.join(self.badwords.keys())
            await ctx.send(f'Category `{category}` does not exist. Available: {available}')
            return

        word_lower = word.lower()
        existing = [w.lower() for w in self.badwords[category]]
        if word_lower in existing:
            await ctx.send(f'`{word}` is already in category `{category}`.')
            return

        self.badwords[category].append(word)
        self.save_badwords()
        await ctx.send(f'Added `{word}` to category `{category}`.')

async def setup(bot):
    await bot.add_cog(Automod(bot))
