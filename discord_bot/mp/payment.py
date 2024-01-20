from typing import Optional
from dataclasses import dataclass
from xlsxwriter import Workbook
from xlsxwriter.worksheet import Worksheet, Format

import discord

from .config import get_any

PR_FEE = get_any("PR_FEE")
QC_FEE = get_any("QC_FEE")
POOP_URL = get_any("POOP_URL")


@dataclass
class ChapterAndFees:
    chapter: dict
    tl_fee: Optional[float]
    pr_fee: Optional[float]
    cln_fee: Optional[float]
    ts_fee: Optional[float]
    qc_fee: Optional[float]

    @property
    def check_if_any_fee_exist(self) -> bool:
        return bool(self.tl_fee) or bool(self.pr_fee) or bool(self.cln_fee) or bool(self.ts_fee) or bool(self.qc_fee)


# Changing here is recommended
def calculate_pay(size: int, pred: int):
    base = 0
    if size < 2500:
        base = 0.2
    elif size < 3500:
        base = 0.25
    elif size < 4500:
        base = 0.3
    elif size < 5500:
        base = 0.35
    elif size < 6500:
        base = 0.40
    elif size < 7500:
        base = 0.45
    elif size < 8500:
        base = 0.50
    elif size < 9500:
        base = 0.55
    elif size < 10500:
        base = 0.60
    elif size >= 10500:
        base = 0.65

    if not pred:
        return round(base + 0.15, 2)
    else:
        return round(base, 2)


def extract_all_personnel_ids_chapters(chdata: list[ChapterAndFees]) -> set:
    raw_ids = set()
    for cf in chdata:
        if cf.tl_fee:
            raw_ids.add(cf.chapter["tl_id"])
        if cf.pr_fee:
            raw_ids.add(cf.chapter["pr_id"])
        if cf.cln_fee:
            raw_ids.add(cf.chapter["clnr_id"])
        if cf.ts_fee:
            raw_ids.add(cf.chapter["ts_id"])
        if cf.qc_fee:
            raw_ids.add(cf.chapter["qc_id"])

    return raw_ids


def match_personnel_ids_with_names_and_add_worksheet(ids: set, bot: discord.Bot, book: Workbook) -> dict[int, tuple[str, Worksheet]]:
    members = list(bot.get_all_members())
    member_dict = {}
    for i in ids:
        for m in members:
            if i == m.id:
                member_dict[i] = (m.name, book.add_worksheet(m.name))
                break
    return member_dict


def prepare_sheet(sheet: Worksheet, merge_format: Format):
    sheet.set_column(0, 0, 30)
    sheet.set_column(3, 3, 30)
    sheet.set_column(6, 6, 30)
    sheet.set_column(8, 8, 30)
    sheet.set_column(11, 12, 17)

    sheet.write("A1", "PERSONAL MONTHLY FEES")
    sheet.merge_range("A1:J1", "PERSONAL MONTHLY FEES", merge_format)
    sheet.write("A3", "UNCONTROLLED TL / TS")
    sheet.write("B3", "KB")
    sheet.write("C3", "FEE")
    sheet.write("D3", "CONTROLLED TL / TS")
    sheet.write("E3", "KB")
    sheet.write("F3", "FEE")
    sheet.write("G3", "CLEAN / PR / QC")
    sheet.write("H3", "FEE")
    sheet.write("I3", "EXTRAS")
    sheet.write("J3", "FEE")
    sheet.write("L3", "TOTAL FEE")
    sheet.write("M3", "TOTAL CHAPTERS WORKED ON")
    sheet.write_formula("L4", "=SUM(C4:C500, F4:F500, H4:H500, J4:J500)")
    sheet.write_formula("M4", "=SUM(COUNTA(C4:C500), COUNTA(F4:F500), COUNTA(H4:H500), COUNTA(J4:J500))")


