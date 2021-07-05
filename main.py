from accessify import private
from Request import Request
from Parser import Parser
from Analytics import AverageTimeForRequest
from PySide6 import QtCore, QtWidgets, QtGui
import datetime
import random
import sys

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.hello = ["Hallo Welt", "Hei maailma", "Hola Mundo", "Привет мир"]

        self.button = QtWidgets.QPushButton("Click me!")
        self.text = QtWidgets.QLabel("Hello World", alignment=QtCore.Qt.AlignCenter)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)

        self.button.clicked.connect(self.magic)

    @QtCore.Slot()
    def magic(self):
        self.text.setText(random.choice(self.hello))

test = datetime.datetime(1999, 1, 1, 0, 0) - datetime.datetime(2001, 2, 2, 1, 1)
print(test)
print(type(test))
parser = Parser("1.xlsx", "TDSheet")
parser.parse("A1")
for i in parser.requests.values():
    print(i.get())

a = AverageTimeForRequest(parser.requests)
print(a.analyse())
app = QtWidgets.QApplication([])

widget = MyWidget()
widget.resize(800, 600)
widget.show()

sys.exit(app.exec())
