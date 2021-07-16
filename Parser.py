from datetime import datetime

import openpyxl as xl

from Request import Request


class Parser(object):
    requests = {}
    managers = {}
    engineers = {}

    def __init__(self, path_, sheet_):
        self.file = xl.load_workbook(filename=path_)
        self.sheet = self.file[sheet_]

    def parse(self):
        error_output = open('errors_while_parsing.txt', 'w')
        for i in self.sheet:
            if self.requests.get(i[1].value) is not None:
                continue
            elif i[8].value == 'Закрыто' and i[7].value is None:
                error_output.write(str(i[1].value) + " - не проставлена дата закрытия\n")
            elif i[7].value is not None and datetime.strptime(i[7].value, '%d.%m.%Y %H:%M:%S').year < 2018:
                error_output.write(str(i[1].value) + " - неправильный год\n")
            elif i[7].value is not None and datetime.strptime(i[7].value, '%d.%m.%Y %H:%M:%S') > datetime.today():
                error_output.write(str(i[1].value) + " - дата закрытия превышает сегодняшнюю")
            else:
                self.requests[i[1].value] = Request(begin_=i[4].value, end_=i[7].value, id_=i[1].value, status_=i[8].value,
                manager_=i[9].value, engineer_="", warranty_=i[11].value, request_state_=i[12].value, client_=i[14].value)
