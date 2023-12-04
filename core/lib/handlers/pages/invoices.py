from datetime import date, timedelta

from config import INVOICES_TABLE_COLUMNS_COUNT
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QDialog, QTableWidgetItem
from PyQt6.uic import loadUi


class InvoicesPage(QDialog):
    def __init__(self, widget, dbutil):
        super(InvoicesPage, self).__init__()
        loadUi("uis/invoices/Invoices.ui", self)

        self.widget = widget
        self.dbutil = dbutil

        self.newInvoiceButton.clicked.connect(self.makeNewInvoice)
        self.showInvoicesButton.clicked.connect(self.showInvocies)
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
        self.showInvocies()

    def makeNewInvoice(self):
        self.widget.widget(1).setNewInvoice()
        self.widget.setCurrentIndex(1)

    def showInvocies(self):
        date1 = self.datePicker1.date().toString("yyyy-MM-dd")
        date2 = self.datePicker2.date().toString("yyyy-MM-dd")

        select = f"select id, date, invoice_name as 'Invoice Name', goods, earning from invoices where date between '{date1}' and '{date2}'"
        result = self.dbutil.select(select)

        self.tableWidget.setRowCount(len(result))

        for i, row in enumerate(result):
            for j in range(INVOICES_TABLE_COLUMNS_COUNT):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(row[j])))

    def goToInvoice(self, index):
        row = self.tableWidget.item(self.tableWidget.currentRow(), 0).text()
        self.widget.setCurrentIndex(1)
        self.widget.widget(1).changeInfo(row)

    def showPlots(self):
        self.widget.setCurrentIndex(2)

    def showReports(self):
        self.widget.widget(3).showReports()
        self.widget.setCurrentIndex(3)
