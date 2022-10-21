import analytics
from parser import Parser
import datetime

parser = Parser("16.08big.xlsx", "TDSheet")
parser.parse()
data = parser.requests
#
# more = 0
# less = 0
#
# for i in parser.requests.values():
#     if i.date_end != '' and i.date_begin != '':
#         if i.date_end > i.date_begin:
#             more += 1
#         else:
#             less += 1
#
# print(f"{more} {less}")
# requests = pd.read_excel('16.08big.xlsx', header=5)
# print(requests.columns)

waiting = analytics.Phases(data, datetime.date(2016, 1, 1), datetime.date.today(), 'Все', 'week')
