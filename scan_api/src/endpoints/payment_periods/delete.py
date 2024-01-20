from fastapi import APIRouter
from chs.main import ChapterEngine
from chs.models import DeletePayperiodResponse, DeleteAllPayperiodsResponse


router = APIRouter(
    prefix="/delete",
    tags=["PaymentPeriods/delete"],
    responses={404: {"description": "Not found"}},
)

data_engine = ChapterEngine()


@router.delete("/{period_id}", response_model=DeletePayperiodResponse)
async def delete_chapter(period_id: int):
    try:
        data_engine.connect()
        data_engine.delete_row(data_engine.pay_periods, period_id)
        data_engine.disconnect()

        return {
            "msg": "Payment period successfully deleted!",
            "id": period_id
        }
    except Exception as e:
        print(e)
        

@router.delete("/", response_model=DeleteAllPayperiodsResponse)
async def delete_all_periods():
    try:
        data_engine.connect()
        data_engine.delete_all(data_engine.pay_periods)
        data_engine.disconnect()

        return {
            "msg": "All payment periods successfully deleted!",
        }
    except Exception as e:
        print(e)
