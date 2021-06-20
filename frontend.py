import tkinter as tk
from  tkinter import filedialog
from tkinter.ttk import Progressbar, Frame, Button, Label



class Application():

    def __init__(self):
        self.root = tk.Tk()
        self.root.title('DelDupsV1')
        self.root.geometry('250x100')
        self.root.resizable(0, 0)
        # self.mainframe = Frame(self.root)
        # self.mainframe.grid(
        #     column=0,
        #     row=0,
        #     sticky=(tk.N, tk.W, tk.E, tk.S),
        # )
        self.make_widgets()
        self.run()

    def run(self):
        self.root.mainloop()

    def make_buttons(self):
        self.select_dir_btn = self.make_btn(
            self.root,
            'Выбрать папку',
            self.select_dir
        )
        self.launch_btn = self.make_btn(
            self.root,
            'Запустить',
            self.progress_step
        )
        self.select_dir_btn.grid(
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

    def make_widgets(self):
        self.make_buttons()
        self.progressbar = Progressbar(self.root)
        self.progressbar.grid(
            row=1,
            column=0,
            rowspan=1,
            columnspan=2,
            sticky=(tk.N, tk.W, tk.E, tk.S),
            padx=3,
            pady=3,
        )
        self.info_label = Label(
            self.root,
            text='Удалено дубликатов изображений: 0'
        )
        self.info_label.grid(
            row=2,
            column=0,
            rowspan=1,
            columnspan=2,
            sticky=(tk.N, tk.W, tk.E, tk.S),
            padx=3,
            pady=3,
        )

    def select_dir(self, event):
        self.dir = filedialog.askdirectory()

    def progress_step(self, event):
        self.progressbar.step()

    def make_btn(self, master, text, func):
        btn = Button(
            master=master,
            text=text,
        )
        btn.bind(
            '<Button-1>',
            func=func,
        )
        return btn


if __name__ == '__main__':
    a = Application()


