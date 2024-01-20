from fastapi import FastAPI
from datetime import datetime
from routes.api import router as api_router

app = FastAPI()

app.include_router(api_router)


@app.get("/")
async def root():
    numnam = datetime.now()

    response = {
        "code": 200,
        "about": "API made by NandeMD for benevolent scanlations",
        "datetime": f"{numnam.day}/{numnam.month}/{numnam.year}    {numnam.time()}",
        "mostRecentVer": "v1"
    }

    return response

