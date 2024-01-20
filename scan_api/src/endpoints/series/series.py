from fastapi import APIRouter
from sqa.main import DataEngine
from src.endpoints.series import get, post, update, delete

router = APIRouter(
    prefix="/series",
    tags=["Series"],
    responses={404: {"description": "Not found"}},
)

data_engine = DataEngine()

router.include_router(get.router)
router.include_router(post.router)
router.include_router(update.router)
router.include_router(delete.router)
