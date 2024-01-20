from fastapi import APIRouter
from sqa.main import DataEngine
from sqa.models import SeriesResponse, OrderedSeriesResponse

router = APIRouter(
    prefix="/get",
    tags=["Series/get"],
    responses={404: {"description": "Not found"}},
)

data_engine = DataEngine()


@router.get("/", response_model=SeriesResponse)
async def send_all_series():
    data_engine.connect()
    all_series = data_engine.select_all()
    data_engine.disconnect()

    return {"series": all_series}


@router.get("/order-by/", response_model=OrderedSeriesResponse)
async def order_by(param: str, mode: str = "asc"):
    data_engine.connect()
    ordered = data_engine.order_by(param.casefold(), mode.casefold())
    data_engine.disconnect()

    return {
        "parameter": param,
        "mode": mode,
        "results": ordered
    }


@router.get("/filter-by/")
async def filnter_by(params: str):
    data_engine.connect()
    filtered = data_engine.filter_by(params)
    data_engine.disconnect()

    return {
        "params": params,
        "results": filtered
    }


@router.get("/sts-homepage")
async def sts_homepage():
    data_engine.connect()
    series = data_engine.get_homepage()
    data_engine.disconnect()

    return series


@router.get("/sts-personnel-page")
async def sts_personnel_page():
    data_engine.connect()
    series = data_engine.get_personnel_page()
    data_engine.disconnect()

    return series
