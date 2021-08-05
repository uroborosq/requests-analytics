import datetime
import json
import sys

from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QGridLayout, QVBoxLayout, \
    QFormLayout, QApplication, QMessageBox, QGroupBox
from PyQt5.QtCore import Qt
from openpyxl.utils import exceptions

import Analytics
import files
import plots
from Parser import Parser


def json_dump():
    file = open(".autocomplete.json", 'w')
    json.dump(autocomplete, file, indent=4)
    file.close()


class PrioritySettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.line = QLineEdit()
        button_set = QPushButton('Применить настройки')
        button_set.clicked.connect(self.set_custom)
        self.button_set_default = QPushButton('Установить настройки по умолчанию')
        self.button_set_default.clicked.connect(files.set_default_priority)
        self.line.returnPressed.connect(self.set_custom)
        with open('.priority_settings.json', 'r') as file:
            settings = json.load(file)
            for i in list(settings.keys())[:-1]:
                self.line.setText(self.line.text() + ',' + i)
        self.line.setText(self.line.text()[1:])
        layout.addWidget(self.line)
        layout.addWidget(button_set)
        layout.addWidget(self.button_set_default)

        self.setLayout(layout)

    def set_custom(self):
        keys = [i for i in self.line.text().split(',')]
        settings = {}
        for i in keys:
            settings[i] = []
        settings['Неизвестный тип или не заполнено'] = []
        file = open('.priority_settings.json', 'w')
        json.dump(settings, file, indent=4)
        file.close()


class DayScheduleWindow(QMainWindow):
    def __init__(self, arr):
        super().__init__()
        self.data = arr
        self.layout = QGridLayout()
        button_create_form = QPushButton("Сгенерировать форму")
        label_info = QLabel("Введите дату в формате Д.М.Г(21.04.2019)")
        self.line_date = QLineEdit()
        if autocomplete.get('day_schedule_date') is not None:
            self.line_date.setText(autocomplete['day_schedule_date'])

        self.label_result = QLabel('')
        button_create_form.clicked.connect(self.create_form)
        self.line_date.returnPressed.connect(self.create_form)

        self.layout.addWidget(label_info)
        self.layout.addWidget(self.line_date)
        self.layout.addWidget(button_create_form)
        self.layout.addWidget(self.label_result)

        self.wnd = QWidget()
        self.wnd.setLayout(self.layout)
        self.setCentralWidget(self.wnd)

    def create_form(self):
        try:
            autocomplete['day_schedule_date'] = self.line_date.text()
            json_dump()
            date = datetime.datetime.strptime(self.line_date.text(), '%d.%m.%Y')
            output_file = files.DaySchedule(Analytics.DaySchedule(self.data, date).get(), date).get()
            self.label_result.setText('Форма сохранена в файл\n' + output_file)
        except ValueError:
            QMessageBox(text='Неверные данные').exec()
        except KeyError:
            QMessageBox(text='KeyError').exec()


class ParserSettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        layout = QFormLayout()

        self.lines = [QLineEdit() for _ in range(files.return_number())]

        button_set = QPushButton('Применить настройки')
        button_set.clicked.connect(self.set_custom)
        self.button_set_default = QPushButton('Установить настройки по умолчанию')
        self.button_set_default.clicked.connect(files.set_default)
        self.lines[-1].returnPressed.connect(self.set_custom)
        with open('.parser_settings.json', 'r') as file:
            settings = json.load(file)
            j = 0
            for i in settings.values():
                self.lines[j].setText(i)
                j += 1

        layout.addRow(self.tr('&Наряд заказ'), self.lines[0])
        layout.addRow(self.tr('&Дата поступления'), self.lines[1])
        layout.addRow(self.tr('&Дата закрытия'), self.lines[2])
        layout.addRow(self.tr('&Дата начала работ'), self.lines[3])
        layout.addRow(self.tr('&Статус'), self.lines[4])
        layout.addRow(self.tr('&Фаза'), self.lines[5])
        layout.addRow(self.tr('&Менеджер'), self.lines[6])
        layout.addRow(self.tr('&Инженер'), self.lines[7])
        layout.addRow(self.tr('&Гарантийность'), self.lines[8])
        layout.addRow(self.tr('&Клиент'), self.lines[9])
        layout.addRow(self.tr('&Адрес'), self.lines[10])
        layout.addRow(self.tr('&Модель'), self.lines[11])
        layout.addRow(self.tr("&Приоритет"), self.lines[12])
        layout.addRow(self.tr('&Количество строк в загововке'), self.lines[13])
        layout.addWidget(button_set)
        layout.addWidget(self.button_set_default)

        self.wnd = QWidget()
        self.wnd.setLayout(layout)
        self.setCentralWidget(self.wnd)

    def set_custom(self):
        try:
            if self.__check__():
                settings = {}
                j = 0
                for i in files.set_default():
                    settings[i] = self.lines[j].text()
                    j += 1

                file = open('.parser_settings.json', 'w')
                json.dump(settings, file, indent=4)
                file.close()
        except ValueError:
            QMessageBox(text='Неверные данные').exec()
        except KeyError:
            QMessageBox(text='KeyError').exec()

    def __check__(self):
        for i in self.lines[:1]:
            for j in i.text():
                if not ('A' <= j <= 'Z'):
                    raise ValueError

        if self.lines[-1].text().isdigit():
            return True
        raise ValueError


