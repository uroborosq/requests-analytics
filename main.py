import datetime
import sys
import os

from PyQt6.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QGridLayout, QVBoxLayout, \
    QFormLayout, QApplication, QMessageBox, QGroupBox, QCheckBox, QCalendarWidget, QListWidget, QFileDialog, QDialog, \
    QListView, QListWidgetItem, QComboBox, QDateEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from openpyxl.utils import exceptions
import analytics
import files
import plots
from parser import Parser
from analytic_filters import filter
from title_builder import DefaultTitleBuilder


class DataAndManagerChooser(QDialog):
    def __init__(self, data_begin_enable: bool, data_end_enable: bool, manager_enable: bool):
        super(DataAndManagerChooser, self).__init__()
        self.layout = QGridLayout()

        if data_begin_enable:
            self.data_begin_label = QLabel("Выберите начало периода")
            self.data_begin_checkbox = QCheckBox()
            self.data_begin_calendar = QCalendarWidget()

            self.layout.addWidget(self.data_begin_label, 0, 0)
            self.layout.addWidget(self.data_begin_calendar, 1, 0)
            self.layout.addWidget(self.data_begin_checkbox, 2, 0)

        if data_end_enable:
            self.data_end_label = QLabel("Выберите конец периода")
            self.data_end_checkbox = QCheckBox()
            self.data_end_calendar = QCalendarWidget()
            self.layout.addWidget(self.data_end_label, 0, 1)
            self.layout.addWidget(self.data_end_calendar, 1, 1)
            self.layout.addWidget(self.data_end_checkbox, 2, 1)

        if manager_enable:
            self.manager_chooser = QComboBox()
            self.manager_chooser.addItem('Все')
            for i in managers:
                self.manager_chooser.addItem(i)

            self.layout.addWidget(self.manager_chooser)
        self.is_submitted = False
        self.data_submit_button = QPushButton("Применить")
        self.data_submit_button.clicked.connect(self.submit)
        self.layout.addWidget(self.data_submit_button)
        self.setLayout(self.layout)

    def get_date_begin(self):
        if self.data_begin_checkbox is not None:
            if self.data_begin_checkbox.isChecked():
                return self.data_begin_calendar.selectedDate().toPyDate()
        return datetime.date.min

    def get_date_end(self):
        if self.data_end_checkbox is not None:
            if self.data_end_checkbox.isChecked():
                return self.data_end_calendar.selectedDate().toPyDate()
        return datetime.date.max

    def get_manager(self):
        return self.manager_chooser.currentText()

    def submit(self):
        self.is_submitted = True
        self.close()


class PrioritySettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.line = QLineEdit()
        button_set = QPushButton('Применить настройки')
        button_set.clicked.connect(self.set_custom)
        self.button_set_default = QPushButton('Установить настройки по умолчанию')
        self.button_set_default.clicked.connect(self.set_default)
        self.line.returnPressed.connect(self.set_custom)
        settings = files.get_settings()[3]
        for i in list(settings.keys()):
            self.line.setText(self.line.text() + ',' + i)
        self.line.setText(self.line.text()[1:])
        layout.addWidget(self.line)
        layout.addWidget(button_set)
        layout.addWidget(self.button_set_default)
        self.setWindowIcon(QIcon(os.path.dirname(os.path.realpath(__file__)) + os.path.sep + '1.png'))
        self.setLayout(layout)

    def set_custom(self):
        keys = [i for i in self.line.text().split(',')]
        for i in keys:
            files.set_settings(3, i, [])

    def set_default(self):
        files.set_default(3)


