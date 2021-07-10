import sys
import matplotlib
from PyQt5 import QtCore, QtWidgets
from Parser import Parser
import Analytics
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
matplotlib.use('Qt5Agg')


class MyWidget(QtWidgets.QMainWindow):
    def __init__(self, arr):
        super().__init__()
        sc = MplCanvas(self, width=5, height=4, dpi=100)
        if arr is not None:
            sc.axes.plot(arr[0].keys(), arr[0].values(), linestyle='solid', label='Поступило')
            sc.axes.plot(arr[4].keys(), arr[4].values(), linestyle='solid', label='Выполнено')
            sc.axes.legend()
            sc.axes.grid(True)
            self.setCentralWidget(sc)
            self.show()


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        wnd = QtWidgets.QWidget()
        self.layout = QtWidgets.QVBoxLayout(self)
        self.button = QtWidgets.QPushButton("Старт")
        self.text1 = QtWidgets.QLabel("Введите адрес файла формата xlsx")
        self.text2 = QtWidgets.QLabel("Введите адрес имя листа")
        self.input_1 = QtWidgets.QLineEdit()
        self.input_1.setMaximumWidth(250)
        self.input_2 = QtWidgets.QLineEdit()
        self.input_2.setMaximumWidth(250)
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
            # self.widget1.setFixedHeight(150)
            # self.widget1.setFixedWidth(400)
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
