import sqlite3
import sys
from datetime import date, timedelta, datetime

import matplotlib.pyplot as plt
import numpy as np
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import *
from PyQt6.uic import loadUi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class Invoices(QDialog):
    def __init__(self):
        super(Invoices, self).__init__()
        loadUi("uis/invoices/Invoices.ui", self)
        self.newInvoiceButton.clicked.connect(self.makeNewInvoice)
        self.showInvoicesButton.clicked.connect(self.showInvocies)
        self.PlotsButton.clicked.connect(self.showPlots)
        self.ReportsButton.clicked.connect(self.showReports)

        self.tableWidget.doubleClicked.connect(self.goToInvoice)

        self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tableWidget.setColumnHidden(0, 1)

        second_date = date.today()
        first_date = date.today() - timedelta(days=30)
        self.datePicker1.setDate(first_date)
        self.datePicker2.setDate(second_date)
        self.showInvocies()

    def makeNewInvoice(self):
        invoice.setNewInvoice()
        widget.setCurrentIndex(1)

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
        widget.setCurrentIndex(1)
        invoice.changeInfo(row)

    def showPlots(self):
        widget.setCurrentIndex(2)

    def showReports(self):
        widget.setCurrentIndex(3)


class Invoice(QDialog):
    currentId = 0
    newRows = 0
    maxGoodsId = 0

    def __init__(self):
        super(Invoice, self).__init__()
        loadUi("uis/invoice/Invoice.ui", self)

        self.goBackToInvoicesButton.clicked.connect(self.goBackToInvoices)
        self.addRowButton.clicked.connect(self.addRow)
        self.deleteRowButton.clicked.connect(self.deleteRow)
        self.calculateButton.clicked.connect(self.calculate)
        self.saveButton.clicked.connect(self.save)

        self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tableWidget.setColumnHidden(0,1)

    def goBackToInvoices(self):
        invoices.showInvocies()
        widget.setCurrentIndex(0)

    def setNewInvoice(self):
        self.newRows = 0

        select = "select max(id) from goods"
        result = dbutil.select(select)
        self.maxGoodsId = result[0][0]

        if not self.maxGoodsId:
            self.maxGoodsId = 0

        select = "select max(id) from invoices"
        result = dbutil.select(select)
        newId = int(result[0][0]) + 1
        self.currentId = newId

        self.textbox.setText('')
        self.dateEdit.setDate(date.today())
        self.tableWidget.setRowCount(0)

    def changeInfo(self, index):
        self.newRows = 0
        self.currentId = index

        select = "select max(id) from goods"
        result = dbutil.select(select)
        self.maxGoodsId = result[0][0]

        if not self.maxGoodsId:
            self.maxGoodsId = 0

        select = "select id, invoice_name, date, goods, goods_unique, earning from invoices where id = " + index
        result = dbutil.select(select)

        self.textbox.setText(str(result[0][1]))
        self.dateEdit.setDate(datetime.strptime(result[0][2], '%Y-%m-%d'))
        self.date.setText(str(datetime.strptime(result[0][2], '%Y-%m-%d').strftime('%d.%m.%Y')))
        self.uniqueGoods.setText(str(result[0][4]) + " positions")
        self.goods.setText(str(result[0][3]))
        self.sum.setText(str(result[0][5]))

        select = "select id, width, height, count, price, total_price from goods where invoice = " + index
        result = dbutil.select(select)

        self.tableWidget.setRowCount(len(result))
        for i in range(len(result)):
            for j in range(6):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(result[i][j])))

    def addRow(self):
        newId = int(self.maxGoodsId) + self.newRows + 1
        currentRow = self.tableWidget.currentRow()
        self.tableWidget.insertRow(currentRow + 1)
        self.tableWidget.setItem(currentRow + 1, 0, QTableWidgetItem(str(newId)))
        self.newRows += 1

    def deleteRow(self):
        if self.tableWidget.rowCount() > 0:
            currentRow = self.tableWidget.currentRow()

            if currentRow < 0:
                currentRow = 0

            self.tableWidget.removeRow(currentRow)

    def calculate(self):
        sum = 0
        goods = 0
        notNullRows = 0

        for i in range(self.tableWidget.rowCount()):
            if self.upgradedCheck(self.tableWidget.item(i, 1), self.tableWidget.item(i, 2), self.tableWidget.item(i, 3),
                                  self.tableWidget.item(i, 4)):
                count = int(self.tableWidget.item(i, 3).text())
                price = float(self.tableWidget.item(i, 4).text())

                self.tableWidget.setItem(i, 5, QTableWidgetItem(str(count * price)))

                sum += count * price
                goods += count
                notNullRows += 1

        self.uniqueGoods.setText(str(notNullRows) + " positions")
        self.goods.setText(str(goods))
        self.sum.setText(str(sum))

    def numberCheck(self, number):
        try:
            float(number)
            return True
        except ValueError:
            return False

    def upgradedCheck(self, width, height, count, price):
        if not (width is None or height is None or count is None or price is None):
            if self.numberCheck(width.text()) and self.numberCheck(
                    height.text()) and count.text().isdigit() and self.numberCheck(price.text()):
                return True

        return False

    def save(self):
        self.calculate()

        select = "update invoices set invoice_name = '" + self.textbox.toPlainText() + "', date = '" + \
                 self.dateEdit.date().toString('yyyy-MM-dd') + "', goods = " + self.goods.text() + ", goods_unique = " + \
                 self.uniqueGoods.text().replace(' positions', '') + ", earning = " + self.sum.text() + " where id = " + \
                 self.currentId
        result = dbutil.select(select)

        ids = []

        for i in range(self.tableWidget.rowCount()):
            if self.upgradedCheck(self.tableWidget.item(i, 1), self.tableWidget.item(i, 2), self.tableWidget.item(i, 3),
                                  self.tableWidget.item(i, 4)):
                ids.append(int(self.tableWidget.item(i, 0).text()))

                if int(self.tableWidget.item(i, 0).text()) > self.maxGoodsId:
                    select = "insert into goods (invoice, width, height, count, price, total_price) values (" + \
                             str(self.currentId) + ", " + self.tableWidget.item(i, 1).text() + ", " + \
                             self.tableWidget.item(i, 2).text() + ", " + self.tableWidget.item(i, 3).text() + \
                             ", " + self.tableWidget.item(i, 4).text() + ", " + self.tableWidget.item(i, 5).text() + ")"
                    result = dbutil.select(select)
                else:
                    select = "update goods set width = " + self.tableWidget.item(i, 1).text() + ", height = " + \
                             self.tableWidget.item(i, 2).text() + ", count = " + self.tableWidget.item(i, 3).text() + \
                             ", price = " + self.tableWidget.item(i, 4).text() + ", total_price = " + \
                             self.tableWidget.item(i, 5).text() + " where id = " + self.tableWidget.item(i, 0).text()
                    result = dbutil.select(select)

        select = "select id from goods where invoice = " + str(self.currentId)
        result = dbutil.select(select)

        array = [a[0] for a in result]
        toDelete = set(array) - set(ids)

        for id in toDelete:
            select = "delete from goods where id = " + str(id)
            result = dbutil.select(select)



class Plots(QDialog):
    def __init__(self):
        super(Plots, self).__init__()
        loadUi("uis/plots/Plots.ui", self)
        self.goBackToInvoicesButton.clicked.connect(self.goBackToInvoices)
        self.showPlotButton.clicked.connect(self.show_func)

    def show_func(self):
        scene = QtWidgets.QGraphicsScene()
        self.View = QtWidgets.QGraphicsView(scene, self.graphicsView)

        x = np.arange(0, 3 * np.pi, 0.1)
        y = np.sin(x)

        fig, ax = plt.subplots()
        fig.gca()
        ax.plot(x, y)
        ax.grid()
        canvas = FigureCanvas(fig)
        proxy_widget = QtWidgets.QGraphicsProxyWidget()
        proxy_widget.setWidget(canvas)
        scene.addItem(proxy_widget)

        self.View.resize(650, 500)
        self.View.show()

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
        self.select("UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='goods';")

    def select(self, select):
        self.cursor.execute(select)
        self.connection.commit()

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