class DayScheduleWindow(QWidget):
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
        self.setWindowIcon(QIcon(os.path.dirname(os.path.realpath(__file__)) + os.path.sep + '1.png'))
        self.layout.addWidget(label_info)
        self.layout.addWidget(self.line_date)
        self.layout.addWidget(button_create_form)
        self.layout.addWidget(self.label_result)

        self.setLayout(self.layout)

    def create_form(self):
        try:
            files.set_settings(1, 'day_schedule_date', self.line_date.text())
            date = datetime.datetime.strptime(self.line_date.text(), '%d.%m.%Y')
            output_file = files.DaySchedule(analytics.DaySchedule(self.data, date).get(), date).get()
            self.label_result.setText('Форма сохранена в файл\n' + output_file)
        except ValueError as e:
            QMessageBox(text=f"Неверные данные.\n Текст для отладки: {e.args}").exec()
        except KeyError:
            QMessageBox(text='KeyError').exec()


class ParserSettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout()

        self.lines = [QLineEdit() for _ in range(files.len_dct(2))]

        button_set = QPushButton('Применить настройки')
        button_set.clicked.connect(self.set_custom)
        self.button_set_default = QPushButton('Установить настройки по умолчанию')
        self.button_set_default.clicked.connect(self.set_default)
        self.lines[-1].returnPressed.connect(self.set_custom)

        settings = files.get_settings()
        j = 0
        for i in settings[2].values():
            self.lines[j].setText(i)
            j += 1
        self.setWindowIcon(QIcon(os.path.dirname(os.path.realpath(__file__)) + os.path.sep + '1.png'))
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

        self.setLayout(layout)

    def set_custom(self):
        try:
            if self.__check__():
                j = 0
                for i in files.default_settings()[2]:
                    files.set_settings(2, i, self.lines[j].text())
                    j += 1
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

    def set_default(self):
        files.set_default(2)


class FileChoice(QWidget):
    def __init__(self):
        super().__init__()
        self.w = 0
        self.layout = QVBoxLayout()
        # self.file = QFileDialog()
        self.button = QPushButton("Старт")
        button_settings_parser = QPushButton("Настройки парсера")

        self.text1 = QLabel("Введите адрес файла формата xlsx")
        self.input_1 = QLineEdit()
        self.input_1.returnPressed.connect(self.get_text)
        if autocomplete.get('main_window_path') is not None:
            self.input_1.setText(autocomplete['main_window_path'])

        self.label_parser = QLabel('')

        self.layout.addWidget(self.text1)
        self.layout.addWidget(self.input_1)
        self.layout.addWidget(self.button)
        self.layout.addWidget(button_settings_parser)

        self.setLayout(self.layout)
        self.button.clicked.connect(self.get_text)
        button_settings_parser.clicked.connect(self.settings_parser)

        self.setWindowTitle("Окно ввода данных")
        self.show()

    def get_text(self):
        self.label_parser.setText("Считывание данных...")
        if self.input_1.text() != '':
            try:
                files.set_settings(1, 'main_window_path', self.input_1.text())
                parser = Parser(self.input_1.text(), 'TDSheet')
                parser.parse()
                global managers
                managers = analytics.Managers(parser.requests).get()
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

    def settings_parser(self):
        self.w = ParserSettingsWindow()
        self.w.setWindowTitle('Настройки парсера')
        self.w.show()


