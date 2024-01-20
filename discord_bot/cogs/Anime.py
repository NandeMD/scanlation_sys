import discord
from discord import Colour, Embed
from discord.ext import commands

import json

from requests import get as rget

NEKOS_BEST_CATEGORIES = [
    "waifu", "husbando", "kitsune", "lurk", "shoot",
    "sleep", "shrug", "stare", "poke", "smile",
    "blush", "yeet", "feed", "peck", "handhold", 
    "nom", "yawn", "cuddle", "laugh", "pout",
    "happy", "hug", "pat", "thumbsup", "cry"
]

WAIFU_SFW_CATEGORIES = [
    "rastgele", "waifu", "neko", "shinobu", "megumin",
    "cuddle", "cry", "smug", "bonk",
    "hug", "awoo", "kiss", "lick", "pat", 
    "blush", "smile", "highfive", "cringe",
    "handhold", "bite", "glomp", "slap",
    "wink", "poke", "dance", 
]


class Anime(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        
    anime = discord.SlashCommandGroup("anime", "Anime photos or gifs or...")
    waifu = anime.create_subgroup("waifu", "Waifu photos or gifs.")
        
    @anime.command(name="quote", description="Random anime quotes.")
    async def anime_quotes(self, ctx: discord.ApplicationContext):
        with rget("https://animechan.xyz/api/random") as resp:
            data = json.loads(resp.text)
        
        em = Embed(description=data["quote"], color=Colour.random())
        em.set_footer(text=f"By: {data['character']} | Anime: {data['anime']}")
        
        await ctx.respond(embed=em)
    
    @anime.command(name="photo", description="Random anime photos or gifs by category.")
    async def random_anime_by_category(
        self, 
        ctx: discord.ApplicationContext, 
        category: discord.Option(
            str, name="category",
            description="Photo category.",
            choices=NEKOS_BEST_CATEGORIES
        )
    ):
        with rget(f"https://nekos.best/api/v2/{category}?amount=1") as resp:
            data = json.loads(resp.text)
        
        em = Embed(title=data["results"][0].get("anime_name") or data["results"][0]["artist_name"], color=Colour.random())
        em.set_image(url=data["results"][0]["url"])
        
        await ctx.respond(embed=em)
        
    @waifu.command(name="sfw", description="Photos that you can see in public transport.")
    async def waifu_sfw(
        self, 
        ctx: discord.ApplicationContext,
        category: discord.Option(
            str,
            name="category",
            description="Photo category: default: 'random'",
            default="random",
            choices=WAIFU_SFW_CATEGORIES
        )
    ):
        if category == "random":
            with rget("https://api.waifu.im/search?is_nsfw=false") as resp:
                data = json.loads(resp.text)
            await ctx.respond(data["images"][0]["url"])
        else:
            with rget(f"https://api.waifu.pics/sfw/{category}") as resp:
                data = json.loads(resp.text)
            await ctx.respond(data["url"])


def setup(bot: discord.Bot):
    bot.add_cog(Anime(bot))
    