import os
from datetime import date, timedelta

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QDialog, QHeaderView, QTableWidgetItem

from conf.config import REPORTS_TABLE_COLUMNS_COUNT
from core.db.crud import reports as crud
from core.db.util import get_application_path
from core.utils.overwrites import loadUi_


class ReportsPage(QDialog):
    widget: QtWidgets.QStackedWidget
    """
    The ReportsPage class is responsible for displaying reports based on selected date ranges.
    It provides functionality to update the summary labels and table with data from the database.
    """

    def __init__(self, widget: QtWidgets.QStackedWidget):
        super(ReportsPage, self).__init__()
        loadUi_(os.path.join(get_application_path(), "uis/reports/Reports.ui"), self)

        self.widget = widget

        self.datePicker1.setDate(date.today() - timedelta(days=30))
        self.datePicker2.setDate(date.today())

        self.goBackToInvoicesButton.clicked.connect(self.goBackToInvoices)
        self.showReportsButton.clicked.connect(self.showReports)

        self.tableWidget.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.tableWidget.setSortingEnabled(True)

        self.showReports()

    def datePickerValidation(self):
        """
        Validates the selected date range and ensures that the start date is not greater than the end date.
        """
        if self.datePicker1.date() > self.datePicker2.date():
            self.datePicker1.setDate(self.datePicker2.date())
            self.datePicker2.setDate(self.datePicker1.date())

    def showReports(self):
        """
        Updates the summary labels and table with data based on the selected date range.
        """
        date1 = self.datePicker1.date().toString("yyyy-MM-dd")
        date2: str = (self.datePicker2.date().toPyDate() + timedelta(days=1)).strftime(
            "yyyy-MM-dd"
        )

        self.datePickerValidation()

        self.updateSummaryLabels(date1, date2)
        self.updateTable(date1, date2)

    def updateSummaryLabels(self, date1: str, date2: str):
        """
        Updates the summary labels with the total count and total price of goods within the specified date range.

        Args:
            date1: The start date of the date range.
            date2: The end date of the date range.
        """
        result = crud.get_goods_summary(date1=date1, date2=date2)[0]

        self.goodsLabel.setText(result.count if result.count else "0")
        self.sumLabel.setText(result.total_price if result.total_price else "0")

    def updateTable(self, date1: str, date2: str):
        """
        Updates the table with the width, height, count, and total price of goods within the specified date range.

        Args:
            date1: The start date of the date range.
            date2: The end date of the date range.
        """
        result = crud.get_goods_parameters(date1=date1, date2=date2)

        self.tableWidget.setRowCount(len(result))

        for i, row in enumerate(result):
            self.tableWidget.setItem(i, 0, QTableWidgetItem(row.width))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(row.height))
            self.tableWidget.setItem(i, 2, QTableWidgetItem(row.count))
            self.tableWidget.setItem(i, 3, QTableWidgetItem(row.price))

    def goBackToInvoices(self):
        """
        Navigates back to the invoices page.
        """
        self.widget.setCurrentIndex(0)
