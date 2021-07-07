from Request import Request
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
from collections import OrderedDict


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

    def __sunday__(self, to_sunday):
        return to_sunday + timedelta(6 - to_sunday.weekday(), 0, 0, 0, 0, 0, 0)

    def __collect__(self):
        self.requests_by_weeks = {}
        self.requests_by_years = {}
        self.requests_by_months = {}
        self.requests_by_quarters = {}

        self.done_requests_by_weeks = {}
        self.done_requests_by_months = {}
        self.done_requests_by_years = {}
        self.done_requests_by_quarters = {}


        for i in self.array.values():
            if self.requests_by_months.get(datetime(i.get()[0].year, i.get()[0].month, 1)) is None: #months
                self.requests_by_months[datetime(i.get()[0].year, i.get()[0].month, 1)] = 1
            else:
                self.requests_by_months[datetime(i.get()[0].year, i.get()[0].month, 1)] += 1

            if self.requests_by_years.get(datetime(i.get()[0].year, 1, 1)) is None: #years
                self.requests_by_years[datetime(i.get()[0].year, 1, 1)] = 1
            else:
                self.requests_by_years[datetime(i.get()[0].year, 1, 1)] += 1

            if self.requests_by_quarters.get(datetime(i.get()[0].year, int(i.get()[0].month / 4) + 1, 1)) is None: #quarters
                self.requests_by_quarters[datetime(
                    i.get()[0].year, int(i.get()[0].month / 4) + 1, 1)] = 1
            else:
                self.requests_by_quarters[datetime(
                    i.get()[0].year, int(i.get()[0].month / 4) + 1, 1)] += 1

            if self.requests_by_weeks.get(self.__sunday__(i.get()[0].date())) is None: #weeks
                self.requests_by_weeks[self.__sunday__(i.get()[0].date())] = 1
            else:
                self.requests_by_weeks[self.__sunday__(i.get()[0].date())] += 1

            if i.get()[1] is not None and i.get()[3] == "Закрыто":
                if self.done_requests_by_weeks.get(self.__sunday__(i.get()[1].date())) is None:
                    self.done_requests_by_weeks[self.__sunday__(i.get()[1].date())] = 1
                else:
                    self.done_requests_by_weeks[self.__sunday__(i.get()[1].date())] += 1

                if self.done_requests_by_months.get(datetime(i.get()[1].year, i.get()[1].month, 1)) is None: #months
                    self.done_requests_by_months[datetime(i.get()[1].year, i.get()[1].month, 1)] = 1
                else:
                    self.done_requests_by_months[datetime(i.get()[1].year, i.get()[1].month, 1)] += 1

                if self.done_requests_by_years.get(datetime(i.get()[1].year, 1, 1)) is None: #years
                    self.done_requests_by_years[datetime(i.get()[1].year, 1, 1)] = 1
                else:
                    self.done_requests_by_years[datetime(i.get()[1].year, 1, 1)] += 1

                if self.done_requests_by_quarters.get(datetime(i.get()[1].year, int(i.get()[1].month / 4) + 1, 1)) is None: #quarters
                    self.done_requests_by_quarters[datetime(
                        i.get()[1].year, int(i.get()[1].month / 4) + 1, 1)] = 1
                else:
                    self.done_requests_by_quarters[datetime(
                        i.get()[1].year, int(i.get()[1].month / 4) + 1, 1)] += 1

    def __time_iter__(self, date, type):
        if type == "year":
            return datetime(date.year + 1, 1, 1)
        elif type == "month":
            if date.month != 12:
                return datetime(date.year, date.month + 1, 1)
            else:
                return datetime(date.year + 1, 1, 1)
        elif type == "week":
            return date + timedelta(7, 0, 0, 0, 0, 0, 0)
        elif type == "quarter":
            if date.month == 4:
                return datetime(date.year + 1, 1, 1)
            else:
                return datetime(date.year, date.month + 1, 1)


    def __fix_array__(self, array, type):
        begin = list(array.keys())[0]
        end = list(array.keys())[len(array.keys()) - 1]
        while begin != end:
            if array.get(begin) is None:
                array[begin] = 0
            begin = self.__time_iter__(begin, type)
        return array


    def __prepare_data__(self):
        self.__fix_array__(self.requests_by_years, "year")
        self.__fix_array__(self.requests_by_weeks, "week")
        self.__fix_array__(self.requests_by_months, "month")
        self.__fix_array__(self.requests_by_quarters, "quarter")
        self.__fix_array__(self.done_requests_by_weeks, "week")

    def make_plot(self):
        self.__collect__()
        self.__prepare_data__()

        a = sorted(list(self.requests_by_weeks.keys()))
        b = sorted(list(self.done_requests_by_weeks.keys()))
        new = {}
        new_again = {}
        for i in a:
            new[i] = self.requests_by_weeks[i]
        for i in b:
            new_again[i] = self.done_requests_by_weeks[i]
        sum1 = 0
        sum2 = 0

        for i in new.values():
            sum1 += i
        for i in new_again.values():
            sum2 += i
        print(sum1 - sum2)
        
        plt.plot_date(a, new.values(), linestyle='solid', label = 'Поступило')
        plt.plot_date(b, new_again.values(), linestyle='solid', label = 'Выполнено')
        plt.legend()
        plt.grid(True)
        plt.show()
