from fastapi import APIRouter
from . import get

# Speedrun endpoints are not implemented yet. I don't have enough time.

router = APIRouter(
    prefix="/speedruns",
    tags=["Speedruns"],
    responses={404: {"description": "Not found"}},
)

router.include_router(get.router)