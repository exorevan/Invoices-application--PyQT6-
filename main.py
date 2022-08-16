import sqlite3
import sys

# from PyQt5.QtWidgets import *
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import *
from PyQt6.uic import loadUi


class Invoices(QDialog):
    def __init__(self):
        super(Invoices, self).__init__()
        loadUi("uis/invoices/Invoices.ui", self)
        self.newInvoiceButton.clicked.connect(self.makeNewInvoice)
        self.showInvoicesButton.clicked.connect(self.showInvocies)
        self.PlotsButton.clicked.connect(self.showPlots)
        self.ReportsButton.clicked.connect(self.showReports)

        self.tableWidget.doubleClicked.connect(self.goToInvoice)

        self.tableWidget.setColumnWidth(0, 0)

    def makeNewInvoice(self):
        widget.setCurrentIndex(1)
        # invoice = Invoice()
        # widget.setCurrentWidget(invoice)

    def showInvocies(self):
        date1 = self.datePicker1.date().toString('yyyy-MM-dd')
        date2 = self.datePicker2.date().toString('yyyy-MM-dd')

        select = "select id, date, invoice_name as 'Invoice Name', goods, earning from invoices where date between '" + date1 + "' and '" + date2 + "'"
        result = dbutil.select(select)

        self.tableWidget.setRowCount(len(result))

        for i in range(len(result)):
            for j in range(5):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(result[i][j])))

    def goToInvoice(self, index):
        row = self.tableWidget.item(self.tableWidget.currentRow(), 0).text()
        invoice.changeInfo(row)
        widget.setCurrentIndex(1)

    def showPlots(self):
        widget.setCurrentIndex(2)

    def showReports(self):
        widget.setCurrentIndex(3)


class Invoice(QDialog):
    def __init__(self):
        super(Invoice, self).__init__()
        loadUi("uis/invoice/Invoice.ui", self)

        self.goBackToInvoicesButton.clicked.connect(self.goBackToInvoices)
        self.addRowButton.clicked.connect(self.addRow)
        self.deleteRowButton.clicked.connect(self.deleteRow)

        self.tableWidget.setColumnWidth(0, 0)

    def goBackToInvoices(self):
        widget.setCurrentIndex(0)

    def changeInfo(self, index):
        select = "select id, width, height, count, price, total_price as 'Total price' from goods where invoice = " + index
        result = dbutil.select(select)

        for i in range(len(result)):
            for j in range(6):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(result[i][j])))

    def addRow(self):
        currentRow = self.tableWidget.currentRow()
        self.tableWidget.insertRow(currentRow + 1)

    def deleteRow(self):
        if self.tableWidget.rowCount() >= 0:
            currentRow = self.tableWidget.currentRow()
            self.tableWidget.removeRow(currentRow + 1)


class Plots(QDialog):
    def __init__(self):
        super(Plots, self).__init__()
        loadUi("uis/plots/Plots.ui", self)
        self.goBackToInvoicesButton.clicked.connect(self.goBackToInvoices)

    def goBackToInvoices(self):
        widget.setCurrentIndex(0)


class Reports(QDialog):
    def __init__(self):
        super(Reports, self).__init__()
        loadUi("uis/reports/Reports.ui", self)
        self.goBackToInvoicesButton.clicked.connect(self.goBackToInvoices)

    def goBackToInvoices(self):
        widget.setCurrentIndex(0)


class DBUtil():
    def __init__(self):
        self.connection = sqlite3.connect('db/Accounting.db')
        self.cursor = self.connection.cursor()

    def select(self, select):
        self.cursor.execute(select)

        return self.cursor.fetchall()


dbutil = DBUtil()
app = QApplication(sys.argv)
widget = QtWidgets.QStackedWidget()

invoices = Invoices()
invoice = Invoice()
plots = Plots()
reports = Reports()

widget.addWidget(invoices)
widget.addWidget(invoice)
widget.addWidget(plots)
widget.addWidget(reports)

widget.setFixedWidth(960)
widget.setFixedHeight(560)
widget.show()

sys.exit(app.exec())
dbutil.connection.close()
