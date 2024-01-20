from fastapi import APIRouter, HTTPException
from chs.main import ChapterEngine
from chs.models import PayPeriods, PayPeriodUpdateResponse


router = APIRouter(
    prefix="/update",
    tags=["PaymentPeriods/update"],
    responses={404: {"description": "Not found"}},
)

data_engine = ChapterEngine()


@router.patch("/", response_model=PayPeriodUpdateResponse)
async def update_a_chapter(periods: PayPeriods):
    if not periods.id:
        return HTTPException(status_code=400, detail="You have to specify an ID!", headers={"short_code": "nif"})
    
    data_engine.connect()
    data_engine.update_columns(periods, data_engine.pay_periods)
    data_engine.disconnect()

    return {"msg": "Update successful!"}
