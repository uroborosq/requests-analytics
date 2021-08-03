from datetime import datetime
import json
import openpyxl as xl

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
        self.file = xl.load_workbook(filename=path_)
        self.sheet = self.file[sheet_]
        self.settings = {}

    def parse(self):

        try:
            settings_file = open('.parser_settings.json', 'r')
            self.settings = json.load(settings_file)
        except FileNotFoundError:
            files.set_default()
        except json.decoder.JSONDecodeError:
            files.set_default()

        error_output = open('errors_while_parsing.txt', 'w')
        counter = 0
        lines_to_skip = 7
        if self.settings.get('lines_to_skip') is not None:
            lines_to_skip = self.settings['lines_to_skip']

        for i in self.sheet:
            if counter < 7:
                counter += 1
                continue
            if self.requests.get(i[1].value) is not None:
                self.requests[i[1].value].add_engineer(i[__row_to_index__(self.settings['engineer'])].value)
            elif i[7].value is not None and datetime.strptime(i[7].value, '%d.%m.%Y %H:%M:%S').year < 2018:
                error_output.write(str(i[1].value) + " - неправильный год\n")
            elif i[7].value is not None and datetime.strptime(i[7].value, '%d.%m.%Y %H:%M:%S') > datetime.today():
                error_output.write(str(i[1].value) + " - дата закрытия превышает сегодняшнюю\n")
            else:
                self.requests[i[1].value] = Request(
                    begin_=i[__row_to_index__(self.settings['date_begin'])].value if self.settings.get('date_begin') is not None else files.return_dict()['date_begin'],
                    end_=i[__row_to_index__(self.settings['date_end'])].value if self.settings.get('date_begin') is not None else files.return_dict()['date_end'],
                    id_=i[__row_to_index__(self.settings['id'])].value if self.settings.get('id') is not None else files.return_dict()['id'],
                    status_=i[__row_to_index__(self.settings['status'])].value if self.settings.get('status') is not None else files.return_dict()['status'],
                    manager_=i[__row_to_index__(self.settings['manager'])].value if self.settings.get('manager') is not None else files.return_dict()['manager'],
                    engineer_=i[__row_to_index__(self.settings['engineer'])].value if self.settings.get('engineer') is not None else files.return_dict()['engineer'],
                    warranty_=i[__row_to_index__(self.settings['type'])].value if self.settings.get('type') is not None else files.return_dict()['type'],
                    request_state_=i[__row_to_index__(self.settings['phase'])].value if self.settings.get('phase') is not None else files.return_dict()['phase'],
                    client_=i[__row_to_index__(self.settings['client'])].value if self.settings.get('client') is not None else files.return_dict()['client'],
                    begin_working_=i[__row_to_index__(self.settings['date_begin_working'])].value if self.settings.get('date_begin_working') is not None else files.return_dict()['date_begin_working'],
                    model_=i[__row_to_index__(self.settings['model'])].value if self.settings.get('model') is not None else files.return_dict()['model'],
                    address_=i[__row_to_index__(self.settings['address'])].value if self.settings.get('address') is not None else files.return_dict()['address'],
                    priority_=i[__row_to_index__(self.settings['priority'])].value if self.settings.get('priority') is not None else files.return_dict()['priority']
                )
