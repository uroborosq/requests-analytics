from datetime import datetime
from datetime import timedelta


def __sunday__(to_sunday):
    return (to_sunday + timedelta(6 - to_sunday.weekday(), 0, 0, 0, 0, 0, 0)).date()


def __time_iter__(date, type_period):
    if type_period == "year":
        return datetime(date.year + 1, 1, 1)
    elif type_period == "month":
        if date.month != 12:
            return datetime(date.year, date.month + 1, 1)
        else:
            return datetime(date.year + 1, 1, 1)
    elif type_period == "week":
        return date + timedelta(7, 0, 0, 0, 0, 0, 0)
    elif type_period == "quarter":
        if date.month == 4:
            return datetime(date.year + 1, 1, 1)
        else:
            return datetime(date.year, date.month + 1, 1)


def __fix_array__(array, type_period):
    begin = list(array.keys())[0]
    end = list(array.keys())[len(array.keys()) - 1]
    while begin != end:
        if array.get(begin) is None:
            array[begin] = 0
        begin = __time_iter__(begin, type_period)
    return array


def __sort_by_date__(array):
    keys = array.keys()
    keys = sorted(keys)

    new_array = {}
    for i in keys:
        new_array[i] = array[i]
    return new_array


def __init_dict__(array, year):
    for i in range(12):
        array[datetime(year, i + 1, 1)] = 0


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
        self.requests_by_weeks = {}
        self.done_requests_by_weeks = {}
        self.__init_dict()

        for i in self.array.values():
            if i.get()[1] is not None and i.get()[5] == "Закрыто" and i.get()[1].year == datetime.today().year:
                if self.done_requests_by_weeks.get(__sunday__(i.get()[1].date())) is None:
                    self.done_requests_by_weeks[__sunday__(i.get()[1].date())] = 1
                else:
                    self.done_requests_by_weeks[__sunday__(i.get()[1].date())] += 1

    def __init_dict(self):
        pointer = __sunday__(datetime(datetime.today().year, 1, 1))
        while pointer.year == datetime.today().year:
            self.done_requests_by_weeks[pointer] = 0
            pointer = __time_iter__(pointer, 'week')

    def get(self):
        return [self.requests_by_weeks, self.done_requests_by_weeks]


class PlotThreeYears(object):

    def __init__(self, array):
        self.current_year = datetime.today().year
        self.array = dict(array)
        self.year0 = {}
        self.year1 = {}
        self.year2 = {}
        __init_dict__(self.year0, self.current_year)
        __init_dict__(self.year1, self.current_year - 1)
        __init_dict__(self.year2, self.current_year - 2)
        print(self.year2)

        for i in self.array.values():
            if i.get()[0].year == self.current_year:
                self.year0[datetime(i.get()[0].year, i.get()[0].month, 1)] += 1

            elif i.get()[0].year == self.current_year - 1:
                self.year1[datetime(i.get()[0].year, i.get()[0].month, 1)] += 1

            elif i.get()[0].year == self.current_year - 2:
                self.year2[datetime(i.get()[0].year, i.get()[0].month, 1)] += 1

        # __fix_array__(self.year0, "month")
        # __fix_array__(self.year1, "month")
        # __fix_array__(self.year2, "month")
        # __sort_by_date__(self.year0)
        # __sort_by_date__(self.year1)
        # __sort_by_date__(self.year2)

    def get(self):
        return [self.year0, self.year1, self.year2, self.current_year]


class PlotAverageTime(object):
    def __init__(self, array):
        self.array = dict(array)
        self.year = {}
        for i in range(12):
            self.year[datetime(datetime.today().year, i + 1, 1)] = []

        for i in self.array.values():
            if i.get()[1] != '':
                if str(i.get()[5]).find('Закрыто') != -1 and i.get()[1].year == datetime.today().year:
                    self.year[datetime(i.get()[1].year, i.get()[1].month, 1)].append(abs(i.get()[1] - i.get()[0]))

        self.months_time = {}
        self.months_number = {}
        print(self.year)

        for i in self.year.keys():
            summ = timedelta(0, 0, 0, 0, 0)
            for j in self.year[i]:
                summ += j
            if len(self.year[i]) != 0:
                self.months_time[i] = (summ / len(self.year[i])).days
                self.months_number[i] = len(self.year[i])

    def get(self):
        return [self.months_time, self.months_number]


