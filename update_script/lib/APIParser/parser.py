from .cls import Manga
from typing import List
from ..utils import timer


@timer
def parse_api_json(data: dict) -> List[Manga]:
    mangas = []
    series = data["series"]
    for s in series:
        mangas.append(
            Manga(s)
        )

    return mangas
