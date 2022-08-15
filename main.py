import sys

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import *
from PyQt6.uic import loadUi


class Invoices(QDialog):
    def __init__(self):
        super(Invoices, self).__init__()
        loadUi("Invoices.ui", self)


class Invoice(QDialog):
    def __init__(self):
        super(Invoice, self).__init__()
        loadUi("Invoice.ui", self)


app = QApplication(sys.argv)
mainwindow = Invoices()
widget = QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)
widget.setFixedWidth(960)
widget.setFixedHeight(560)
widget.show()
sys.exit(app.exec())
