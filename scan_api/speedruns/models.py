from pydantic import BaseModel
from typing import Optional, List


class SpeedrunSeries(BaseModel):
    id: Optional[int]
    serie_id: Optional[int]
    serie_name: Optional[str]
    creator_id: Optional[int]
    creator_name: Optional[str]
    created_at: Optional[int]
    is_manga: Optional[int]
    duration: Optional[int]
    fee: Optional[float]


class SpeedrunWorks(BaseModel):
    id: Optional[int]
    creator_id: Optional[int]
    creator_name: Optional[str]
    created_at: Optional[int]
    work_type: Optional[int]
    sr_id: Optional[int]


class Work(BaseModel):
    class Config:
        orm_mode = True
    id: int
    creator_id: int
    creator_name: str
    created_at: int
    work_type: int
    sr_id: int


class SR(BaseModel):
    class Config:
        orm_mode = True
    id: int
    serie_id: int
    serie_name: str
    creator_id: int
    creator_name: str
    created_at: int
    is_manga: int
    duration: int
    fee: float
    works: list[Work]


class AllSpeedrunsResponse(BaseModel):
    all_speedruns: list[SR]


class ActiveSpeedrunsResponse(BaseModel):
    activez_speedruns: list[SR]


class AllSpeedrunSeriesResponse(BaseModel):
    all_srs: list[SpeedrunSeries]


class AllSpeedrunWorksResponse(BaseModel):
    all_wrks: list[SpeedrunWorks]
