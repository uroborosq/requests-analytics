import sys

from PyQt5 import QtWidgets

import Analytics
from Parser import Parser


class MyWidget(QtWidgets.QMainWindow):
    def __init__(self, arr):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout()
        self.button_plot_time_weeks = QtWidgets.QPushButton("График по неделям")
        self.button_plot_time_weeks.clicked.connect()
        self.wnd = QtWidgets.QWidget()
        self.wnd.setLayout(self.layout)
        self.setCentralWidget(self.wnd)

    #     # self.plots = QtWidgets.QWidget()
    #     # self.layout = QtWidgets.QVBoxLayout()
    #     print(arr)


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        wnd = QtWidgets.QWidget()
        self.layout = QtWidgets.QVBoxLayout(self)
        self.button = QtWidgets.QPushButton("Старт")
        self.text1 = QtWidgets.QLabel("Введите адрес файла формата xlsx")
        self.text2 = QtWidgets.QLabel("Введите имя листа")
        self.input_1 = QtWidgets.QLineEdit()
        self.input_1.setMaximumWidth(250)
        self.input_1.setText("3.xlsx")
        self.input_2 = QtWidgets.QLineEdit()
        self.input_2.setMaximumWidth(250)
        self.input_2.setText("TDSheet")
        self.button.setMaximumWidth(50)

        self.layout.addWidget(self.text1)
        self.layout.addWidget(self.input_1)
        self.layout.addWidget(self.text2)
        self.layout.addWidget(self.input_2)
        self.layout.addWidget(self.button)
        wnd.setLayout(self.layout)
        self.button.clicked.connect(self.get_text)
        self.input_2.returnPressed.connect(self.get_text)
        self.setFixedSize(300, 200)
        self.setCentralWidget(wnd)
        self.setWindowTitle("Окно ввода данных")
        self.show()

    def get_text(self):
        if self.input_1.text() != '' and self.input_2.text() != '':
            parser = Parser(self.input_1.text(), self.input_2.text())
            parser.parse()
            a = Analytics.PlotRequestsByTime(parser.requests)
            b = a.get()
            self.widget1 = MyWidget(b)
            self.widget1.setWindowTitle("Аналитика сервиса")
            self.hide()
            self.widget1.show()
            
        else:
            warn = QtWidgets.QMessageBox()
            warn.setText("Заполните поля")
            warn.setWindowTitle("Э")
            warn.exec()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec())
