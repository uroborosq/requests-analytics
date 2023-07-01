import os

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QMessageBox

import fs.settings
import fs.report
from gui.plot_choice import PlotChoice
from parser.parser import Parser


class FileChoice(QWidget):
    __settings_manager__: fs.settings.SettingsManager
    widget: QWidget

    def __init__(self, settings_manager: fs.settings.SettingsManager, work_dir: str):
        super().__init__()
        os.chdir(work_dir)
        self.__settings_manager__ = settings_manager
        self.layout = QVBoxLayout()
        # self.file = QFileDialog()
        self.button = QPushButton("Старт")
        button_settings_parser = QPushButton("Настройки парсера")
        self.text1 = QLabel("Введите адрес файла формата xlsx")
        self.report_file_path_label = QLabel("Введите путь к файлу для отчета")
        self.input_1 = QLineEdit()
        self.report_file_path_line = QLineEdit()
        self.input_1.returnPressed.connect(self.get_text)
        self.input_1.textChanged.connect(self.change_report_line)

        if self.__settings_manager__.get_autocompletion('file_choice', 'main_window_path') is not None:
            self.input_1.setText(self.__settings_manager__.get_autocompletion('file_choice', 'main_window_path'))
        if self.__settings_manager__.get_autocompletion('file_choice', "report_path") is not None:
            self.report_file_path_line.setText(self.__settings_manager__.get_autocompletion('file_choice', 'report_path'))

        self.label_parser = QLabel('')

        self.layout.addWidget(self.text1)
        self.layout.addWidget(self.input_1)
        self.layout.addWidget(self.report_file_path_label)
        self.layout.addWidget(self.report_file_path_line)
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
                self.__settings_manager__.set_autocompletion('file_choice', 'main_window_path', self.input_1.text())
                self.__settings_manager__.set_autocompletion('file_choice', 'report_path', self.report_file_path_line.text())
                parser = Parser(self.input_1.text(), 'TDSheet', 5)
                parser.parse()
                report_builder = fs.report.ReportBuilder(self.report_file_path_line.text(), self.report_file_path_line.text() == self.input_1.text())
                report_builder.write_invalid(parser.invalid)
                self.widget = PlotChoice(parser, self.__settings_manager__, report_builder)
                self.widget.setWindowTitle("Выбор графиков")
                self.widget.show()
                self.hide()
            except FileNotFoundError:
                warn = QMessageBox()
                warn.setText("Файл не найден")
                warn.setWindowTitle("Файл не найден")
                warn.exec()
        else:
            warn = QMessageBox()
            warn.setText("Заполните поля")
            warn.setWindowTitle("Э")
            warn.exec()

    def settings_parser(self):
        warn = QMessageBox(parent=self)
        warn.setText("Функция временно отключена. Следите за обновлениями")
        warn.setWindowTitle("Э")
        warn.exec()

    def change_report_line(self):
        self.report_file_path_line.setText("report_" + self.input_1.text())
