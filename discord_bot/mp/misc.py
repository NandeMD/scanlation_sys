from discord import Bot
from .colors import Colors as Clrs
from discord.errors import (
    ExtensionAlreadyLoaded,
    ExtensionNotFound,
    ExtensionFailed,
    NoEntryPointError,
    ExtensionNotLoaded
)
from os import listdir
from traceback import format_exc
from typing import List


def get_all_cogs():
    cogs = ["cogs." + cog.replace("\n", "").replace(".py", "") for cog in listdir("cogs")]
    if "cogs.__pycache__" in cogs:
        cogs.remove("cogs.__pycache__")

    return cogs


def load_cog(cog: str, bot: Bot) -> bool:
    try:
        bot.load_extension(cog)
        print(f"{Clrs.yellow}[INIT]\t{Clrs.cyan}{cog}{Clrs.reset} loaded!")
        return True
    except ExtensionNotFound:
        print(f"{Clrs.red}[ERROR]\t{Clrs.cyan}{cog}{Clrs.purple} not found.{Clrs.reset}")
        return False
    except ExtensionAlreadyLoaded:
        print(f"{Clrs.red}[ERROR]\t{Clrs.cyan}{cog}{Clrs.purple} already loaded.{Clrs.reset}")
        return False
    except NoEntryPointError:
        print(f"{Clrs.red}[ERROR]\t{Clrs.cyan}{cog}{Clrs.purple} does not have a setup function.{Clrs.reset}")
        return False
    except ExtensionFailed:
        print(f"{Clrs.red}[ERROR]\t{Clrs.cyan}{cog}{Clrs.purple} has a Python error..{Clrs.reset}")
        print(format_exc())
        return False


def load_cogs(cogs: list, bot: Bot):
    print(f"{Clrs.yellow}[INIT]\t{Clrs.reset}Cogs loading...")

    for cog in cogs:
        load_cog(cog, bot)

    print(f"{Clrs.yellow}[INIT]\t{Clrs.reset}Cogs loaded!")


def load_all_cogs(bot: Bot):
    load_cogs(get_all_cogs(), bot)


def unload_cog(cog: str, bot: Bot) -> bool:
    try:
        bot.unload_extension(cog)
        print(f"{Clrs.yellow}[INFO]\t{Clrs.cyan}{cog}{Clrs.reset} unloaded!")
        return True
    except ExtensionNotFound:
        print(f"{Clrs.red}[ERROR]\t{Clrs.cyan}{cog}{Clrs.purple} not found.{Clrs.reset}")
        return False
    except ExtensionNotLoaded:
        print(f"{Clrs.red}[ERROR]\t{Clrs.cyan}{cog}{Clrs.purple} already not loaded.{Clrs.reset}")
        return False


def unload_cogs(cogs: list, bot: Bot):
    print(f"{Clrs.yellow}[INFO]\t{Clrs.reset}Cogs unloading...")

    for cog in cogs:
        unload_cog(cog, bot)

    print(f"{Clrs.yellow}[INFO]\t{Clrs.reset}Cogs unloaded!")


def unload_all_cogs(bot: Bot):
    unload_cogs(get_all_cogs(), bot)
    
    
def create_member_work_field(text: str) -> List[str]:
    fields = []

    if len(text) > 824:
        splitted = text.split("\n")
        field = []

        for part in splitted:
            if len("\n".join(field)) + len("\n") + len(part) < 1024:
                field.append(part)
            else:
                fields.append("\n".join(field))
                field.clear()
                field.append(part)
        if field:
            fields.append("\n".join(field))
    else:
        fields.append(text)

    return fields


def find_serie_by_channel(series, channel_id) -> dict | int:
    for serie in series:
        if serie["channel_id"] == channel_id:
            return serie
    return 0


def divide_list_into_max_fields(lst: list):
    for i in range(0, len(lst), 25):
        yield lst[i:i + 25]
        
        
def create_channel_mention(channel_id: int) -> str:
    if len(str(channel_id)) > 1:
        return f"<#{channel_id}>"
    else:
        if channel_id == 0:
            return "None"
        elif channel_id == 1:
            return "Rookie"
        elif channel_id == 2:
            return "Manga"
        elif channel_id == 3:
            return "Season Finale"
        elif channel_id == 4:
            return "Hiatus"
        

def create_staff_role_mention(role_id: int, rtype: str) -> str:
    if len(str(role_id)) > 1:
        return f"<@{role_id}>"
    else:
        if role_id == 0:
            return "None"
        elif role_id == 1:
            return "Rookie"
        elif role_id == 2:
            return "Manga"
        elif role_id == 3:
            return "Season Finale"
        elif role_id == 4:
            return "Hiatus"


def ext_from_filename(file_name: str) -> str:
    return file_name.split(".")[-1]


def find_serie_by_id(series, serie_id) -> dict | int:
    for serie in series:
        if serie["id"] == serie_id:
            return serie
    return 0
