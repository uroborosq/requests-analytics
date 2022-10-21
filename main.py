import datetime
import sys
import os

from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QGridLayout, QVBoxLayout, \
    QFormLayout, QApplication, QMessageBox, QGroupBox, QCheckBox, QCalendarWidget, QListWidget, QFileDialog, QDialog, \
    QListView, QListWidgetItem, QComboBox, QDateEdit, QSpinBox, QHBoxLayout, QDateTimeEdit
from PyQt5.QtGui import QIcon
from openpyxl.utils import exceptions
import analytics
import files
import plots
from parser import Parser
from title_builder import TitleBuilder, DefaultTitleBuilder


class ThreeYearsChooserBuilder:
    def __init__(self):
        self.widget = QDialog()
        layout = QVBoxLayout()
        self.first_year = QSpinBox()
        self.second_year = QSpinBox()
        self.third_year = QSpinBox()
        self.first_year.setMinimum(min_date.year)
        self.second_year.setMinimum(min_date.year)
        self.third_year.setMinimum(min_date.year)
        self.first_year.setMaximum(datetime.date.today().year)
        self.second_year.setMaximum(datetime.date.today().year)
        self.third_year.setMaximum(datetime.date.today().year)

        self.first_year.setValue(datetime.date.today().year)
        self.second_year.setValue(datetime.date.today().year - 1)
        self.third_year.setValue(datetime.date.today().year - 2)

        button_confirm = QPushButton('Применить')
        button_confirm.clicked.connect(self.confirm)

        information_label = QLabel('Выберите года для сравнения')

        years_group = QGroupBox()
        years_group_layout = QHBoxLayout()
        years_group_layout.addWidget(self.first_year)
        years_group_layout.addWidget(self.second_year)
        years_group_layout.addWidget(self.third_year)
        years_group.setLayout(years_group_layout)

        self.checkbox_exclude_requests = QCheckBox("Исключить внутренние заявки")


        layout.addWidget(information_label)
        layout.addWidget(years_group)
        layout.addWidget(self.checkbox_exclude_requests)
        layout.addWidget(button_confirm)

        self.is_submitted = False
        self.widget.setLayout(layout)

    def confirm(self):
        self.widget.close()
        self.is_submitted = True

    def build(self):
        return self.widget

    def get_years(self):
        return self.first_year.value(), self.second_year.value(), self.third_year.value()

    def get_excluding_requests(self):
        return self.checkbox_exclude_requests.isChecked()


