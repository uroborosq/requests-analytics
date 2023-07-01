import os

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QFormLayout

import fs.settings


class PrioritySettingsWindow(QWidget):
    __settings_manager__: fs.settings.SettingsManager

    def __init__(self, settings_manager: fs.settings.SettingsManager):
        super().__init__()
        self.__settings_manager__ = settings_manager
        layout = QVBoxLayout()
        self.line = QLineEdit()
        button_set = QPushButton('Применить настройки')
        button_set.clicked.connect(self.set_custom)
        self.button_set_default = QPushButton(
            'Установить настройки по умолчанию')
        self.button_set_default.clicked.connect(self.set_default)
        self.line.returnPressed.connect(self.set_custom)
        settings = self.__settings_manager__.get_priorities()
        for i in settings:
            self.line.setText(self.line.text() + ',' + i)
        self.line.setText(self.line.text()[1:])
        layout.addWidget(self.line)
        layout.addWidget(button_set)
        layout.addWidget(self.button_set_default)
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(
            os.path.realpath(__file__)), 'assets', 'icons', 'app_icon.png')))
        self.setLayout(layout)

    def set_custom(self):
        keys = [i for i in self.line.text().split(',')]
        self.__settings_manager__.set_priorities(keys)

    def set_default(self):
        self.__settings_manager__.set_default()


# class ParserSettingsWindow(QWidget):
#     def __init__(self):
#         super().__init__()
#         layout = QFormLayout()
#
#         self.lines = [QLineEdit() for _ in range(files.len_dct(2))]
#
#         button_set = QPushButton('Применить настройки')
#         button_set.clicked.connect(self.set_custom)
#         self.button_set_default = QPushButton(
#             'Установить настройки по умолчанию')
#         self.button_set_default.clicked.connect(self.set_default)
#         self.lines[-1].returnPressed.connect(self.set_custom)
#
#         settings = files.get_settings()
#         j = 0
#         for i in settings[2].values():
#             self.lines[j].setText(i)
#             j += 1
#         self.setWindowIcon(QIcon(os.path.dirname(
#             os.path.realpath(__file__)) + os.path.sep + '1.png'))
#         layout.addRow(self.tr('&Наряд заказ'), self.lines[0])
#         layout.addRow(self.tr('&Дата поступления'), self.lines[1])
#         layout.addRow(self.tr('&Дата закрытия'), self.lines[2])
#         layout.addRow(self.tr('&Дата начала работ'), self.lines[3])
#         layout.addRow(self.tr('&Статус'), self.lines[4])
#         layout.addRow(self.tr('&Фаза'), self.lines[5])
#         layout.addRow(self.tr('&Менеджер'), self.lines[6])
#         layout.addRow(self.tr('&Инженер'), self.lines[7])
#         layout.addRow(self.tr('&Гарантийность'), self.lines[8])
#         layout.addRow(self.tr('&Клиент'), self.lines[9])
#         layout.addRow(self.tr('&Адрес'), self.lines[10])
#         layout.addRow(self.tr('&Модель'), self.lines[11])
#         layout.addRow(self.tr("&Приоритет"), self.lines[12])
#         layout.addRow(self.tr('&Количество строк в загововке'), self.lines[13])
#         layout.addWidget(button_set)
#         layout.addWidget(self.button_set_default)
#
#         self.setLayout(layout)
#
#     def set_custom(self):
#         try:
#             if self.__check__():
#                 j = 0
#                 for i in files.default_settings()[2]:
#                     files.set_settings(2, i, self.lines[j].text())
#                     j += 1
#         except ValueError:
#             QMessageBox(text='Неверные данные').exec()
#         except KeyError:
#             QMessageBox(text='KeyError').exec()
#
#     def __check__(self):
#         for i in self.lines[:1]:
#             for j in i.text():
#                 if not ('A' <= j <= 'Z'):
#                     raise ValueError
#
#         if self.lines[-1].text().isdigit():
#             return True
#         raise ValueError
#
#     def set_default(self):
#         files.set_default(2)
