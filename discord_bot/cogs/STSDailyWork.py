from json import loads

import discord
from discord.abc import GuildChannel, PrivateChannel
from discord.ext import commands, tasks
from requests import get as rget

from mp import config
from mp.jobs import Jobs

API = config.get_api_ip()


class STSDaily(commands.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot
        self.is_watching = False
        # Change the channel ID
        self.DAILY_CHANNEL_ID = config.get_any("DAILY_CHANNEL_ID")
        self.daily_work_channel = self.bot.get_channel(self.DAILY_CHANNEL_ID) if self.bot.is_ready() else None

    @commands.Cog.listener()
    async def on_ready(self):
        self.daily_work_channel = self.bot.get_channel(self.DAILY_CHANNEL_ID)
        
    @discord.slash_command(name="daily_watcher", description="Toggle the daily work watcher.")
    @discord.default_permissions(administrator=True)
    async def stsdaily(self, ctx: discord.ApplicationContext):
        if self.is_watching:
            self.send_daily.stop()
            self.is_watching = False
            await ctx.respond("Stopped daily work watcher.")
        else:
            if self.send_daily.is_running():
                self.send_daily.restart()
                await ctx.respond(f"Restarted daily work watcher. Interval: `{self.send_daily.hours}` hours.")
            else:
                self.send_daily.start()
                await ctx.respond(f"Started daily work watcher. Interval: `{self.send_daily.hours}` hours.")
            self.is_watching = True
         
    @discord.slash_command(name="daily_watch_interval", description="Change the daily work watcher interval.")
    @discord.default_permissions(administrator=True)
    async def daily_interval(self, ctx: discord.ApplicationContext, sure: discord.Option(int, name="interval", description="Interval in hours")):
        self.send_daily.change_interval(hours=sure)
        await ctx.respond(f"Daily work watcher interval changed to: `{sure}` hours.")
        
    @discord.slash_command(description="Print all awaiting works to the channel.")
    async def daily(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        await self.do_the_work(ctx)
        await ctx.respond("Posted daily works.")
        
    @tasks.loop(hours=12)
    async def send_daily(self):
        await self.do_the_work(self.daily_work_channel)

    @staticmethod
    async def do_the_work(ctx: discord.ApplicationContext | GuildChannel | PrivateChannel):
        with rget(f"{API}/series/get/") as response:
            series = loads(response.text)["series"]

        jobs = Jobs(series)

        translator_text = "--- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- " \
                          "--- --- --- --- --- --- --- --- --- ---\n" \
                          "***Waiting Translations;***\n\n"
        translator_text += jobs.create_main_text("tl")
        translator_text += "--- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---" \
                           " --- --- --- --- --- --- --- --- --- ---\n"

        if len(translator_text) < 2000:
            await ctx.send(translator_text)
        else:
            sections = jobs.split_daily_text(translator_text)
            for section in sections:
                await ctx.send("\n\n".join(section))

        pr_text = "--- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- " \
                  "--- --- --- --- --- --- --- --- --- ---\n" \
                  "***Waiting Proofreads;***\n\n"
        pr_text += jobs.create_main_text("pr")
        pr_text += "--- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---" \
                   " --- --- --- --- --- --- --- --- --- ---\n"

        if len(pr_text) < 2000:
            await ctx.send(pr_text)
        else:
            sections = jobs.split_daily_text(pr_text)
            for section in sections:
                await ctx.send("\n\n".join(section))

        cleaner_text = "--- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --" \
                       "- --- --- --- --- --- --- --- --- --- ---\n" \
                       "***Waiting Cleans;***\n\n"
        cleaner_text += jobs.create_main_text("clnr")
        cleaner_text += "--- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- -" \
                        "-- --- --- --- --- --- --- --- --- --- ---\n"

        if len(cleaner_text) < 2000:
            await ctx.send(cleaner_text)
        else:
            sections = jobs.split_daily_text(cleaner_text)
            for section in sections:
                await ctx.send("\n\n".join(section))

        ts_text = "--- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- -" \
                  "-- --- --- --- --- --- --- --- --- ---\n" \
                  "***Waiting Typesets;***\n\n"
        ts_text += jobs.create_main_text("tser")
        ts_text += "--- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- " \
                   "--- --- --- --- --- --- --- --- --- ---\n"

        if len(ts_text) < 2000:
            await ctx.send(ts_text)
        else:
            sections = jobs.split_daily_text(ts_text)
            for section in sections:
                await ctx.send("\n\n".join(section))

        """ qc_text = "--- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- " \
                                "--- --- --- --- --- --- --- --- --- --- --- ---\n" \
                                "***Waiting Quality Checks;***\n\n"
        qc_text += jobs.create_main_text("qcer")
        qc_text += "--- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---" \
                                 " --- --- --- --- --- --- --- --- --- --- --- ---\n"

        if len(qc_text) < 2000:
            await ctx.send(qc_text)
        else:
            sections = jobs.split_daily_text(qc_text)
            for section in sections:
                await ctx.send("\n\n".join(section)) """
        
        
def setup(bot: discord.Bot):
    bot.add_cog(STSDaily(bot))
    