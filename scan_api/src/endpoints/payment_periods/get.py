from fastapi import APIRouter
from chs.main import ChapterEngine
from chs.models import PayPeriodsResponse, SinglePayPeriodResponse, OrderedPayPeriodsResponse, FilteredPayPeriodsResponse


router = APIRouter(
    prefix="/get",
    tags=["PaymentPeriods/get"],
    responses={404: {"description": "Not found"}},
)

data_engine = ChapterEngine()


@router.get("/", response_model=PayPeriodsResponse)
async def send_all_payment_periods():
    data_engine.connect()
    all_periods = data_engine.select_all(data_engine.pay_periods)
    data_engine.disconnect()

    return {"periods": all_periods}


@router.get("/last-period", response_model=SinglePayPeriodResponse)
async def send_last_period():
    data_engine.connect()
    last_period = data_engine.select_all(data_engine.pay_periods)
    data_engine.disconnect()
    
    if len(last_period) == 0:
        return {404: {"description": "No payment period found!"}}
    
    last_period = last_period[-1]
    
    return {"pay_period": last_period}


@router.get("/{period_id}", response_model=SinglePayPeriodResponse)
async def send_chapter_by_id(period_id: int):
    data_engine.connect()
    period = data_engine.select_by_id(data_engine.pay_periods, period_id)[0]
    data_engine.disconnect()
    
    return {"pay_period": period}


@router.get("/{timestamp}", response_model=SinglePayPeriodResponse)
async def send_chapter_by_timestamp(timestamp: float):
    data_engine.connect()
    period = data_engine.select_period_by_timestamp(timestamp)
    data_engine.disconnect()
    
    return {"pay_period": period}


@router.get("/order-by/", response_model=OrderedPayPeriodsResponse)
async def order_by(param: str, mode: str = "asc"):
    data_engine.connect()
    ordered = data_engine.order_by_(param.casefold(), mode.casefold(), "pay_periods")
    data_engine.disconnect()

    return {
        "parameter": param,
        "mode": mode,
        "results": ordered
    }
    

@router.get("/filter-by/", response_model=FilteredPayPeriodsResponse)
async def filter_by(params: str):
    data_engine.connect()
    filtered = data_engine.filter_by(params, "pay_periods")
    data_engine.disconnect()

    return {
        "params": params,
        "results": filtered
    }
