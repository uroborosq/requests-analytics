from datetime import datetime
from datetime import timedelta
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
        pd.set_option('chained_assignment', None)

        df = pd.read_excel(self.__file_path__, skiprows=self.__skip_rows__, index_col=1)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        df = df.drop(['№ п/п'], axis=1)

        duplicates = df[df.index.duplicated(keep='first')]
        df = df[~df.index.duplicated(keep='first')]
        df['Ссылка.Исполнители.Исполнитель'] = df['Ссылка.Исполнители.Исполнитель'].apply(lambda x: [x])

        counter = 0
        duplicates_length = len(duplicates)
        for key, row in df.iterrows():
            if counter == duplicates_length:
                break
            if key == duplicates.index[counter]:
                row['Ссылка.Исполнители.Исполнитель'].append(duplicates.iloc[counter]['Ссылка.Исполнители.Исполнитель'])
                counter += 1
                while counter < duplicates_length and duplicates.index[counter] == duplicates.index[counter - 1]:
                    row['Ссылка.Исполнители.Исполнитель'].append(duplicates.iloc[counter]['Ссылка.Исполнители.Исполнитель'])
                    counter += 1

        for column in ['Дата', 'Дата окончания работ', 'Дата начала работ']:
            df[column] = pd.to_datetime(df[column], errors='coerce', format='%d.%m.%Y %H:%M:%S')

        valid = df[(pd.isnull(df['Дата окончания работ'])) != (df['Статус'] == 'Закрыто')]
        valid = valid[(valid['Дата'] - valid['Дата окончания работ'] < timedelta(1)) | (valid['Статус'] != 'Закрыто')]
        self.requests = valid[(datetime.today() >= valid['Дата окончания работ']) | (valid['Статус'] != 'Закрыто')]

        self.invalid = df[~df.index.isin(self.requests.index)]
        self.__comment_invalid__()
        self.invalid = self.invalid["Причина ошибки"]

        self.engineers = self.requests['Ссылка.Исполнители.Исполнитель'].drop_duplicates().values
        self.managers = self.requests['Исполнитель'].drop_duplicates()
        self.managers = self.managers[~pd.isnull(self.managers)].values

    def __comment_invalid__(self):
        self.invalid.loc[:, "Причина ошибки"] = ""

        for key, row in self.invalid.iterrows():
            if (pd.isnull(row['Дата окончания работ'])) == (row['Статус'] == 'Закрыто'):
                self.invalid.loc[key, "Причина ошибки"] = "Выставлен статус закрыто, но не выставлена дата закрытия, " \
                                                          "либо выставлена " \
                                        "дата закрытия, но не выставлен статус Закрыто"
            elif (row['Статус'] == 'Закрыто') and (row['Дата'] - row['Дата окончания работ'] >= timedelta(1)):
                self.invalid.loc[key, "Причина ошибки"] = "Дата регистрации заявки позже даты закрытия более чем на 1 " \
                                                          "день"
            elif (row['Статус'] == 'Закрыто') and (row['Дата окончания работ'] > pd.Timestamp.today()):
                self.invalid.loc[key, "Причина ошибки"] = "Дата закрытия превышает сегодняшнюю"

