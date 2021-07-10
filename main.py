import time

from Parser import Parser
from Analytics import AverageTimeForRequest
from Analytics import PlotRequestsByTime

parser = Parser("1.xlsx", "TDSheet")
parser.parse("A1")
parser.parse("A1")
a = AverageTimeForRequest(parser.requests)
a.analyse()
b = PlotRequestsByTime(parser.requests)
b.get()
