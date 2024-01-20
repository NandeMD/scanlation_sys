from pydantic import BaseModel
from typing import Optional, List


class Chapters(BaseModel):
    id:             Optional[int]
    serie_id:       Optional[int]
    serie_name:     Optional[str]
    chapter_num:    Optional[float]
    creator_id:     Optional[int]
    creator_name:   Optional[str]
    created_at:     Optional[float]
    
    tl_id:          Optional[int]
    tl_name:        Optional[str]
    tl_at:          Optional[float]
    tl_bytes:       Optional[int]
    should_pred:    Optional[int]
    
    pr_id:      Optional[int]
    pr_name:    Optional[str]
    pr_at:      Optional[float]
    
    clnr_id:    Optional[int]
    clnr_name:  Optional[str]
    clnr_at:    Optional[float]
    
    ts_id:      Optional[int]
    ts_name:    Optional[str]
    ts_at:      Optional[float]
    
    qc_id:          Optional[int]
    qc_name:        Optional[str]
    qc_at:          Optional[float]
    should_qced:    Optional[int]
    
    closer_id:      Optional[int]
    closer_name:    Optional[str]
    closed_at:      Optional[float]
    
    
class NewChapter(BaseModel):
    serie_id: int
    serie_name: str
    chapter_num: float
    creator_id: int
    creator_name: str
    created_at: float
    
    
class ChapterResponse(BaseModel):
    chapters: List[Chapters]
    

class SingleChapterResponse(BaseModel):
    chapter: Chapters
    
    
class PayPeriods(BaseModel):
    id:             Optional[int]
    creator_id:     Optional[int]
    creator_name:   Optional[str]
    created_at:     Optional[float]
    
    closer_id:      Optional[int]
    closer_name:    Optional[str]
    closed_at:  Optional[float]
    
    
class PayPeriodsResponse(BaseModel):
    periods: List[PayPeriods]
    
    
class SinglePayPeriodResponse(BaseModel):
    pay_period: PayPeriods
    
    
class NewPeriod(BaseModel):
    creator_id: int
    creator_name: str
    created_at: float
    
    
class BasePeriodTime(BaseModel):
    value: float
    type: str = "arrow timestamp"
    
    
class NewPeriodResponse(BaseModel):
    msg: str = "New payment period successfully created!"
    creator_name: str
    creator_id: int
    created_at: BasePeriodTime
    

class PeriodChaptersResponse(BaseModel):
    period_id: Optional[int]
    period_creator_id: Optional[int]
    period_creator_name: Optional[str]
    period_created_at: Optional[float]
    period_closer_id: Optional[int]
    period_closer_name: Optional[str]
    period_closed_at: Optional[float]
    chapters: List[Chapters]
    

class NewChapterResponse(BaseModel):
    msg: str = "New chapter successfully created!"
    serie_name: str
    chapter_num: float
    
    
class ChapterUpdateResponse(BaseModel):
    msg: str = "Update successful!"
    

class DeleteChapterResponse(BaseModel):
    msg: str = "Chapter successfully deleted!"
    id: int
    
    
class DeleteAllChaptersResponse(BaseModel):
    msg: str = "All chapters successfully deleted!"
    

class DeletePayperiodResponse(BaseModel):
    msg: str = "Payment period successfully deleted!"
    id: int
    
    
class DeleteAllPayperiodsResponse(BaseModel):
    msg: str = "All payment periods successfully deleted!"


class PayPeriodUpdateResponse(BaseModel):
    msg: str = "Update successful!"
    

class OrderedChaptersResponse(BaseModel):
    parameter: str
    mode: str
    results: List[Chapters]
    

class FilteredChapterResponse(BaseModel):
    params: str
    results: List[Chapters]
    
    
class OrderedPayPeriodsResponse(BaseModel):
    parameter: str
    mode: str
    results: List[PayPeriods]
    

class FilteredPayPeriodsResponse(BaseModel):
    params: str
    results: List[PayPeriods]
