from json import loads
from sys import argv

with open("config.json") as cf:
    conf = loads(cf.read())


def get_api_ip() -> str:
    if "debug" in argv:
        return conf["TEST_API_IP"]
    else:
        return conf["API_IP"]


def get_secret_key() -> str:
    return conf["SECRET"]


def get_timezone() -> str:
    return conf["T_ZONE"]


def get_locale() -> str:
    return conf["LOCALE"]
