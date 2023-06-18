import datetime

from matplotlib import use, rcParams, pyplot as plt
from matplotlib.pyplot import subplots, show, text, xticks
import matplotlib.dates as mdates
use("QtAgg")

months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь",
          "Ноябрь", "Декабрь"]


class PlotThreeYears(object):
    def __init__(self, data, first_year, second_year, third_year):
        rcParams.update({'font.size': 8})

        fig, axes = subplots(nrows=1, ncols=1, num="Поступившие заявки на " + str(datetime.datetime.today().date())
                                                   + ". Сравнение 3-х лет.")

        stop = 12
        for i in reversed(data[0].keys()):
            if data[0][i] != 0:
                stop = i.month - 1
                break
        axes.plot(months[:stop + 1], list(data[0].values())[:stop + 1], linestyle='solid',
                  label=first_year, marker="o")
        axes.plot(months, data[1].values(), linestyle='solid', label=second_year,
                  marker="o")
        axes.plot(months, data[2].values(), linestyle='solid', label=third_year,
                  marker="o")
        axes.set_ylabel('Количество поступивших, шт')
        axes.set_xlabel('Время, месяцы')
        axes.set_title("Поступившие заявки на " + str(datetime.datetime.today().date())
                       + ".\nСравнение 3-х лет")
        axes.legend()
        axes.grid(True)
        xticks(rotation=45, ha='right')
        show()


class PlotAverageTime(object):
    def __init__(self, array: dict, title: str):
        fig, axes = subplots(nrows=1, ncols=1, num='Скорость закрытия заявок')
        axes.plot(array.keys(), array.values(), marker='o')
        rcParams.update({'font.size': 8})

        for i in array.keys():
            axes.annotate("  " + str(array[i]) + " дней", [i, array[i]])
        axes.set_title(title)
        axes.set_ylabel('Средний срок закрытия, дни')
        axes.set_xlabel('Время, месяцы')
        xticks(rotation=45, ha='right')
        axes.grid(True)
        show()


class DoneWaitReceive(object):
    def __init__(self, data, title):
        fig, axes = subplots(nrows=1, ncols=1, num=title)
        stop = len(data[0])

        for i in reversed(data[0].values()):
            if i != 0:
                break
            stop -= 1
        rcParams.update({'font.size': 8})

        axes.plot(list(data[0].keys())[:stop + 1], list(data[0].values())[:stop + 1], label='Поступившие', marker='o')
        axes.plot(list(data[1].keys())[:stop + 1], list(data[1].values())[:stop + 1], label='Незакрытые', marker='o')
        axes.plot(list(data[2].keys())[:stop + 1], list(data[2].values())[:stop + 1], label='Закрытые', marker='o')
        
        axes.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        axes.xaxis.set_major_formatter(mdates.DateFormatter('%m'))

        axes.legend()
        axes.grid(True)

        axes.set_title(title)

        show()


class Pie(object):
    def __init__(self, data: dict, title: str, suptitle: str):
        fig, axes = subplots(nrows=1, ncols=1, num=title)
        rcParams.update({'font.size': 8})

        if sum(data.values()) == 0:
            axes.pie([1], colors=['white'])
            text(0, -1.25, "Заявок с данными параметрами не обнаружено", fontsize='x-large', ha='center')
        else:
            labels = list(data.keys())
            for i in range(len(labels)):
                labels[i] = labels[i] + ": " + str(data[labels[i]]) + " шт" + '(' + \
                            str("%.1f" % (data[labels[i]] / sum(data.values()) * 100)) + '%)'
            explode = []
            for i in data.values():
                if sum(data.values()) == 0 or i == 0:
                    explode.append(0)
                else:
                    explode.append(0.000025 / (i / sum(data.values())))

            axes.pie(data.values(), labels=labels, explode=explode)
            rcParams.update({'font.size': 8})

            axes.axis('equal')
            text(0, -1.25, 'Всего заявок:' + str(sum(data.values())), fontsize='x-large', ha='center')
            fig.suptitle(suptitle)
        show()
