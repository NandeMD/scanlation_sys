from .Settings import SETTINGS


def match_manga_settings(manga):
    url = manga.ing_url

    for setting in SETTINGS:
        for short in setting.shorts:
            if short in url:
                manga.setting = setting
                return
