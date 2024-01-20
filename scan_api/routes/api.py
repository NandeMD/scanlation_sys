from src.endpoints.series import series
from src.endpoints.chapters import chapters
from src.endpoints.payment_periods import payperiods
from fastapi import APIRouter

router = APIRouter()

router.include_router(series.router)
router.include_router(chapters.router)
router.include_router(payperiods.router)