def split_all_work(data: list[ChapterAndFees], personnel_id, series: list, clean_fees: dict, lb: int, ub: int, extras = None) -> list[list[list]]:
    uwu = [[], [], [], []]
    for cf in data:
        if cf.chapter["tl_id"] == personnel_id and cf.chapter["should_pred"] == 0 and check_if_work_is_in_between_tstamps(cf.chapter, "tl_at", lb, ub):
            uwu[0].append([f"{cf.chapter['serie_name']} {cf.chapter['chapter_num']} Translated", cf.chapter["tl_bytes"]])
        elif cf.chapter["tl_id"] == personnel_id and cf.chapter["should_pred"] == 1 and check_if_work_is_in_between_tstamps(cf.chapter, "tl_at", lb, ub):
            uwu[1].append([f"{cf.chapter['serie_name']} {cf.chapter['chapter_num']} Translated", cf.chapter["tl_bytes"]])

        if cf.chapter["pr_id"] == personnel_id and check_if_work_is_in_between_tstamps(cf.chapter, "pr_at", lb, ub):
            uwu[2].append([f"{cf.chapter['serie_name']} {cf.chapter['chapter_num']} Proofread", PR_FEE])

        if cf.chapter["clnr_id"] == personnel_id and check_if_work_is_in_between_tstamps(cf.chapter, "clnr_at", lb, ub):
            fee = None
            for s in series:
                if s["id"] == cf.chapter["serie_id"]:
                    fee = clean_fees[str(s["role_id"])]
            uwu[2].append([f"{cf.chapter['serie_name']} {cf.chapter['chapter_num']} Cleaned", fee])

        if cf.chapter["ts_id"] == personnel_id and cf.chapter["should_qced"] == 0 and check_if_work_is_in_between_tstamps(cf.chapter, "ts_at", lb, ub):
            uwu[0].append([f"{cf.chapter['serie_name']} {cf.chapter['chapter_num']} Typeset", cf.chapter["tl_bytes"]])
        elif cf.chapter["ts_id"] == personnel_id and cf.chapter["should_qced"] == 1 and check_if_work_is_in_between_tstamps(cf.chapter, "ts_at", lb, ub):
            uwu[1].append([f"{cf.chapter['serie_name']} {cf.chapter['chapter_num']} Typeset", cf.chapter["tl_bytes"]])

        if cf.chapter["qc_id"] == personnel_id and check_if_work_is_in_between_tstamps(cf.chapter, "qc_at", lb, ub):
            uwu[2].append([f"{cf.chapter['serie_name']} {cf.chapter['chapter_num']} Quality Checked", QC_FEE])

    return uwu


def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]


def generate_embeds_from_fields(field_list: list[discord.EmbedField], membr: discord.Member | discord.User, j_type: str) -> list[discord.Embed]:
    if len(field_list) == 0:
        return []
    embed_list: list[discord.Embed] = []
    work_count = len(field_list)
    chunks = list(divide_chunks(field_list, 19))

    start_em = discord.Embed(
        title=f"User {membr.name}: {j_type}",
    )
    start_em.set_author(name=membr.name, icon_url=membr.avatar.url if membr.avatar.url else POOP_URL)  # Add a poop image url
    for f in chunks[0]:
        start_em.append_field(f)

    embed_list.append(start_em)

    if len(chunks) > 1:
        for i in range(1, len(chunks)):
            other_em = discord.Embed()
            for f in chunks[i]:
                other_em.append_field(f)
            embed_list.append(other_em)
    embed_list[-1].set_footer(text=f"Worked on: {work_count} chapters")

    return embed_list


# Damn discord api limitations
def split_a_page(uwu: list[discord.Embed]) -> list[discord.Embed] | None:
    total = 0
    if not uwu:
        return None

    for i in range(len(uwu)):
        em = uwu[i]
        total += len(em.title) + len(em.description) + len(em.footer.text) + len(em.author.name)
        for f in em.fields:
            total += len(f.name) + len(f.value)

        if total > 6000:
            new = uwu[i-1:len(uwu)]
            for item in new:
                uwu.remove(item)
            return new

    return None


# noinspection PyChainedComparisons
def check_if_work_is_in_between_tstamps(chapter, field: str, lb, ub) -> bool:
    if chapter[field] >= lb and chapter[field] <= ub:
        return True

    return False

