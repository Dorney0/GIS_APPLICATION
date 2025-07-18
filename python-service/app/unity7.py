import os
import numpy as np
from osgeo import gdal
import matplotlib.pyplot as plt
from fastapi import HTTPException  # импорт исключения

def combine_and_visualize_tiff_bands_by_path(
    relative_folder_path: str,
    target_bands=("B1", "B2", "B3", "B4", "B5", "B6", "B7"),
    visualize_rgb_bands=("B7", "B6", "B2")
):
    """
    Объединяет указанные каналы из папки (относительно корня проекта) в многослойный TIFF и визуализирует RGB.

    :param relative_folder_path: Относительный путь до папки с tif-каналами от корня проекта
    :param target_bands: Каналы для объединения
    :param visualize_rgb_bands: Каналы для визуализации RGB
    """
    # Абсолютный путь к корню проекта (предполагается, что функция лежит в 3-х уровнях ниже корня)

    current_file_path = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
    folder_path = os.path.join(project_root, relative_folder_path)

    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Папка не найдена: {folder_path}")

    all_files = os.listdir(folder_path)
    tif_files = [f for f in all_files if f.lower().endswith(".tif")]

    image_files = []
    for band in target_bands:
        found = [f for f in tif_files if f"_{band}." in f]
        if not found:
            raise FileNotFoundError(f"Канал {band} не найден в папке {folder_path}")
        image_files.append(found[0])

    base_name = image_files[0].rsplit('_', 1)[0]
    merged_path = os.path.join(folder_path, f"{base_name}_merged.tif")

    if os.path.exists(merged_path):
        raise HTTPException(status_code=409, detail="Изображение уже объединено")

    first_band_path = os.path.join(folder_path, image_files[0])
    first_band_ds = gdal.Open(first_band_path)
    width, height = first_band_ds.RasterXSize, first_band_ds.RasterYSize

    img = np.zeros((height, width, len(image_files)), dtype=np.float32)

    print(f"\nЗагрузка каналов: {target_bands}")
    for i, filename in enumerate(image_files):
        band_path = os.path.join(folder_path, filename)
        print(f'  -> {band_path}')
        ds = gdal.Open(band_path)
        img[:, :, i] = ds.ReadAsArray()

    driver = gdal.GetDriverByName("GTiff")
    ds_out = driver.Create(merged_path, width, height, len(image_files), gdal.GDT_Float32)
    for i in range(len(image_files)):
        ds_out.GetRasterBand(i + 1).WriteArray(img[:, :, i])
    ds_out.FlushCache()
    ds_out = None

    print(f"\nСохранено объединённое изображение: {merged_path}")

    band_dict = {band: idx for idx, band in enumerate(target_bands)}


    def normalize_band(band):
        min_val, max_val = np.min(band), np.max(band)
        return (band - min_val) / (max_val - min_val) if max_val > min_val else np.zeros_like(band)


    try:
        rgb_indices = [band_dict[b] for b in visualize_rgb_bands]
    except KeyError as e:
        print(f"Ошибка визуализации: канал {e} не был объединён")
        return

    rgb_bands = [normalize_band(img[:, :, i]) for i in rgb_indices]
    rgb_image = np.dstack(rgb_bands)

    folder_path_png = os.path.join(project_root, "Front", "public")
    os.makedirs(folder_path_png, exist_ok=True)

    # PNG сохранение
    merged_png_path = os.path.join(folder_path_png, f"{base_name}_merged.png")
    plt.imsave(merged_png_path, rgb_image)
    plt.close()
    print(f"Сохранено RGB изображение в PNG: {merged_png_path}")

    # # Визуализация (если нужно показать)
    # plt.figure(figsize=(10, 10))
    # plt.imshow(rgb_image)
    # plt.title(f'RGB: {visualize_rgb_bands}')
    # plt.axis('off')
    # plt.show()

    return merged_path