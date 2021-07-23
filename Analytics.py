from datetime import datetime
from datetime import timedelta


def __sunday__(to_sunday):
    return to_sunday + timedelta(6 - to_sunday.weekday(), 0, 0, 0, 0, 0, 0)


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


class DoneRequests(object):
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
        pointer = __sunday__(datetime(datetime.today().year, 1, 1)).date()
        while pointer.year == datetime.today().year:
            self.done_requests_by_weeks[pointer] = 0
            pointer = __time_iter__(pointer, 'week')

    def get(self):
        return [self.requests_by_weeks, self.done_requests_by_weeks]


class AllRequestsThreeYears(object):
    def __init__(self, array):
        self.current_year = datetime.today().year

        self.year0 = {}
        self.year1 = {}
        self.year2 = {}
        __init_dict__(self.year0, self.current_year)
        __init_dict__(self.year1, self.current_year - 1)
        __init_dict__(self.year2, self.current_year - 2)
        print(self.year2)

        for i in array.values():
            if i.get()[0].year == self.current_year and i.get()[0].month != datetime.today().month:
                self.year0[datetime(i.get()[0].year, i.get()[0].month, 1)] += 1

            elif i.get()[0].year == self.current_year - 1:
                self.year1[datetime(i.get()[0].year, i.get()[0].month, 1)] += 1

            elif i.get()[0].year == self.current_year - 2:
                self.year2[datetime(i.get()[0].year, i.get()[0].month, 1)] += 1

    def get(self):
        return [self.year0, self.year1, self.year2, self.current_year]


class AverageTime(object):
    def __init__(self, array):
        self.array = dict(array)
        self.year = {}
        for i in range(12):
            self.year[datetime(datetime.today().year, i + 1, 1)] = []

        for i in self.array.values():
            if i.get()[1] != '':
                if str(i.get()[5]).find('Закрыто') != -1 and i.get()[1].year == datetime.today().year \
                        and i.get()[1].month != datetime.today().month:
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


class Phases(object):
    def __init__(self, data):
        types_total = {}

        for i in data.values():
            if i.get()[5] != 'Закрыто':
                if types_total.get(i.get()[3]) is None:
                    types_total[i.get()[3]] = 1
                else:
                    types_total[i.get()[3]] += 1

        self.sorted_dict = {}
        sorted_keys = reversed(sorted(types_total, key=types_total.get))
        for i in sorted_keys:
            self.sorted_dict[i] = types_total[i]

    def get(self):
        return self.sorted_dict


class Warranty(object):
    def __init__(self, array, **kwargs):
        output_file = open('ГарантияИстекаетСрок' + str(datetime.today()) + '.txt', 'w')

        if kwargs.get('first') is not None and kwargs.get('second') is not None:
            for i in array.values():
                if i.get()[4] == 'Гарантия' and i.get()[5] != 'Закрыто' \
                        and timedelta(eval(kwargs['second']), 0, 0, 0, 0) >= datetime.today() - i.get()[0]\
                        >= timedelta(eval(kwargs['first']), 0, 0, 0, 0):
                    output_file.write(i.get()[2] + ' - ' + str((datetime.today() - i.get()[0])) + '\n')
        elif kwargs.get('begin') is not None and kwargs.get('end') is not None:
            for i in array.values():
                if i.get()[4] == 'Гарантия' and i.get()[5] != 'Закрыто' \
                        and datetime.strptime(kwargs['end'], '%d.%m.%Y') >= i.get()[0] \
                        >= datetime.strptime(kwargs['begin'], '%d.%m.%Y'):
                    output_file.write(i.get()[2] + ' - ' + str((datetime.today() - i.get()[0])) + ' '
                                      + str(i.get()[0]) + '\n')
        else:
            raise KeyError('Некорректные данные')


class DelayProvider(object):
    def __init__(self, array):
        output_file = open('ПросрочкаПоставщика.txt', 'w')
        for i in array.values():
            if i.get()[4] != 'Гарантия' and i.get()[3] == 'Заказаны запчасти' \
                    and datetime.today() - i.get()[0] >= timedelta(180, 0, 0, 0, 0):
                output_file.write(i.get()[2] + ' - ' + str((datetime.today() - i.get()[0]).days) + 'дней\n')


class Types(object):
    def __init__(self, array):
        types = {}

        for i in array.values():
            tmp = i.get()[4] if i.get()[4] is not None else 'Не указано'
            if types.get(tmp) is None:
                types[tmp] = 1
            else:
                types[tmp] += 1

        self.sorted_dict = {}
        self.final = {}
        sorted_keys = list(reversed(sorted(types, key=types.get)))
        for i in range(len(types) // 2):
            self.sorted_dict[sorted_keys[i]] = types[sorted_keys[i]]
            self.sorted_dict[sorted_keys[- i - 1]] = types[sorted_keys[- i - 1]]
        if len(self.sorted_dict) < len(sorted_keys):
            self.sorted_dict[sorted_keys[len(types) // 2 + 1]] = types[sorted_keys[len(types) // 2 + 1]]

    def get(self):
        return self.sorted_dict


class Managers(object):
    def __init__(self, array, names, date_begin, date_end):
        self.managers = {}
        is_full = False if names == '' else True
        for i in names.split(','):
            self.managers[i] = 0

        if date_begin == '':
            date_begin = datetime.min.date()
        if date_end == '':
            date_end = datetime.max.date()

        for i in array.values():
            if date_end >= i.get()[0].date() >= date_begin:
                tmp = 'Ошибки заполнения'
                if i.get()[6] is not None and is_full:
                    for j in names.split(','):
                        if i.get()[6].find(j) != -1:
                            tmp = j
                elif i.get()[6] is not None:
                    tmp = i.get()[6]

                if self.managers.get(tmp) is None:
                    self.managers[tmp] = 1
                else:
                    self.managers[tmp] += 1

        tmp = []
        for i in self.managers.keys():
            if self.managers[i] == 0:
                tmp.append(i)
        for i in tmp:
            del self.managers[i]

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


class WaitingRequests(object):
    def __init_dict(self):
        pointer = __sunday__(datetime(datetime.today().year, 1, 1)).date()
        while pointer.year == datetime.today().year:
            self.requests[pointer] = 0
            pointer = __time_iter__(pointer, 'week')

    def __init__(self, array):
        cur_year = datetime.today().year
        self.requests = {}
        self.__init_dict()
        for i in array.values():
            if i.get()[0].year == cur_year and i.get()[5] == 'Закрыто':
                pointer = __sunday__(i.get()[0]).date()
                while pointer < i.get()[1].date():
                    self.requests[pointer] += 1
                    pointer = __time_iter__(pointer, 'week')
            elif i.get()[0].year == cur_year and i.get()[5] != 'Закрыто':
                pointer = __sunday__(i.get()[0]).date()
                while pointer < datetime.today().date():
                    self.requests[pointer] += 1
                    pointer = __time_iter__(pointer, 'week')

    def get(self):
        return self.requests
