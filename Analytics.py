import json
from datetime import datetime
from datetime import timedelta

import files


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


def __init_dict__(array, year, mode, value):
    if mode == 'month':
        for i in range(12):
            array[datetime(year, i + 1, 1)] = value
    elif mode == 'week':
        pointer = __sunday__(datetime(datetime.today().year, 1, 1)).date()
        while pointer.year == datetime.today().year:
            array[pointer] = value
            pointer = __time_iter__(pointer, 'week')
    return array


class Done(object):
    def __init__(self, requests):
        self.array = dict(requests)
        self.requests = {}
        __init_dict__(self.requests, datetime.today().year, 'week', 0)

        for i in self.array.values():
            if i.date_end != '' and i.status == "Закрыто" and i.date_end.year == datetime.today().year:
                self.requests[__sunday__(i.date_end.date())] += 1

    def get(self):
        return self.requests


class Received(object):
    def __init__(self, array, year, mode):
        self.year = {}
        __init_dict__(self.year, year, mode, 0)

        for i in array.values():
            if i.date_begin.year == year:
                if mode == 'month':
                    self.year[datetime(i.date_begin.year, i.date_begin.month, 1)] += 1
                elif mode == 'week':
                    self.year[__sunday__(i.date_begin.date())] += 1

    def get(self):
        return self.year


class Waiting(object):
    def __init__(self, array):
        cur_year = datetime.today().year
        self.requests = {}
        __init_dict__(self.requests, datetime.today().year, 'week', 0)

        for i in array.values():
            if i.date_begin.year == cur_year and i.status == 'Закрыто'\
                    and i.date_end != '':

                pointer = __sunday__(i.date_begin).date()
                while pointer < i.date_end.date():
                    self.requests[pointer] += 1
                    pointer = __time_iter__(pointer, 'week')

            elif i.date_begin.year == cur_year and i.status != 'Закрыто':

                pointer = __sunday__(i.date_begin).date()
                while pointer < datetime.today().date():
                    self.requests[pointer] += 1
                    pointer = __time_iter__(pointer, 'week')

    def get(self):
        return self.requests


class AverageTime(object):
    def __init__(self, array):
        self.array = dict(array)
        self.year = {}
        for i in range(12):
            self.year[datetime(datetime.today().year, i + 1, 1)] = list()
        #self.year = __init_dict__(self.year, datetime.today().year, 'month', [])

        for i in self.array.values():
            if i.date_end != '':
                if str(i.status).find('Закрыто') != -1 and i.date_end.year == datetime.today().year \
                        and i.date_end.month != datetime.today().month:
                    self.year[datetime(i.date_end.year, i.date_end.month, 1)].append(abs(i.date_end - i.date_begin))

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
            if i.status != 'Закрыто':
                if types_total.get(i.phase) is None:
                    types_total[i.phase] = 1
                else:
                    types_total[i.phase] += 1

        self.sorted_dict = {}
        sorted_keys = reversed(sorted(types_total, key=types_total.get))
        for i in sorted_keys:
            self.sorted_dict[i] = types_total[i]

    def get(self):
        return self.sorted_dict


