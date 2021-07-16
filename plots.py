import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Qt5Agg")

months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь",
          "Ноябрь", "Декабрь"]

class PlotReceivedRequestsThreeYears(object):
    def __init__(self, arr):
        fig, axes = plt.subplots(nrows=1, ncols=1)
        stop = 12
        for i in reversed(arr[0].keys()):
            if arr[0][i] != 0:
                stop = i.month - 1
                break
            print(arr[0][i])

        axes.plot(months[:stop], list(arr[0].values())[:stop], linestyle='solid', label=str(arr[3]), marker="o")
        axes.plot(months, arr[1].values(), linestyle='solid', label=str(arr[3] - 1), marker="o")
        axes.plot(months, arr[2].values(), linestyle='solid', label=str(arr[3] - 2), marker="o")
        axes.set_ylabel('Количество закрытых заявок, штуки')
        axes.set_xlabel('Время, месяцы')
        axes.set_title("Поступившие заявки. Сравнение текущего года с 2-мя предыдущими")
        axes.legend()
        axes.grid(True)

        plt.show()


class PieTypesRequests(object):
    def __init__(self, arr):
        fig, axes = plt.subplots(nrows=1, ncols=2)

        labels = list(arr.keys())

        for i in range(len(labels)):
            labels[i] = labels[i] + ". Кол-во: " + str(arr[labels[i]])
        print(labels)

        wedges = axes[0].pie(arr.values(), labels=list(arr.keys()), autopct='%1.1f%%', explode=[0.01] * len(arr))
 
        axes[0].axis('equal')
        axes[1].axis('off')
        axes[1].legend(wedges[0], labels, loc="center", title="Фазы заявок. Всего заявок: " + str(sum(arr.values())))

        fig.suptitle("Вклад каждой из фаз незакрытых заявок")
        plt.show()


class PlotAverageTime(object):
    def __init__(self, array):
        fig, axes = plt.subplots(nrows=1, ncols=1)

        axes.plot(months[:len(array[1])], array[1].values(), linestyle='solid', marker='o')
        axes.set_title('Количество заявок по месяцам')

        for i in array[0].keys():
            axes.annotate("  " + str(array[0][i]) + " дней", [months[i.month - 1], array[1][i]])
        axes.set_ylabel('Количество закрытых заявок, штуки')
        axes.set_xlabel('Время, месяцы')
        axes.grid(True)
        plt.show()


class PieTypesClients(object):
    def __init__(self, arr):
        fig, axes = plt.subplots(nrows=1, ncols=2)

        labels = list(arr.keys())
        print(labels)
        for i in range(len(labels)):
            labels[i] = labels[i] + ". Кол-во: " + str(arr[labels[i]])

        wedges = axes[0].pie(arr.values(), labels=list(arr.keys()), autopct='%1.1f%%', explode=[0.01] * len(arr))

        axes[0].axis('equal')
        axes[1].axis('off')
        axes[1].legend(wedges[0], labels, loc="center", title="Типы заявок по гарантии. Всего заявок: "
                                                              + str(sum(arr.values())))

        fig.suptitle("Типы заявок по гарантии")
        plt.show()


class PieManagers(object):
    def __init__(self, arr):
        fig, axes = plt.subplots(nrows=1, ncols=2)

        labels = list(arr.keys())
        print(labels)
        for i in range(len(labels)):
            labels[i] = labels[i] + ". Кол-во: " + str(arr[labels[i]])

        wedges = axes[0].pie(arr.values(), labels=list(arr.keys()), autopct='%1.1f%%', explode=[0.01] * len(arr))

        axes[0].axis('equal')
        axes[1].axis('off')
        axes[1].legend(wedges[0], labels, loc="center", title="Список менеджеров. Всего заявок: "
                                                              + str(sum(arr.values())))

        fig.suptitle("Вклад каждого менеджера")
        plt.show()


class PlotDoneRequests(object):
    def __init__(self, array):
        fig, axes = plt.subplots(nrows=1, ncols=1)

        axes.plot(array[1].keys(), array[1].values(), linestyle='solid', marker='o')
        axes.grid(True)
        fig.suptitle('Количество закрытых заявок')
        plt.show()
