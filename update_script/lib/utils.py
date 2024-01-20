from lib.highlighter import print_time
from time import perf_counter
from requests import get
from orjson import loads
from lib.SettingsParser import match_manga_settings
from re import findall


def timer(func):
    def wrap(*args, **kwargs):
        start = perf_counter()
        result = func(*args, **kwargs)
        end = perf_counter()

        print_time(end-start)
        return result
    return wrap


@timer
def get_api_data(url: str) -> dict:
    with get(url) as response:
        data = loads(response.text)
    return data


@timer
def match_series(series):
    for serie in series:
        match_manga_settings(serie)
    

def get_only_chapter_number(text: str):
    integers = findall(r"\d+", text)
    dot_floats = findall(r"\d+\.\d+", text)
    comma_floats = findall(r"\d+\,\d+", text)
    
    integers = [float(integer) for integer in integers]
    dot_floats = [float(df) for df in dot_floats]
    comma_floats = [float(cf.replace(",", ".")) for cf in comma_floats]
    
    all_nums = [*integers, *dot_floats, *comma_floats]
    
    return str(max(all_nums))