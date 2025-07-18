import pandas as pd
import numpy as np
import rasterio
from glob import glob
from functools import reduce
from tqdm import tqdm
#from detected_fire import detect_fire
import shutil
import cv2
import os
import sys

# Параметры
MASKS_ALGORITHMS = ['Schroeder', 'Murphy', 'Kumar-Roy']
MASKS_FOR_COMPLETE_SCENE = True
NUM_VOTINGS = 1
IMAGE_SIZE = (256, 256)


def get_abs_paths(relative_path: str):
    current_file_path = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
    in_dir = os.path.join(project_root, relative_path, "masks")
    out_dir = in_dir  # сохраняем в ту же папку
    return in_dir, out_dir


def load_masks_in_dataframe(in_dir):
    masks = glob(os.path.join(in_dir, '*.tif')) + glob(os.path.join(in_dir, '*.TIF'))
    print('Masks found: {}'.format(len(masks)))

    df = pd.DataFrame(masks, columns=['masks_path'])
    df['original_name'] = df.masks_path.apply(os.path.basename)
    df['image_name'] = df.original_name.apply(remove_algorithms_name)

    print('Spliting masks...')
    total = 0
    dataframes = []

    for i, algorithm in enumerate(MASKS_ALGORITHMS):
        dataframes.append(df[df['original_name'].str.contains(algorithm)])

        num_images = len(dataframes[i].index)
        total += num_images
        print('{} - Images: {}'.format(algorithm, num_images))

    return dataframes


def remove_algorithms_name(mask_name):
    for algorithm in MASKS_ALGORITHMS:
        mask_name = mask_name.replace(f'_{algorithm}', '')
    return mask_name


def make_intersection_masks(relative_path: str):
    in_dir, out_dir = get_abs_paths(relative_path)
    os.makedirs(out_dir, exist_ok=True)

    dataframes = load_masks_in_dataframe(in_dir)
    df_joined = reduce(lambda x, y: pd.merge(x, y, on='image_name'), dataframes)

    print('Generating Intersection masks')
    print(f'Images to process: {len(df_joined.index)}')

    masks_columns = [col for col in df_joined.columns if col.startswith('masks_path')]

    for _, row in tqdm(df_joined.iterrows(), total=len(df_joined)):
        image_size = IMAGE_SIZE
        if MASKS_FOR_COMPLETE_SCENE:
            mask, _ = get_mask_arr(row[masks_columns[0]])
            image_size = mask.shape

        final_mask = np.ones(image_size, dtype=bool)

        for mask_column in masks_columns:
            mask, profile = get_mask_arr(row[mask_column])
            final_mask = np.logical_and(final_mask, mask)

        has_fire = final_mask.sum() > 0
        if has_fire:
            write_mask(
                os.path.join(out_dir, row['image_name'].replace('_RT', '_RT_Intersection')),
                final_mask,
                profile
            )

    print('Intersection masks created')

def detect_fire(row, masks_columns) -> tuple[np.ndarray, bool, dict]:
    """
    Объединяет маски и определяет наличие пожара.
    Возвращает финальную маску, флаг has_fire и rasterio profile.
    """
    image_size = IMAGE_SIZE
    profile = {}

    # Вычисление размера из первой доступной маски
    if MASKS_FOR_COMPLETE_SCENE:
        for mask_column in masks_columns:
            if isinstance(row[mask_column], str):
                mask, _ = get_mask_arr(row[mask_column])
                image_size = mask.shape
                break

    final_mask = np.zeros(image_size)

    for mask_column in masks_columns:
        if not isinstance(row[mask_column], str):
            mask = np.zeros(image_size, dtype=bool)
        else:
            mask, profile = get_mask_arr(row[mask_column])
            print(f"Mask shape: {mask.shape}, Sum of mask: {mask.sum()}")
        final_mask += mask

    final_mask = (final_mask >= NUM_VOTINGS)
    has_fire = final_mask.sum() > 0
    return final_mask, has_fire, profile

def make_voting_masks(relative_path: str) -> dict:
    in_dir, out_dir = get_abs_paths(relative_path)
    os.makedirs(out_dir, exist_ok=True)

    # Создаём отдельную папку для PNG рядом с out_dir
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    base_name = os.path.basename(relative_path)
    png_folder = os.path.join(project_root, "Front", "public", base_name)
    os.makedirs(png_folder, exist_ok=True)

    existing_voting_masks = glob(os.path.join(out_dir, '*_Voting.TIF'))
    if existing_voting_masks:
        print("[INFO] Обнаружены уже существующие маски голосования. Прерывание.")
        return {"status": "exists", "fire": None}

    dataframes = load_masks_in_dataframe(in_dir)
    df_joined = reduce(lambda x, y: pd.merge(x, y, on='image_name', how='outer'), dataframes)

    print('Generating Voting masks')
    print(f'Images to process: {len(df_joined.index)}')

    masks_columns = [col for col in df_joined.columns if col.startswith('masks_path')]

    any_created = False
    any_fire = False

    for _, row in tqdm(df_joined.iterrows(), total=len(df_joined)):
        final_mask, has_fire, profile = detect_fire(row, masks_columns)

        voting_mask_path = os.path.join(
            out_dir, row['image_name'].replace('.TIF', '').replace('.tif', '') + '_Voting.TIF'
        )

        print(f"[INFO] Для изображения {row['image_name']} пожар {'обнаружен' if has_fire else 'не обнаружен'} на маске.")

        if has_fire:
            write_mask(voting_mask_path, final_mask, profile)
            any_created = True
            any_fire = True

            # Сохраняем PNG маску отдельно (например, с matplotlib или PIL)
            png_mask_path = os.path.join(
                png_folder,
                row['image_name'].replace('.TIF', '').replace('.tif', '') + '_Voting.png'
            )
            # Пример сохранения через matplotlib (если final_mask - ndarray):
            import matplotlib.pyplot as plt
            plt.imsave(png_mask_path, final_mask, cmap='gray')
            plt.close()
            print(f"[INFO] Маска сохранена в PNG: {png_mask_path}")

    if any_created:
        return {"status": "created", "fire": any_fire}
    else:
        return {"status": "no_fire", "fire": False}


def get_mask_arr(path):
    with rasterio.open(path) as src:
        img = src.read().transpose((1, 2, 0))
        seg = np.array(img, dtype=int)
        return seg[:, :, 0], src.profile


def write_mask(mask_path, mask, profile={}):
    profile.update({'dtype': rasterio.uint8, 'count': 1})
    with rasterio.open(mask_path, 'w', **profile) as dst:
        dst.write_band(1, mask.astype(rasterio.uint8))


# if __name__ == '__main__':
#     rel_path = 'geo-images/LC08_L1TP_136022_20220516_20220519_02_T1'  # пример
#     if MASKS_FOR_COMPLETE_SCENE:
#         print(f'Вычисляются маски Voting ({NUM_VOTINGS} votes) и Intersection для всей сцены')
#     else:
#         print('Вычисляются маски для нарезанных патчей')
#
#     make_voting_masks(rel_path)
#     # make_intersection_masks(rel_path)