class Warranty(object):
    def __init__(self, array):
        output_file = open('ГарантияИстекаетСрок' + str(datetime.today().strftime('%d-%m-%Y-%H-%M')) + '.txt', 'w')
        self.types = {}
        for i in array.values():
            if i.warranty == 'Гарантия' and i.status != 'Закрыто':
                if timedelta(45, 0, 0, 0, 0) >= datetime.today() - i.date_begin >= timedelta(31, 0, 0, 0, 0):
                    output_file.write(i.id + ' - ' + str((datetime.today() - i.date_begin)) + '\n')
                    if self.types.get('31-45 дней') is not None:
                        self.types['31-45 дней'] += 1
                    else:
                        self.types['31-45 дней'] = 1
                elif timedelta(30, 0, 0, 0, 0) >= datetime.today() - i.date_begin >= timedelta(16, 0, 0, 0, 0):
                    output_file.write(i.id + ' - ' + str((datetime.today() - i.date_begin)) + '\n')
                    if self.types.get('16-30 дней') is not None:
                        self.types['16-30 дней'] += 1
                    else:
                        self.types['16-30 дней'] = 1
                elif timedelta(15, 0, 0, 0, 0) >= datetime.today() - i.date_begin >= timedelta(6, 0, 0, 0, 0):
                    output_file.write(i.id + ' - ' + str((datetime.today() - i.date_begin)) + '\n')
                    if self.types.get('6-15 дней') is not None:
                        self.types['6-15 дней'] += 1
                    else:
                        self.types['6-15 дней'] = 1
                elif timedelta(5, 0, 0, 0, 0) >= abs(datetime.today() - i.date_begin) >= timedelta(0, 0, 0, 0, 0):
                    output_file.write(i.id + ' - ' + str((datetime.today() - i.date_begin)) + '\n')
                    if self.types.get('0-5 дней') is not None:
                        self.types['0-5 дней'] += 1
                    else:
                        self.types['0-5 дней'] = 1
                else:
                    output_file.write(i.id + ' - ' + str((datetime.today() - i.date_begin)) + '\n')
                    if self.types.get('45+ дней') is not None:
                        self.types['45+ дней'] += 1
                    else:
                        self.types['45+ дней'] = 1

    def get(self):
        return self.types


class DelayProvider(object):
    def __init__(self, array):
        output_file = open('ПросрочкаПоставщика.txt', 'w')
        for i in array.values():
            if i.warranty != 'Гарантия' and i.phase == 'Заказаны запчасти' \
                    and datetime.today() - i.date_begin >= timedelta(180, 0, 0, 0, 0):
                output_file.write(i.id + ' - ' + str((datetime.today() - i.date_begin).days) + 'дней\n')


class Types(object):
    def __init__(self, array, begin, end):
        types = {}
        self.begin = begin
        self.end = end
        for i in array.values():
            if end >= i.date_begin.date() >= begin:
                tmp = i.warranty if i.warranty is not None else 'Не указано'
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
            self.sorted_dict[sorted_keys[len(types) // 2]] = types[sorted_keys[len(types) // 2]]

    def get(self):
        return [self.sorted_dict, self.begin, self.end]


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
            if date_end >= i.date_begin.date() >= date_begin:
                tmp = 'Ошибки заполнения'
                if i.manager is not None and is_full:
                    for j in names.split(','):
                        if i.manager.find(j) != -1:
                            tmp = j
                elif i.manager is not None:
                    tmp = i.manager

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
            if i.date_begin > datetime(datetime.today().year, 1, 1):
                if i.client is None:
                    print(0)
                    self.clients['Клиент не указан'] = 1
                else:
                    self.clients[i.client] = 1

    def get(self):
        return len(self.clients)


class DaySchedule(object):
    def __init__(self, data, date):
        self.engeenires = {}
        for i in data.values():
            if i.begin_working != '':
                if i.begin_working.date() == date.date():
                    for j in i.engineer:
                        if self.engeenires.get(j) is None:
                            self.engeenires[j] = [[i.id, i.warranty]]
                        else:
                            self.engeenires[j].append([i.id, i.warranty])

    def get(self):
        return self.engeenires


class RequestRepeats(object):
    def __init__(self, data):
        self.requests = {}
        file = open("Повторы.txt", 'w')
        for i in data.values():
            with [i.model, i.address] as key:
                if self.requests.get(key) is not None:
                    pass
                else:
                    self.requests[key] = [[i.date_begin]]


class Priority(object):
    def __init__(self, data):
        try:
            file = open('.priority_settings.json', 'r')
            self.requests = json.load(file)
            file.close()
        except FileNotFoundError:
            self.requests = files.set_default_priority()
        except json.decoder.JSONDecodeError:
            self.requests = files.set_default_priority()

        file = open('Приоритеты.txt', 'w')

        for i in data.values():
            if i.status != 'Закрыто':
                if self.requests.get(i.priority) is not None:
                    self.requests[i.priority].append(i.id)
                else:
                    self.requests['Неизвестный тип или не заполнено'].append(i.id)

        for i in self.requests:
            file.write(i + ':\n')
            for j in self.requests[i]:
                file.write(j + '\n')

        for i in self.requests:
            self.requests[i] = len(self.requests[i])

    def get(self):
        return self.requests


