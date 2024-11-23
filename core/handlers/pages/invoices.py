import os
from datetime import date, datetime, timedelta

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QDialog, QTableWidgetItem

from conf.config import INVOICES_TABLE_COLUMNS_COUNT
from core.db.crud import invoices as crud
from core.db.util import get_application_path
from core.utils.overwrites import loadUi_


class InvoicesPage(QDialog):
    widget: QtWidgets.QStackedWidget

    def __init__(self, widget: QtWidgets.QStackedWidget):
        super(InvoicesPage, self).__init__()
        loadUi_(os.path.join(get_application_path(), "uis/invoices/Invoices.ui"), self)

        self.widget = widget

        self.newInvoiceButton.clicked.connect(self.makeNewInvoice)
        self.showInvoicesButton.clicked.connect(self.showInvoices)
        self.PlotsButton.clicked.connect(self.showPlots)
        self.ReportsButton.clicked.connect(self.showReports)

        self.tableWidget.doubleClicked.connect(self.goToInvoice)

        self.tableWidget.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch
        )
        self.tableWidget.setColumnHidden(0, 1)
        self.tableWidget.setSortingEnabled(True)

        second_date = date.today()
        first_date = date.today() - timedelta(days=30)
        self.datePicker1.setDate(first_date)
        self.datePicker2.setDate(second_date)
        self.showInvoices()

    def makeNewInvoice(self):
        self.widget.widget(1).setNewInvoice()
        self.widget.setCurrentIndex(1)

    def showInvoices(self):
        date1: str = self.datePicker1.date().toString("yyyy-MM-dd")
        date2: str = (self.datePicker2.date().toPyDate() + timedelta(days=1)).strftime(
            "yyyy-MM-dd"
        )

        result = crud.get_invoices(date1, date2)

        self.tableWidget.setRowCount(len(result))

        for i, row in enumerate(result):
            self.tableWidget.setItem(i, 0, QTableWidgetItem(row.id))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(row.date))
            self.tableWidget.setItem(i, 2, QTableWidgetItem(row.name))
            self.tableWidget.setItem(i, 3, QTableWidgetItem(row.goods))
            self.tableWidget.setItem(i, 4, QTableWidgetItem(row.earning))

    def goToInvoice(self, index):
        row = self.tableWidget.item(self.tableWidget.currentRow(), 0).text()
        self.widget.setCurrentIndex(1)
        self.widget.widget(1).changeInfo(row)

    def showPlots(self):
        self.widget.setCurrentIndex(2)

    def showReports(self):
        self.widget.widget(3).showReports()
        self.widget.setCurrentIndex(3)
