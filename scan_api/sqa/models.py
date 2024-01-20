from pydantic import BaseModel
from typing import Optional, List


class Options(BaseModel):
    id: int
    name: Optional[str] = None
    image_url: Optional[str] = None
    source_url: Optional[str] = None
    base_url: Optional[str] = None
    source_chap: Optional[str] = None
    base_chap: Optional[str] = None
    waiting_pr: Optional[str] = None
    pred: Optional[str] = None
    last_readed: Optional[str] = None
    cleaned: Optional[str] = None
    completed: Optional[str] = None
    role_id: Optional[int] = None
    channel_id: Optional[int] = None
    discord_last_sent: Optional[str] = None
    last_chapter_url: Optional[str] = None
    main_category: Optional[int] = None
    tl: Optional[int] = None
    pr: Optional[int] = None
    lr: Optional[int] = None
    clnr: Optional[int] = None
    tser: Optional[int] = None
    qcer: Optional[int] = None
    last_qced: Optional[str] = None
    drive_url: Optional[str] = None
    time2: Optional[str] = None
    time1: Optional[str] = None
    time_tl: Optional[str] = None
    time_pr: Optional[str] = None
    time_lr: Optional[str] = None
    time_cln: Optional[str] = None
    time_ts: Optional[str] = None
    time_qc: Optional[str] = None
    
class Ser(BaseModel):
    id: int
    name: Optional[str] = None
    image_url: Optional[str] = None
    source_url: Optional[str] = None
    base_url: Optional[str] = None
    source_chap: Optional[float] = None
    base_chap: Optional[float] = None
    waiting_pr: Optional[float] = None
    pred: Optional[float] = None
    last_readed: Optional[float] = None
    cleaned: Optional[float] = None
    completed: Optional[float] = None
    role_id: Optional[int] = None
    channel_id: Optional[int] = None
    discord_last_sent: Optional[float] = None
    last_chapter_url: Optional[str] = None
    main_category: Optional[int] = None
    tl: Optional[int] = None
    pr: Optional[int] = None
    lr: Optional[int] = None
    clnr: Optional[int] = None
    tser: Optional[int] = None
    qcer: Optional[int] = None
    last_qced: Optional[float] = None
    drive_url: Optional[str] = None
    time2: Optional[str] = None
    time1: Optional[str] = None
    time_tl: Optional[str] = None
    time_pr: Optional[str] = None
    time_lr: Optional[str] = None
    time_cln: Optional[str] = None
    time_ts: Optional[str] = None
    time_qc: Optional[str] = None
    

class SeriesResponse(BaseModel):
    series: List[Ser]
    

class OrderedSeriesResponse(BaseModel):
    parameter: str
    mode: str
    results: List[Ser]
    
    
class FilteredSeriesResponse(BaseModel):
    params: str
    results: List[Options]


class URLs(BaseModel):
    name: str
    image_url: str
    source_url: str
    base_url: str
    source_chap: float
    base_chap: float
    role_id: int
    channel_id: int
    last_chapter_url: str
    main_category: int
    tl: int
    pr: int
    lr: int
    clnr: int
    tser: int
    qcer: int
    

class DeleteMangaResponse(BaseModel):
    msg: str = "Manga successfully deleted!"
    id: int
    
    
class NewMangaUrlsBase(BaseModel):
    source: str
    base: str

    
class NewMangaResponse(BaseModel):
    msg: str = "New manga successfully created!"
    urls: NewMangaUrlsBase
    
    
class MangaUpdateResponse(BaseModel):
    msg: str = "Update successful!"
