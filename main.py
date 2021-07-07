from Request import Request
from Parser import Parser
from Analytics import AverageTimeForRequest
from Analytics import PlotRequestsByTime
#from PySide6 import QtCore, QtWidgets, QtGui
import datetime
import random
import sys


parser = Parser("1.xlsx", "TDSheet")
parser.parse("A1")

# a = AverageTimeForRequest(parser.requests)
# print(a.analyse())
# app = QtWidgets.QApplication([])

# widget = MyWidget()
# widget.resize(800, 600)
# widget.show()

# sys.exit(app.exec())
b = PlotRequestsByTime(parser.requests)
b.make_plot()
