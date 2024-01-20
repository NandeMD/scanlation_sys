from fastapi import APIRouter, HTTPException
from chs.main import ChapterEngine
from chs.models import Chapters, ChapterUpdateResponse


router = APIRouter(
    prefix="/update",
    tags=["Chapters/update"],
    responses={404: {"description": "Not found"}},
)

data_engine = ChapterEngine()


@router.patch("/", response_model=ChapterUpdateResponse)
async def update_a_chapter(chapters: Chapters):
    if not chapters.id:
        return HTTPException(status_code=400, detail="You have to specify an ID!", headers={"short_code": "nif"})
    
    data_engine.connect()
    data_engine.update_columns(chapters, data_engine.chapters)
    data_engine.disconnect()

    return {"msg": "Update successful!"}
