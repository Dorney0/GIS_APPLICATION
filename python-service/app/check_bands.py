import os
import rasterio
import numpy as np


def check_bands(in_dir, image_name):
    filepath = os.path.join(in_dir, image_name + '.TIF')
    with rasterio.open(filepath) as src:
        print(f"Количество каналов в изображении: {src.count}")
        print("Индексы каналов в файле (1-based):", list(range(1, src.count + 1)))

        # Если каналов >=7, читаем первые 7, иначе читаем все
        num_bands_to_check = min(7, src.count)

        for i in range(1, num_bands_to_check + 1):  # 1-based индексация каналов
            band = src.read(i)
            print(f"Канал {i}: min={np.min(band)}, max={np.max(band)}, mean={np.mean(band)}")


if __name__ == "__main__":
    in_dir = r'../../geo-images/LC08_L1TP_136022_20220516_20220519_02_T1/'  # поменяй на свою папку
    image_name = 'LC08_L1TP_136022_20220516_20220519_02_T1_merged'  # имя файла без расширения
    check_bands(in_dir, image_name)
