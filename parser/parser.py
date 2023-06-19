from datetime import datetime
import pandas as pd


class Parser(object):
    requests = {}
    managers = {}
    engineers = {}
    invalid: []

    __file_path__: str
    __sheet_name__: str
    __skip_rows__: int

    def __init__(self, path, sheet_name, skip_rows):
        self.__file_path__ = path
        self.__sheet_name__ = sheet_name
        self.__skip_rows__ = skip_rows

    def parse(self):
        df = pd.read_excel(self.__sheet_name__, skiprows=self.__skip_rows__, index_col=1)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        df = df.drop(['№ п/п'], axis=1)
        df = df.drop(['Дата начала работ'], axis=1)
        for column in ['Дата', 'Дата окончания работ']:
            df[column] = pd.to_datetime(df[column], errors='coerce', format='%d.%m.%Y %H:%M:%S')
        valid = df[(~pd.isnull(df['Дата окончания работ'])) | (df['Статус'] != 'Закрыто')]

        self.requests = valid[datetime.today() >= valid['Дата окончания работ']]
        self.invalid = df[(datetime.today() <= df['Дата окончания работ']) | (pd.isnull(df['Дата окончания работ']) & (df['Статус'] == 'Закрыто'))]

        self.engineers = self.requests['Ссылка.Исполнители.Исполнитель'].drop_duplicates().values
        self.managers = self.requests['Исполнитель'].drop_duplicates().values
