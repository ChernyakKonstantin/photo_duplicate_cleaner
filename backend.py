import collections
import filecmp
import os
import time
from typing import Any



class RemainTimeEstimator:
    def __init__(self):
        self._moving_average_time_data = collections.deque(maxlen=10)
        self._elapsed_time = 0
        self._total_files = None

    def estimate(self) -> float:
        assert self._total_files is not None, 'Number of files is uknown. Method "estimate" might be called before method "update"'
        time_per_file = sum(self._moving_average_time_data) / len(self._moving_average_time_data)
        expected_time = time_per_file * self._total_files
        remain_time = expected_time - self._elapsed_time
        remain_time = remain_time if remain_time > 0 else 0
        return remain_time

    def update(self, value: float, total_files: int) -> None:
        self._moving_average_time_data.append(value)
        self._elapsed_time += value
        self._total_files = total_files


class Backend:
    @property
    def directory(self):
        return self._path_to_dir

    @directory.setter
    def directory(self, value):
        self._path_to_dir = value

    def __init__(self, path_to_dir: str = None):
        self._path_to_dir = path_to_dir
        self._remain_time_estimator = RemainTimeEstimator()
        self._update_progressbar = None
        self._on_delete_message = None

    # ____PRIVATE_METHODS____

    def _get_file_paths(self, path_to_dir: str) -> list:
        """Функция возвращает список путей к каждому файлу в данной папке (включая файлы в подпапках)"""
        entries = list(os.scandir(path_to_dir))
        file_paths = [entry.path for entry in entries if entry.is_file()]
        subdirs = [entry for entry in entries if entry.is_dir()]
        for dir in subdirs:
            file_paths.extend(self._get_file_paths(dir.path))
        return file_paths

    def _find_duplicates(self, file_paths: list, progress_bar: Any = None) -> dict:
        duplicates = {}
        for file_path_1 in file_paths:
            start_time = time.time()
            duplicates[file_path_1] = []
            for file_path_2 in file_paths:
                if file_path_1 != file_path_2 and filecmp.cmp(file_path_1, file_path_2, shallow=True):
                    duplicates[file_path_1].append(file_path_2)
                    file_paths.remove(file_path_2)
            finish_time = time.time()
            elapsed_time = finish_time - start_time
            self._remain_time_estimator.update(elapsed_time, len(file_paths))
            remain_time = self._remain_time_estimator.estimate()
            if self._on_remain_time_estimate_message:
                self._on_remain_time_estimate_message(remain_time)
            if self._update_progressbar:
                self._update_progressbar(len(file_paths))
        duplicates = dict(filter(lambda x: len(x[1]) != 0, duplicates.items()))
        filecmp.clear_cache()
        return duplicates

    def _show_duplicates(self, duplicates: dict) -> None:
        print('Duplicates found:')
        for k, v in duplicates.items():
            print(f'{os.path.basename(k)} --> {[os.path.basename(el) for el in v]}')

    def _delete(self, duplicates: dict) -> None:
        for value in duplicates.values():
            for el in value:
                os.remove(el)

    # ____PUBLIC_METHODS____

    def connect_progress_bar(self, caller: Any):
        """Caller - функция с аргументом value: int"""
        self._update_progressbar = caller

    def connect_on_delete_message(self, caller: Any):
        """Caller - функция с аргументом value: int"""
        self._on_delete_message = caller

    def connect_on_remain_time_estimate_message(self, caller: Any):
        """Caller - функция с аргументом value: int"""
        self._on_remain_time_estimate_message = caller

    def run(self, show: bool = True):
        assert self._path_to_dir is not None, 'Target folder is not specified'
        file_paths = self._get_file_paths(self._path_to_dir)
        duplicates = self._find_duplicates(file_paths)
        if show:
            self._show_duplicates(duplicates)
        if self._on_delete_message:
            self._on_delete_message(len(duplicates))
        # self._delete(duplicates)
