from multiprocessing import Pool, cpu_count
from os import scandir, remove
from os.path import basename
from time import time

import cv2 as cv
import numpy as np
from PIL import Image


def get_file_paths(path_to_dir: str) -> list:
    """Функция возвращает список путей к каждому файлу в данной папке (включая файлы в подпапках)"""
    entries = list(scandir(path_to_dir))
    file_paths = [entry.path for entry in entries if entry.is_file()]
    subdirs = [entry for entry in entries if entry.is_dir()]
    for dir in subdirs:
        file_paths.extend(get_file_paths(dir.path))
    return file_paths


def read_file(file_path: str) -> np.array:
    img = Image.open(file_path)
    img = img.convert('RGB')
    img = np.array(img)
    least_size = min(img.shape[:-1])
    img = cv.resize(img, (least_size, least_size))
    img = img.astype("int64")
    return img


def integral_image_diagonal(img: np.array) -> list:
    diagonal = []
    cum_sum = np.array([0, 0, 0], dtype='int64')
    for i in range(img.shape[1]):
        right = np.sum(img[: i + 1, i], axis=(0, 1))
        bottom = np.sum(img[i, : i + 1], axis=(0, 1))
        overlap = img[i, i]
        img_sum = cum_sum + right + bottom - overlap
        diagonal.append(img_sum)
        cum_sum = img_sum.copy()
    return diagonal


def process_image(image_path: str) -> dict:
    img = read_file(image_path)
    diagonal = {'name': image_path, 'value': integral_image_diagonal(img)}
    return diagonal


def equal_diagonals(diagonal_1: list, diagonal_2: list) -> bool:
    if len(diagonal_1) != len(diagonal_2):
        return False
    else:
        for el_1, el_2 in zip(diagonal_1, diagonal_2):
            if np.any(el_1 != el_2):
                return False
    return True


def get_extension(path: str) -> str:
    extension = path.split('.')[-1]
    return extension.lower()


def find_duplicates(root_dir: str) -> dict:
    EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}
    file_paths = get_file_paths(root_dir)
    image_paths = [path for path in file_paths if get_extension(path) in EXTENSIONS]

    agents = cpu_count()
    chunk_size = len(image_paths) // agents
    t1 = time()
    with Pool(processes=agents) as pool:
        diagonals = pool.map(process_image, image_paths, chunk_size)
    t2 = time()

    print(f'Total_files: {len(image_paths)}')
    print(f'Total_diagonals: {len(diagonals)}')
    print(f'Analysis is done in {t2 - t1} seconds')
    print()

    t1 = time()
    duplicates = {}
    for diagonal_1 in diagonals:
        duplicates[diagonal_1['name']] = []
        for diagonal_2 in diagonals:
            if diagonal_1['name'] != diagonal_2['name']:
                if equal_diagonals(diagonal_1['value'], diagonal_2['value']):
                    duplicates[diagonal_1['name']].append(diagonal_2['name'])
                    diagonals.remove(diagonal_2)
    t2 = time()
    print(f'Finding duplicates is done in {t2 - t1} seconds')

    keys_to_drop = []
    for k, v in duplicates.items():
        if len(v) == 0:
            keys_to_drop.append(k)

    for key in keys_to_drop:
        duplicates.pop(key)

    print('Duplicates found:')
    for k, v in duplicates.items():
        print(f'{basename(k)} --> {[basename(el) for el in v]}')
    return duplicates


def delete(duplicates: dict) -> None:
    t1 = time()
    for value in duplicates.values():
        for el in value:
            remove(el)
    t2 = time()
    print(f'Deletion is done in {t2 - t1} seconds')


if __name__ == '__main__':
    ROOT_DIR = r'C:\Users\zvfrf\Pictures'
    duplicates = find_duplicates(ROOT_DIR)
    delete(duplicates)

