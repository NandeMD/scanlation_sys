from fastapi import APIRouter
from . import delete, get, post, update

router = APIRouter(
    prefix="/chapters",
    tags=["Chapters"],
    responses={404: {"description": "Not found"}},
)

router.include_router(get.router)
router.include_router(post.router)
router.include_router(update.router)
router.include_router(delete.router)
