from datetime import date, timedelta

from config import REPORTS_TABLE_COLUMNS_COUNT
from PyQt6.QtWidgets import QDialog, QHeaderView, QTableWidgetItem
from PyQt6.uic import loadUi


class ReportsPage(QDialog):
    """
    The ReportsPage class is responsible for displaying reports based on selected date ranges.
    It provides functionality to update the summary labels and table with data from the database.
    """

    def __init__(self, widget, dbutil):
        """
        Initializes the ReportsPage class by loading the UI file, setting up the initial date range,
        connecting signals to slots, and showing the reports.

        Args:
            widget: The widget that contains the ReportsPage.
            dbutil: The database utility object used to interact with the database.
        """
        super(ReportsPage, self).__init__()
        loadUi("uis/reports/Reports.ui", self)

        self.widget = widget
        self.dbutil = dbutil

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
        date2 = self.datePicker2.date().toString("yyyy-MM-dd")

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
        select = f"select sum(count), sum(total_price) from goods inner join invoices on goods.invoice = invoices.id where date between '{date1}' and '{date2}'"
        result = self.dbutil.select(select)

        self.goodsLabel.setText(str(result[0][0]))
        self.sumLabel.setText(str(result[0][1]))

    def updateTable(self, date1: str, date2: str):
        """
        Updates the table with the width, height, count, and total price of goods within the specified date range.

        Args:
            date1: The start date of the date range.
            date2: The end date of the date range.
        """
        select = f"select width, height, sum(count), sum(total_price) from goods inner join invoices on goods.invoice = invoices.id where date between '{date1}' and '{date2}' group by width, height"
        result = self.dbutil.select(select)

        self.tableWidget.setRowCount(len(result))

        for i, row in enumerate(result):
            for j in range(REPORTS_TABLE_COLUMNS_COUNT):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(row[j])))

    def goBackToInvoices(self):
        """
        Navigates back to the invoices page.
        """
        self.widget.setCurrentIndex(0)
