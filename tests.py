import sys

from PyQt5 import QtWidgets
import datetime

from openpyxl.utils import exceptions

import Analytics
import plots
from Parser import Parser


class ManagersBox(QtWidgets.QGroupBox):
    def __init__(self, data):
        super(ManagersBox, self).__init__('Распределение нагрузки на инженеров')
        self.data = dict(data)

        layout = QtWidgets.QVBoxLayout()

        label_managers_names = QtWidgets.QLabel('Введите фамилии инженеров в формате Фамилия1,Фамилия2,Фамилия3.\n'
                                                'Через запятую без пробелов')
        self.line_managers_name = QtWidgets.QLineEdit()
        self.line_managers_name.setText('Тихомиров,Гусев,Баранов')
        label_dates_managers = QtWidgets.QLabel('Введите период для аналитики. Если оставить поле пустым,'
                                                ' то ограничений на период с этой стороны не будет')
        label_begin = QtWidgets.QLabel('Дата начала периода в формате d.m.Y\nПример: 01.01.2021')
        label_end = QtWidgets.QLabel('Дата конца периода в формате d.m.Y')
        self.line_managers_dates_begin = QtWidgets.QLineEdit()
        self.line_managers_dates_end = QtWidgets.QLineEdit()
        button_pie_managers = QtWidgets.QPushButton("Диаграмма про менеджеров")
        button_pie_managers.clicked.connect(self.pie_managers)

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
                end = datetime.datetime.strptime(self.line_managers_dates_begin.text(), '%d.%m.%Y')
                end = end.date()

            names = self.line_managers_name.text()
            plots.PieManagers(Analytics.Managers(self.data, names, begin, end).get())
        except ValueError:
            warn = QtWidgets.QMessageBox()
            warn.setText("Данные введены некорректно")
            warn.exec()


class WarrantyBox(QtWidgets.QGroupBox):
    def __init__(self, data):
        super().__init__('Поиск незакрытых гарантийных заявок по заданному критерию')
        self.data = dict(data)
        self.radio1 = QtWidgets.QRadioButton("Поиск по количеству дней до текущей даты")
        self.line_warranty_number_of_days_begin = QtWidgets.QLineEdit()
        self.line_warranty_number_of_days_end = QtWidgets.QLineEdit()
        self.radio2 = QtWidgets.QRadioButton("Поиск в определенном периоде")
        self.line_warranty_time_period_begin = QtWidgets.QLineEdit()
        self.line_warranty_time_period_end = QtWidgets.QLineEdit()
        self.radio1.setChecked(True)
        button_warranty = QtWidgets.QPushButton('Вывести в файл незакрытые гарантийные заявки')
        button_warranty.clicked.connect(self.find_warranty)
        warranty_layout = QtWidgets.QGridLayout()
        warranty_layout.addWidget(self.radio1, 0, 0)
        warranty_layout.addWidget(self.line_warranty_number_of_days_begin, 0, 1)
        warranty_layout.addWidget(self.line_warranty_number_of_days_end, 1, 1)
        warranty_layout.addWidget(self.radio2, 2, 0)
        warranty_layout.addWidget(self.line_warranty_time_period_begin, 2, 1)
        warranty_layout.addWidget(self.line_warranty_time_period_end, 3, 1)
        warranty_layout.addWidget(button_warranty, 4, 1)
        self.setLayout(warranty_layout)

    def find_warranty(self):
        try:
            if self.radio1.isChecked():
                Analytics.Warranty(self.data, first=self.line_warranty_number_of_days_begin.text(),
                                   second=self.line_warranty_number_of_days_end.text())
            else:
                Analytics.Warranty(self.data, begin=self.line_warranty_time_period_begin.text(),
                                   end=self.line_warranty_time_period_end.text())
        except ValueError:
            QtWidgets.QMessageBox(text='Неверные данные').exec()
        except KeyError:
            QtWidgets.QMessageBox(text='Неверные аргументы функции(отладка)')


