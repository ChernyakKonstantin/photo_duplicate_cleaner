import threading
import tkinter as tk
from tkinter import filedialog
from tkinter.ttk import Progressbar, Button, Label
import datetime
from backend import Backend
# import multiprocessing
import queue

class Application():

    def __init__(self):
        self._backend = Backend()
        self._make_root()
        self._make_widgets()
        self._backend.connect_progress_bar(self._update_progress_bar)
        self._backend.connect_on_delete_message(self._on_delete_message)
        self._backend.connect_on_remain_time_estimate_message(self._on_remain_time_estimate_message)
        self._run()

    def _run(self):
        self.root.mainloop()

    def _make_root(self):
        self.root = tk.Tk()
        self.root.title('DelDupsV1')
        # self.root.geometry('250x100')
        self.root.resizable(0, 0)

    def _make_buttons(self):
        self._select_dir_btn = self._make_btn(
            self.root,
            'Выбрать папку',
            self._select_dir
        )
        self.launch_btn = self._make_btn(
            self.root,
            'Запустить',
            self._run_backend
        )
        self.stop_btn = self._make_btn(
            self.root,
            'Остановить',
            self._stop_backend
        )
        self._select_dir_btn.grid(
            row=0,
            column=0,
            rowspan=1,
            columnspan=1,
            sticky=(tk.N, tk.W, tk.E, tk.S),
            padx=3,
            pady=3,
        )
        self.launch_btn.grid(
            row=0,
            column=1,
            rowspan=1,
            columnspan=1,
            sticky=(tk.N, tk.W, tk.E, tk.S),
            padx=3,
            pady=3,
        )
        self.stop_btn.grid(
            row=0,
            column=2,
            rowspan=1,
            columnspan=1,
            sticky=(tk.N, tk.W, tk.E, tk.S),
            padx=3,
            pady=3,
        )

    def _make_widgets(self):
        self._make_buttons()
        self.progressbar = Progressbar(self.root)
        self.progressbar.grid(
            row=1,
            column=0,
            rowspan=1,
            columnspan=3,
            sticky=(tk.N, tk.W, tk.E, tk.S),
            padx=3,
            pady=3,
        )
        self.info_label = Label(
            self.root,
            text=''
        )
        self.info_label.grid(
            row=2,
            column=0,
            rowspan=1,
            columnspan=3,
            sticky=(tk.N, tk.W, tk.E, tk.S),
            padx=3,
            pady=3,
        )

    def _select_dir(self, event):
        self._backend.directory = filedialog.askdirectory()

    def _run_backend(self, event):
        self._backend_thread = threading.Thread(target=self._backend.run, daemon=True)
        self._backend_thread.start()
        # self._backend_process = multiprocessing.Pool(1)
        # self._backend_process.map(self._backend.run, [])

    def _stop_backend(self, event):
        if self._backend_thread.is_alive:
            self._backend_thread.terminate()
        # self._backend_process.terminate()

    def _make_btn(self, master, text, func):
        btn = Button(
            master=master,
            text=text,
        )
        btn.bind(
            '<Button-1>',
            func=func,
        )
        return btn

    def _update_progress_bar(self, max_value):
        self.progressbar['maximum'] = max_value
        self.progressbar.step()

    def _on_delete_message(self, value):
        self.info_label['text'] = f'Удалено дубликатов: {value}'

    def _on_remain_time_estimate_message(self, value):
        self.info_label['text'] = f'Оставшееся время: {datetime.timedelta(seconds=round(value, 0))}.'


if __name__ == '__main__':
    application = Application()
