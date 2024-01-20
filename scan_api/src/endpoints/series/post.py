from fastapi import APIRouter, HTTPException
from sqa.main import DataEngine, IntegrityError, MissingSchema, ConnectionError
from sqa.models import URLs, NewMangaResponse


router = APIRouter(
    prefix="/post",
    tags=["Series/post"],
    responses={404: {"description": "Not found"}},
)

data_engine = DataEngine()


@router.post("/new/", response_model=NewMangaResponse)
async def create_new_manga(urls: URLs):
    try:
        data_engine.connect()
        data_engine.insert_row(
            urls.name,
            urls.image_url,
            urls.source_url,
            urls.base_url,
            urls.source_chap,
            urls.base_chap,
            urls.role_id,
            urls.channel_id,
            urls.last_chapter_url,
            urls.main_category,
            urls.tl,
            urls.pr,
            urls.lr,
            urls.clnr,
            urls.tser,
            urls.qcer
        )
        data_engine.disconnect()

        return {
            "msg": "New manga successfully created!",
            "urls": {
                "eng": urls.source_url,
                "tr": urls.base_url
            }
        }
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Manga already exists!", headers={"short_code": "mae"})
    except IndexError:
        raise HTTPException(status_code=400, detail="Wrong URL! ZINK", headers={"short_code": "wurl"})
    except MissingSchema:
        raise HTTPException(status_code=400, detail="Wrong URL! ZONK", headers={"short_code": "wurl"})
    except ConnectionError:
        raise HTTPException(status_code=400, detail="Connection error!", headers={"short_code": "con"})
