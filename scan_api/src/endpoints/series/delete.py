from fastapi import APIRouter, HTTPException
from sqa.main import DataEngine, IntegrityError, MissingSchema, ConnectionError
from sqa.models import DeleteMangaResponse


router = APIRouter(
    prefix="/delete",
    tags=["Series/delete"],
    responses={404: {"description": "Not found"}},
)

data_engine = DataEngine()


@router.get("/{manga_id}", response_model=DeleteMangaResponse)
async def delete_manga(manga_id: int):
    try:
        data_engine.connect()
        data_engine.delete_row(manga_id)
        data_engine.disconnect()

        return {
            "msg": "Manga successfully deleted!",
            "id": manga_id
        }
    except Exception as e:
        print(e)
