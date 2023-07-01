import os
import datetime

import analytic as analytic

import fs.day_scheduler
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QGridLayout, QPushButton, QLabel, QDateTimeEdit, QMessageBox, QWidget
from fs.settings import SettingsManager


class DayScheduleWindow(QWidget):
    __settings_manager__: SettingsManager

    def __init__(self, arr, settings_manager: SettingsManager):
        super().__init__()
        self.__settings_manager__ = settings_manager
        self.data = arr
        self.layout = QGridLayout()
        button_create_form = QPushButton("Сгенерировать форму")
        label_info = QLabel("Введите дату в формате Д.М.Г(21.04.2019)")
        self.line_date = QDateTimeEdit(datetime.datetime.today())
        self.line_date.setDisplayFormat("dd.MM.yyyy")
        if self.__settings_manager__.get_autocompletion('day_schedule', 'day_schedule_date') is not None:
            self.line_date.setDate(self.__settings_manager__.get_autocompletion('day_schedule', 'day_schedule_date'))

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
            self.__settings_manager__.set_autocompletion('day_schedule', 'day_schedule_date', self.line_date.date())
            given_date = datetime.datetime.strptime(
                self.line_date.text(), '%d.%m.%Y')
            output_file = fs.day_scheduler.DaySchedule(
                analytic.analyzer.DayScheduler(self.data, given_date).get(), given_date).get()
            self.label_result.setText('Форма сохранена в файл\n' + output_file)
        except ValueError as e:
            QMessageBox(
                text=f"Неверные данные.\n Текст для отладки: {e.args}").exec()
        except KeyError as e:
            QMessageBox(text='KeyError' + str(e.args)).exec()
