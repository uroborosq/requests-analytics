import sys
import matplotlib
from PyQt5 import QtWidgets
from Parser import Parser
import Analytics
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
matplotlib.use('Qt5Agg')


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100, pos=111):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        # self.axes = fig.add_subplot(pos)
        super(MplCanvas, self).__init__(self.fig)


class MyWidget(QtWidgets.QMainWindow):
    def __init__(self, arr):
        super().__init__()
        self.plots = QtWidgets.QWidget()
        self.layout = QtWidgets.QVBoxLayout()

        figure = MplCanvas(self, width=5, height=4, dpi=100, pos=111)
        weeks = figure.fig.add_subplot(221)
        months = figure.fig.add_subplot(222)
        quarters = figure.fig.add_subplot(223)
        years = figure.fig.add_subplot(224)
        if arr is not None:
            self.__set_plot__(weeks, 0, arr, "По неделям")
            self.__set_plot__(months, 1, arr, "По месяцам")
            self.__set_plot__(quarters, 2, arr, "По кварталам")
            self.__set_plot__(years, 3, arr, "По годам")

            self.layout.addWidget(figure)
            self.plots.setLayout(self.layout)
            self.setCentralWidget(self.plots)
            self.show()

    def __set_plot__(self, plot, it, arr, name):
        plot.plot(arr[it].keys(), arr[it].values(), linestyle='solid', label='Поступило')
        plot.plot(arr[it + 4].keys(), arr[it + 4].values(), linestyle='solid', label='Выполнено')
        plot.legend()
        plot.set_title(name)
        plot.grid(True)
        return plot


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
        self.input_1.setText("1.xlsx")
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
