import os
import matplotlib.pyplot as plt
from osgeo import gdal
import numpy as np

def inspect_tif_folder(folder_path: str):
    """
    Открывает все .tif изображения в папке, выводит информацию по каналам и визуализирует их.
    """
    # Получаем список всех tif-файлов в папке
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.tif')]

    if not image_files:
        print("В папке нет изображений .tif")
        return

    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        dataset = gdal.Open(image_path)

        if not dataset:
            print(f"Не удалось открыть изображение: {image_path}")
            continue

        print(f"\nОткрыто изображение: {image_path}")

        # Читаем до трёх каналов
        band1 = dataset.GetRasterBand(1).ReadAsArray()
        band2 = dataset.GetRasterBand(2).ReadAsArray() if dataset.RasterCount > 1 else np.zeros_like(band1)
        band3 = dataset.GetRasterBand(3).ReadAsArray() if dataset.RasterCount > 2 else np.zeros_like(band1)

        print(f"Минимум/максимум канала 1: {np.min(band1)}, {np.max(band1)}")
        print(f"Минимум/максимум канала 2: {np.min(band2)}, {np.max(band2)}")
        print(f"Минимум/максимум канала 3: {np.min(band3)}, {np.max(band3)}")

        def normalize_band(band):
            min_val, max_val = np.min(band), np.max(band)
            return (band - min_val) / (max_val - min_val) if max_val > min_val else np.zeros_like(band)

        band1 = normalize_band(band1)
        band2 = normalize_band(band2)
        band3 = normalize_band(band3)

        if np.all(band2 == 0) and np.all(band3 == 0):
            rgb_image = band1  # grayscale
        else:
            rgb_image = np.dstack((band1, band2, band3))  # RGB

        plt.figure(figsize=(10, 10))
        plt.imshow(rgb_image, cmap='gray' if rgb_image.ndim == 2 else None)
        plt.title(f"Изображение: {image_file}")
        plt.axis('off')
        plt.show()
