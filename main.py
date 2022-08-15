import sqlite3
import sys

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import *
from PyQt6.uic import loadUi


class Invoices(QDialog):
    def __init__(self):
        super(Invoices, self).__init__()
        loadUi("Invoices.ui", self)
        self.newInvoiceButton.clicked.connect(self.makeNewInvoice)
        self.showInvoicesButton.clicked.connect(self.showInvocies)

    def makeNewInvoice(self):
        widget.setCurrentIndex(widget.currentIndex() + 1)
        # invoice = Invoice()
        # widget.setCurrentWidget(invoice)

    def showInvocies(self):
        date1 = self.datePicker1.date().toString('yyyy-MM-dd')
        date2 = self.datePicker2.date().toString('yyyy-MM-dd')

        select = "select date, invoice_name as 'Invoice Name', goods, earning from invoices where date between '" + date1 + "' and '" + date2 + "'"
        result = dbutil.select(select)

        self.tableWidget.setRowCount(len(result))

        for i in range(len(result)):
            for j in range(4):
                self.tableWidget.setItem(i, j, QTableWidgetItem(result[i][j]))

        a = 10


class Invoice(QDialog):
    def __init__(self):
        super(Invoice, self).__init__()
        loadUi("Invoice.ui", self)
        self.goBackToInvoicesButton.clicked.connect(self.goBackToInvoices)

    def goBackToInvoices(self):
        widget.setCurrentIndex(widget.currentIndex() - 1)


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
widget.addWidget(invoices)
invoice = Invoice()
widget.addWidget(invoice)

widget.setFixedWidth(960)
widget.setFixedHeight(560)
widget.show()
sys.exit(app.exec())
dbutil.connection.close()
