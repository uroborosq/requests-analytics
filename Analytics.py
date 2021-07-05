from Request import Request
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt


class AverageTimeForRequest(object):
    def __init__(self, requests):
        self.array = dict(requests)

    def analyse(self):
        counter = 0
        summ = timedelta(0, 0, 0, 0, 0)
        for i in self.array.values():
            if i.get()[1] is not None and i.get()[3] == "Закрыто":
                summ += abs(i.get()[1] - i.get()[0])
                counter += 1
        summ /= counter
        return summ


class PlotRequestsByTime(object):
    def __init__(self, requests):
        self.array = dict(requests)

    def make_plot(self):
        requests_by_weeks = {}
        requests_by_years = {}
        requests_by_months = {}
        requests_by_quarters = {}

        date_end = datetime(date_begin.year, 1, 1, 0, 0, 0, 0)

        for i in self.array.values():
            if requests_by_months.get(datetime(i.get()[0].year, i.get()[0].month, 1)) is None:
                requests_by_months[datetime(i.get()[0].year, i.get()[0].month, 1)] = 1
            else:
                requests_by_months[datetime(i.get()[0].year, i.get()[0].month, 1)] += 1

            if requests_by_years.get(datetime(i.get()[0].year, 1, 1)) is None:
                requests_by_years[datetime(i.get()[0].year, 1, 1)] = 1
            else:
                requests_by_years[datetime(i.get()[0].year, 1, 1)] = 1
        
