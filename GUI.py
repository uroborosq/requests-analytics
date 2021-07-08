from tkinter import *


class GUI(object):

    def __init__(self):
        self.str_address = ''
        self.str_sheet = ''
        self.flag = 0

        self.wnd = Tk()
        self.wnd.title("Аналитика работы сервиса")
        self.wnd.geometry("800x600")
        self.lbl = Label(self.wnd, text="Введите адрес файла формата xlxs", font=("Arial Bold", 13))
        self.lbl.place(x=10, y=30)
        self.address = Entry(master=self.wnd, width=40)
        self.address.place(x=10, y=60)

        self.lbl_2 = Label(self.wnd, text='Введите название листа с данными', font=("Arial Bold", 13))
        self.lbl_2.place(x=10, y=90)

        self.sheet = Entry(master=self.wnd, width=40)
        self.sheet.place(x=10, y=120)

        self.btn = Button(self.wnd, text="Старт", font=("Courier New Bold", 13), command=self.clicked)
        self.btn.place(x=10, y=150, width=170, height=30)
        self.wnd.mainloop()

    def clicked(self):
        self.str_address = self.address.get()
        self.str_sheet = self.sheet.get()
        self.flag = 1
        self.wnd.destroy()



