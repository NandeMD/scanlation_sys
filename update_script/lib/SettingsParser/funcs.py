from lxml import html
from requests import get as rget, post as rpost
from re import search as research
from typing import Tuple
from orjson import loads as orloads
from cloudscraper import create_scraper
from fspy import FlareSolverr
from configparser import ConfigParser

html_parser = html.HTMLParser(collect_ids=False)

config = ConfigParser()
config.read('config.ini')
config = config['DEFAULT']

FLARE_SOLVERR_SESSION_NAME = config["FlareSolverSessionName"]


def __fetch_url(url) -> str:
    scraper = create_scraper()
    with scraper.get(url) as response:
        site = response.text

    del scraper
    del response

    return site


def get_your_own_chap(url: str) -> str:
    # Your websites xpath expression but you can do whatever you want
    xp = ""
    tree = html.fromstring(__fetch_url(url), parser=html_parser)

    chapters = tree.xpath(xp)
    ch = chapters[0]

    del xp
    del tree
    del chapters

    return ch


def __fetch_with_solver(url) -> str:
    solver = FlareSolverr()
    if FLARE_SOLVERR_SESSION_NAME not in solver.sessions:
        solver.create_session(FLARE_SOLVERR_SESSION_NAME)

    response = solver.request_get(url, FLARE_SOLVERR_SESSION_NAME, max_timeout=10000)

    return response.solution.response


def default(url: str, xc: str, xu: str) -> Tuple[str, str]:
    tree = html.fromstring(__fetch_url(url), parser=html_parser)
    chapters = tree.xpath(xc)
    urls = tree.xpath(xu)

    ch = chapters[0]
    uri = urls[0]

    del tree
    del chapters
    del urls

    return ch, uri


def default_with_solver(url: str, xc: str, xu: str) -> Tuple[str, str]:
    tree = html.fromstring(__fetch_with_solver(url), parser=html_parser)
    chapters = tree.xpath(xc)
    urls = tree.xpath(xu)

    ch = chapters[0]
    uri = urls[0]

    del tree
    del chapters
    del urls

    return ch, uri


def ajaxers(url: str, xc: str, xu: str) -> Tuple[str, str]:
    ajax_url = url + "ajax/chapters/"

    with rpost(ajax_url) as response:
        data = response.text

    tree = html.fromstring(data, parser=html_parser)

    chapters = tree.xpath(xc)
    urls = tree.xpath(xu)

    ch = chapters[0]
    uri = urls[0]

    del tree
    del chapters
    del urls

    return ch, uri


def __get_mangadex_id(url: str) -> str:
    return url.split("/")[-2]


def mangadex(url: str, xc: str, xu: str):
    params = {
        "manga": __get_mangadex_id(url),
        "translatedLanguage[]": ["en"],
        "order[chapter]": "desc"
    }
    with rget("https://api.mangadex.org/chapter", params=params) as response:
        data = orloads(response.text)["data"]

    last_ch_obj = data[0]
    last_ch = last_ch_obj["attributes"]["chapter"]
    last_url = f"https://mangadex.org/chapter/{last_ch_obj['id']}"

    del data
    del params
    del response

    return last_ch, last_url
