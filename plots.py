import matplotlib
import matplotlib.pyplot as plt
import datetime
matplotlib.use("Qt5Agg")

months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь",
          "Ноябрь", "Декабрь"]


class PlotThreeYears(object):
    def __init__(self, data, wait):
        fig, axes = plt.subplots(nrows=2, ncols=1, num='Поступившие заявки. Сранение текущего года с 2-мя предыдущими')
        stop = 12
        for i in reversed(data[0].keys()):
            if data[0][i] != 0:
                stop = i.month - 1
                break

        axes[0].plot(months[:stop], list(data[0].values())[:stop], linestyle='solid', label=str(data[3]), marker="o")
        axes[0].plot(months, data[1].values(), linestyle='solid', label=str(data[3] - 1), marker="o")
        axes[0].plot(months, data[2].values(), linestyle='solid', label=str(data[3] - 2), marker="o")
        axes[0].set_ylabel('Количество поступивших, шт')
        axes[0].set_xlabel('Время, месяцы')
        axes[0].set_title("Поступившие заявки. Сравнение текущего года с 2-мя предыдущими")
        axes[0].legend()
        axes[0].grid(True)

        weeks_to_months = [str(k + 1) for k in range(len(wait))]
        j = 1
        axes[1].plot(weeks_to_months, wait.values(), linestyle='solid', marker='o')
        for i in wait.keys():
            if i - datetime.date(i.year, i.month, 1) <= datetime.timedelta(7, 0, 0, 0, 0, 0, 0):
                axes[1].annotate(months[i.month - 1], [str(j), wait[i]])
            j += 1
        axes[1].minorticks_on()
        axes[1].grid(True)

        axes[1].set_title('Количество незакрытых заявок')
        plt.show()


class PiePhases(object):
    def __init__(self, arr):
        fig, axes = plt.subplots(nrows=1, ncols=2, num='Фазы незакрытых заявок')

        labels = list(arr.keys())

        for i in range(len(labels)):
            labels[i] = labels[i] + ": " + str(arr[labels[i]]) + " шт" + '(' + \
                        str("%.1f" % (arr[labels[i]] / sum(arr.values()) * 100)) + '%)'
        explode = []
        for i in arr.values():
            explode.append(0.0025 / (i / sum(arr.values())))

        wedges = axes[0].pie(arr.values(), labels=list(labels), explode=explode)
 
        axes[0].axis('equal')
        axes[1].axis('off')
        axes[1].legend(wedges[0], arr.keys(), loc="upper right", title="Фазы заявок")

        fig.suptitle("Фазы незакрытых заявок. Всего незакрытых: " + str(sum(arr.values())))
        plt.show()


class PlotAverageTime(object):
    def __init__(self, array):
        fig, axes = plt.subplots(nrows=1, ncols=1, num='Скорость закрытия заявок')

        axes.plot(months[:len(array[0])], array[0].values(), linestyle='solid', marker='o')
        axes.set_title('Скорость закрытия заявок')

        for i in array[0].keys():
            axes.annotate("  " + str(array[0][i]) + " дней", [months[i.month - 1], array[0][i]])
        axes.set_ylabel('Средний срок закрытия, дни')
        axes.set_xlabel('Время, месяцы')
        axes.grid(True)
        plt.show()


class PieTypes(object):
    def __init__(self, arr):
        fig, axes = plt.subplots(nrows=1, ncols=2, num="Распределение заявок по типам в "
                                                       + str(datetime.datetime.today().year) + "году")

        labels = list(arr.keys())

        for i in range(len(labels)):
            labels[i] = labels[i] + ": " + str(arr[labels[i]]) + " шт" + '(' + \
                        str("%.1f" % (arr[labels[i]] / sum(arr.values()) * 100)) + '%)'
        explode = []
        for i in arr.values():
            explode.append(0.000025 / (i / sum(arr.values())))

        wedges = axes[0].pie(arr.values(), labels=labels, explode=explode)

        axes[0].axis('equal')
        axes[1].axis('off')
        axes[1].legend(wedges[0], labels, loc="upper right", title="Типы заявок")

        fig.suptitle("Распределение заявок по типам в " + str(datetime.datetime.today().year) + "году")
        plt.show()


class PieManagers(object):
    def __init__(self, data):
        fig, axes = plt.subplots(nrows=1, ncols=2, num='Распределение нагрузки на менеджеров')
        labels = list(data.keys())

        for i in range(len(labels)):
            labels[i] = labels[i] + ": " + str(data[labels[i]]) + " шт" + '(' + \
                        str("%.1f" % (data[labels[i]] / sum(data.values()) * 100)) + '%)'

        wedges = axes[0].pie(data.values(), labels=labels)

        axes[0].axis('equal')
        axes[1].axis('off')
        axes[1].legend(wedges[0], data.keys(), loc="upper right", title="Список менеджеров")

        fig.suptitle("Распределение нагрузки на менеджеров. Всего заявок: " + str(sum(data.values())))
        plt.show()


class PlotDoneRequests(object):
    def __init__(self, array):
        fig, axes = plt.subplots(nrows=1, ncols=1, num='Динамика закрытия заявок')

        axes.plot(array[1].keys(), array[1].values(), linestyle='solid', marker='o')
        axes.grid(True)
        fig.suptitle('Количество закрытых заявок')
        plt.show()


class PlotWaitingRequests(object):
    def __init__(self, data):
        fig, axes = plt.subplots(nrows=1, ncols=1)

        axes.plot(data.keys(), data.values())
        axes.grid(True)
        fig.suptitle('Количество незакрытых заявок')
        plt.show()
