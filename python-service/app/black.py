import os
import rasterio
import numpy as np

def blackout_tif(tif_path: str, overwrite: bool = True):
    if not os.path.exists(tif_path):
        raise FileNotFoundError(f"Файл не найден: {tif_path}")

    # Чтение изображения
    with rasterio.open(tif_path) as src:
        profile = src.profile
        width = src.width
        height = src.height
        count = src.count  # кол-во каналов

    # Создание полностью чёрного массива
    black_data = np.zeros((count, height, width), dtype=np.uint8)

    # Обновление профиля: 1 канал, если нужно
    profile.update(dtype=rasterio.uint8, count=count)

    # Сохранение
    output_path = tif_path if overwrite else tif_path.replace('.tif', '_black.tif').replace('.TIF', '_black.TIF')
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(black_data)

    print(f"[INFO] Изображение сделано черным и сохранено в: {output_path}")

if __name__ == '__main__':
    path = r'D:\GIS_APPLICATION\geo-images\LC08_L1TP_136022_20220516_20220519_02_T1\masks\LC08_L1TP_136022_20220516_20220519_02_T1_Voting.TIF'
    blackout_tif(path, overwrite=True)  # или False, если не хочешь затирать оригинал
