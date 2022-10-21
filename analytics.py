import json
from datetime import datetime
from datetime import date
from datetime import timedelta

import files


def manager_filter(requests: dict, manager: str) -> dict:
    if manager == 'Все':
        return requests
    filtered = {}
    for i in requests:
        if requests[i].manager == manager:
            filtered[i] = requests[i]
    return filtered


def warranty_type_filter(requests: dict, type: list[str]) -> dict:
    filtered = {}
    for i in requests:
        if requests[i].warranty in type:
            filtered[i] = requests[i]

    return filtered


def __sunday__(to_sunday):
    return to_sunday + timedelta(6 - to_sunday.weekday(), 0, 0, 0, 0, 0, 0)


def __time_iter__(old_date, type_period):
    if type_period == "year":
        return datetime(old_date.year + 1, 1, 1)
    elif type_period == "month":
        if old_date.month != 12:
            return datetime(old_date.year, old_date.month + 1, 1).date()
        else:
            return datetime(old_date.year + 1, 1, 1).date()
    elif type_period == "week":
        return old_date + timedelta(7, 0, 0, 0, 0, 0, 0)
    elif type_period == "quarter":
        if old_date.month == 4:
            return datetime(old_date.year + 1, 1, 1)
        else:
            return datetime(old_date.year, old_date.month + 1, 1)


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


def __init_dict__(array: dict, date_begin: date, date_end: date, mode, value):
    if mode == 'month':
        pointer = datetime(date_begin.year, date_begin.month, 1).date()
        while pointer <= date_end:
            array[pointer] = value
            if pointer.month != 12:
                pointer = datetime(pointer.year, pointer.month + 1, 1).date()
            else:
                pointer = datetime(pointer.year + 1, 1, 1).date()
    elif mode == 'week':
        pointer = __sunday__(date_begin)
        while pointer <= date_end:
            array[pointer] = value
            pointer = __time_iter__(pointer, 'week')
        array[pointer] = value
    return array


class Managers(object):
    def __init__(self, data: dict):
        self.managers = []

        for i in data.values():
            if i.manager not in self.managers:
                self.managers.append(i.manager)
        self.managers.remove(None)
        self.managers.append('Не выбран')

    def get(self):
        return self.managers


class Done:
    def __init__(self, requests, date_begin, date_end, manager, exclude_requests):
        self.array = dict(requests)
        self.requests = {}
        __init_dict__(self.requests, date_begin, date_end, 'week', 0)

        for i in self.array.values():
            if i.date_end != '' and i.status == "Закрыто":
                if date_begin <= i.date_end.date() <= date_end:
                    if i.manager == manager or manager == 'Все':
                        if not exclude_requests or i.warranty == "Внутренние работы":
                            self.requests[__sunday__(i.date_end.date())] += 1

    def get(self):
        return self.requests


class Received(object):
    def __init__(self, array, mode, date_begin, date_end, manager, exclude_requests: bool):
        self.year = {}
        __init_dict__(self.year, date_begin, date_end, mode, 0)

        for i in array.values():
            if date_begin <= i.date_begin.date() <= date_end and (i.manager == manager or manager == 'Все'):
                if not exclude_requests or i.warranty == "Внутренние работы":
                    if mode == 'month':
                        self.year[datetime(
                            i.date_begin.year, i.date_begin.month, 1).date()] += 1
                    elif mode == 'week':
                        self.year[__sunday__(i.date_begin.date())] += 1

    def get(self):
        return self.year


class Waiting(object):
    def __init__(self, array, date_begin, date_end, manager, mode, exclude_requests: bool):
        self.requests = {}
        __init_dict__(self.requests, date_begin, date_end, mode, 0)
        if mode == 'week':
            for i in array.values():
                if i.manager == manager or manager == 'Все':
                    if i.status == 'Закрыто' and i.date_end != '':
                        if i.date_end.date() <= date_end:
                            if not exclude_requests or i.warranty == "Внутренние работы":
                                pointer = __sunday__(i.date_begin).date()
                                while pointer < i.date_end.date():
                                    if self.requests.get(pointer) is not None:
                                        self.requests[pointer] += 1
                                    pointer = __time_iter__(pointer, 'week')
                    elif i.status != 'Закрыто':
                        pointer = __sunday__(i.date_begin).date()
                        while pointer < datetime.today().date():
                            if self.requests.get(pointer) is not None:
                                self.requests[pointer] += 1
                            pointer = __time_iter__(pointer, 'week')
        elif mode == 'month':
            for i in array.values():
                if i.manager == manager or manager == 'Все':
                    if i.status == 'Закрыто' and i.date_end != '':
                        if i.date_end >= date_end:
                            pointer = __time_iter__(i.date_begin.date(), "month")
                            while pointer < i.date_end.date():
                                if self.requests.get(pointer) is not None:
                                    self.requests[pointer] += 1
                                pointer = __time_iter__(pointer, mode)

                    elif i.status != 'Закрыто':
                        pointer = __sunday__(i.date_begin).date()
                        while pointer < datetime.today().date():
                            if self.requests.get(pointer) is not None:
                                self.requests[pointer] += 1
                            pointer = __time_iter__(pointer, mode)

    def get(self):
        return self.requests


