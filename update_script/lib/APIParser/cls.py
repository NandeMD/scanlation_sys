from dataclasses import dataclass
from typing import Optional
from ..SettingsParser.Settings import BaseSetting


@dataclass
class Manga:
    id: Optional[int]
    name: Optional[str]
    image_url: Optional[str]
    source_url: Optional[str]
    base_url: Optional[str]
    source_chap: Optional[float]
    base_chap: Optional[float]
    waiting_pr: Optional[float]
    pred: Optional[float]
    cleaned: Optional[float]
    completed: Optional[float]
    role_id: Optional[int]
    channel_id: Optional[int]
    discord_last_sent: Optional[float]
    last_chapter_url: Optional[str]
    main_category: Optional[int]
    current_category: Optional[int]
    tl: Optional[int]
    pr: Optional[int]
    clnr: Optional[int]
    tser: Optional[int]
    qcer: Optional[int]
    last_qced: Optional[float]
    drive_url: Optional[str]
    time2: Optional[str]
    time1: Optional[str]
    time_tl: Optional[str]
    time_pr: Optional[str]
    time_cln: Optional[str]
    time_ts: Optional[str]
    time_qc: Optional[str]
    setting: Optional[BaseSetting]

    def __init__(self, serie: dict) -> None:
        self.__dict__ = serie
