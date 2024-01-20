from fastapi import APIRouter, HTTPException
from speedruns.main import SpeedrunsEngine
from speedruns.models import (
    AllSpeedrunsResponse,
    AllSpeedrunSeriesResponse,
    AllSpeedrunWorksResponse,
    ActiveSpeedrunsResponse,
    SR
)

from traceback import format_exc


router = APIRouter(
    prefix="/get",
    tags=["Speedruns/get"],
    responses={404: {"description": "Not found"}}
)

data_engine = SpeedrunsEngine()


@router.get("/", response_model=AllSpeedrunsResponse)
async def send_all_series_and_works():
    try:
        data_engine.connect()
        all_data = data_engine.get_all_and_match()
        data_engine.disconnect()
        if not all_data:
            return HTTPException(
                status_code=404,
                detail="No speedrun series/works found."
            )

    except Exception as e:
        return HTTPException(
            status_code=500,
            detail=f"An unknown exception occured while getting all speedruns: {e}",
            headers={"cause": e, "traceback": format_exc()}
        )

    return {"all_speedruns": all_data}


@router.get("/all-sr-series", response_model=AllSpeedrunSeriesResponse)
async def all_sr_series():
    try:
        data_engine.connect()
        sr_series = data_engine.select_all(data_engine.sr_series)
        data_engine.disconnect()
        if not sr_series:
            return HTTPException(
                status_code=404,
                detail="No speedrun series found."
            )
    except Exception as e:
        return HTTPException(
            status_code=500,
            detail=f"An unknown exception occured while getting all speedrun series: {e}",
            headers={"cause": e, "traceback": format_exc()}
        )

    return {"all_srs": sr_series}


@router.get("/all-sr-works/{count}", response_model=AllSpeedrunWorksResponse)
async def all_sr_works(count: int = 1500):
    try:
        data_engine.connect()
        sr_works = data_engine.select_many(data_engine.sr_works, count)
        data_engine.disconnect()
        if not sr_works:
            return HTTPException(
                status_code=404,
                detail="No speedrun works found."
            )
    except Exception as e:
        return HTTPException(
            status_code=500,
            detail=f"An unknown exception occured while getting all speedrun works: {e}",
            headers={"cause": e, "traceback": format_exc()}
        )

    return {"all_wrks": sr_works}


@router.get("/active", response_model=ActiveSpeedrunsResponse)
async def get_active_speedruns():
    try:
        data_engine.connect()
        active_srs = data_engine.get_active_and_match()
        data_engine.disconnect()
        if not active_srs:
            return HTTPException(
                status_code=404,
                detail="No active speedruns found."
            )
    except Exception as e:
        return HTTPException(
            status_code=500,
            detail=f"An unknown exception occured while getting all active speedruns: {e}",
            headers={"cause": e, "traceback": format_exc()}
        )

    return {"active_speedruns": active_srs}


@router.get("/single/{sr_id}", response_model=SR)
async def get_single_sr(sr_id: int):
    try:
        data_engine.connect()
        sr = data_engine.get_single_sr_from_id(sr_id)
        data_engine.disconnect()
        if not sr:
            return HTTPException(
                status_code=404,
                detail=f"No active speedrun found id == {sr_id}"
            )
    except Exception as e:
        return HTTPException(
            status_code=500,
            detail=f"An unknown exception occured while getting speedrun id = {sr_id}: {e}",
            headers={"cause": e, "traceback": format_exc()}
        )

    return sr
