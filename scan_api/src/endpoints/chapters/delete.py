from fastapi import APIRouter
from chs.main import ChapterEngine
from chs.models import DeleteChapterResponse, DeleteAllChaptersResponse


router = APIRouter(
    prefix="/delete",
    tags=["Chapters/delete"],
    responses={404: {"description": "Not found"}},
)

data_engine = ChapterEngine()


@router.delete("/{chapter_id}", response_model=DeleteChapterResponse)
async def delete_chapter(chapter_id: int):
    try:
        data_engine.connect()
        data_engine.delete_row(data_engine.chapters, chapter_id)
        data_engine.disconnect()

        return {
            "msg": "Chapter successfully deleted!",
            "id": chapter_id
        }
    except Exception as e:
        print(e)
        

@router.delete("/", response_model=DeleteAllChaptersResponse)
async def delete_all_chapters():
    try:
        data_engine.connect()
        data_engine.delete_all(data_engine.chapters)
        data_engine.disconnect()

        return {
            "msg": "All chapters successfully deleted!",
        }
    except Exception as e:
        print(e)
