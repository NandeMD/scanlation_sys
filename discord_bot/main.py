import discord
from mp.misc import *
from mp.colors import Colors as clrs
from mp.config import get_token_env_var

from os import getenv

bot = discord.Bot(
    intents=discord.Intents.all(),
    auto_sync_commands=True
)

ALL_COGS = get_all_cogs()


@bot.event
async def on_ready():
    print(f"{clrs.green}[READY]{clrs.reset}\tBot is ready!")


@bot.command(name="load_cog", description="Load cog.")
@discord.default_permissions(administrator=True)
async def load_single_cog(ctx: discord.ApplicationContext, cog_name: discord.Option(str, description="Cog name.", choices=ALL_COGS)):
    result = load_cog(cog_name, bot)
    if result:
        await ctx.respond(f"Cog `{cog_name}` loaded.")
    else:
        await ctx.respond(f"An error occured while loading Cog `{cog_name}`! See logs for details.")


@bot.command(name="unload_cog", description="Remove a Cog.")
@discord.default_permissions(administrator=True)
async def unload_single_cog(ctx: discord.ApplicationContext, cog_name: discord.Option(str, description="Cog name.", choices=ALL_COGS)):
    result = unload_cog(cog_name, bot)
    if result:
        await ctx.respond(f"Cog `{cog_name}` removed.")
    else:
        await ctx.respond(f"An error occured while removing Cog `{cog_name}`! See logs for details.")


@bot.command(name="load_all", description="Load all cogs. (Not recommended!!!)")
@discord.default_permissions(administrator=True)
async def loadallcogs(ctx: discord.ApplicationContext):
    try:
        load_all_cogs(bot)
        await ctx.respond("All cogs loaded successfully.")
    except Exception as e:
        await ctx.respond(f"An error occured while loading Cogs! Error: {e}\nSee logs for details.")


@bot.command(name="unload_all", description="Unload all cogs. (Not recommended!!!)")
@discord.default_permissions(administrator=True)
async def unloadallcogs(ctx: discord.ApplicationContext):
    try:
        unload_all_cogs(bot)
        await ctx.respond("All cogs unloaded successfully.")
    except Exception as e:
        await ctx.respond(f"An error occured while unloading Cogs! Error: {e}\nSee logs for details.")


load_all_cogs(bot)

bot_token_var = get_token_env_var()
print(f"{Clrs.yellow}[INIT]\t{Clrs.reset}Using Token: {bot_token_var}")
bot.run(bot_token_var)
