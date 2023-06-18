import enum
from datetime import datetime
from datetime import date
from datetime import timedelta

from fs import settings
import pandas as pd


def __sunday__(to_sunday: datetime) -> date:
    return (to_sunday + timedelta(6 - to_sunday.weekday(), 0, 0, 0, 0, 0, 0)).date()

def __first_month_day__(to_first: datetime) -> date:
    return datetime(to_first.year, to_first.month, 1).date()

class TimePeriod(enum.Enum):
    week = 1
    month = 2

def __fill_gaps_with_zeros__(df: pd.DataFrame, period: TimePeriod) -> pd.DataFrame:
    time_period = None
    match period:
        case TimePeriod.month:
            time_period = 'MS'
        case TimePeriod.week:
            time_period = 'W'

    idx = pd.date_range(df.index[0], df.index[-1], freq=time_period)
    return df.reindex(idx, fill_value=0)


class AbstractAnalyzer:
    __df__: pd.DataFrame

    def __init__(self, df: pd.DataFrame) -> None:
        self.__df__ = df

    def get(self) -> pd.DataFrame:
        pass


class ManagersAnalyzer(AbstractAnalyzer):
    def get(self) -> pd.DataFrame:
        return self.__df__.groupby(['Исполнитель'])['Исполнитель'].count()


class DoneRequestsAnalyzer(AbstractAnalyzer):
    def get(self) -> pd.DataFrame:
        done = self.__df__[(self.__df__['Статус'] == 'Закрыто') & (~pd.isnull(self.__df__['Дата окончания работ']))]
        done['Дата окончания работ'] = done['Дата окончания работ'].apply(__sunday__)
        done['Дата окончания работ'] = done['Дата окончания работ'].apply(lambda x: x.date())
        return done.groupby(['Дата окончания работ'])['Дата окончания работ'].count()


class ReceivedRequestsWeeksAnalyzer(AbstractAnalyzer):
    def get(self) -> pd.DataFrame:
        self.__df__['Дата окончания работ'] = self.__df__['Дата окончания работ'].apply(__sunday__)
        self.__df__['Дата окончания работ'] = self.__df__['Дата окончания работ'].apply()
        return self.__df__.groupby(['Дата окончания работ'])['Дата окончания работ'].count()


class ReceivedRequestsMonthAnalyzer(AbstractAnalyzer):
    def get(self) -> pd.DataFrame:
        self.__df__['Дата окончания работ'] = self.__df__['Дата окончания работ'].apply(__first_month_day__)
        self.__df__['Дата окончания работ'] = self.__df__['Дата окончания работ'].apply(lambda x: x.date())
        return self.__df__.groupby(['Дата окончания работ'])['Дата окончания работ'].count()


class WaitingRequestAnalyzer(AbstractAnalyzer):
    def get(self) -> pd.DataFrame:
        index = pd.date_range(__sunday__(self.__df__['Дата'].min()).date(),
                              __sunday__(self.__df__['Дата окончания работ'].max().date()), freq='W')
        result = pd.Series(0, index=index)

        for index, row in self.__df__.iterrows():
            date_begin = row['Дата'].date()
            date_end = datetime.today().date()
            if row['Статус'] == 'Закрыто':
                date_end = row['Дата окончания работ'].date()

            request_time_range = pd.date_range(__sunday__(date_begin), __sunday__(date_end), freq='W')
            request_time_series = pd.Series(1, index=request_time_range)
            result = result.add(request_time_series, fill_value=0).astype('Int64')

        return result


class AverageTimeAnalyzer(AbstractAnalyzer):
    def get(self) -> pd.DataFrame:
        self.__df__ = self.__df__['Дата окончания работ'].apply(__first_month_day__)
        self.__df__ = self.__df__.groupby(['Дата окончания работ'])

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
            if i.date_end != '' and (i.manager == manager or manager == 'Все сотрудники'):
                if i.status == 'Закрыто' and not (i.date_end.month == datetime.today().month and i.date_end.year == datetime.today().year):
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
            if i.status != 'Закрыто' and (i.manager == manager or manager == 'Все сотрудники'):
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
            if i.date_begin.date() >= begin and (i.manager == manager or manager == 'Все сотрудники'):
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
            if i.manager == manager or manager == 'Все сотрудники':
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
    def __init__(self, data, given_date):
        self.request = {}
        for i in data.values():
            if i.begin_working != '':
                if i.begin_working.date() == given_date.date():
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
            if i.status != 'Закрыто' and i.date_begin.date() >= begin and (i.manager == manager or manager == 'Все сотрудники'):
                if not exclude_requests or i.warranty == "Внутренние работы":

                    if self.requests.get(i.priority) is not None:
                        self.requests[i.priority].append(i.id)
                    else:
                        self.requests['Неизвестный тип или не заполнено'].append(i.id)

        for i in self.requests:
            file.write(i + ':\n')
            for j in self.requests[i]:
                file.write(j + '\n')
        to_remove = []
        for i in self.requests:
            self.requests[i] = len(self.requests[i])
            if self.requests[i] == 0:
                to_remove.append(i)
        for i in to_remove:
            self.requests.pop(i)

    def get(self):
        return self.requests


def find_min_date(array: dict):
    min = datetime.max
    for i in array.values():
        if i.date_begin < min:
            min = i.date_begin
    return min.date()