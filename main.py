import sqlite3
import sys
from datetime import date, timedelta, datetime

import matplotlib.pyplot as plt
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
        reports.showReports()
        widget.setCurrentIndex(3)


class Invoice(QDialog):
    currentId = 0
    newRows = 0
    maxGoodsId = 0
    deleted = False

    def __init__(self):
        super(Invoice, self).__init__()
        loadUi("uis/invoice/Invoice.ui", self)

        self.goBackToInvoicesButton.clicked.connect(self.goBackToInvoices)
        self.addRowButton.clicked.connect(self.addRow)
        self.deleteRowButton.clicked.connect(self.deleteRow)
        self.calculateButton.clicked.connect(self.calculate)
        self.saveButton.clicked.connect(self.save)
        self.deleteButton.clicked.connect(self.delete)

        self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tableWidget.setColumnHidden(0, 1)

    def goBackToInvoices(self):
        invoices.showInvocies()
        widget.setCurrentIndex(0)

    def setNewInvoice(self):
        self.newRows = 0
        self.deleted = False

        select = "select max(id) from goods"
        result = dbutil.select(select)
        self.maxGoodsId = result[0][0]

        if not self.maxGoodsId:
            self.maxGoodsId = 0

        select = "select max(id) from invoices"
        result = dbutil.select(select)
        newId = int(result[0][0]) + 1
        self.currentId = newId

        self.textbox.setText(str(datetime.now()))
        self.dateEdit.setDate(date.today())
        self.date.setText(str(datetime.strptime(str(date.today()), '%Y-%m-%d').strftime('%d.%m.%Y')))
        self.tableWidget.setRowCount(0)

        self.uniqueGoods.setText('0')
        self.goods.setText('0')
        self.sum.setText('0')

    def changeInfo(self, index):
        self.newRows = 0
        self.currentId = index
        self.deleted = False

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
        if self.textbox.toPlainText() != "" and self.goods.text() != '' and self.uniqueGoods.text() != '' and self.sum.text() != '':
            select = "select max(id) from invoices"
            result = dbutil.select(select)

            if int(self.currentId) > int(result[0][0]) or self.deleted:
                select = "insert into invoices (id, invoice_name, date, goods, goods_unique, earning) values (" + str(
                    self.currentId) + ", '', '2000-01-01', 0, 0, 0)"
                result = dbutil.select(select)

            self.calculate()

            select = "update invoices set invoice_name = '" + self.textbox.toPlainText() + "', date = '" + \
                     self.dateEdit.date().toString(
                         'yyyy-MM-dd') + "', goods = " + self.goods.text() + ", goods_unique = " + \
                     self.uniqueGoods.text().replace(' positions',
                                                     '') + ", earning = " + self.sum.text() + " where id = " + \
                     str(self.currentId)
            result = dbutil.select(select)

            ids = []

            for i in range(self.tableWidget.rowCount()):
                if self.upgradedCheck(self.tableWidget.item(i, 1), self.tableWidget.item(i, 2),
                                      self.tableWidget.item(i, 3),
                                      self.tableWidget.item(i, 4)):
                    ids.append(int(self.tableWidget.item(i, 0).text()))

                    if int(self.tableWidget.item(i, 0).text()) > self.maxGoodsId:
                        select = "insert into goods (invoice, width, height, count, price, total_price) values (" + \
                                 str(self.currentId) + ", " + self.tableWidget.item(i, 1).text() + ", " + \
                                 self.tableWidget.item(i, 2).text() + ", " + self.tableWidget.item(i, 3).text() + \
                                 ", " + self.tableWidget.item(i, 4).text() + ", " + self.tableWidget.item(i,
                                                                                                          5).text() + ")"
                        result = dbutil.select(select)
                    else:
                        select = "update goods set width = " + self.tableWidget.item(i, 1).text() + ", height = " + \
                                 self.tableWidget.item(i, 2).text() + ", count = " + self.tableWidget.item(i,
                                                                                                           3).text() + \
                                 ", price = " + self.tableWidget.item(i, 4).text() + ", total_price = " + \
                                 self.tableWidget.item(i, 5).text() + " where id = " + self.tableWidget.item(i,
                                                                                                             0).text()
                        result = dbutil.select(select)

            select = "select id from goods where invoice = " + str(self.currentId)
            result = dbutil.select(select)

            array = [a[0] for a in result]
            toDelete = set(array) - set(ids)

            for id in toDelete:
                select = "delete from goods where id = " + str(id)
                result = dbutil.select(select)

        self.deleted = False

    def delete(self):
        self.deleted = True

        select = "delete from goods where invoice = " + str(self.currentId)
        result = dbutil.select(select)

        select = "delete from invoices where id = " + str(self.currentId)
        result = dbutil.select(select)

        select = "select max(id) from goods"
        result = dbutil.select(select)
        self.maxGoodsId = result[0][0]


