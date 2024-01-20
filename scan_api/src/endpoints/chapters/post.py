from fastapi import APIRouter, HTTPException
from chs.models import NewChapter, NewChapterResponse
from chs.main import ChapterEngine


router = APIRouter(
    prefix="/new",
    tags=["Chapters/post"],
    responses={404: {"description": "Not found"}},
)

data_engine = ChapterEngine()


@router.post("/", response_model=NewChapterResponse)
async def create_new_chapter(chapters: NewChapter):
    try:
        data_engine.connect()
        check = data_engine.check_if_chapter_exists(chapters.serie_id, chapters.chapter_num)
        data_engine.disconnect()
        
        if len(check) != 0:
            raise HTTPException(status_code=400, detail="Chapter already exists!", headers={"short_code": "exists"})
        
        data_engine.connect()
        data_engine.insert_chapter(
            chapters.serie_id,
            chapters.serie_name,
            chapters.chapter_num,
            chapters.creator_id,
            chapters.creator_name,
            chapters.created_at
        )
        data_engine.disconnect()

        return {
            "msg": "New chapter successfully created!",
            "serie_name": chapters.serie_name,
            "chapter_num": chapters.chapter_num
        }
    except IndexError:
        raise HTTPException(status_code=400, detail="Wrong URL! ZINK", headers={"short_code": "wurl"})
    except ConnectionError:
        raise HTTPException(status_code=400, detail="Connection error!", headers={"short_code": "con"})
