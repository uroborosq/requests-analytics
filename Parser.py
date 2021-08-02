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
        for i in self.sheet:
            if self.requests.get(i[1].value) is not None:
                self.requests[i[1].value].add_engineer(i[__row_to_index__(self.settings['engineer'])].value)
            elif i[7].value is not None and datetime.strptime(i[7].value, '%d.%m.%Y %H:%M:%S').year < 2018:
                error_output.write(str(i[1].value) + " - неправильный год\n")
            elif i[7].value is not None and datetime.strptime(i[7].value, '%d.%m.%Y %H:%M:%S') > datetime.today():
                error_output.write(str(i[1].value) + " - дата закрытия превышает сегодняшнюю\n")
            else:
                self.requests[i[1].value] = Request(
                    begin_=i[__row_to_index__(self.settings['date_begin'])].value,
                    end_=i[__row_to_index__(self.settings['date_end'])].value,
                    id_=i[__row_to_index__(self.settings['id'])].value,
                    status_=i[__row_to_index__(self.settings['status'])].value,
                    manager_=i[__row_to_index__(self.settings['manager'])].value,
                    engineer_=i[__row_to_index__(self.settings['engineer'])].value,
                    warranty_=i[__row_to_index__(self.settings['type'])].value,
                    request_state_=i[__row_to_index__(self.settings['phase'])].value,
                    client_=i[__row_to_index__(self.settings['client'])].value,
                    begin_working_=i[__row_to_index__(self.settings['date_begin_working'])].value,
                    model_=i[__row_to_index__(self.settings['model'])].value,
                    address_=i[__row_to_index__(self.settings['address'])].value
                )