class PlotChoice(QWidget):
    def __init__(self, arr):
        super().__init__()
        self.data = arr
        layout = QVBoxLayout()

        button_three_years = QPushButton("График про три года")
        button_phases = QPushButton("Диаграмма про фазы")
        button_average_time = QPushButton("График про среднее время")
        button_done_wait_received = QPushButton("Поступившие, закрытые и не закрытые")
        button_provider_delay = QPushButton("Вывести в файл просрочки поставщика")
        button_daily_scheluder = QPushButton("Форма для дневного отчета")
        button_warranty = QPushButton("Диаграмма про гарантию и вывод в файл")
        button_priorities = QPushButton("Распределение приоритетов")
        button_repeats = QPushButton("Найти повторы заявок")
        button_settings_priorities = QPushButton("Настройки диаграммы приоритетов")
        button_types = QPushButton("Распределение заявок по гарантийности")

        label_clients_counter = QLabel('Клиентов за текущий год насчитано: ' +
                                       str(analytics.ClientsCounter(self.data).get()))
        label_version = QLabel('version ' + files.default_settings()[0]['version'])

        layout.addWidget(button_three_years)
        layout.addWidget(button_phases)
        layout.addWidget(button_phases)
        layout.addWidget(button_average_time)
        layout.addWidget(button_done_wait_received)
        layout.addWidget(button_provider_delay)
        layout.addWidget(button_daily_scheluder)
        layout.addWidget(button_warranty)
        layout.addWidget(button_priorities)
        layout.addWidget(button_repeats)
        layout.addWidget(button_types)
        layout.addWidget(button_settings_priorities)
        layout.addWidget(label_clients_counter)
        layout.addWidget(label_version)

        button_types.clicked.connect(self.types)

        self.setLayout(layout)


    def three_years(self):
        plots.PlotThreeYears([
            analytics.Received(self.data, datetime.datetime.today().year, 'month').get(),
            analytics.Received(self.data, datetime.datetime.today().year - 1, 'month').get(),
            analytics.Received(self.data, datetime.datetime.today().year - 2, 'month').get()
        ])

    def phases(self):
        plots.Pie(analytics.Phases(self.data).get(), title='Фазы незакрытых заявок',
                  suptitle="Фазы незакрытых заявок" + '. Отчет сформирован ' + str(datetime.datetime.today().date()))

    def average_time(self):
        dialog = DataAndManagerChooser(True, True, True)
        dialog.exec()

        if dialog.is_submitted:
            begin = dialog.get_date_begin()
            end = dialog.get_date_end()
            manager = dialog.get_manager()

            builder = DefaultTitleBuilder()
            builder.join("Cреднее время закрытия заявок\n")
            builder.add_time_period(begin, end)
            builder.add_manager(manager)

            plots.PlotAverageTime(analytics.AverageTime(self.data).get())

    def done_wait_receive(self):
        plots.DoneWaitReceive([
            analytics.Received(self.data, datetime.datetime.today().year, 'week').get(),
            analytics.Waiting(self.data).get(),
            analytics.Done(self.data).get()
        ])

    def provider_delay(self):
        analytics.DelayProvider(self.data)
        QMessageBox(text='Записано в файл!').exec()

    def daily_scheduler(self):
        self.w = DayScheduleWindow(self.data)
        self.w.setWindowTitle("Выбор даты")
        self.w.show()

    def warranty(self):
        plots.Pie(analytics.Warranty(self.data).get(), title='Распределение незакрытых гарантийных заявок по срокам на'
                                                             + str(datetime.datetime.today().date()),
                  suptitle='Распределение незакрытых гарантийных заявок по срокам\n на '
                           + str(datetime.datetime.today().date()))

    def priorities(self):
        plots.Pie(analytics.Priority(self.data).get(), title='Распределение приоритетов в незакрытых заявках',
                  suptitle='Распределение приоритетов в незакрытых заявках на ' + str(datetime.datetime.today().date()))

    def repeats(self):
        analytics.RequestRepeats(self.data)
        QMessageBox(text='Записано в файл!').exec()

    def types(self):
        dialog = DataAndManagerChooser(data_begin_enable=True,
                                       data_end_enable=True,
                                       manager_enable=True)
        dialog.exec()

        if dialog.is_submitted:
            begin = dialog.get_date_begin()
            end = dialog.get_date_end()
            manager = dialog.get_manager()

            builder = DefaultTitleBuilder()
            builder.join("Распределение заявок по гарантийности\n")
            builder.add_time_period(begin, end)
            builder.add_manager(manager)
            title = builder.build()

            plots.Pie(analytics.Types(self.data, begin, end, manager).get(),
                      suptitle=title,
                      title=title)

    def settings_priorities(self):
        self.w = PrioritySettingsWindow()
        self.w.setWindowTitle('Настройки диаграммы приоритетов')
        self.w.show()


managers = []
if __name__ == "__main__":
    autocomplete = files.get_settings()[1]
    app = QApplication(sys.argv)
    window = FileChoice()
    sys.exit(app.exec())
