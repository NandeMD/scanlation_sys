from asyncio import sleep as asleep
from typing import Any

import arrow
from orjson import loads

import discord
from discord import Color, Embed, Member, EmbedField
from discord.ext import commands
from discord.ext.pages import Page, Paginator
from requests import get as rget

from mp import config
from mp.payment import calculate_pay
from mp.scp_related import find_chapters_from_a_serie, tstamp_to_ist, sort_work_embed_fields
from mp.misc import (create_channel_mention, create_staff_role_mention, find_serie_by_channel)

API = config.get_api_ip()
TZ = config.get_timezone()
LOCALE = config.get_locale()


class Other(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    # noinspection PyProtectedMember
    @discord.slash_command(name="work", description="Look at your works!")
    async def work_man_work(self, ctx: discord.ApplicationContext, member: Member = None):
        membr = member
        if not membr:
            membr = ctx.user

        with rget(f"{API}/series/get/") as response:
            series = loads(response.text)["series"]

        with rget(f"{API}/chapters/get/filter-by/?params=closer_id%20IS%20NULL&count=1500") as response:
            chapters = loads(response.text)["results"]

        worksworks = {
            "tl": [],
            "pr": [],
            "clnr": [],
            "tser": []
        }

        for serie in series:
            if membr.id == serie["tl"]:
                worksworks["tl"].append(serie)
            if membr.id == serie["pr"]:
                worksworks["pr"].append(serie)
            if membr.id == serie["clnr"]:
                worksworks["clnr"].append(serie)
            if membr.id == serie["tser"]:
                worksworks["tser"].append(serie)

        em = Embed(title=f"{membr.display_name}'s Remaining Works",
                   colour=Color.random())
        em.set_author(name=membr.display_name, icon_url=membr.display_avatar.url)
        
        em_tl = Embed(title=f"{membr.display_name}'s Remaining Translations")
        em_tl.set_author(name=membr.display_name, icon_url=membr.display_avatar.url)
        
        em_pr = Embed(title=f"{membr.display_name}'s Remaining Proofreads")
        em_pr.set_author(name=membr.display_name, icon_url=membr.display_avatar.url)
        
        em_cln = Embed(title=f"{membr.display_name}'s Remaining Cleanings")
        em_cln.set_author(name=membr.display_name, icon_url=membr.display_avatar.url)
        
        em_ts = Embed(title=f"{membr.display_name}'s Remaining Typesets")
        em_ts.set_author(name=membr.display_name, icon_url=membr.display_avatar.url)

        tl_fields: list[list[EmbedField | Any]] = []
        pr_fields: list[list[EmbedField | Any]] = []
        cln_fields: list[list[EmbedField | Any]] = []
        ts_fields: list[list[EmbedField | Any]] = []

        for key, value in worksworks.items():
            if key == "tl":
                for s in value:
                    s_chapters = find_chapters_from_a_serie(s, chapters)
                    for chap in s_chapters:
                        if not chap["tl_id"]:
                            chapter_date = tstamp_to_ist(chap["created_at"]) or arrow.utcnow()
                            due_date = chapter_date.shift(hours=+72).timestamp()
                            tl_fields.append([
                                discord.EmbedField(
                                    name=f"{s['name']} {chap['chapter_num']}",
                                    value=str(due_date),
                                    inline=False
                                ),
                                s['channel_id']
                            ])
            elif key == "pr":
                for s in value:
                    s_chapters = find_chapters_from_a_serie(s, chapters)
                    for chap in s_chapters:
                        if chap["tl_id"] and not chap["pr_id"] and len(str(s["pr"])) > 1:
                            chapter_date = tstamp_to_ist(chap["tl_at"]) or arrow.utcnow()
                            due_date = chapter_date.shift(hours=+48).timestamp()
                            pr_fields.append([
                                discord.EmbedField(
                                    name=f"{s['name']} {chap['chapter_num']}",
                                    value=str(due_date),
                                    inline=False
                                ),
                                s['channel_id']
                            ])
            elif key == "clnr":
                for s in value:
                    s_chapters = find_chapters_from_a_serie(s, chapters)
                    for chap in s_chapters:
                        if not chap["clnr_id"]:
                            chapter_date = tstamp_to_ist(chap["created_at"]) or arrow.utcnow()
                            due_date = chapter_date.shift(hours=+72).timestamp()
                            cln_fields.append([
                                discord.EmbedField(
                                    name=f"{s['name']} {chap['chapter_num']}",
                                    value=str(due_date),
                                    inline=False
                                ),
                                s['channel_id']
                            ])
            elif key == "tser":
                for s in value:
                    s_chapters = find_chapters_from_a_serie(s, chapters)
                    for chap in s_chapters:
                        if len(str(s["clnr"])) > 1:
                            if len(str(s["pr"])) > 1:
                                if not chap["ts_id"] and chap["clnr_id"] and chap["pr_id"]:
                                    chapter_date = tstamp_to_ist(chap["clnr_at"]) or arrow.utcnow()
                                    chapter_date2 = tstamp_to_ist(chap["pr_at"]) or arrow.utcnow()
                                    chapter_date = chapter_date.shift(hours=+72).timestamp()
                                    chapter_date2 = chapter_date2.shift(hours=+72).timestamp()
                                    due_date = int(max([chapter_date, chapter_date2]))
                                    ts_fields.append([
                                        discord.EmbedField(
                                            name=f"{s['name']} {chap['chapter_num']}",
                                            value=str(due_date),
                                            inline=False
                                        ),
                                        s['channel_id']
                                    ])
                            else:
                                if not chap["ts_id"] and chap["clnr_id"] and chap["tl_id"]:
                                    chapter_date = tstamp_to_ist(chap["clnr_at"]) or arrow.utcnow()
                                    chapter_date2 = tstamp_to_ist(chap["tl_at"]) or arrow.utcnow()
                                    chapter_date = chapter_date.shift(hours=+72).timestamp()
                                    chapter_date2 = chapter_date2.shift(hours=+72).timestamp()
                                    due_date = int(max([chapter_date, chapter_date2]))
                                    ts_fields.append([
                                        discord.EmbedField(
                                            name=f"{s['name']} {chap['chapter_num']}",
                                            value=str(due_date),
                                            inline=False
                                        ),
                                        s['channel_id']
                                    ])
                        else:
                            if len(str(s["pr"])) > 1:
                                if not chap["ts_id"] and chap["pr_id"]:
                                    chapter_date = tstamp_to_ist(chap["pr_at"]) or arrow.utcnow()
                                    due_date = chapter_date.shift(hours=+72).timestamp()
                                    ts_fields.append([
                                        discord.EmbedField(
                                            name=f"{s['name']} {chap['chapter_num']}",
                                            value=str(due_date),
                                            inline=False
                                        ),
                                        s['channel_id']
                                    ])
                            else:
                                if not chap["ts_id"] and chap["tl_id"]:
                                    chapter_date = tstamp_to_ist(chap["tl_at"]) or arrow.utcnow()
                                    due_date = chapter_date.shift(hours=+72).timestamp()
                                    ts_fields.append([
                                        discord.EmbedField(
                                            name=f"{s['name']} {chap['chapter_num']}",
                                            value=str(due_date),
                                            inline=False
                                        ),
                                        s['channel_id']
                                    ])

        all_fields = [tl_fields, pr_fields, cln_fields, ts_fields]
        for fields in all_fields:
            fields.sort(key=sort_work_embed_fields)
            for field in fields:
                field[0].value = f"> <#{field[1]}>\n Remaining Time: {arrow.get(float(field[0].value), tzinfo=TZ).humanize(locale=LOCALE)}"

        em_tl._fields.extend([f[0] for f in tl_fields])
        em_pr._fields.extend([f[0] for f in pr_fields])
        em_cln._fields.extend([f[0] for f in cln_fields])
        em_ts._fields.extend([f[0] for f in ts_fields])

        all_embeds = [em_tl, em_pr, em_cln, em_ts]
        for i in range(len(all_embeds)-1, -1, -1):
            if not all_embeds[i].fields:
                del all_embeds[i]
        
        if not all_embeds:
            await ctx.respond(f"Congratz, {membr.mention} has no remaning work!")
            return

        work_pages = [Page(embeds=[work_em]) for work_em in all_embeds]
        paginator = Paginator(pages=work_pages, timeout=360)
        await paginator.respond(ctx.interaction)
        
    @discord.slash_command(description="Inspect a channel's serie.")
    async def info(self, ctx: discord.ApplicationContext, keyword: discord.Option(str, description="You can look payments info if you want.", choices=["payment", "details"]) = None):
        with rget(f"{API}/series/get/") as response:
            series = loads(response.text)["series"]

        serie = find_serie_by_channel(series, ctx.channel.id)

        if not serie:
            await ctx.respond("No serie belonging to this channel.")
            return

        if keyword == "payment":
            with rget(f"{API}/payperiods/get/last-period") as resp:
                last_period = loads(resp.text)["pay_period"]

            with rget(f"{API}/chapters/get/between-dates/?lower_bound={int(last_period['created_at'])}&upper_bound={int(arrow.utcnow().timestamp())}") as resp:
                chapters = loads(resp.text)["results"]

            with open("mp/clean_fees.json") as file:
                clean_fees = loads(file.read())

            serie_chapters = find_chapters_from_a_serie(serie, chapters)

            tl_embed = Embed(title=f"{serie['name']} TLs")
            pr_embed = Embed(title=f"{serie['name']} PRs")
            cln_embed = Embed(title=f"{serie['name']} CLNs")
            ts_embed = Embed(title=f"{serie['name']} TSs")
            qc_embed = Embed(title=f"{serie['name']} QCs")

            for schap in serie_chapters:
                if schap["tl_id"]:
                    tl_embed.add_field(
                        name=str(schap["chapter_num"]),
                        value=f"<@{schap['tl_id']}> -- {round(schap['tl_bytes']/1000)} KB -- {round(calculate_pay(schap['tl_bytes'], schap['should_pred']), 2)}"
                    )
                if schap["pr_id"]:
                    pr_embed.add_field(
                        name=str(schap["chapter_num"]),
                        value=f"<@{schap['pr_id']}> -- 0.3 $"
                    )
                if schap["clnr_id"]:
                    cln_embed.add_field(
                        name=str(schap["chapter_num"]),
                        value=f"<@{schap['clnr_id']}> -- {clean_fees[serie['role_id']]} $"
                    )
                if schap["ts_id"]:
                    ts_embed.add_field(
                        name=str(schap["chapter_num"]),
                        value=f"<@{schap['ts_id']}> -- {round(schap['tl_bytes']/1000)} KB -- {round(calculate_pay(schap['tl_bytes'], schap['should_qced']), 2)}"
                    )
                if schap["qc_id"]:
                    qc_embed.add_field(
                        name=str(schap["chapter_num"]),
                        value=f"<@{schap['qc_id']}> -- 0.3 $"
                    )

            pages = [Page(embeds=[emem]) for emem in [tl_embed, pr_embed, cln_embed, ts_embed, qc_embed]]
            paginator = Paginator(pages=pages, show_disabled=False, disable_on_timeout=True, timeout=300)
            await paginator.respond(ctx.interaction)

        elif keyword == "details":
            em = Embed(
                title=serie["name"],
                url=serie["base_url"],
                description=f"\nSerie id: {serie['id']}"
                            f"\n[Source]({serie['source_url']})"
                            f"\n[Your Base]({serie['base_url']})"
                            f"\n[Last Source Chapter]({serie['last_chapter_url']})"
                            f"\n[Drive URL]({serie['drive_url']})",
                colour=Color.random()
            )

            em.set_author(
                name="Serie Info",
                icon_url=serie["image_url"]
            )

            em.set_image(url=serie["image_url"])
            em.set_thumbnail(url=serie["image_url"])

            em.add_field(name="Last Source Chapter", value="> " + str(serie["source_chap"]))
            em.add_field(name="Last Date", value="> " + str(serie["time1"]) if serie["time1"] else 'yok')
            em.add_field(name="Last Base Chapter", value="> " + str(serie["base_chap"]))
            em.add_field(name="QC", value="> " + "Needed" if serie["qcer"] else "Not Needed")
            if len(str(serie["pr"])) > 1:
                em.add_field(name="TL (not pred)", value="> " + str(serie["waiting_pr"]))
            em.add_field(name="TL", value="> " + str(serie["pred"]))
            em.add_field(name="CLN", value="> " + str(serie["cleaned"]))
            em.add_field(name="TS", value="> " + str(serie["completed"]))
            if serie["qcer"]:
                em.add_field(name="QC", value="> " + str(serie["last_qced"]))
            em.add_field(name="Role", value=f"> <@&{serie['role_id']}>")
            em.add_field(name="Category", value="> " + create_channel_mention(serie["main_category"]))
            em.add_field(name="Translator", value="> " + create_staff_role_mention(serie["tl"], "tl"))
            if len(str(serie["pr"])) > 1:
                em.add_field(name="Proofreader", value="> " + create_staff_role_mention(serie["pr"], "pr"))
            em.add_field(name="Cleaner", value="> " + create_staff_role_mention(serie["clnr"], "cln"))
            em.add_field(name="Typesetter", value="> " + create_staff_role_mention(serie["tser"], "ts"))

            await ctx.respond(embed=em)
        else:
            em = Embed(
                title=f"{serie['name']}: {serie['id']}",
                url=serie["source_url"],
                colour=Color.random()
            )

            em.add_field(
                name="Last Source Chapter",
                value=f"> [{serie['source_chap']}]({serie['last_chapter_url']})"
            )
            em.add_field(
                name="Last Base Chapter",
                value=f"> {serie['base_chap']}"
            )
            em.add_field(
                name="Last TL:",
                value=f"> {serie['waiting_pr']}"
            )
            if len(str(serie["pr"])) > 1:
                em.add_field(
                    name="Last PR",
                    value=f"> {serie['pred']}"
                )
            em.add_field(
                name="Last TS",
                value=f"> {serie['completed']}"
            )
            await ctx.respond(embed=em)
            
    @discord.slash_command(desciption="Delete messages!")
    @discord.default_permissions(manage_messages=True)
    async def delmessages(
        self, 
        ctx: discord.ApplicationContext, 
        count: discord.Option(
            int, 
            name="count",
            description="Message count",
            min_value=1,
            max_value=100
        )
    ):
        response = await ctx.respond("Purging...")
        await asleep(1)
        await response.delete_original_response()
        await ctx.channel.purge(limit=count)


def setup(bot: discord.Bot):
    bot.add_cog(Other(bot))
