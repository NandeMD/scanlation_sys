from fastapi import APIRouter, HTTPException
from sqa.main import DataEngine, IntegrityError
from sqa.models import Options


router = APIRouter(
    prefix="/update",
    tags=["Series/update"],
    responses={404: {"description": "Not found"}},
)

data_engine = DataEngine()


@router.post("/manga/")
async def update_manga(options: Options):

    if not options.id:
        return HTTPException(status_code=400, detail="You have to specify an ID!", headers={"short_code": "nif"})

    try:
        data_engine.connect()
        data_engine.update_columns(options)
        data_engine.disconnect()
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Name already exists!", headers={"short_code": "nae"})

    return {"msg": "Update successful!"}
