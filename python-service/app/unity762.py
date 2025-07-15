import os
import numpy as np
from osgeo import gdal
import matplotlib.pyplot as plt
from fastapi import HTTPException

def process_geotiff_folder(relative_path: str):
    """
    Обрабатывает TIFF-изображения с каналами B7, B6, B2 в папке relative_path (относительно корня проекта),
    объединяет эти каналы, сохраняет результат и строит RGB-изображение.
    """
    current_file_path = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
    folder_path = os.path.join(project_root, relative_path)

    if not os.path.exists(folder_path):
        raise HTTPException(status_code=400, detail=f"Папка не найдена: {folder_path}")

    TARGET_BANDS = ["B7", "B6", "B2"]  # порядок важен

    all_files = os.listdir(folder_path)
    searched_files = [f for f in all_files if f.lower().endswith(".tif")]

    # Проверяем наличие нужных файлов и собираем их в порядке TARGET_BANDS
    image_files = []
    for band in TARGET_BANDS:
        band_files = [f for f in searched_files if f"_{band}." in f]
        if not band_files:
            raise FileNotFoundError(f"Файл для канала {band} не найден в {folder_path}")
        image_files.append(band_files[0])

    # Берём размеры с первого канала (B7)
    first_band_path = os.path.join(folder_path, image_files[0])
    first_band_ds = gdal.Open(first_band_path)
    image_width = first_band_ds.RasterXSize
    image_height = first_band_ds.RasterYSize

    # Создаём массив для 3 каналов
    img = np.zeros((image_height, image_width, len(TARGET_BANDS)), dtype=np.float32)

    # Загружаем данные каналов в правильном порядке
    for i, band_file in enumerate(image_files):
        band_path = os.path.join(folder_path, band_file)
        band_ds = gdal.Open(band_path)
        if band_ds is None:
            raise RuntimeError(f"Не удалось открыть файл {band_path}")
        band_img = band_ds.ReadAsArray()
        if band_img.shape != (image_height, image_width):
            raise ValueError(f"Размеры канала {band_file} не совпадают с базовыми размерами")
        img[:, :, i] = band_img

    # Путь для сохранения результата
    OUTPUT_PATH = os.path.join(project_root, "output_images")
    os.makedirs(OUTPUT_PATH, exist_ok=True)

    base_name = image_files[0].rsplit('_', 1)[0]
    output_image = os.path.join(folder_path, f"{base_name}_merged.tif")

    # Сохраняем TIFF с 3 каналами
    driver = gdal.GetDriverByName("GTiff")
    dataset = driver.Create(output_image, image_width, image_height, len(TARGET_BANDS), gdal.GDT_Float32)
    for i in range(len(TARGET_BANDS)):
        dataset.GetRasterBand(i + 1).WriteArray(img[:, :, i])
    dataset.FlushCache()
    dataset = None

    print(f"Многослойное изображение с каналами B7, B6, B2 сохранено: {output_image}")

    # Нормализация каналов для отображения
    def normalize_band(band):
        min_val, max_val = np.min(band), np.max(band)
        return (band - min_val) / (max_val - min_val) if max_val > min_val else np.zeros_like(band)

    band7 = normalize_band(img[:, :, 0])
    band6 = normalize_band(img[:, :, 1])
    band2 = normalize_band(img[:, :, 2])

    rgb_image = np.dstack((band7, band6, band2))

    plt.figure(figsize=(10, 10))
    plt.imshow(rgb_image)
    plt.title('RGB изображение с каналами B7, B6, B2')
    plt.axis('off')
    plt.show()

    return output_image