class SimplePlots(QGroupBox):
    def __init__(self, data):
        super().__init__('Аналитика без параметров')
        self.data = dict(data)
        button_plot_three_years = QPushButton("График про три года")
        button_pie_phases = QPushButton("Диаграмма про фазы")
        button_average_time = QPushButton("График про среднее время")
        button_waitdonerecieve = QPushButton('Поступившие, закрытые и незакрытые заявки')
        button_provider_delay = QPushButton('Вывести в файл просрочки поставщика')
        button_day_schedule = QPushButton("Форма для дневного отчета")
        button_warranty = QPushButton("Диаграмма про гарантию и вывод в файл")
        button_priority = QPushButton("Распределение приоритетов")

        button_plot_three_years.clicked.connect(self.plot_three_years)
        button_warranty.clicked.connect(self.warranty)
        button_pie_phases.clicked.connect(self.pie_phases)
        button_average_time.clicked.connect(self.plot_average_time)
        button_waitdonerecieve.clicked.connect(self.plot_donewaitrecieve)
        button_provider_delay.clicked.connect(self.find_provider_delay)
        button_day_schedule.clicked.connect(self.day_schedule)
        button_priority.clicked.connect(self.priority)

        layout = QVBoxLayout()
        layout.addWidget(button_plot_three_years)
        layout.addWidget(button_pie_phases)
        layout.addWidget(button_average_time)
        layout.addWidget(button_waitdonerecieve)
        layout.addWidget(button_provider_delay)
        layout.addWidget(button_day_schedule)
        layout.addWidget(button_warranty)
        layout.addWidget(button_priority)

        self.setLayout(layout)
        self.w = 0

    def plot_three_years(self):
        plots.PlotThreeYears([
            Analytics.Received(self.data, datetime.datetime.today().year, 'month').get(),
            Analytics.Received(self.data, datetime.datetime.today().year - 1, 'month').get(),
            Analytics.Received(self.data, datetime.datetime.today().year - 2, 'month').get()
        ])

    def pie_phases(self):
        plots.PiePhases(Analytics.Phases(self.data).get())

    def plot_average_time(self):
        plots.PlotAverageTime(Analytics.AverageTime(self.data).get())

    def find_provider_delay(self):
        Analytics.DelayProvider(self.data)
        QMessageBox(text='Записано в файл!').exec()

    def day_schedule(self):
        self.w = DayScheduleWindow(self.data)
        self.w.setWindowTitle("Выбор даты")
        self.w.show()

    def warranty(self):
        plots.WarrantyPie(Analytics.Warranty(self.data).get())

    def plot_donewaitrecieve(self):
        plots.DoneWaitReceive([
            Analytics.Received(self.data, datetime.datetime.today().year, 'week').get(),
            Analytics.Waiting(self.data).get(),
            Analytics.Done(self.data).get()
        ])

    def priority(self):
        plots.Pie(Analytics.Priority(self.data).get(), title='Распределение приоритетов в незакрытых заявках',
                  suptitle='Распределение приоритетов в незакрытых заявках')