class SimplePlots(QtWidgets.QGroupBox):
    def __init__(self, data):
        super().__init__('Аналитика без параметров')
        self.data = dict(data)
        button_plot_three_years = QtWidgets.QPushButton("График про три года")
        button_pie_phases = QtWidgets.QPushButton("Диаграмма про фазы")
        button_average_time = QtWidgets.QPushButton("График про среднее время")
        button_types = QtWidgets.QPushButton("Диаграмма про типы")
        button_done_requests = QtWidgets.QPushButton("График про закрытые заявки")
        button_provider_delay = QtWidgets.QPushButton('Вывести в файл просрочки поставщика')
        button_plot_three_years.clicked.connect(self.plot_three_years)
        button_pie_phases.clicked.connect(self.pie_phases)

        button_average_time.clicked.connect(self.plot_average_time)
        button_types.clicked.connect(self.pie_types)
        button_done_requests.clicked.connect(self.plot_done_requests)
        button_provider_delay.clicked.connect(self.find_provider_delay)
        label_client_counter = QtWidgets.QLabel()
        label_client_counter.setText(
            'Клиентов за текущий год насчитано: ' + str(Analytics.ClientsCounter(self.data).get()))

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(button_plot_three_years)
        layout.addWidget(button_pie_phases)
        layout.addWidget(button_average_time)
        layout.addWidget(button_types)
        layout.addWidget(button_done_requests)
        layout.addWidget(button_provider_delay)
        layout.addWidget(label_client_counter)

        self.setLayout(layout)

    def plot_three_years(self):
        plots.PlotThreeYears(Analytics.AllRequestsThreeYears(self.data).get(),
                             Analytics.WaitingRequests(self.data).get())

    def pie_phases(self):
        plots.PiePhases(Analytics.Phases(self.data).get())

    def plot_average_time(self):
        plots.PlotAverageTime(Analytics.AverageTime(self.data).get())

    def pie_types(self):
        plots.PieTypes(Analytics.Types(self.data).get())

    def plot_done_requests(self):
        plots.PlotDoneRequests(Analytics.DoneRequests(self.data).get())

    def find_provider_delay(self):
        Analytics.DelayProvider(self.data)


class MyWidget(QtWidgets.QMainWindow):
    def __init__(self, arr):
        super().__init__()
        self.data = arr
        self.layout = QtWidgets.QGridLayout()

        warranty_box = WarrantyBox(self.data)
        managers_box = ManagersBox(self.data)
        other = SimplePlots(self.data)
        self.layout.addWidget(managers_box, 0, 0)
        self.layout.addWidget(warranty_box, 1, 0)
        self.layout.addWidget(other, 0, 1)

        self.wnd = QtWidgets.QWidget()
        self.wnd.setLayout(self.layout)
        self.setCentralWidget(self.wnd)


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        wnd = QtWidgets.QWidget()
        self.layout = QtWidgets.QVBoxLayout()
        self.button = QtWidgets.QPushButton("Старт")
        self.text1 = QtWidgets.QLabel("Введите адрес файла формата xlsx")
        self.text2 = QtWidgets.QLabel("Введите имя листа")
        self.input_1 = QtWidgets.QLineEdit()
        self.input_1.setMaximumWidth(250)
        self.input_1.setText("3.xlsx")
        self.input_2 = QtWidgets.QLineEdit()
        self.input_2.setMaximumWidth(250)
        self.input_2.setText("TDSheet")
        self.button.setMaximumWidth(50)
        self.label_parser = QtWidgets.QLabel('')

        self.layout.addWidget(self.text1)
        self.layout.addWidget(self.input_1)
        self.layout.addWidget(self.text2)
        self.layout.addWidget(self.input_2)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.label_parser)
        wnd.setLayout(self.layout)
        self.button.clicked.connect(self.get_text)
        self.input_2.returnPressed.connect(self.get_text)
        # self.setFixedSize(300, 200)
        self.setCentralWidget(wnd)
        self.setWindowTitle("Окно ввода данных")
        self.show()

    def get_text(self):
        self.
        self.label_parser.setText("Считывание данных...")
        if self.input_1.text() != '' and self.input_2.text() != '':
            try:
                parser = Parser(self.input_1.text(), self.input_2.text())
                parser.parse()
                self.widget = MyWidget(parser.requests)
                self.widget.setWindowTitle("Выбор графиков")
                self.hide()
                self.widget.show()
            except FileNotFoundError:
                warn = QtWidgets.QMessageBox()
                warn.setText("Файл не найден")
                warn.setWindowTitle("Э")
                warn.exec()
            except exceptions.InvalidFileException:
                warn = QtWidgets.QMessageBox()
                warn.setText("Неверный формат файла")
                warn.setWindowTitle("Э")
                warn.exec()
            # except:
            #     warn = QtWidgets.QMessageBox()
            #     warn.setText("Непонятно, что сломалось")
            #     warn.setWindowTitle("Э")
            #     warn.exec()
        else:
            warn = QtWidgets.QMessageBox()
            warn.setText("Заполните поля")
            warn.setWindowTitle("Э")
            warn.exec()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec())
