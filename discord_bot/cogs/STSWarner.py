import discord
from discord.ext import commands
from discord.ext import tasks

import arrow
from requests import get as rget
from orjson import loads

from mp.config import get_api_ip, get_warn_hours, get_any, bot_id
from mp.scp_related import search_serie_by_id, update_chapter
from mp.colors import Colors as clrs


API = get_api_ip()
FIRST_WARN, SECOND_WARN = get_warn_hours()
ADMIN_WARN_CHANNEL_ID = get_any("ADMIN_WARN_CHANNEL_ID")
QC_WORK_CHANNEL_ID = get_any("QC_WORK_CHANNEL_ID")
BOT_ID = bot_id()


# noinspection DuplicatedCode
class STSWarner(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.is_messaging = False
        self.admin_warn_channel: discord.TextChannel | None = None
        self.qc_work_channel: discord.TextChannel | None = None

        # Change channel IDs
        if self.bot.is_ready():
            self.admin_warn_channel = self.bot.get_channel(ADMIN_WARN_CHANNEL_ID)
            self.qc_work_channel = self.bot.get_channel(QC_WORK_CHANNEL_ID)

    @commands.Cog.listener("on_ready")
    async def set_admin_warn_channel(self):
        self.admin_warn_channel = self.bot.get_channel(ADMIN_WARN_CHANNEL_ID)
        self.qc_work_channel = self.bot.get_channel(QC_WORK_CHANNEL_ID)

    warner_commands = discord.SlashCommandGroup("warner", "Warn your slaves! They must do their work!")

    @warner_commands.command(name="start", description="Toggle the warner.")
    @discord.default_permissions(administrator=True)
    async def start_warner(self, ctx: discord.ApplicationContext):
        if self.is_messaging:
            self.warn_members.stop()
            self.is_messaging = False
            await ctx.respond("Stopped warner.")
        else:
            if self.warn_members.is_running():
                self.warn_members.restart()
                await ctx.respond(
                    f"Restarted warner. Interval: `{self.warn_members.hours}` hours.")
            else:
                self.warn_members.start()
                await ctx.respond(f"Started warner. Interval: `{self.warn_members.hours}` hours.")
            self.is_messaging = True

    @warner_commands.command(name="interval", description="Change the interval of warner.")
    @discord.default_permissions(administrator=True)
    async def retime_warner(
            self,
            ctx: discord.ApplicationContext,
            loop_interval: discord.Option(
                int,
                name="interval",
                description="interval in hours",
                required=True
            )
    ):
        self.warn_members.change_interval(hours=loop_interval)
        await ctx.respond(f"Warner interval changed to: `{loop_interval}` hours.")

    @tasks.loop(hours=24)
    async def warn_members(self):
        print(f"{clrs.yellow}[INFO]\t{clrs.reset}Warning slaves...")
        warner_start = arrow.utcnow()
        with rget(f"{API}/chapters/get/filter-by/?params=closer_id%20IS%20NULL&count=1500") as response:
            rchapters = loads(response.text).get("results")

        if not rchapters:
            return

        with rget(f"{API}/series/get/") as response:
            series = loads(response.text).get("series")

        if not series:
            return

        for chapter in rchapters:
            ser = search_serie_by_id(series, chapter["serie_id"])
            if not ser:
                continue
            ser = ser[0]

            created_at_time = arrow.get(chapter["created_at"], tzinfo="UTC") if chapter["created_at"] else None
            tl_time = arrow.get(chapter["tl_at"], tzinfo="UTC") if chapter["tl_at"] else None
            pr_time = arrow.get(chapter["pr_at"], tzinfo="UTC") if chapter["pr_at"] else None
            clnr_time = arrow.get(chapter["clnr_at"], tzinfo="UTC") if chapter["clnr_at"] else arrow.get(0, tzinfo="UTC")
            ts_time = arrow.get(chapter["ts_at"], tzinfo="UTC") if chapter["ts_at"] else None
            qc_time = arrow.get(chapter["qc_at"], tzinfo="UTC") if chapter["qc_at"] else None

            now_time = arrow.utcnow()

            if not chapter["tl_id"] and not chapter["tl_name"] and created_at_time:
                diff = now_time - created_at_time
                hours, remainder = divmod(diff.total_seconds(), 3600)
                if ser["tl"] is None or len(str(ser["tl"])) <= 1:
                    pass
                elif hours >= SECOND_WARN:
                    serie_channel = self.bot.get_channel(ser["channel_id"])
                    if serie_channel:
                        await serie_channel.send(
                            f"{chapter['chapter_num']}. It has been **{SECOND_WARN}** hours since the chapter's release. "
                            f"<@{ser['tl']}>, chapter will be distributed!"
                        )
                elif hours >= FIRST_WARN:
                    serie_channel = self.bot.get_channel(ser["channel_id"])
                    if serie_channel:
                        await serie_channel.send(
                            f"{chapter['chapter_num']}. It has been **{FIRST_WARN}** hours since the chapter's release. "
                            f"<@{ser['tl']}>, please pay attention!"
                        )
            if chapter["should_pred"] and chapter["tl_id"] and not chapter["pr_id"] and not chapter["pr_name"] and tl_time:
                diff = now_time - tl_time
                hours, remainder = divmod(diff.total_seconds(), 3600)
                pr_uwu = f"<@{ser['pr']}>" if ser["pr"] else "Dang"
                if hours >= FIRST_WARN:
                    serie_channel = self.bot.get_channel(ser["channel_id"])
                    if serie_channel:
                        await serie_channel.send(
                            f"{chapter['chapter_num']}. It has been **{FIRST_WARN}** hours since the chapter's translation. "
                            f"{pr_uwu}, chapter will be distributed!"
                        )
                elif hours >= 24:
                    serie_channel = self.bot.get_channel(ser["channel_id"])
                    if serie_channel:
                        await serie_channel.send(
                            f"{chapter['chapter_num']}. It has been **{FIRST_WARN}** hours since the chapter's translation. "
                            f"{pr_uwu} please pay attention!"
                        )
            if len(str(ser["clnr"])) > 1 and not chapter["clnr_id"] and not chapter["clnr_name"] and created_at_time:
                diff = now_time - created_at_time
                hours, remainder = divmod(diff.total_seconds(), 3600)
                if hours >= SECOND_WARN:
                    serie_channel = self.bot.get_channel(ser["channel_id"])
                    if serie_channel:
                        await serie_channel.send(
                            f"{chapter['chapter_num']}. It has been **{SECOND_WARN}** hours since the chapter's release. "
                            f"<@{ser['clnr']}>, chapter will be distributed!"
                        )
                elif hours >= FIRST_WARN:
                    serie_channel = self.bot.get_channel(ser["channel_id"])
                    if serie_channel:
                        await serie_channel.send(
                            f"{chapter['chapter_num']}. It has been **{FIRST_WARN}** hours since the chapter's release. "
                            f"<@{ser['clnr']}>, please pay attention!"
                        )
            if not chapter["ts_id"] and not chapter["ts_name"] and ((len(str(ser["clnr"])) > 1 and chapter["clnr_id"] and chapter["clnr_name"]) or len(str(ser["clnr"])) == 1):
                if chapter["should_pred"] and chapter["pr_id"] and chapter["pr_name"] and pr_time:
                    initial_time = max([clnr_time.timestamp(), pr_time.timestamp()])
                    initial_time = arrow.get(initial_time, tzinfo="UTC")
                    diff = now_time - initial_time
                    hours, remainder = divmod(diff.total_seconds(), 3600)
                    if hours >= SECOND_WARN:
                        serie_channel = self.bot.get_channel(ser["channel_id"])
                        if serie_channel:
                            await serie_channel.send(
                                f"{chapter['chapter_num']}. It has been **{SECOND_WARN}** hours since the chapter's release. "
                                f"<@{ser['tser']}>, chapter will be distributed!"
                            )
                    elif hours >= FIRST_WARN:
                        serie_channel = self.bot.get_channel(ser["channel_id"])
                        if serie_channel:
                            await serie_channel.send(
                                f"{chapter['chapter_num']}. It has been **{FIRST_WARN}** hours since the chapter's release. "
                                f"<@{ser['tser']}>, please pay attention!"
                            )
                elif tl_time and chapter["tl_id"] and chapter["tl_name"]:
                    initial_time = max([clnr_time.timestamp(), tl_time.timestamp()])
                    initial_time = arrow.get(initial_time, tzinfo="UTC")
                    diff = now_time - initial_time
                    hours, remainder = divmod(diff.total_seconds(), 3600)
                    if hours >= SECOND_WARN:
                        serie_channel = self.bot.get_channel(ser["channel_id"])
                        if serie_channel:
                            await serie_channel.send(
                                f"{chapter['chapter_num']}. It has been **{SECOND_WARN}** hours since the chapter's release. "
                                f"<@{ser['tser']}>, chapter will be distributed!"
                            )
                    elif hours >= FIRST_WARN:
                        serie_channel = self.bot.get_channel(ser["channel_id"])
                        if serie_channel:
                            await serie_channel.send(
                                f"{chapter['chapter_num']}. It has been **{FIRST_WARN}** hours since the chapter's release. "
                                f"<@{ser['tser']}>, please pay attention!"
                            )
            if chapter["should_qced"] and qc_time:
                if ser["base_chap"] < chapter["chapter_num"]:
                    await self.admin_warn_channel.send(
                        f"{chapter['serie_name']} chapter {chapter['chapter_num']} is ready to upload!"
                    )
                else:
                    close_response = update_chapter(
                        id=chapter["id"],
                        closer_id=BOT_ID,
                        closer_name="Bot",
                        closed_at=int(arrow.utcnow().timestamp())
                    )
                    if close_response.ok:
                        print(f"{clrs.yellow}[INFO]\t{clrs.reset}Closed a chapter: {clrs.cyan}{chapter['serie_name']} {chapter['chapter_num']}{clrs.reset}")
                    else:
                        print(f"{clrs.red}[ERROR]\t{clrs.reset}An error occured while closing a chapter: {clrs.cyan}{chapter['serie_name']} {chapter['chapter_num']} -- {chapter['id']}{clrs.reset}")

            elif chapter["should_qced"] and not qc_time:
                await self.qc_work_channel.send(
                    f"{chapter['serie_name']} chapter {chapter['chapter_num']} needs QC!"
                )
            elif not chapter["should_qced"] and ts_time:
                if ser["base_chap"] < chapter["chapter_num"]:
                    await self.admin_warn_channel.send(
                        f"{chapter['serie_name']} chapter {chapter['chapter_num']} is ready to upload!"
                    )
                else:
                    close_response = update_chapter(
                        id=chapter["id"],
                        closer_id=BOT_ID,
                        closer_name="Bot",
                        closed_at=int(arrow.utcnow().timestamp())
                    )
                    if close_response.ok:
                        print(
                            f"{clrs.yellow}[INFO]\t{clrs.reset}Closed a chapter: {clrs.cyan}{chapter['serie_name']} {chapter['chapter_num']}{clrs.reset}")
                    else:
                        print(
                            f"{clrs.red}[ERROR]\t{clrs.reset}An error occured while closing a chapter: {clrs.cyan}{chapter['serie_name']} {chapter['chapter_num']} -- {chapter['id']}{clrs.reset}")

        warner_end = arrow.utcnow()
        warner_time = warner_end - warner_start

        print(f"{clrs.yellow}[INFO]\t{clrs.reset}All warns sent! Time taken: {warner_time.total_seconds()} seconds.")


def setup(bot: discord.Bot):
    bot.add_cog(STSWarner(bot))
