import discord
from discord import Colour, Embed
from discord.ext import commands

import json

from requests import get as rget


class Drinks(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        
    @discord.command(name="coffe", description="Random coffe photos.")
    async def coffe_photo(self, ctx: discord.ApplicationContext):
        with rget("https://coffee.alexflipnote.dev/random.json") as resp:
            data = json.loads(resp.text)
            
        await ctx.respond(data["file"])
    
    @discord.command(name="beer", description="Random beer recommendation.")
    async def bira_bilgi(self, ctx: discord.ApplicationContext):
        with rget("https://api.punkapi.com/v2/beers/random") as resp:
            data = json.loads(resp.text)[0]
            
        em = Embed(
            color=Colour.random(),
            title=f"{data['name']} - {data['tagline']}",
            description=data["description"]
        )
        
        em.add_field(name="First brewed:", value=data["first_brewed"])
        em.add_field(name="Alcohol and pH", value=f"{data['abv']} - {data['ph']}")
        em.add_field(name="Details:", value=data.get("method", "None").get("twist", "None"))
        em.add_field(
            name="Food Pairing:",
            value="\n".join(data["food_pairing"]),
            inline=False
        )
        em.add_field(name="Tips", value=data["brewers_tips"])
        
        em.set_image(url=data["image_url"])
        
        await ctx.respond(embed=em)


def setup(bot: discord.Bot):
    bot.add_cog(Drinks(bot))
        