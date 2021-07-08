import time

from Parser import Parser
from Analytics import AverageTimeForRequest
from Analytics import PlotRequestsByTime
from GUI import GUI


# parser = Parser("1.xlsx", "TDSheet")
# parser.parse("A1")
app = GUI()

print (app.str_sheet + " " + app.str_address)


# b = PlotRequestsByTime(parser.requests)
# b.make_plot()