class ManagersBox(QGroupBox):
    def __init__(self, data):
        super(ManagersBox, self).__init__('Распределение нагрузки на инженеров')
        self.data = dict(data)

        layout = QVBoxLayout()

        label_managers_names = QLabel('Введите фамилии инженеров в формате Фамилия1,Фамилия2,Фамилия3.\n'
                                      'Через запятую без пробелов')
        self.line_managers_name = QLineEdit()
        self.line_managers_dates_begin = QLineEdit()
        self.line_managers_dates_end = QLineEdit()
        if autocomplete.get('managers_names') is not None:
            self.line_managers_name.setText(autocomplete['managers_names'])
        if autocomplete.get('managers_begin') is not None:
            self.line_managers_dates_begin.setText(autocomplete['managers_begin'])
        if autocomplete.get('managers_end') is not None:
            self.line_managers_dates_end.setText(autocomplete['managers_end'])

        label_dates_managers = QLabel('Введите период для аналитики. Если оставить поле пустым,'
                                      ' то ограничений на период с этой стороны не будет')
        label_begin = QLabel('Дата начала периода в формате d.m.Y\nПример: 01.01.2021')
        label_end = QLabel('Дата конца периода в формате d.m.Y')

        button_pie_managers = QPushButton("Диаграмма про менеджеров")
        button_pie_managers.clicked.connect(self.pie_managers)
        self.line_managers_name.returnPressed.connect(self.pie_managers)
        self.line_managers_dates_end.returnPressed.connect(self.pie_managers)

        layout.addWidget(label_managers_names)
        layout.addWidget(self.line_managers_name)
        layout.addWidget(label_dates_managers)
        layout.addWidget(label_begin)
        layout.addWidget(self.line_managers_dates_begin)
        layout.addWidget(label_end)
        layout.addWidget(self.line_managers_dates_end)
        layout.addWidget(button_pie_managers)

        self.setLayout(layout)

    def pie_managers(self):
        begin, end = '', ''
        try:
            if self.line_managers_dates_begin.text() != '':
                begin = datetime.datetime.strptime(self.line_managers_dates_begin.text(), '%d.%m.%Y')
                begin = begin.date()
            if self.line_managers_dates_end.text() != '':
                end = datetime.datetime.strptime(self.line_managers_dates_end.text(), '%d.%m.%Y')
                end = end.date()

            names = self.line_managers_name.text()

            plots.PieManagers(Analytics.Managers(self.data, names, begin, end).get())
            autocomplete['managers_names'] = self.line_managers_name.text()
            autocomplete['managers_begin'] = self.line_managers_dates_begin.text()
            autocomplete['managers_end'] = self.line_managers_dates_end.text()
            json_dump()
        except ValueError:
            warn = QMessageBox()
            warn.setText("Данные введены некорректно")
            warn.exec()


class TypesBox(QGroupBox):
    def __init__(self, data):
        super(TypesBox, self).__init__('Распределение заявок по гарантийности')
        self.data = dict(data)

        layout = QVBoxLayout()

        label_begin = QLabel('Дата начала периода в формате d.m.Y\nПример: 01.01.2021')
        label_end = QLabel('Дата конца периода в формате d.m.Y')
        self.line_begin = QLineEdit()
        self.line_end = QLineEdit()

        if autocomplete.get('types_begin') is not None:
            self.line_begin.setText(autocomplete['types_begin'])
        if autocomplete.get('types_end') is not None:
            self.line_end.setText(autocomplete['types_end'])

        button_pie_managers = QPushButton("Построить диаграмму")
        button_pie_managers.clicked.connect(self.pie_types)

        layout.addWidget(label_begin)
        layout.addWidget(self.line_begin)
        layout.addWidget(label_end)
        layout.addWidget(self.line_end)
        layout.addWidget(button_pie_managers)

        self.setLayout(layout)

    def pie_types(self):
        try:
            if self.line_begin.text() != '':
                begin = datetime.datetime.strptime(self.line_begin.text(), '%d.%m.%Y').date()
            else:
                begin = datetime.datetime.min.date()

            if self.line_end.text() != '':
                end = datetime.datetime.strptime(self.line_end.text(), '%d.%m.%Y').date()
            else:
                end = datetime.datetime.max.date()

            plots.PieTypes(Analytics.Types(self.data, begin, end).get())
            autocomplete['types_begin'] = self.line_begin.text()
            autocomplete['types_end'] = self.line_end.text()
            json_dump()
        except ValueError:
            warn = QMessageBox()
            warn.setText("Данные введены некорректно")
            warn.exec()


