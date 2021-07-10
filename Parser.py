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
        for i in self.sheet:
            if self.requests.get(i[4].value) is None:
                self.requests[i[1].value] = Request(i[4].value, i[5].value, i[1].value, i[6].value, i[10].value, "", "")
            else:
                print("Не опять, а снова")
