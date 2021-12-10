import datetime

from matplotlib import use
from matplotlib.pyplot import subplots, show, text
import matplotlib.dates as mdates
use("Qt5Agg")

months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь",
          "Ноябрь", "Декабрь"]


class PlotThreeYears(object):
    def __init__(self, data):
        fig, axes = subplots(nrows=1, ncols=1, num="Поступившие заявки на " + str(datetime.datetime.today().date())
                                                   + ". Сравнение текущего года с 2-мя предыдущими.")
        stop = 12
        for i in reversed(data[0].keys()):
            if data[0][i] != 0:
                stop = i.month - 1
                break

        axes.plot(months[:stop + 1], list(data[0].values())[:stop + 1], linestyle='solid',
                  label=str(datetime.datetime.today().year), marker="o")
        axes.plot(months, data[1].values(), linestyle='solid', label=str(datetime.datetime.today().year - 1),
                  marker="o")
        axes.plot(months, data[2].values(), linestyle='solid', label=str(datetime.datetime.today().year - 2),
                  marker="o")
        axes.set_ylabel('Количество поступивших, шт')
        axes.set_xlabel('Время, месяцы')
        axes.set_title("Поступившие заявки на " + str(datetime.datetime.today().date())
                       + ".\nСравнение текущего года с 2-мя предыдущими.")
        axes.legend()
        axes.grid(True)

        show()


class PlotAverageTime(object):
    def __init__(self, array):
        fig, axes = subplots(nrows=1, ncols=1, num='Скорость закрытия заявок')

        axes.plot(months[:len(array[0])], array[0].values(), linestyle='solid', marker='o')
        axes.set_title('Скорость закрытия заявок. Отчет сформирован ' + str(datetime.datetime.today().date()))

        for i in array[0].keys():
            axes.annotate("  " + str(array[0][i]) + " дней", [months[i.month - 1], array[0][i]])
        axes.set_ylabel('Средний срок закрытия, дни')
        axes.set_xlabel('Время, месяцы')
        axes.grid(True)
        show()


class DoneWaitReceive(object):
    def __init__(self, data):
        fig, axes = subplots(nrows=1, ncols=1, num='Соотношение поступивших, незакрытых и закрытых заявок в ' +
                                                   str(datetime.datetime.today().year) + ' году')

        stop = len(data[0])

        for i in reversed(data[0].values()):
            if i != 0:
                break
            stop -= 1

        axes.plot(list(data[0].keys())[:stop + 1], list(data[0].values())[:stop + 1], label='Поступившие', marker='o')
        axes.plot(list(data[1].keys())[:stop + 1], list(data[1].values())[:stop + 1], label='Незакрытые', marker='o')
        axes.plot(list(data[2].keys())[:stop + 1], list(data[2].values())[:stop + 1], label='Закрытые', marker='o')

        axes.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        axes.xaxis.set_major_formatter(mdates.DateFormatter('%m'))

        axes.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=6, interval=1))

        axes.legend()
        axes.grid(True)

        axes.set_title(' Соотношение поступивших, незакрытых и закрытых заявок\n в ' +
                       str(datetime.datetime.today().year) + ' году')

        show()


class Pie(object):
    def __init__(self, data, title, suptitle):
        fig, axes = subplots(nrows=1, ncols=1, num=title)
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

        axes.axis('equal')
        text(0, -1.25, 'Всего заявок:' + str(sum(data.values())), fontsize='x-large', ha='center')
        fig.suptitle(suptitle)
        show()
