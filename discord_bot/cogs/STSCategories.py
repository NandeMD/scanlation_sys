import os
import sys
import traceback

import discord
from discord import CategoryChannel, TextChannel
from discord.abc import GuildChannel, PrivateChannel
from discord.ext import commands, tasks
from requests import get as rget
from requests import post as rpost

from mp import config
from mp.colors import Colors

API = config.get_api_ip()


CATEGORIES = config.get_categories()


async def change_category(channel: TextChannel, category: CategoryChannel | GuildChannel | PrivateChannel, payload: dict):
    serie_category = channel.category
    if serie_category.id != category.id:
        await channel.edit(category=category)
        print(f"{Colors.green}[INFO]\t{Colors.reset}Channel {Colors.cyan}{channel.name}{Colors.reset}"
              f" has moved: {Colors.cyan}{category.name}{Colors.reset}")
        rpost(f"{API}/series/update/manga", json=payload)


class CategoryWatcher(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.is_watching = False

        self.current_category = None
        self.current2_category = None
        self.ready_category = None
        self.check_category = None
        self.category_full_safety = None
        
    @commands.Cog.listener()
    async def on_ready(self):
        self.current_category = self.bot.get_channel(CATEGORIES["current"])
        self.current2_category = self.bot.get_channel(CATEGORIES["current2"])
        self.ready_category = self.bot.get_channel(CATEGORIES["ready"])
        self.check_category = self.bot.get_channel(CATEGORIES["check"])
        self.category_full_safety = self.bot.get_channel(CATEGORIES["category_full_safety"])
        
    @discord.slash_command(name="watch_categories", description="Toggle the categorie watcher.")
    @discord.default_permissions(administrator=True)
    async def toggle_sts_category_watcher(self, ctx: discord.ApplicationContext):
        if self.is_watching:
            self.check_categories.stop()
            self.is_watching = False
            await ctx.respond("Categorie watcher stopped.")
        else:
            if self.check_categories.is_running():
                self.check_categories.restart()
                await ctx.respond(f"Categorie watcher restarted."
                                  f" Interval: `{self.check_categories.seconds}` seconds.")
            else:
                self.check_categories.start()
                await ctx.respond(f"Categorie watcher started. Interval: `{self.check_categories.seconds}` seconds.")
            self.is_watching = True
    
    @discord.slash_command(name="cat_watch_interval", description="Change categorie watcher interval.")
    @discord.default_permissions(administrator=True)     
    async def change_category_watcher_interval(
        self, 
        ctx: discord.ApplicationContext, 
        secs: discord.Option(int, name="seconds", description="Interval in seconds.")
    ):
        self.check_categories.change_interval(seconds=secs)
        await ctx.respond(f"Categorie watcher interval changed to: `{secs}` seconds")
        
    @tasks.loop(seconds=60)
    async def check_categories(self):
        try:
            with rget(f"{API}/series/get/") as response:
                series = response.json()["series"]

            for serie in series:
                if len(str(serie["main_category"])) == 1:
                    continue
                else:
                    serie_channel: TextChannel | GuildChannel | PrivateChannel = self.bot.get_channel(serie["channel_id"])

                    if serie["source_chap"] <= serie["base_chap"]:
                        try:
                            payload = {
                                "id": serie["id"],
                                "current_category": self.current_category.id
                            }
                            await change_category(serie_channel, self.current_category, payload)
                            continue
                        except (discord.HTTPException, discord.InvalidArgument, discord.Forbidden):
                            payload = {
                                "id": serie["id"],
                                "current_category": self.current2_category.id
                            }
                            await change_category(serie_channel, self.current2_category, payload)
                            continue
                    elif bool(serie["qcer"]) and (serie["last_qced"] > serie["base_chap"] or
                                                  serie["last_qced"] < serie["completed"]):
                        if serie["last_qced"] > serie["base_chap"]:
                            payload = {
                                "id": serie["id"],
                                "current_category": self.ready_category.id
                            }
                            await change_category(serie_channel, self.ready_category, payload)
                            continue
                        if serie["last_qced"] < serie["completed"]:
                            payload = {
                                "id": serie["id"],
                                "current_category": self.check_category.id
                            }
                            await change_category(serie_channel, self.check_category, payload)
                            continue
                    elif not bool(serie["qcer"]) and serie["completed"] > serie["base_chap"]:
                        payload = {
                            "id": serie["id"],
                            "current_category": self.ready_category.id
                        }
                        await change_category(serie_channel, self.ready_category, payload)
                        continue
                    else:
                        try:
                            main_category = self.bot.get_channel(
                            serie["main_category"])
                            payload = {
                                "id": serie["id"],
                                "current_category": main_category.id
                            }
                            await change_category(serie_channel, main_category, payload)
                            continue
                        except (discord.HTTPException, discord.InvalidArgument, discord.Forbidden):
                            payload = {
                                "id": serie["id"],
                                "current_category": self.category_full_safety.id
                            }
                            await change_category(serie_channel, self.category_full_safety, payload)
                            continue

        except Exception as e:
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(
                f"{Colors.red}[ERROR]\t{Colors.purple}"
                f"An error occured - {exc_type} : {fname}:{exc_tb.tb_lineno}\n"
                f"{e}\n{traceback.format_exc()}{Colors.reset}"
            )


def setup(bot: discord.Bot):
    bot.add_cog(CategoryWatcher(bot))