class SettingsBox(QGroupBox):
    def __init__(self, data):
        super(SettingsBox, self).__init__('Прочее')
        layout = QVBoxLayout()
        label_client_counter = QLabel()

        label_client_counter.setText(
            'Клиентов за текущий год насчитано: ' + str(Analytics.ClientsCounter(data).get()))
        button_settings = QPushButton("Настройки парсера")
        button_priority = QPushButton("Настройки диаграммы приоритетов")
        layout.addWidget(button_settings)
        layout.addWidget(button_priority)
        layout.addWidget(label_client_counter)
        label_version = QLabel("Версия 0.0.3 alpha")
        label_version.setAlignment(Qt.AlignRight)
        button_settings.clicked.connect(self.open_settings)
        button_priority.clicked.connect(self.open_priority)

        layout.addWidget(label_version)

        self.setLayout(layout)

    def open_settings(self):
        self.w = ParserSettingsWindow()
        self.w.setWindowTitle('Настройки парсера')
        self.w.show()

    def open_priority(self):
        self.w = PrioritySettingsWindow()
        self.w.setWindowTitle('Настройки диаграммы приоритетов')
        self.w.show()


class Window(QWidget):
    def __init__(self):
        super().__init__()
        # wnd =  QWidget()
        self.layout = QVBoxLayout()
        self.button = QPushButton("Старт")
        self.text1 = QLabel("Введите адрес файла формата xlsx")
        self.input_1 = QLineEdit()
        self.input_1.setMaximumWidth(250)
        self.input_1.returnPressed.connect(self.get_text)

        if autocomplete.get('main_window_path') is not None:
            self.input_1.setText(autocomplete['main_window_path'])

        self.button.setMaximumWidth(50)
        self.label_parser = QLabel('')

        self.layout.addWidget(self.text1)
        self.layout.addWidget(self.input_1)
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)
        self.button.clicked.connect(self.get_text)

        # self.setCentralWidget(wnd)
        self.setWindowTitle("Окно ввода данных")
        self.show()

    def get_text(self):
        self.label_parser.setText("Считывание данных...")
        if self.input_1.text() != '':
            try:
                autocomplete['main_window_path'] = self.input_1.text()
                json_dump()
                parser = Parser(self.input_1.text(), 'TDSheet')
                parser.parse()
                self.widget = PlotChoice(parser.requests)
                self.widget.setWindowTitle("Выбор графиков")
                self.widget.show()
                self.hide()
            except FileNotFoundError:
                warn = QMessageBox()
                warn.setText("Файл не найден")
                warn.setWindowTitle("Э")
                warn.exec()
            except exceptions.InvalidFileException:
                warn = QMessageBox()
                warn.setText("Неверный формат файла")
                warn.setWindowTitle("Э")
                warn.exec()
        else:
            warn = QMessageBox()
            warn.setText("Заполните поля")
            warn.setWindowTitle("Э")
            warn.exec()


class PlotChoice(QMainWindow):
    def __init__(self, arr):
        super().__init__()
        self.data = arr
        self.layout = QGridLayout()

        managers_box = ManagersBox(self.data)
        other = SimplePlots(self.data)
        types_box = TypesBox(self.data)
        settings_box = SettingsBox(self.data)

        self.layout.addWidget(managers_box, 0, 0)
        self.layout.addWidget(other, 0, 1)
        self.layout.addWidget(types_box, 1, 0)
        self.layout.addWidget(settings_box, 1, 1)

        self.wnd = QWidget()
        self.wnd.setLayout(self.layout)
        self.setCentralWidget(self.wnd)


try:
    f = open('.autocomplete.json', 'r')
    autocomplete = json.load(f)
    f.close()
except json.decoder.JSONDecodeError:
    print("Warning: new file created")
    f = open('.autocomplete.json', 'w')
    autocomplete = {}
    json.dump(autocomplete, f, indent=4)
    f.close()
except FileNotFoundError:
    print("Warning: new file created")
    f = open('.autocomplete.json', 'w')
    autocomplete = {}
    json.dump(autocomplete, f, indent=4)
    f.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec())