class DataAndManagerChooser(QDialog):
    def __init__(self, data_begin_enable: bool, data_end_enable: bool, manager_enable, requests_type_enable=True):
        super(DataAndManagerChooser, self).__init__()
        self.layout = QGridLayout()
        self.data_begin_checkbox = None
        self.data_end_checkbox = None
        if data_begin_enable:
            self.data_begin_label = QLabel("Выберите начало периода")
            self.data_begin_checkbox = QCheckBox('Учитывать дату')
            self.data_begin_calendar = QDateTimeEdit(datetime.datetime.today())
            self.data_begin_calendar.setDisplayFormat("dd.MM.yyyy")
            self.data_begin_checkbox.setChecked(True)
            self.layout.addWidget(self.data_begin_label, 0, 0)
            self.layout.addWidget(self.data_begin_calendar, 1, 0)
            self.layout.addWidget(self.data_begin_checkbox, 2, 0)

        if data_end_enable:
            self.data_end_label = QLabel("Выберите конец периода")
            self.data_end_checkbox = QCheckBox('Учитывать дату')
            self.data_end_checkbox.setChecked(True)
            self.data_end_calendar = QDateTimeEdit(datetime.datetime.today())
            self.data_end_calendar.setDisplayFormat("dd.MM.yyyy")
            self.layout.addWidget(self.data_end_label, 0, 1)
            self.layout.addWidget(self.data_end_calendar, 1, 1)
            self.layout.addWidget(self.data_end_checkbox, 2, 1)

        if manager_enable:
            self.manager_chooser = QComboBox()
            self.manager_chooser.addItem('Все')
            for i in managers:
                self.manager_chooser.addItem(i)

            self.layout.addWidget(self.manager_chooser)

        if requests_type_enable:
            self.requests_type_checkbox = QCheckBox(
                "Исключить внутренние заявки")
            self.requests_type_checkbox.setChecked(True)
            self.layout.addWidget(self.requests_type_checkbox)

        self.is_submitted = False
        self.data_submit_button = QPushButton("Применить")
        self.data_submit_button.clicked.connect(self.submit)
        self.layout.addWidget(self.data_submit_button)
        self.setLayout(self.layout)

    def get_date_begin(self):
        if self.data_begin_checkbox is not None:
            if self.data_begin_checkbox.isChecked():
                return self.data_begin_calendar.date().toPyDate()
        return min_date

    def get_date_end(self):
        if self.data_end_checkbox is not None:
            if self.data_end_checkbox.isChecked():
                return self.data_end_calendar.date().toPyDate()
        return datetime.date.today()

    def get_manager(self):
        return self.manager_chooser.currentText()

    def get_request_excluding_status(self):
        if self.requests_type_checkbox is not None:
            return self.requests_type_checkbox.isChecked()
        else:
            return False

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
        self.button_set_default = QPushButton(
            'Установить настройки по умолчанию')
        self.button_set_default.clicked.connect(self.set_default)
        self.line.returnPressed.connect(self.set_custom)
        settings = files.get_settings()[3]
        for i in list(settings.keys()):
            self.line.setText(self.line.text() + ',' + i)
        self.line.setText(self.line.text()[1:])
        layout.addWidget(self.line)
        layout.addWidget(button_set)
        layout.addWidget(self.button_set_default)
        self.setWindowIcon(QIcon(os.path.dirname(
            os.path.realpath(__file__)) + os.path.sep + '1.png'))
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
        self.line_date = QDateTimeEdit(datetime.datetime.today())
        self.line_date.setDisplayFormat("dd.MM.yyyy")
        if autocomplete.get('day_schedule_date') is not None:
            self.line_date.setText(autocomplete['day_schedule_date'])

        self.label_result = QLabel('')
        button_create_form.clicked.connect(self.create_form)
        self.setWindowIcon(QIcon(os.path.dirname(
            os.path.realpath(__file__)) + os.path.sep + '1.png'))
        self.layout.addWidget(label_info)
        self.layout.addWidget(self.line_date)
        self.layout.addWidget(button_create_form)
        self.layout.addWidget(self.label_result)

        self.setLayout(self.layout)

    def create_form(self):
        try:
            files.set_settings(1, 'day_schedule_date', self.line_date.text())
            date = datetime.datetime.strptime(
                self.line_date.text(), '%d.%m.%Y')
            output_file = files.DaySchedule(
                analytics.DaySchedule(self.data, date).get(), date).get()
            self.label_result.setText('Форма сохранена в файл\n' + output_file)
        except ValueError as e:
            QMessageBox(
                text=f"Неверные данные.\n Текст для отладки: {e.args}").exec()
        except KeyError:
            QMessageBox(text='KeyError').exec()


class ParserSettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout()

        self.lines = [QLineEdit() for _ in range(files.len_dct(2))]

        button_set = QPushButton('Применить настройки')
        button_set.clicked.connect(self.set_custom)
        self.button_set_default = QPushButton(
            'Установить настройки по умолчанию')
        self.button_set_default.clicked.connect(self.set_default)
        self.lines[-1].returnPressed.connect(self.set_custom)

        settings = files.get_settings()
        j = 0
        for i in settings[2].values():
            self.lines[j].setText(i)
            j += 1
        self.setWindowIcon(QIcon(os.path.dirname(
            os.path.realpath(__file__)) + os.path.sep + '1.png'))
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
                global min_date
                min_date = analytics.find_min_date(parser.requests)
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


def __call_dialog_and_fetch_data__(date_begin_enable, date_end_enable, manager_enable, excluding_requests):
    dialog = DataAndManagerChooser(
        date_begin_enable, date_end_enable, manager_enable, excluding_requests)
    dialog.exec()

    if dialog.is_submitted:
        return True, dialog.get_date_begin(), dialog.get_date_end(), dialog.get_manager(), dialog.get_request_excluding_status()
    else:
        return [False, 0, 0, 0, False]


