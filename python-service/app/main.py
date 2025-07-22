from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse

from ViewMasks import inspect_tif_folder
from unity762 import process_geotiff_folder
from unity7 import combine_and_visualize_tiff_bands_by_path
from create_3masks import process_3masks
from create_voting_masks import make_voting_masks
import os

app = FastAPI()

@app.get("/process-folder/")
async def process_folder(path: str = Query(..., description="Путь к папке с TIFF изображениями")):

    # Запуск обработки
    try:
        output_file = combine_and_visualize_tiff_bands_by_path(path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not os.path.exists(output_file):
        raise HTTPException(status_code=500, detail="Файл результата не найден")

    return FileResponse(output_file, media_type="image/tiff", filename=os.path.basename(output_file))
@app.get("/combine-bands/")
async def combine_bands(
    folder_path: str = Query(..., description="Путь к папке с TIFF файлами"),
    target_bands: str = Query("B1,B2,B3,B4,B5,B6,B7", description="Каналы для объединения через запятую"),
    visualize_rgb_bands: str = Query("B7,B6,B2", description="Каналы для визуализации RGB через запятую")
):
    try:
        target_bands_list = tuple(target_bands.split(","))
        visualize_rgb_list = tuple(visualize_rgb_bands.split(","))
        output_file = combine_and_visualize_tiff_bands_by_path(
            relative_folder_path=folder_path,
            target_bands=target_bands_list,
            visualize_rgb_bands=visualize_rgb_list
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not os.path.exists(output_file):
        raise HTTPException(status_code=500, detail="Файл результата не найден")

    return FileResponse(output_file, media_type="image/tiff", filename=os.path.basename(output_file))

@app.get("/create-3masks/")
async def detect_fires(folder_path: str = Query(..., description="Путь к папке с изображением")):
    try:
        result = process_3masks(folder_path)
        return {"status": "success", "message": "Маски сформированы успешно"}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при детекции пожаров: {str(e)}")

@app.get("/create-voting-masks/")
async def create_voting_masks(folder_path: str = Query(..., description="Путь к папке с изображением")):
    try:
        result = make_voting_masks(folder_path)

        if result["status"] == "exists":
            raise HTTPException(status_code=400, detail="Маска (Voting) уже существуют")

        if result["status"] == "no_fire":
            return {"status": "ok", "message": "Обработка завершена, но пожары не обнаружены", "fire": False}

        return {"status": "success", "message": "Voting маски успешно созданы", "fire": result["fire"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/create-full-mask/")
async def create_full_mask(folder_path: str = Query(..., description="Путь к папке с изображением")):
    try:
        # Сначала создаём 3 маски
        process_3masks(folder_path)

        # Затем создаём voting-маски
        result = make_voting_masks(folder_path)

        if result["status"] == "exists":
            raise HTTPException(status_code=400, detail="Маска (Voting) уже существует")

        if result["status"] == "no_fire":
            return {"status": "ok", "message": "Обработка завершена, но пожары не обнаружены", "fire": False}

        return {
            "status": "success",
            "message": "3 маски и Voting маска успешно созданы",
            "fire": result["fire"]
        }

    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при создании масок: {str(e)}")

@app.get("/inspect")
def inspect(folder_path: str = Query(..., description="Путь к папке с .tif файлами")):
    """
    Вызывает функцию визуального осмотра tif-файлов в указанной папке.
    """
    try:
        inspect_tif_folder(folder_path)
        return {"status": "OK", "message": f"Обработка папки {folder_path} завершена."}
    except Exception as e:
        return {"status": "error", "detail": str(e)}