class PieTypesRequests(object):
    def __init__(self, array):
        self.array = dict(array)

        self.types_total = {}
        self.types_year = {}
        self.types_month = {}

        for i in self.array.values():
            if i.get()[5] != 'Закрыто':
                if self.types_total.get(i.get()[3]) is None:
                    self.types_total[i.get()[3]] = 1
                else:
                    self.types_total[i.get()[3]] += 1


    def get(self):
        return self.types_total


class FindWarrantyNearToEnd(object):
    def __init__(self, array):
        output_file = open('ГарантияИстекаетСрок.txt', 'w')
        for i in array.values():
            if i.get()[4] == 'Гарантия' and i.get()[5] != 'Закрыто' \
                    and timedelta(45, 0, 0, 0, 0) >= datetime.today() - i.get()[0] >= timedelta(30, 0, 0, 0, 0):
                output_file.write(i.get()[2] + '\n')


class FindDelayProvider(object):
    def __init__(self, array):
        output_file = open('ПросрочкаПоставщика.txt', 'w')
        for i in array.values():
            if i.get()[4] != 'Гарантия' and i.get()[3] == 'Заказаны запчасти' \
                    and datetime.today() - i.get()[0] >= timedelta(180, 0, 0, 0, 0):
                output_file.write(i.get()[2] + '\n')


class PlotTypesClients(object):
    def __init__(self, array):
        self.types = {}

        for i in array.values():
            tmp = i.get()[4] if i.get()[4] is not None else 'Не указано менеджером'
            if self.types.get(tmp) is None:
                self.types[tmp] = 1
            else:
                self.types[tmp] += 1

    def get(self):
        return self.types


class PieManagers(object):
    def __init__(self, array, names):
        self.managers = {}
        for i in names:
            self.managers.fromkeys(i, 0)

        for i in array.values():
            if i.get()[0] >= datetime(datetime.today().year, datetime.today().month, 1):
                tmp = 'Ошибки заполнения'
                if i.get()[6] is not None:
                    for j in names:
                        if i.get()[6].find(j) != -1:
                            tmp = j

                if self.managers.get(tmp) is None:
                    self.managers[tmp] = 1
                else:
                    self.managers[tmp] += 1

    def get(self):
        return self.managers


class ClientsCounter(object):
    def __init__(self, array):
        self.clients = {}

        for i in array.values():
            if i.get()[0] > datetime(datetime.today().year, 1, 1):
                if i.get()[7] is None:
                    print(0)
                    self.clients['Клиент не указан'] = 1
                else:
                    self.clients[i.get()[7]] = 1

    def get(self):
        return len(self.clients)


class PlotNotDoneRequests(object):
    def __init_dict(self):
        pointer = __sunday__(datetime(datetime.today().year, 1, 1))
        while pointer.year == datetime.today().year:
            self.requests[pointer] = 0
            pointer = __time_iter__(pointer, 'week')

    def __init__(self, array):
        cur_year = datetime.today().year
        self.requests = {}
        self.__init_dict()
        for i in array.values():
            if i.get()[0].year == cur_year and i.get()[5] == 'Закрыто':
                pointer = __sunday__(i.get()[0])
                while pointer < i.get()[1].date():
                    self.requests[pointer] += 1
                    pointer = __time_iter__(pointer, 'week')
            elif i.get()[0].year == cur_year and i.get()[5] != 'Закрыто':
                pointer = __sunday__(i.get()[0])
                while pointer < datetime.today().date():
                    self.requests[pointer] += 1
                    pointer = __time_iter__(pointer, 'week')

    def get(self):
        return self.requests

#
# class FindRepeats(object):
#     def __init__(self, data):
#
#         for i in data.values():
#
