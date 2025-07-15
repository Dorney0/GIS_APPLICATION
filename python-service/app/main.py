from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse
from unity762 import process_geotiff_folder
import os

app = FastAPI()

@app.get("/process-folder/")
async def process_folder(path: str = Query(..., description="Путь к папке с TIFF изображениями")):

    # Запуск обработки
    try:
        output_file = process_geotiff_folder(path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not os.path.exists(output_file):
        raise HTTPException(status_code=500, detail="Файл результата не найден")

    return FileResponse(output_file, media_type="image/tiff", filename=os.path.basename(output_file))