class AverageTime(object):
    def __init__(self, array: dict, manager, begin, end, exclude_requests: bool):
        self.year = {}
        pointer = datetime(begin.year, begin.month, 1).date()
        while pointer <= end:
            self.year[pointer] = []
            if pointer.month != 12:
                pointer = datetime(pointer.year, pointer.month + 1, 1).date()
            else:
                pointer = datetime(pointer.year + 1, 1, 1).date()

        for i in array.values():
            if i.date_end != '' and (i.manager == manager or manager == 'Все'):
                if i.status == 'Закрыто' and i.date_end.month != datetime.today().month:
                    if not exclude_requests or i.warranty == "Внутренние работы":
                        if self.year.get(datetime(i.date_end.year, i.date_end.month, 1).date()) is not None:
                            self.year[date(i.date_end.year, i.date_end.month, 1)].append(abs(i.date_end - i.date_begin))

        self.months_time = {}
        self.months_number = {}

        for i in self.year.keys():
            if begin <= i <= end:
                time_sum = timedelta(0, 0, 0, 0, 0)
                for j in self.year[i]:
                    time_sum += j
                if len(self.year[i]) != 0:
                    self.months_time[i] = (time_sum / len(self.year[i])).days
                    self.months_number[i] = len(self.year[i])

        self.months_time = __sort_by_date__(self.months_time)

    def get(self):
        return self.months_time


class Phases(object):
    def __init__(self, data, date_begin, manager, exclude_requests: bool):
        types_total = {}
        for i in data.values():
            if i.status != 'Закрыто' and (i.manager == manager or manager == 'Все'):
                if i.date_begin.date() >= date_begin:
                    if not exclude_requests or i.warranty == "Внутренние работы":
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
    def __init__(self, array, begin, manager):
        output_file = open('ГарантияИстекаетСрок' + str(datetime.today().strftime('%d-%m-%Y-%H-%M')) + '.txt', 'w')
        self.types = {}
        for i in array.values():
            if i.date_begin.date() >= begin and (i.manager == manager or manager == 'Все'):
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
    def __init__(self, array, begin, end, manager):
        types = {}
        self.begin = begin
        self.end = end
        for i in array.values():
            if i.manager == manager or manager == 'Все':
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
        return self.sorted_dict


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
        self.request = {}
        for i in data.values():
            if i.begin_working != '':
                if i.begin_working.date() == date.date():
                    if self.request.get(i.id) is None:
                        self.request[i.id] = [[i.engineer, i.warranty, i.address]]
                    else:
                        self.request[i.id].append([i.engineer, i.warranty, i.address])

    def get(self):
        return self.request


class RequestRepeats(object):
    def __init__(self, data):
        self.requests = {}
        file = open("Повторы.txt", 'w')
        for i in data.values():
            key = (i.model, i.address)
            if self.requests.get(key) is not None:
                if len(self.requests[key]) == 1:
                    self.requests[key].append([i.id, i.date_begin])
                elif len(self.requests[key]) == 2:
                    if datetime.today() - i.date_begin <= timedelta(45) and i.address.lower().find(
                            'ремзона') == -1 and i.address.lower().find('сц') == -1 and i.address.lower().find(
                            'сервис центр'):
                        self.requests[key].append([i.id, i.date_begin])
                        file.write('Модель: ' + i.model + ', адрес: ' + i.address + '\n')
                        for it in self.requests[key]:
                            file.write('Наряд-заказ: ' + it[0] + ', дата открытия: ' + str(it[1]) + '\n')
            else:
                self.requests[key] = [[i.id, i.date_begin]]


class Priority(object):
    def __init__(self, data, begin, manager, exclude_requests: bool):
        self.requests = files.get_settings()[3]
        self.requests['Неизвестный тип или не заполнено'] = []
        file = open('Приоритеты.txt', 'w')

        for i in data.values():
            if i.status != 'Закрыто' and i.date_begin.date() >= begin and (i.manager == manager or manager == 'Все'):
                if not exclude_requests or i.warranty == "Внутренние работы":

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


def find_min_date(array: dict):
    min = datetime.max
    for i in array.values():
        if i.date_begin < min:
            min = i.date_begin
    return min.date()
