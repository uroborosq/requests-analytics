from datetime import datetime
import json
from openpyxl import load_workbook

import files
from Request import Request


def __row_to_index__(row):
    res = 0
    for i in reversed(range(len(row))):
        res += (ord(row[i]) - 65) * pow(26, i)

    return res


class Parser(object):
    requests = {}
    managers = {}
    engineers = {}

    def __init__(self, path_, sheet_):
        self.file = load_workbook(filename=path_, read_only=True)
        self.sheet = self.file[sheet_]
        self.set = {}
        self.lines_to_skip = 6

    def __determine_settings__(self):
        try:
            settings_file = open('.parser_settings.json', 'r')
            self.set = json.load(settings_file)
        except FileNotFoundError:
            self.set = files.set_default()
        except json.decoder.JSONDecodeError:
            self.set = files.set_default()

        if self.set.get('lines_to_skip') is not None:
            self.lines_to_skip = eval(self.set['lines_to_skip'])

        for i in [
            'id',
            'date_begin',
            'date_end',
            'date_begin_working',
            'status',
            'phase',
            'engineer',
            'manager',
            'type',
            'priority',
            'client',
            'model',
            'address'
        ]:
            if self.set.get(i) is None:
                self.set[i] = files.return_dict()[i]

        for i in self.set:
            self.set[i] = __row_to_index__(self.set[i])

    def parse(self):
        error_output = open('errors_while_parsing.txt', 'w')
        counter = 0
        self.__determine_settings__()
        for i in self.sheet:
            if counter < self.lines_to_skip:
                counter += 1
                continue
            if self.requests.get(i[self.set['id']].value) is not None:
                self.requests[i[self.set['id']].value].add_engineer(i[self.set['engineer']].value)
            elif i[self.set['date_end']].value is not None and\
                    datetime.strptime(i[self.set['date_end']].value, '%d.%m.%Y %H:%M:%S').year < 2018:
                error_output.write(i[self.set['id']].value + " - неправильный год\n")
            elif i[self.set['date_end']].value is not None and\
                    datetime.strptime(i[self.set['date_end']].value, '%d.%m.%Y %H:%M:%S') > datetime.today():
                error_output.write(i[self.set['id']].value + " - дата закрытия превышает сегодняшнюю\n")
            else:
                if i[self.set['date_end']].value is None and i[self.set['status']].value == 'Закрыто':
                    error_output.write(i[self.set['id']].value + " - не указана дата закрытия\n")

                self.requests[i[self.set['id']].value] = Request(
                    begin_=i[self.set['date_begin']].value,
                    end_=i[self.set['date_end']].value,
                    id_=i[self.set['id']].value,
                    status_=i[self.set['status']].value,
                    manager_=i[self.set['manager']].value,
                    engineer_=i[self.set['engineer']].value,
                    warranty_=i[self.set['type']].value,
                    request_state_=i[self.set['phase']].value,
                    client_=i[self.set['client']].value,
                    begin_working_=i[self.set['date_begin_working']].value,
                    model_=i[self.set['model']].value,
                    address_=i[self.set['address']].value,
                    priority_=i[self.set['priority']].value
                )
