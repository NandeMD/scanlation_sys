import arrow
import discord
from discord import Embed, User, Member

from .config import get_api_ip, get_timezone, get_locale, get_any

from orjson import loads
from requests import get as rget
from requests import post as rpost
from requests import patch as rpatch
from requests import Response


API = get_api_ip()
TZ = get_timezone()
LOCALE = get_locale()


chapter_done_channel_ids = get_any("CHAPTER_DONE_CHNL_IDS")


class DummyUser:
    def __init__(self, id, name):
        self.id = id
        self.name = name


def tstamp_to_ist(ts: int) -> arrow.Arrow | None:
    try:
        return arrow.get(ts, tzinfo="UTC").to(TZ)
    except TypeError:
        return None


def search_serie_by_role(data: list, target: int) -> tuple[dict, int] | bool:
    for item in data:
        if int(item["role_id"]) == target:
            index = data.index(item)
            return item, index
    return False


def search_serie_by_id(data: list, target_id: int) -> tuple[dict, int] | bool:
    for item in data:
        if int(item["id"]) == target_id:
            index = data.index(item)
            return item, index
    return False


def create_chapter(serie: dict, no: int | float, usr: User | Member | DummyUser) -> Response:
    payload = {
        "serie_id": serie["id"],
        "serie_name": serie["name"],
        "chapter_num": no,
        "creator_id": usr.id,
        "creator_name": usr.name,
        "created_at": int(arrow.utcnow().timestamp())
    }

    response = rpost(f"{API}/chapters/new/", json=payload)
    response.close()
    return response


def update_chapter(**kwargs) -> Response:
    response = rpatch(f"{API}/chapters/update/", json=dict(kwargs))
    response.close()

    return response


def update_period(**kwargs) -> Response:
    response = rpatch(f"{API}/payperiods/update/", json=dict(kwargs))
    response.close()

    return response


def update_serie(**kwargs) -> Response:
    response = rpost(f"{API}/series/update/manga/", json=dict(kwargs))
    response.close()

    return response


def create_single_period_embed(p: dict) -> Embed:
    em = Embed(title="Payment period", description=f"Period ID: `{p['id']}`")

    em.add_field(name="Creator:", value=f"<@{p['creator_id']}>" if p['creator_id'] else "None")
    em.add_field(
        name="Created At:",
        value=tstamp_to_ist(p["created_at"]).format("D MMMM YYYY HH:mm", locale=LOCALE) if p["created_at"] else "None"
    )
    em.add_field(name="Closer:", value=f"<@{p['closer_id']}>" if p["closer_id"] else "Yok")
    em.add_field(
        name="Closed At:",
        value=tstamp_to_ist(p["closed_at"]).format("D MMMM YYYY HH:mm", locale=LOCALE) if p["closed_at"] else "None"
    )

    return em


def find_chapters_from_a_serie(serie: dict, chapters: dict):
    results = []

    def filter_func(var):
        if var["serie_id"] == serie["id"]:
            return True
        else:
            return False

    return filter(filter_func, chapters)


def sort_work_embed_fields(field):
    return float(field[0].value)


def find_chapter(chs: list[dict], serid: int, chap_no: float) -> dict | None:
    for ch in chs:
        if ch["serie_id"] == serid and ch["chapter_num"] == chap_no:
            return ch
    return None


def find_chapter_from_role_id_chap_num(role_id: int, chapter_no) -> tuple[dict, dict] | None:
    with rget(f"{API}/series/get/") as response:
        series = loads(response.text)["series"]
    ser = search_serie_by_role(series, role_id)[0]
    if not ser:
        return None

    with rget(f"{API}/chapters/get/filter-by/?params=closer_id%20IS%20NULL&count=1500") as response:
        rchapters = loads(response.text)["results"]
    return ser, find_chapter(rchapters, ser["id"], chapter_no)


def find_serie_and_chapter(role_id: int, chapter_no) -> tuple[dict, dict] | None:
    with rget(f"{API}/series/get/") as response:
        series = loads(response.text)["series"]
    ser = search_serie_by_role(series, role_id)[0]
    if not ser:
        return None

    with rget(f"{API}/chapters/get/filter-by/?params=closer_id%20IS%20NULL&count=1500") as response:
        rchapters = loads(response.text)["results"]
    return ser, find_chapter(rchapters, ser["id"], chapter_no)


async def message_related_channel(bot: discord.Bot, role: discord.Role, chapter_no, j_type: str, ctx: discord.ApplicationContext, pred=None, kb=None):
    chnl: discord.TextChannel | None = None
    if j_type == "TL" and pred == "No":
        chnl = bot.get_channel(chapter_done_channel_ids["PR"])
    else:
        chnl = bot.get_channel(chapter_done_channel_ids[j_type])

    if not chnl:
        return

    text = f"{role.mention} | {chapter_no} ({j_type}) is done by {ctx.user.mention}!"
    if j_type == "TL" or j_type == "TS":
        text += f" KB: `{kb}`"

    await chnl.send(text)