class PlotChoice(QWidget):
    def __init__(self, arr):
        super().__init__()
        self.data = arr
        layout = QVBoxLayout()

        button_three_years = QPushButton("График про три года")
        button_phases = QPushButton("Диаграмма про фазы")
        button_average_time = QPushButton("График про среднее время")
        button_done_wait_received = QPushButton(
            "Поступившие, закрытые и не закрытые")
        button_provider_delay = QPushButton(
            "Вывести в файл просрочки поставщика")
        button_daily_scheluder = QPushButton("Форма для дневного отчета")
        button_warranty = QPushButton("Диаграмма про гарантию и вывод в файл")
        button_priorities = QPushButton("Распределение приоритетов")
        button_repeats = QPushButton("Найти повторы заявок")
        button_settings_priorities = QPushButton(
            "Настройки диаграммы приоритетов")
        button_types = QPushButton("Распределение заявок по гарантийности")

        label_clients_counter = QLabel('Клиентов за текущий год насчитано: ' +
                                       str(analytics.ClientsCounter(self.data).get()))
        label_version = QLabel(
            'version ' + files.default_settings()[0]['version'])

        layout.addWidget(button_three_years)
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

        button_three_years.clicked.connect(self.three_years)
        button_phases.clicked.connect(self.phases)
        button_done_wait_received.clicked.connect(self.done_wait_receive)
        button_average_time.clicked.connect(self.average_time)
        button_daily_scheluder.clicked.connect(self.daily_scheduler)
        button_warranty.clicked.connect(self.warranty)
        button_priorities.clicked.connect(self.priorities)
        button_repeats.clicked.connect(self.repeats)
        button_settings_priorities.clicked.connect(self.settings_priorities)
        button_types.clicked.connect(self.types)
        button_provider_delay.clicked.connect(self.provider_delay)

        self.setLayout(layout)

    def three_years(self):
        self.years_window = ThreeYearsChooserBuilder()
        self.years_window.widget.exec()

        if self.years_window.is_submitted:
            first_year, second_year, third_year = self.years_window.get_years()
            is_exclude = self.years_window.get_excluding_requests()
            plots.PlotThreeYears([
                analytics.Received(self.data, 'month', datetime.date(
                    first_year, 1, 1), datetime.date(first_year, 12, 31), 'Все', is_exclude).get(),
                analytics.Received(self.data, 'month', datetime.date(second_year, 1, 1), datetime.date(second_year, 12, 31),
                                   "Все", is_exclude).get(),
                analytics.Received(self.data, 'month', datetime.date(third_year, 1, 1), datetime.date(third_year, 12, 31),
                                   "Все", is_exclude).get()
            ], first_year, second_year, third_year)

    def phases(self):
        is_submitted, begin, end, manager, excluding_status = __call_dialog_and_fetch_data__(
            True, False, True, True)
        if is_submitted:
            title = DefaultTitleBuilder(
                "Распределение незакрытых заявок по фазам", begin, end, manager).build()
            plots.Pie(analytics.Phases(self.data, begin, manager, excluding_status).get(), title='Фазы незакрытых заявок',
                      suptitle=title)

    def average_time(self):
        is_submitted, begin, end, manager, excluding_status = __call_dialog_and_fetch_data__(
            True, True, True, True)
        if is_submitted:
            title = DefaultTitleBuilder(
                "Среднее время выполнения заявок", begin, end, manager).build()
            plots.PlotAverageTime(analytics.AverageTime(
                self.data, manager, begin, end, excluding_status).get(), title)

    def done_wait_receive(self):
        is_submitted, begin, end, manager, excluding_status = __call_dialog_and_fetch_data__(
            True, True, True, True)
        if is_submitted:
            title = DefaultTitleBuilder("Сравнение поступивших, выполненных и ожидающих заявок", begin, end,
                                        manager).build()
            plots.DoneWaitReceive([
                analytics.Received(self.data, 'week', begin,
                                   end, manager, excluding_status).get(),
                analytics.Waiting(self.data, begin, end,
                                  manager, 'week', excluding_status).get(),
                analytics.Done(self.data, begin, end, manager, excluding_status).get()
            ],
                title)

    def provider_delay(self):
        analytics.DelayProvider(self.data)
        QMessageBox(text='Записано в файл!').exec()

    def daily_scheduler(self):
        self.w = DayScheduleWindow(self.data)
        self.w.setWindowTitle("Выбор даты")
        self.w.show()

    def warranty(self):
        is_submitted, begin, end, manager = __call_dialog_and_fetch_data__(
            True, False, True, False)
        if is_submitted:
            title = DefaultTitleBuilder(
                "Распределение незакрытых гарантийных заявок", begin, end, manager).build()
            plots.Pie(analytics.Warranty(self.data, begin, manager).get(),
                      title,
                      title)

    def priorities(self):
        is_submitted, begin, end, manager, excluding_status = __call_dialog_and_fetch_data__(
            True, False, True, True)
        if is_submitted:
            title = DefaultTitleBuilder(
                "Распределение приоритетов в незакрытых заявках", begin, end, manager).build()
            plots.Pie(analytics.Priority(self.data, begin, manager, excluding_status).get(),
                      title,
                      title)

    def repeats(self):
        analytics.RequestRepeats(self.data)
        QMessageBox(text='Записано в файл!').exec()

    def types(self):
        is_submitted, begin, end, manager, excluding_status = __call_dialog_and_fetch_data__(
            True, True, True, False)
        if is_submitted:
            title = DefaultTitleBuilder(
                "Распределение заявок по гарантийности", begin, end, manager).build()
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
