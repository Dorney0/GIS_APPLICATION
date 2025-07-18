import os
import rasterio
from glob import glob

def detect_fire_from_mask(relative_path: str) -> bool:
    """
    Ищет маску *_Voting.TIF по относительному пути, проверяет наличие пожара.
    """
    current_file_path = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
    in_dir = os.path.join(project_root, relative_path, "masks")

    # Ищем файл *_Voting.TIF
    voting_masks = glob(os.path.join(in_dir, '*_Voting.TIF'))
    if not voting_masks:
        raise FileNotFoundError("Маска *_Voting.TIF не найдена в указанной папке")

    mask_path = voting_masks[0]  # берём первую найденную

    with rasterio.open(mask_path) as src:
        data = src.read(1)
        return bool((data > 0).any())
