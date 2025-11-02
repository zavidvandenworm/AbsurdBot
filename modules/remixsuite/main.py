from io import BytesIO

from fastapi import File, UploadFile, HTTPException, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from .remix import remix_song

app = FastAPI()

origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/remix")
async def upload(file: UploadFile = File(...)):
    output = BytesIO()
    try:
        file.file.seek(0)
        remix = remix_song(file.file, file.filename.split(".")[-1])
        remix.export(output, format="mp3")
        output.seek(0)
        return Response(content=output.read(), media_type="audio/mp3",
                        headers={"Content-Disposition": f"attachment; filename=remixed_{file.filename}"})

    except Exception as exc:
        print(exc)
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        await file.close()
