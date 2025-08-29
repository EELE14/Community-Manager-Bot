import os
import json
import asyncio
import discord
from discord.ext import commands
TOKEN = "FakeShit"
OWNER_ID = 1263756486660587543
ALLOWED_GUILD_ID = 1358919712473481507

def load_blacklist():
    
    if not os.path.exists("blacklist.json"):
        return []
    with open("blacklist.json", "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_blacklist(blacklist):
    with open("blacklist.json", "w") as f:
        json.dump(blacklist, f, indent=4)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="m!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ETHAN IS NOOB)")

    cog_folder = "./cog"
    if os.path.exists(cog_folder):
        for filename in os.listdir(cog_folder):
            if filename.endswith(".py"):
                extension = f"cog.{filename[:-3]}"
                try:
                    await bot.load_extension(extension)
                    print(f"Loaded extension: {extension}")
                except Exception as e:
                    print(f"Failed to load extension {extension}: {e}")

    await bot.tree.sync()
    print("Slash commands synced.")

    for guild in bot.guilds:
        if guild.id != ALLOWED_GUILD_ID:
            print(f"Leaving guild: {guild.name} ({guild.id})")
            await guild.leave()

def loading_embed():
    
    return discord.Embed(
        title="Loading...",
        description="<a:loading:1359934124785143908>"
    )

def error_embed(message):
    
    return discord.Embed(
        title="Error!",  
        description=message,
        color=discord.Color.red()
    )

def success_embed(message):
    
    return discord.Embed(
        title="Success!",
        description=message,
        color=discord.Color.green()
    )

@bot.tree.context_menu(name="blacklist add")
async def blacklist_add(interaction: discord.Interaction, user: discord.User):

    if interaction.user.id != OWNER_ID:
   
        await interaction.response.send_message(embed=loading_embed(), ephemeral=False)
        await asyncio.sleep(1)
        await interaction.edit_original_response(embed=error_embed("Missing permissions"))
        return

    await interaction.response.send_message(embed=loading_embed(), ephemeral=False)
    await asyncio.sleep(1)
    
    blacklist = load_blacklist()
    if user.id in blacklist:
        await interaction.edit_original_response(embed=error_embed(f"{user.name} is already blacklisted."))
    else:
        blacklist.append(user.id)
        save_blacklist(blacklist)
        await interaction.edit_original_response(embed=success_embed(f"{user.name} has been successfully added to the blacklist."))

@bot.tree.context_menu(name="blacklist remove")
async def blacklist_remove(interaction: discord.Interaction, user: discord.User):

    if interaction.user.id != OWNER_ID:
    
        await interaction.response.send_message(embed=loading_embed(), ephemeral=False)
        await asyncio.sleep(1)
        await interaction.edit_original_response(embed=error_embed("Missing permissions"))
        return

    await interaction.response.send_message(embed=loading_embed(), ephemeral=False)
    await asyncio.sleep(1)
    
    blacklist = load_blacklist()
    if user.id not in blacklist:
        await interaction.edit_original_response(embed=error_embed(f"{user.name} is not in the blacklist."))
    else:
        blacklist.remove(user.id)
        save_blacklist(blacklist)
        await interaction.edit_original_response(embed=success_embed(f"{user.name} has been successfully removed from the blacklist."))

bot.run(TOKEN)
