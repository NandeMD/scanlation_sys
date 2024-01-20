import discord
from discord.ext import commands

import json

from requests import get as rget


class Animals(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        
    cats = discord.SlashCommandGroup("cat", "Cat photos or gifs.")
    dogs = discord.SlashCommandGroup("dog", "Dog photos or gifs..")
    
    @cats.command(name="photo", description="Random cat photos.")
    async def cat_photo(self, ctx: discord.ApplicationContext):
        with rget("https://cataas.com/cat?json=true") as resp:
            data = json.loads(resp.text)
            
        await ctx.respond(f"https://cataas.com/cat/{data['_id']}")
        
    @cats.command(name="gif", description="Random cat gifs.")
    async def cat_gifs(self, ctx: discord.ApplicationContext):
        with rget("https://cataas.com/cat/gif?json=true") as resp:
            data = json.loads(resp.text)
            
        await ctx.respond(f"https://cataas.com/cat/{data['_id']}")
        
    @dogs.command(name="foto", description="Random dog photos.")
    async def dog_photo(self, ctx: discord.ApplicationContext):
        with rget("https://dog.ceo/api/breeds/image/random") as resp:
            data = json.loads(resp.text)
        
        await ctx.respond(data["message"])
        
    @dogs.command(name="shibe", description="Random shibe photos.")
    async def shibe_photo(self, ctx: discord.ApplicationContext):
        with rget("https://shibe.online/api/shibes?count=1&urls=true") as resp:
            data = json.loads(resp.text)
        
        await ctx.respond(data[0])
        
    @dogs.command(name="random", description="Random dog thingies.")
    async def random_dog(self, ctx: discord.ApplicationContext):
        with rget("https://random.dog/woof.json") as resp:
            data = json.loads(resp.text)
        
        await ctx.respond(data["url"])
    
    @discord.command(name="fox", description="Random fox photos.")
    async def fox_photo(self, ctx: discord.ApplicationContext):
        with rget("https://randomfox.ca/floof/") as resp:
            data = json.loads(resp.text)
        
        await ctx.respond(data["image"])  
        
    @discord.command(name="duck", description="Random duck photos.")
    async def duck_photo(self, ctx: discord.ApplicationContext):
        with rget("https://random-d.uk/api/v2/random") as resp:
            data = json.loads(resp.text)
        
        await ctx.respond(data["url"])  


def setup(bot: discord.Bot):
    bot.add_cog(Animals(bot))
    