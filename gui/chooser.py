import datetime
import fs.settings

import pandas as pd
import numpy as np
from PyQt5.QtWidgets import QPushButton, QCheckBox, QComboBox, QDateTimeEdit, QLabel, QDialog, QGridLayout, QGroupBox, \
    QHBoxLayout, QVBoxLayout, QSpinBox, QDoubleSpinBox


class DataAndManagerChooser(QDialog):
    __autocompletion_unit__: fs.settings.AutocompletionUnit
    __min_date__: datetime.date

    def __init__(self, data_begin_enable: bool, data_end_enable: bool, manager_enable: bool, managers: list[str],
                 autocompletion_unit: fs.settings.AutocompletionUnit,
                 requests_type_enable=True, min_date=datetime.datetime.min):
        super(DataAndManagerChooser, self).__init__()
        self.__min_date__ = min_date
        self.__autocompletion_unit__ = autocompletion_unit
        self.layout = QGridLayout()
        self.data_begin_checkbox = None
        self.data_end_checkbox = None
        self.requests_type_checkbox = None
        if data_begin_enable:
            self.data_begin_label = QLabel("Выберите начало периода")
            self.data_begin_checkbox = QCheckBox('Учитывать дату')
            date_begin = min_date
            if autocompletion_unit.get("date_begin") is not None:
                date_begin = autocompletion_unit.get("date_begin")
            self.data_begin_calendar = QDateTimeEdit(date_begin)
            if autocompletion_unit.get("date_begin_enable") is not None:
                self.data_begin_checkbox.setChecked(autocompletion_unit.get("date_begin_enable"))
            else:
                self.data_begin_checkbox.setChecked(True)

            self.data_begin_calendar.setDisplayFormat("dd.MM.yyyy")

            self.layout.addWidget(self.data_begin_label, 0, 0)
            self.layout.addWidget(self.data_begin_calendar, 1, 0)
            self.layout.addWidget(self.data_begin_checkbox, 2, 0)

        if data_end_enable:
            self.data_end_label = QLabel("Выберите конец периода")
            self.data_end_checkbox = QCheckBox('Учитывать дату')
            date_end = min_date
            if autocompletion_unit.get("date_end") is not None:
                date_end = autocompletion_unit.get("date_end")
            self.data_end_calendar = QDateTimeEdit(date_end)
            if autocompletion_unit.get("date_end_enable") is not None:
                self.data_end_checkbox.setChecked(autocompletion_unit.get("date_end_enable"))
            else:
                self.data_end_checkbox.setChecked(True)
            self.data_end_calendar = QDateTimeEdit(datetime.datetime.today())
            self.data_end_calendar.setDisplayFormat("dd.MM.yyyy")
            self.layout.addWidget(self.data_end_label, 0, 1)
            self.layout.addWidget(self.data_end_calendar, 1, 1)
            self.layout.addWidget(self.data_end_checkbox, 2, 1)

        if manager_enable:
            self.manager_chooser = QComboBox()
            self.manager_chooser.addItem('Все сотрудники')
            for i in managers:
                self.manager_chooser.addItem(i)

            if autocompletion_unit.get("manager") is not None:
                manager = autocompletion_unit.get("manager")
                if manager == 'Все сотрудники':
                    self.manager_chooser.setCurrentIndex(0)
                elif manager in managers:
                    self.manager_chooser.setCurrentIndex(np.where(managers == manager)[0][0] + 1)

            self.layout.addWidget(self.manager_chooser)

        if requests_type_enable:
            self.requests_type_checkbox = QCheckBox(
                "Исключить внутренние заявки")

            if autocompletion_unit.get("is_exclude") is not None:
                self.requests_type_checkbox.setChecked(autocompletion_unit.get("is_exclude"))
            else:
                self.requests_type_checkbox.setChecked(True)

            self.layout.addWidget(self.requests_type_checkbox)

        self.is_submitted = False
        self.data_submit_button = QPushButton("Применить")
        self.data_submit_button.clicked.connect(self.submit)
        self.layout.addWidget(self.data_submit_button)
        self.setLayout(self.layout)

    def get_date_begin(self) -> pd.Timestamp:
        if self.data_begin_checkbox is not None:
            if self.data_begin_checkbox.isChecked():
                self.__autocompletion_unit__.set("date_begin", self.data_begin_calendar.date().toPyDate())
                self.__autocompletion_unit__.set("date_begin_enable", True)
                return pd.Timestamp(self.data_begin_calendar.date().toPyDate())
            self.__autocompletion_unit__.set("date_begin_enable", False)
        return pd.Timestamp(self.__min_date__)

    def get_date_end(self) -> pd.Timestamp:
        if self.data_end_checkbox is not None:
            if self.data_end_checkbox.isChecked():
                self.__autocompletion_unit__.set("date_end", self.data_begin_calendar.date().toPyDate())
                self.__autocompletion_unit__.set("date_end_enable", True)
                return pd.Timestamp(self.data_end_calendar.date().toPyDate())
            self.__autocompletion_unit__.set("date_end_enable", False)
        return pd.Timestamp.today()

    def get_manager(self):
        if self.manager_chooser is not None:
            self.__autocompletion_unit__.set("manager", self.manager_chooser.currentText())
            return self.manager_chooser.currentText()
        return 'Все сотрудники'

    def get_request_excluding_status(self):
        if self.requests_type_checkbox is not None:
            self.__autocompletion_unit__.set("is_exclude", self.requests_type_checkbox.isChecked())
            return self.requests_type_checkbox.isChecked()
        else:
            return False

    def submit(self):
        self.is_submitted = True
        self.close()


