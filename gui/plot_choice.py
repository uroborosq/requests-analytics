import datetime

import pandas as pd
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QMessageBox,
)

import fs.settings
import fs.report
import parser.parser
from gui.chooser import ThreeYearsChooserBuilder, DataAndManagerChooser, SLChooser
from gui.day_schedule import DayScheduleWindow
from gui.settings import PrioritySettingsWindow
from title_builder import DefaultTitleBuilder
import analytic.filter
import analytic.analyzer
from plots import plots


class PlotChoice(QWidget):
    __settings_manager__: fs.settings.SettingsManager
    __parser__: parser.parser.Parser
    __report_builder__: fs.report.ReportBuilder
    w: QWidget
    years_window: ThreeYearsChooserBuilder

    def __init__(
        self,
        data_parser: parser.parser.Parser,
        settings_manager: fs.settings.SettingsManager,
        report_builder: fs.report.ReportBuilder,
    ):
        super().__init__()

        self.__parser__ = data_parser
        self.data = self.__parser__.requests
        self.__report_builder__ = report_builder
        layout = QVBoxLayout()
        self.__settings_manager__ = settings_manager
        button_three_years = QPushButton("График про три года")
        button_phases = QPushButton("Диаграмма про фазы")
        button_average_time = QPushButton("График про среднее время")
        button_done_wait_received = QPushButton("Поступившие, закрытые и не закрытые")
        button_provider_delay = QPushButton("Вывести в файл просрочки поставщика")
        button_daily_scheduler = QPushButton("Форма для дневного отчета")
        button_warranty = QPushButton("Диаграмма про гарантию и вывод в файл")
        button_priorities = QPushButton("Распределение приоритетов")
        button_repeats = QPushButton("Найти повторы заявок")
        button_settings_priorities = QPushButton("Настройки диаграммы приоритетов")
        button_types = QPushButton("Распределение заявок по видам")
        button_sl = QPushButton("Диаграмма SL")

        label_clients_counter = QLabel(
            "Клиентов за текущий год насчитано: "
            + str(analytic.analyzer.ClientCounterAnalyzer(self.data).get().size)
        )
        label_version = QLabel("версия " + self.__settings_manager__.get_version())

        layout.addWidget(button_three_years)
        layout.addWidget(button_phases)
        layout.addWidget(button_average_time)
        layout.addWidget(button_done_wait_received)
        layout.addWidget(button_provider_delay)
        layout.addWidget(button_daily_scheduler)
        layout.addWidget(button_warranty)
        layout.addWidget(button_priorities)
        layout.addWidget(button_repeats)
        layout.addWidget(button_types)
        layout.addWidget(button_sl)
        layout.addWidget(button_settings_priorities)
        layout.addWidget(label_clients_counter)
        layout.addWidget(label_version)

        button_three_years.clicked.connect(self.three_years)
        button_phases.clicked.connect(self.phases)
        button_done_wait_received.clicked.connect(self.done_wait_receive)
        button_average_time.clicked.connect(self.average_time)
        button_daily_scheduler.clicked.connect(self.daily_scheduler)
        button_warranty.clicked.connect(self.warranty)
        button_priorities.clicked.connect(self.priorities)
        button_repeats.clicked.connect(self.repeats)
        button_settings_priorities.clicked.connect(self.settings_priorities)
        button_types.clicked.connect(self.types)
        button_provider_delay.clicked.connect(self.provider_delay)
        button_sl.clicked.connect(self.kpi_sl)

        self.min_date = analytic.analyzer.MinDate(self.data).get()

        self.setLayout(layout)

    def three_years(self):
        self.years_window = ThreeYearsChooserBuilder(
            self.__settings_manager__.get_autocompletion_unit("three_years")
        )
        self.years_window.widget.exec()

        if self.years_window.is_submitted:
            first_year, second_year, third_year = self.years_window.get_years()
            data = self.data.copy()
            if self.years_window.get_excluding_requests():
                data = analytic.filter.internal_requests_filter(self.data)

            plots.PlotThreeYears(
                [
                    analytic.analyzer.ReceivedRequestsMonthAnalyzer(
                        analytic.filter.time_prefilter_by_date_begin(
                            data.copy(),
                            pd.Timestamp(first_year, 1, 1),
                            pd.Timestamp(first_year, 12, 31),
                        )
                    ).get(),
                    analytic.analyzer.ReceivedRequestsMonthAnalyzer(
                        analytic.filter.time_prefilter_by_date_begin(
                            data.copy(),
                            pd.Timestamp(second_year, 1, 1),
                            pd.Timestamp(second_year, 12, 31),
                        )
                    ).get(),
                    analytic.analyzer.ReceivedRequestsMonthAnalyzer(
                        analytic.filter.time_prefilter_by_date_begin(
                            data,
                            pd.Timestamp(third_year, 1, 1),
                            pd.Timestamp(third_year, 12, 31),
                        )
                    ).get(),
                ],
                first_year,
                second_year,
                third_year,
            )

    def phases(self):
        (
            is_submitted,
            begin,
            end,
            manager,
            excluding_status,
        ) = self.__call_dialog_and_fetch_data__(
            True,
            False,
            True,
            True,
            self.__settings_manager__.get_autocompletion_unit("phases"),
        )
        if is_submitted:
            title = DefaultTitleBuilder(
                "Распределение незакрытых заявок по фазам",
                begin,
                end,
                manager,
                excluding_status,
            ).build()
            data = self.data
            if excluding_status:
                data = analytic.filter.internal_requests_filter(data)
            data = analytic.filter.manager_time_prefilter_by_date_begin(
                data, manager, begin, end
            )
            phases_analyzer = analytic.analyzer.PhasesAnalyzer(data)
            data = phases_analyzer.get()
            ids = phases_analyzer.get_ids()

            self.__report_builder__.write_phases(ids)

            plots.Pie(
                data,
                title="Фазы незакрытых заявок",
                suptitle=title,
            )

    def average_time(self):
        (
            is_submitted,
            begin,
            end,
            manager,
            excluding_status,
        ) = self.__call_dialog_and_fetch_data__(
            True,
            True,
            True,
            True,
            self.__settings_manager__.get_autocompletion_unit("average_time"),
        )
        if is_submitted:
            title = DefaultTitleBuilder(
                "Среднее время выполнения заявок", begin, end, manager, excluding_status
            ).build()
            data = self.data
            if excluding_status:
                data = analytic.filter.internal_requests_filter(data)
            data = analytic.filter.manager_filter(data, manager)
            plots.PlotAverageTime(
                analytic.filter.date_postfilter(
                    analytic.analyzer.AverageTimeAnalyzer(data).get(), begin, end
                ),
                title,
            )

    def done_wait_receive(self):
        (
            is_submitted,
            begin,
            end,
            manager,
            excluding_status,
        ) = self.__call_dialog_and_fetch_data__(
            True,
            True,
            True,
            True,
            self.__settings_manager__.get_autocompletion_unit("done_wait_receive"),
        )
        if is_submitted:
            title = DefaultTitleBuilder(
                "Сравнение поступивших, выполненных и ожидающих заявок",
                begin,
                end,
                manager,
                excluding_status,
            ).build()
            data = self.data.copy()
            if excluding_status:
                data = analytic.filter.internal_requests_filter(data)
            data = analytic.filter.manager_filter(data, manager)

            plots.DoneWaitReceive(
                [
                    analytic.filter.date_postfilter(
                        analytic.analyzer.ReceivedRequestsWeeksAnalyzer(
                            data.copy()
                        ).get(),
                        begin,
                        end,
                    ),
                    analytic.filter.date_postfilter(
                        analytic.analyzer.WaitingRequestAnalyzer(data.copy()).get(),
                        begin,
                        end,
                    ),
                    analytic.filter.date_postfilter(
                        analytic.analyzer.DoneRequestsWeeksAnalyzer(data).get(),
                        begin,
                        end,
                    ),
                ],
                title,
            )

    def provider_delay(self):
        delays = analytic.analyzer.DelayProviderAnalyzer(self.data).get()
        self.__report_builder__.write_delay(delays)
        QMessageBox(text="Записано в файл!").exec()

    def daily_scheduler(self):
        self.w = DayScheduleWindow(self.data, self.__settings_manager__)
        self.w.setWindowTitle("Выбор даты")
        self.w.show()

    def warranty(self):
        is_submitted, begin, end, manager, _ = self.__call_dialog_and_fetch_data__(
            True,
            False,
            True,
            False,
            self.__settings_manager__.get_autocompletion_unit("warranty"),
        )
        if is_submitted:
            title = DefaultTitleBuilder(
                "Распределение незакрытых гарантийных заявок",
                begin,
                end,
                manager,
                False,
            ).build()
            data = analytic.filter.manager_time_prefilter_by_date_begin(
                self.data, manager, begin, end
            )
            analyz = analytic.analyzer.WarrantyAnalyzer(data)
            warranty_data = analyz.get()
            self.__report_builder__.write_warranty(analyz.get_ids())
            
            plots.Pie(warranty_data, title, title)

    def priorities(self):
        (
            is_submitted,
            begin,
            end,
            manager,
            excluding_status,
        ) = self.__call_dialog_and_fetch_data__(
            True,
            False,
            True,
            True,
            self.__settings_manager__.get_autocompletion_unit("priorities"),
        )
        if is_submitted:
            title = DefaultTitleBuilder(
                "Распределение приоритетов в незакрытых заявках",
                begin,
                end,
                manager,
                excluding_status,
            ).build()
            data = self.data
            if excluding_status:
                data = analytic.filter.internal_requests_filter(data)
            data = analytic.filter.manager_time_prefilter_by_date_begin(
                data, manager, begin, end
            )
            analyz = analytic.analyzer.PriorityAnalyzer(data)
            self.__report_builder__.write_priorities(analyz.get_ids())
            plots.Pie(analyz.get(), title, title)

    def repeats(self):
        repeats = analytic.analyzer.RequestRepeatsAnalyzer(self.data).get()
        self.__report_builder__.write_repeats(repeats)
        QMessageBox(text="Записано в файл!").exec()

    def types(self):
        (
            is_submitted,
            begin,
            end,
            manager,
            excluding_status,
        ) = self.__call_dialog_and_fetch_data__(
            True,
            True,
            True,
            False,
            self.__settings_manager__.get_autocompletion_unit("types"),
        )
        if is_submitted:
            title = DefaultTitleBuilder(
                "Распределение заявок по гарантийности",
                begin,
                end,
                manager,
                excluding_status,
            ).build()
            data = self.data
            if excluding_status:
                data = analytic.filter.internal_requests_filter(data)

            plots.Pie(
                analytic.analyzer.TypesAnalyzer(data).get(), suptitle=title, title=title
            )

    def settings_priorities(self):
        self.w = PrioritySettingsWindow(self.__settings_manager__)
        self.w.setWindowTitle("Настройки диаграммы приоритетов")
        self.w.show()

    def kpi_sl(self):
        dialog = SLChooser(self.__settings_manager__.get_autocompletion_unit("kpi_sl"))
        dialog.exec()

        if dialog.is_submitted:
            date_begin = dialog.get_date_begin()
            date_end = dialog.get_date_end()
            is_exclude = dialog.get_request_excluding_status()
            sla = dialog.get_sla()
            limit_level = dialog.get_limit_level()
            worker_type = dialog.get_worker_type()

            data = self.data.copy()

            if is_exclude:
                data = analytic.filter.internal_requests_filter(data)
            data = analytic.filter.time_prefilter_by_date_end(
                data, date_begin, date_end
            )

            title = f"""Показатели KPI за период с {date_begin} по {date_end}, внутренние заявки {'исключены' if is_exclude else 'включены'}
            SLA = {sla} дней.
            {worker_type}"""

            if worker_type == "Менеджеры":
                worker_type = analytic.analyzer.WorkerType.Manager
            elif worker_type == "Инженеры":
                worker_type = analytic.analyzer.WorkerType.Engineer

            plots.SLPlot(
                analytic.analyzer.SLAnalyzer(
                    data, datetime.timedelta(sla), worker_type
                ).get(),
                title,
                limit_level,
            )

    def __call_dialog_and_fetch_data__(
        self,
        date_begin_enable,
        date_end_enable,
        manager_enable,
        excluding_requests,
        autocompletion_unit,
    ):
        dialog = DataAndManagerChooser(
            date_begin_enable,
            date_end_enable,
            manager_enable,
            self.__parser__.managers,
            autocompletion_unit,
            requests_type_enable=excluding_requests,
            min_date=self.min_date,
        )
        dialog.exec()

        if dialog.is_submitted:
            return (
                True,
                dialog.get_date_begin(),
                dialog.get_date_end(),
                dialog.get_manager(),
                dialog.get_request_excluding_status(),
            )
        else:
            return [False, 0, 0, 0, False]
