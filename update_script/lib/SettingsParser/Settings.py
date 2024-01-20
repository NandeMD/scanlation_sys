from dataclasses import dataclass
from .funcs import *
from typing import List, Callable, Tuple, Type


@dataclass
class BaseSetting:
    shorts: List[str]
    xpath_chapter: List[str]
    xpath_url: List[str]
    func: Callable[[str, str, str], Tuple[str, str]]
    base: get_your_own_chap


# Some example settings
@dataclass
class MangareaderTheme(BaseSetting):
    shorts = ["asura"]
    xpath_chapter = ["//div[@class='inepcx']/a/span[@class='epcur epcurlast']/text()"]
    xpath_url = ["//div[@class='lastend']/div[@class='inepcx']/a[contains(@href, '.')]/@href"]
    func = default


@dataclass
class Mangadex(BaseSetting):
    shorts = ["mangadex"]
    xpath_chapter = [""]
    xpath_url = [""]
    func = mangadex


SETTINGS: List[Type[BaseSetting]] = [
    MangareaderTheme,
    Mangadex
]
