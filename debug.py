import analytics
import plots
from parser import Parser
import datetime
import files
parser = Parser("09.08.xlsx", "TDSheet")
parser.parse()

# b = Analytics.PlotRequestsByTime(parser.requests)
# plots.P
# print(b.get()[3])

# круговая диаграмма
# b = Analytics.PieTypesRequests(parser.requests)
# plots.PieTypesRequests(b.get())

# график про три года
# b = Analytics.AllRequestsThreeYears(parser.requests)
# plots.PlotThreeYears(b.get())

# график про среднее время закрытия по месяцам
# b = Analytics.PlotAverageTime(parser.requests)
# plots.PlotAverageTime(b.get())

# вывод подходящих к концу заявок по гарантии
# Analytics.FindWarrantyNearToEnd(parser.requests)

# вывод просрочек поставщика
# Analytics.FindDelayProvider(parser.requests)

# вывод типов гарантийности
# b = Analytics.PlotTypesClients(parser.requests)
# plots.PieTypesClients(b.get())

# вклад менеджеров
# b = Analytics.PieManagers(parser.requests, ['Тихомиров', 'Гусев', 'Баранов'])
# plots.PieManagers(b.get())

# количество клиентов
# print(Analytics.ClientsCounter(parser.requests).get())

# количество закрытых заявок
# plots.PlotDoneRequests(Analytics.PlotRequestsByTime(parser.requests).get())

# количество незакрытых заявок по неделямэ
# plots.PlotWaitingRequests(Analytics.PlotNotDoneRequests(parser.requests).get())

# open("ГарантияИстекаетСрок" + str(datetime.datetime.today().strftime('%d-%m-%Y-%H-%M')) + ".txt", 'w')

# print(Analytics.DaySchedule(parser.requests, datetime.datetime(2021, 6, 29)).get())

# files.DaySchedule(Analytics.DaySchedule(parser.requests, datetime.datetime(2021, 6, 29)).get(), datetime.datetime(2021, 6, 29))
#
# print(ord('A'))

# диаграмма про периоды незакрытых гаранийных заявок

#plots.WarrantyPie(Analytics.Warranty(parser.requests).get())

# plots.DoneWaitReceive(
#     [Analytics.Received(parser.requests).get()[0],
#      Analytics.Waiting(parser.requests).get(),
#      Analytics.Done(parser.requests).get()]
#                       )

# повторы заявок
analytics.RequestRepeats(parser.requests)