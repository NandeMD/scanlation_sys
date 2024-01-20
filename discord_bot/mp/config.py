from sys import argv
from json import loads

with open("mp/config.json") as configfile:
    config = loads(configfile.read())


def get_api_ip() -> str:
    if "debug" in argv:
        return config["debug_api_ip"]
    else:
        return config["deployment_api_ip"]


def get_token_env_var() -> str:
    if "debug" in argv:
        return config["test_token"]
    else:
        return config["token"]


def get_timezone() -> str:
    return config["T_ZONE"]


def get_locale() -> str:
    return config["LOCALE"]


def bot_id() -> int:
    return config["BOT_ID"]


def get_any(key: str):
    return config[key]


def get_warn_hours() -> tuple[int, int]:
    return config["FIRST_WARN_HOUR"], config["SECOND_WARN_HOUR"]


def get_categories() -> dict:
    return config["CATEGORIES"]