class Plots(QDialog):
    def __init__(self):
        super(Plots, self).__init__()
        loadUi("uis/plots/Plots.ui", self)
        self.goBackToInvoicesButton.clicked.connect(self.goBackToInvoices)
        self.showPlotButton.clicked.connect(self.show_func)

        second_date = date.today()
        first_date = date.today() - timedelta(days=30)
        self.datePicker1.setDate(first_date)
        self.datePicker2.setDate(second_date)

    def date(self, sdate, edate):
        dates = []
        delta = edate - sdate

        for i in range(delta.days + 1):
            day = sdate + timedelta(days=i)
            dates.append(day.strftime('%Y-%m-%d'))

        return dates

    def show_func(self):
        scene = QtWidgets.QGraphicsScene()
        self.View = QtWidgets.QGraphicsView(scene, self.graphicsView)
        dates = []

        date1 = self.datePicker1.date().toString('yyyy-MM-dd')
        date2 = self.datePicker2.date().toString('yyyy-MM-dd')
        date3 = self.datePicker1.date().toPyDate()
        date4 = self.datePicker2.date().toPyDate()
        # print (date1)
        dates = self.date(date3, date4)

        x = dates

        y = []
        y1 = []

        if len(x) > 31:
            a = int(len(x) / 30.25)
            x = x[::a]

        for i in range(len(x) - 1):
            date1 = x[i]
            date2 = x[i + 1]
            select = "select sum(goods), sum(earning) from invoices where date >= '" + date1 + "' and date < '" + date2 + "'"
            result = dbutil.select(select)
            y.append(result[0][0])
            y1.append(result[0][1])
            if not y[i]:
                y[i] = 0
            if not y1[i]:
                y1[i] = 0

        x = x[:-1]

        # plt.plot(np.arange(0,5, 0.2))

        fig, ax = plt.subplots()

        # ax.set_xticks(dates)
        # fig.gca()
        # plt.plot_date(x, y)

        # plt.subplot(1,3,1)
        ax.plot(x, y, 'o--')
        # plt.plot_date(x,y1)
        # plt.subplot(1,3,2)
        ax.plot(x, y1, 'r--o')

        # ax.grid()
        # plt.fill(dates, y)
        # ax.grid()
        # Устанавливаем интервал основных и
        # вспомогательных делений:
        # ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
        # ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))
        # ax.yaxis.set_major_locator(ticker.MultipleLocator(50))
        # ax.yaxis.set_minor_locator(ticker.MultipleLocator(10))

        # Настраиваем вид основных тиков:
        ax.tick_params(axis='both', # Применяем параметры к обеим осям
                       which='major', # Применяем параметры к основным делениям
                       direction='inout', # Рисуем деления внутри и снаружи графика
                       length=10, # Длинна делений
                       width=2, # Ширина делений
                       color='m', # Цвет делений
                       pad=10, # Расстояние между черточкой и ее подписью
                       labelsize=10, # Размер подписи
                       labelcolor='r', # Цвет подписи
                       # bottom=True, # Рисуем метки снизу
                       # top=True, # сверху
                       # left=True, # слева
                       # right=True, # и справа
                       # labelbottom=True, # Рисуем подписи снизу
                       # labeltop=True, # сверху
                       # labelleft=True, # слева
                       # labelright=True, # и справа
                       labelrotation=90) # Поворот подписей

                        # Настраиваем вид вспомогательных тиков:
                        # ax.tick_params(axis='both', # Применяем параметры к обеим осям
                        # which='minor', # Применяем параметры к вспомогательным делениям
                        # direction='out', # Рисуем деления внутри и снаружи графика
                        # length=10, # Длинна делений
                        # width=2, # Ширина делений
                        # color='m', # Цвет делений
                        # pad=10, # Расстояние между черточкой и ее подписью
                        # labelsize=15, # Размер подписи
                        # labelcolor='r', # Цвет подписи
                        # bottom=True, # Рисуем метки снизу
                        # top=True, # сверху
                        # left=True, # слева
                        # right=True) # и справа
                        #
                        #

                        # Добавляем линии основной сетки:
                        # ax.grid(which='major',
                        # color='m')

                        # Включаем видимость вспомогательных делений:
                        # ax.minorticks_on()

                        # Теперь можем отдельно задавать внешний вид
                        # вспомогательной сетки:
                        # ax.grid(which='minor',
                        # color='m',
                        # linestyle=':')

                        # fig.set_figwidth(12)
                        # fig.set_figheight(8)
                        # ax.grid()

        canvas = FigureCanvas(fig)
        proxy_widget = QtWidgets.QGraphicsProxyWidget()
        proxy_widget.setWidget(canvas)
        scene.addItem(proxy_widget)
        # plt.xlim([0, 25])
        # self.View.resize(650, 500)
        self.View.show()

    def goBackToInvoices(self):
        widget.setCurrentIndex(0)


class Reports(QDialog):
    def __init__(self):
        super(Reports, self).__init__()
        loadUi("uis/reports/Reports.ui", self)
        self.goBackToInvoicesButton.clicked.connect(self.goBackToInvoices)
        self.showReportsButton.clicked.connect(self.showReports)

        self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)

        second_date = date.today()
        first_date = date.today() - timedelta(days=30)
        self.datePicker1.setDate(first_date)
        self.datePicker2.setDate(second_date)

        self.showReports()

    def showReports(self):
        date1 = self.datePicker1.date().toString('yyyy-MM-dd')
        date2 = self.datePicker2.date().toString('yyyy-MM-dd')

        select = "select sum(count), sum(total_price) from goods inner join invoices on goods.invoice = invoices.id where date between '" + date1 + "' and '" + date2 + "'"
        result = dbutil.select(select)

        self.goodsLabel.setText(str(result[0][0]))
        self.sumLabel.setText(str(result[0][1]))

        select = "select width, height, sum(count), sum(total_price) from goods inner join invoices on goods.invoice = invoices.id where date between '" + date1 + "' and '" + date2 + "'group by width, height"
        result = dbutil.select(select)

        self.tableWidget.setRowCount(len(result))

        for i in range(len(result)):
            for j in range(4):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(result[i][j])))

    def goBackToInvoices(self):
        widget.setCurrentIndex(0)


class DBUtil():
    def __init__(self):
        self.connection = sqlite3.connect('db/Accounting.db')
        self.cursor = self.connection.cursor()
        self.select("UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='goods';")
        self.select("UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='invoices';")

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

# widget.setFixedWidth(960)
# widget.setFixedHeight(560)
widget.resize(960, 560)
widget.show()

sys.exit(app.exec())
dbutil.connection.close()
