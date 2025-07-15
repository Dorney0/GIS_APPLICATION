import os
from osgeo import gdal

def check_bands_size(folder_path: str):
    target_bands = {"B7", "B6", "B2"}
    band_sizes = {}

    if not os.path.exists(folder_path):
        print(f"Папка не найдена: {folder_path}")
        return

    files = [f for f in os.listdir(folder_path) if f.lower().endswith('.tif')]

    for filename in files:
        for band in target_bands:
            if f"_{band}." in filename:
                file_path = os.path.join(folder_path, filename)
                ds = gdal.Open(file_path)
                if ds is None:
                    print(f"Не удалось открыть файл {filename}")
                    continue
                width = ds.RasterXSize
                height = ds.RasterYSize
                band_sizes[band] = (width, height)
                print(f"{filename}: width = {width}, height = {height}")

    if len(band_sizes) == len(target_bands):
        sizes = list(band_sizes.values())
        if all(size == sizes[0] for size in sizes):
            print("Все выбранные каналы имеют одинаковый размер.")
        else:
            print("Внимание: размеры выбранных каналов отличаются!")
    else:
        print("Не все целевые каналы найдены в папке.")

if __name__ == "__main__":
    folder = r"D:\GIS_APPLICATION\geo-images\LC08_L1TP_136022_20220516_20220519_02_T1"
    check_bands_size(folder)
