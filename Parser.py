import openpyxl as xl
from Request import Request


class Parser(object):
    requests = {}
    managers = {}
    engineers = {}

    def __init__(self, path_, sheet_):
        self.file = xl.load_workbook(filename=path_)
        self.sheet = file[sheet_]

    def parse(self, begin):
        for i in self.sheet:
               tmp = Request(i[1], end_, id_, status_, type_, manager_, engineer_)


