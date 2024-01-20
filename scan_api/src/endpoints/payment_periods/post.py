from fastapi import APIRouter, HTTPException
from chs.models import NewPeriod, NewPeriodResponse
from chs.main import ChapterEngine


router = APIRouter(
    prefix="/new",
    tags=["PaymentPeriods/post"],
    responses={404: {"description": "Not found"}},
)

data_engine = ChapterEngine()


@router.post("/", response_model=NewPeriodResponse)
async def create_new_period(period: NewPeriod):
    try:        
        data_engine.connect()
        data_engine.insert_pay_period(
            period.creator_id,
            period.creator_name,
            period.created_at
        )
        data_engine.disconnect()

        return {
            "msg": "New payment period successfully created!",
            "creator_name": period.creator_name,
            "creator_id": period.creator_id,
            "created_at": {"value": period.created_at, "type": "arrow timestamp"}
        }
    except IndexError:
        raise HTTPException(status_code=400, detail="Index Error! ZINK", headers={"short_code": "wurl"})
    except ConnectionError:
        raise HTTPException(status_code=400, detail="Connection error!", headers={"short_code": "con"})
