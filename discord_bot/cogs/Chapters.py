import discord
import arrow

from discord.ext import commands
from requests import get as rget, post as rpost
from requests import delete as rdelete
from orjson import loads

from mp.scp_related import search_serie_by_role, update_chapter, create_chapter, find_chapter_from_role_id_chap_num
from mp import config


API = config.get_api_ip()


class Chapters(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    chapters = discord.SlashCommandGroup("chapter", "Commands related chapters.")

    @chapters.command(name="open", description="Open a new chapter.")
    @discord.default_permissions(administrator=True)
    async def open_chapter(
            self,
            ctx: discord.ApplicationContext,
            role: discord.Option(
                discord.Role,
                name="role",
                description="The role of the chapter."
            ),
            chapter_no: discord.Option(
                float,
                name="chapter_no",
                description="Chapter number of the chapter."
            )
    ):
        with rget(f"{API}/series/get") as resp:
            response = resp
            series = loads(response.text)["series"]

        serie_exists = search_serie_by_role(series, role.id)
        if not serie_exists:
            await ctx.respond("Serie does not exist!")
            return

        response = create_chapter(serie_exists[0], chapter_no, ctx.user)

        if response.status_code == 200:
            serie, chapter = find_chapter_from_role_id_chap_num(role.id, chapter_no)
            await ctx.respond(f"{role.mention} `{chapter_no}` created successfully. ID: `{chapter['id']}`")
        elif response.status_code == 422:
            await ctx.respond(f"Incorrect data! Server response:\n```json\n{response.text}```")
        else:
            await ctx.respond(f"An error occured while creating a new chapter! Kod: {response.status_code}\nResponse: {response.text}")

    @chapters.command(name="close", description="Close a chapter!")
    @discord.default_permissions(administrator=True)
    async def close_chapter(
            self,
            ctx: discord.ApplicationContext,
            role: discord.Option(
                discord.Role,
                name="role",
                description="Serie role."
            ),
            chapter_no: discord.Option(
                float,
                name="chapter_no",
                description="Chapter no of the chapter."
            )
    ):

        serie, chapter = find_chapter_from_role_id_chap_num(role.id, chapter_no)
        if not chapter:
            await ctx.respond("No chapter found!")
            return

        response = update_chapter(
            id=chapter["id"],
            closer_id=ctx.user.id,
            closer_name=ctx.user.name,
            closed_at=int(arrow.utcnow().timestamp())
        )

        if response.status_code == 200:
            await ctx.respond(f"Chapter id=`{chapter['id']}` closed successfully!")
        elif response.status_code == 422:
            await ctx.respond(f"Incorrect data! Server response:\n```json\n{response.text}```")
        else:
            await ctx.respond(
                f"An error occured while updating the chapter! Code: {response.status_code}\nResponse: {response.text}")

    @chapters.command(name="delete", description="Delete a chapter!")
    @discord.default_permissions(administrator=True)
    async def delete_chapter(
            self,
            ctx: discord.ApplicationContext,
            chapter_id: discord.Option(
                int,
                name="chapter_id",
                description="ID of the chapter."
            )
    ):
        with rdelete(f"{API}/chapters/delete/{chapter_id}") as response:
            if response.status_code == 200:
                await ctx.respond(f"Chapter id=`{chapter_id}` successfully deleted!")
            elif response.status_code == 422:
                await ctx.respond(f"Incorrect data! Server response:\n```json\n{response.text}```")
            else:
                await ctx.respond(
                    f"An error occured while deleting the chapter! Code: {response.status_code}\nResponse: {response.text}")

    @chapters.command(name="look", description="Look up a chapter!.")
    async def see_chapter(
            self,
            ctx: discord.ApplicationContext,
            role: discord.Option(
                discord.Role,
                name="role",
                description="Role of the chapter."
            ),
            chapter_no: discord.Option(
                float,
                name="chapter_no",
                description="Chapter number of the chapter."
            )
    ):
        serie, chapter = find_chapter_from_role_id_chap_num(role.id, chapter_no)
        if not serie or not chapter:
            await ctx.respond("There is no chapter matching that!")
            return

        desc_str = f"Chapter ID: `{chapter['id']}`\n"\
                   f"Creator: <@{chapter['creator_id']}>\n"\
                   f"Created At: <t:{int(chapter['created_at'])}>"

        if chapter["closer_id"]:
            desc_str += f"\nCloser: <@{chapter['closer_id']}>\n"\
                        f"Closed At: <t:{int(chapter['closed_at'])}>"

        if serie["base_chap"] >= chapter["chapter_num"] or chapter["closer_id"]:
            desc_str += "\nPosted: Yes"
        else:
            desc_str += "\nPosted: No"

        tl_timestamp = chapter['tl_at'] or arrow.utcnow().timestamp()
        pr_timestamp = chapter['pr_at'] or arrow.utcnow().timestamp()
        cln_timestamp = chapter['clnr_at'] or arrow.utcnow().timestamp()
        ts_timestamp = chapter['ts_at'] or arrow.utcnow().timestamp()
        qc_timestamp = chapter['qc_at'] or arrow.utcnow().timestamp()

        chapter_embed = discord.Embed(title=f"{serie['name']} {chapter_no}", description=desc_str)
        chapter_embed.add_field(
            name="TL:",
            value=f"<@{chapter['tl_id']}> -- <t:{int(tl_timestamp)}>"
            if chapter["tl_id"] else f"Not Done -- For: <@{serie['tl']}>",
            inline=False
        )
        if len(str(serie["pr"])) > 1 or chapter["should_pred"]:
            chapter_embed.add_field(
                name="PR:",
                value=f"<@{chapter['pr_id']}> -- <t:{int(pr_timestamp)}>"
                if chapter["pr_id"] else f"Not Done -- For: <@{serie['pr']}>",
                inline=False
            )
        if len(str(serie["clnr"])) > 1:
            chapter_embed.add_field(
                name="Clean:",
                value=f"<@{chapter['clnr_id']}> -- <t:{int(cln_timestamp)}>"
                if chapter["clnr_id"] else f"Not Done -- For: <@{serie['clnr']}>",
                inline=False
            )
        chapter_embed.add_field(
            name="TS:",
            value=f"<@{chapter['ts_id']}> -- <t:{int(ts_timestamp)}>"
            if chapter["ts_id"] else f"Not Done -- For: <@{serie['tser']}>",
            inline=False
        )
        if len(str(serie["qcer"])) > 1 or chapter["should_qced"]:
            chapter_embed.add_field(
                name="QC:",
                value=f"<@{chapter['qc_id']}> -- <t:{qc_timestamp}>"
                if chapter["qc_id"] else "Not done, needed.",
                inline=False
            )

        await ctx.respond(embed=chapter_embed)


def setup(bot: discord.Bot):
    bot.add_cog(Chapters(bot))
