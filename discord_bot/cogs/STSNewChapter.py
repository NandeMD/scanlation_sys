from json import decoder, loads
from typing import Optional

import discord
from discord import TextChannel
from discord.abc import GuildChannel, PrivateChannel
from discord.ext import commands, tasks
from requests import get as rget
from requests import post as rpost
from requests.models import Response

from mp import config
from mp.scp_related import create_chapter, DummyUser
from mp.colors import Colors as Clrs

API = config.get_api_ip()
BOT_ID = config.bot_id()
TO_BE_TRANSLATED_CHANNEL_ID = config.get_any("TO_BE_TRANSLATED_CHANNEL_ID")


async def get(path: str) -> Response:
    with rget(f"{API}{path}") as response:
        res = response
    return res


class STS(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.is_watching = False
        self.to_be_translated_channel: Optional[TextChannel] = None

    @commands.Cog.listener()
    async def on_ready(self):
        self.to_be_translated_channel = self.bot.get_channel(TO_BE_TRANSLATED_CHANNEL_ID)

    @discord.slash_command(name="new_chapter_watcher", description="Toggle the new chapter watcher.")
    @discord.default_permissions(administrator=True)
    async def stswatch(self, ctx: discord.ApplicationContext):
        if self.is_watching:
            self.send_manga.stop()
            self.is_watching = False
            await ctx.respond("Stopped new chapter watcher.")
        else:
            if self.send_manga.is_running():
                self.send_manga.restart()
                await ctx.respond(f"Restarted new chapter watcher."
                                  f" Interval: `{self.send_manga.seconds}` seconds.")
            else:
                self.send_manga.start()
                await ctx.respond(f"Started new chapter watcher. Interval: `{self.send_manga.seconds}` seconds.")
            self.is_watching = True

    @discord.slash_command(name="ststwatch_interval", description="Change the interval of the new chapter watcher.")
    @discord.default_permissions(administrator=True)
    async def stswatch_interval(self, ctx: discord.ApplicationContext, secs: discord.Option(int, name="seconds", description="Interval in seconds.")):
        self.send_manga.change_interval(seconds=secs)
        await ctx.respond(f"Interval changed to: `{secs}` seconds")

    @tasks.loop(seconds=60)
    async def send_manga(self):
        try:
            response = await get("/series/get")
            data: list = loads(response.text)["series"]

            for serie in data:
                if not serie["last_chapter_url"] or serie["base_chap"] < serie["source_chap"]:
                    if serie["discord_last_sent"] < serie["source_chap"]:

                        serie_channel: TextChannel | GuildChannel | PrivateChannel = self.bot.get_channel(serie["channel_id"])
                        serie_role = f"<@&{serie['role_id']}>"

                        start = round(serie["discord_last_sent"])
                        end = int(serie["source_chap"])

                        for i in range(start+1, end+1):
                            chapter_resp = create_chapter(serie, i, DummyUser(BOT_ID, "Bot"))
                            if chapter_resp.status_code != 200:
                                print(
                                    f"{Clrs.red}[ERROR]\t{Clrs.purple}Serie {Clrs.cyan}{serie['name']} {i}{Clrs.purple}"
                                    f" An error occured while creating chapters.\n"
                                    f"Code: {Clrs.cyan}{response.status_code}{Clrs.reset}"
                                )
                            else:
                                f"{Clrs.green}[INFO]\t{Clrs.white}Serie {Clrs.cyan}{serie['name']} {i}"
                                f" {Clrs.white}chapter created!{Clrs.reset}"

                        await self.to_be_translated_channel.send(serie['last_chapter_url'] or "UwU")
                        await serie_channel.send(f"> New Chapter! {serie['source_chap']} {serie_role}\n"
                                                 f"{serie['last_chapter_url'] or 'UwU'}")

                        print(
                            f"{Clrs.green}[INFO]\t{Clrs.white}Serie {Clrs.cyan}{serie['name']}"
                            f" {Clrs.white}notice sent!{Clrs.reset}")

                        payload = {"id": serie["id"], "discord_last_sent": serie["source_chap"]}
                        with rpost(f"{API}/series/update/manga/", json=payload) as resp:
                            response = resp
                        if response.status_code == 200:
                            print(
                                f"{Clrs.green}[INFO]\t{Clrs.white}Serie {Clrs.cyan}{serie['name']}"
                                f" {Clrs.white}API updated!{Clrs.reset}")
                        else:
                            print(f"{Clrs.red}[ERROR]\t{Clrs.purple}Serie {Clrs.cyan}{serie['name']}{Clrs.purple}"
                                  f" An error occured while updating serie.\n"
                                  f"Error: {Clrs.cyan}{response.text}{Clrs.purple}\n"
                                  f"Code: {Clrs.cyan}{response.status_code}{Clrs.reset}")

        except decoder.JSONDecodeError:
            print(f"{Clrs.red}[ERROR]\t{Clrs.purple}An error occured while fetching series from main API.{Clrs.reset}")
        except Exception as e:
            print(f"{Clrs.red}[ERROR]\t{Clrs.purple}An unknown error has occured: {Clrs.cyan}{e}{Clrs.reset}")


def setup(bot: discord.Bot):
    bot.add_cog(STS(bot))
