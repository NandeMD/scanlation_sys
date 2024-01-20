from fastapi import APIRouter, HTTPException
from chs.main import ChapterEngine
from chs.models import ChapterResponse, OrderedChaptersResponse, FilteredChapterResponse, SingleChapterResponse, PeriodChaptersResponse


router = APIRouter(
    prefix="/get",
    tags=["Chapters/get"],
    responses={404: {"description": "Not found"}},
)

data_engine = ChapterEngine()


@router.get("/", response_model=ChapterResponse)
async def send_all_chapters(count: int = 15000):
    data_engine.connect()
    all_series = data_engine.select_many(data_engine.chapters, count)
    data_engine.disconnect()

    return {"chapters": all_series}


@router.get("/last-period-chapters", response_model=PeriodChaptersResponse)
async def send_monthly_chapters():
    data_engine.connect()
    last_period = data_engine.select_all(data_engine.pay_periods)
    data_engine.disconnect()
    
    if len(last_period) == 0:
        return {
            "period_id": 0,
            "period_creator_id": 0,
            "period_creator_name": "",
            "period_created_at": 0,
            "period_closer_id": 0,
            "period_closer_name": "",
            "period_closed_at": 0,
            "chapters": []
    }
    
    last_period = last_period[-1]
    
    data_engine.connect()
    chapters = data_engine.select_last_period_chapters(last_period[3])
    data_engine.disconnect()
    
    return {
        "period_id": last_period[0],
        "period_creator_id": last_period[1],
        "period_creator_name": last_period[2],
        "period_created_at": last_period[3],
        "period_closer_id": last_period[4],
        "period_closer_name": last_period[5],
        "period_closed_at": last_period[6],
        "chapters": chapters
    }
    

@router.get("/send-period-chapters/{period_id}", response_model=PeriodChaptersResponse)
async def select_chapters_by_period(period_id: int):
    data_engine.connect()
    period = data_engine.select_by_id(data_engine.pay_periods, period_id)
    data_engine.disconnect()
    
    if len(period) == 0:
        return {404: {"description": "Period not found!"}}
    
    period = period[0]
    
    data_engine.connect()
    chapters = data_engine.select_chapters_by_period(period[3], period[6])
    data_engine.disconnect()
    
    return {
        "period_id": period[0],
        "period_creator_id": period[1],
        "period_creator_name": period[2],
        "period_created_at": period[3],
        "period_closer_id": period[4],
        "period_closer_name": period[5],
        "period_closed_at": period[6],
        "chapters": chapters
    }


@router.get("/{chapter_id}", response_model=SingleChapterResponse)
async def send_chapter_by_id(chapter_id: int):
    data_engine.connect()
    serie = data_engine.select_by_id(data_engine.chapters, chapter_id)
    data_engine.disconnect()
    
    if len(serie) == 0:
        raise HTTPException(status_code=404, detail="Chapter not found!", headers={"short_code": "chnf"})
    
    return {"chapter": serie[0]}


@router.get("/order-by/", response_model=OrderedChaptersResponse)
async def order_by(param: str, mode: str = "asc", count: int = 1500):
    data_engine.connect()
    ordered = data_engine.order_by_many(param.casefold(), mode.casefold(), "chapters", count)
    data_engine.disconnect()

    return {
        "parameter": param,
        "mode": mode,
        "results": ordered
    }
    

@router.get("/filter-by/", response_model=FilteredChapterResponse)
async def filter_by(params: str, count: int = 1500):
    data_engine.connect()
    filtered = data_engine.filter_by_many(params, "chapters", count)
    data_engine.disconnect()

    return {
        "params": params,
        "results": filtered
    }


@router.get("/between-dates/")
async def between_dates(lower_bound: int, upper_bound: int):
    data_engine.connect()
    filtered = data_engine.between_2_dates(lower_bound, upper_bound)
    data_engine.disconnect()

    return {
        "params": f"lower_bound={lower_bound}&upper_bound={upper_bound}",
        "results": filtered
    }