class ThreeYearsChooserBuilder:
    __autocompletion_unit__: fs.settings.AutocompletionUnit

    def __init__(self, autocompletion_unit: fs.settings.AutocompletionUnit):
        self.__autocompletion_unit__ = autocompletion_unit
        self.widget = QDialog()
        layout = QVBoxLayout()
        self.first_year = QSpinBox()
        self.second_year = QSpinBox()
        self.third_year = QSpinBox()
        self.first_year.setMinimum(datetime.date.min.year)
        self.second_year.setMinimum(datetime.date.min.year)
        self.third_year.setMinimum(datetime.date.min.year)
        self.first_year.setMaximum(datetime.date.today().year)
        self.second_year.setMaximum(datetime.date.today().year)
        self.third_year.setMaximum(datetime.date.today().year)

        if self.__autocompletion_unit__.get("first_year") is not None:
            self.first_year.setValue(self.__autocompletion_unit__.get("first_year"))
        else:
            self.first_year.setValue(datetime.date.today().year)

        if self.__autocompletion_unit__.get("second_year") is not None:
            self.second_year.setValue(self.__autocompletion_unit__.get("second_year"))
        else:
            self.second_year.setValue(datetime.date.today().year - 1)

        if self.__autocompletion_unit__.get("third_year") is not None:
            self.third_year.setValue(self.__autocompletion_unit__.get("third_year"))
        else:
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
        self.__autocompletion_unit__.set("first_year", self.first_year.value())
        self.__autocompletion_unit__.set("second_year", self.second_year.value())
        self.__autocompletion_unit__.set("third_year", self.third_year.value())
        self.widget.close()
        self.is_submitted = True

    def build(self):
        return self.widget

    def get_years(self) -> tuple[int, int, int]:
        return self.first_year.value(), self.second_year.value(), self.third_year.value()

    def get_excluding_requests(self) -> bool:
        return self.checkbox_exclude_requests.isChecked()


class SLChooser(DataAndManagerChooser):
    def __init__(self, autocompletion_unit: fs.settings.AutocompletionUnit):
        super().__init__(True, True, False, [], requests_type_enable=True, autocompletion_unit=autocompletion_unit)

        self.limit_level_label = QLabel("Укажите пороговый Service Level в %")
        self.limit_level_box = QDoubleSpinBox()
        if self.__autocompletion_unit__.get("limit_level") is not None:
            self.limit_level_box.setValue(self.__autocompletion_unit__.get("limit_level"))
        else:
            self.limit_level_box.setValue(80)
        self.limit_level_box.setMaximum(100)
        self.limit_level_box.setMinimum(0)
        self.limit_level_box.setSingleStep(1)

        self.sla_label = QLabel("Укажите SLA в днях")
        self.sla_box = QDoubleSpinBox()
        if self.__autocompletion_unit__.get("sla") is not None:
            self.sla_box.setValue(self.__autocompletion_unit__.get("sla"))
        else:
            self.sla_box.setValue(5)
        self.sla_box.setMinimum(1)
        self.sla_box.setSingleStep(1)

        self.worker_type_label = QLabel("Выберите роль сотрудников")
        self.worker_type_box = QComboBox()

        self.worker_type_box.addItem('Менеджеры')
        self.worker_type_box.addItem('Инженеры')

        if self.__autocompletion_unit__.get("worker_type") is not None:
            role = self.__autocompletion_unit__.get("worker_type")
            if role == 'Менеджеры':
                self.worker_type_box.setCurrentIndex(0)
            elif role == 'Инженеры':
                self.worker_type_box.setCurrentIndex(1)

        self.layout.addWidget(self.limit_level_label)
        self.layout.addWidget(self.limit_level_box)
        self.layout.addWidget(self.sla_label)
        self.layout.addWidget(self.sla_box)
        self.layout.addWidget(self.worker_type_label)
        self.layout.addWidget(self.worker_type_box)

        self.layout.removeWidget(self.data_submit_button)
        self.layout.addWidget(self.data_submit_button)

    def get_sla(self) -> int:
        self.__autocompletion_unit__.set("sla", int(self.sla_box.value()))
        return int(self.sla_box.value())

    def get_limit_level(self) -> int:
        self.__autocompletion_unit__.set("limit_level", int(self.limit_level_box.value()))
        return int(self.limit_level_box.value())

    def get_worker_type(self) -> str:
        self.__autocompletion_unit__.set("worker_type", self.worker_type_box.currentText())
        return self.worker_type_box.currentText()
