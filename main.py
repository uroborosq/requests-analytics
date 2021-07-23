import Analytics
import plots
from Parser import Parser

parser = Parser("3.xlsx", "TDSheet")
parser.parse()

# b = Analytics.PlotRequestsByTime(parser.requests)
# plots.P
# print(b.get()[3])

# круговая диаграмма
# b = Analytics.PieTypesRequests(parser.requests)
# plots.PieTypesRequests(b.get())

# график про три года
# b = Analytics.PlotThreeYears(parser.requests)
# plots.PlotReceivedRequestsThreeYears(b.get())

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
