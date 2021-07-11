import time

from Parser import Parser
from Analytics import AverageTimeForRequest
from Analytics import PlotRequestsByTime

parser = Parser("1.xlsx", "TDSheet")
parser.parse()

b = PlotRequestsByTime(parser.requests)
print(b.get()[3])
