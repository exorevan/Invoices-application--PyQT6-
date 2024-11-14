import sqlite3
import sys
from datetime import date, timedelta, datetime
from math import ceil

import matplotlib.pyplot as plt
import numpy as np
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QIcon
from PyQt6.QtWidgets import *
from core.lib.utils.overwrites import loadUi_
from dateutil import relativedelta
from dateutil.relativedelta import relativedelta
from matplotlib import ticker
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class Invoices(QDialog):
    def __init__(self):
        super(Invoices, self).__init__()
        loadUi_("uis/invoices/Invoices.ui", self)
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
        invoice.setNewInvoice()
        widget.setCurrentIndex(1)

    def showInvocies(self):
        date1 = self.datePicker1.date().toString("yyyy-MM-dd")
        date2 = self.datePicker2.date().toString("yyyy-MM-dd")

        select = (
            "select id, date, invoice_name as 'Invoice Name', goods, earning from invoices where date between '"
            + date1
            + "' and '"
            + date2
            + "'"
        )
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
        loadUi_("uis/invoice/Invoice.ui", self)

        self.goBackToInvoicesButton.clicked.connect(self.goBackToInvoices)
        self.addRowButton.clicked.connect(self.addRow)
        self.deleteRowButton.clicked.connect(self.deleteRow)
        self.calculateButton.clicked.connect(self.calculate)
        self.saveButton.clicked.connect(self.save)
        self.deleteButton.clicked.connect(self.delete)

        self.tableWidget.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch
        )
        self.tableWidget.selectionModel().selectionChanged.connect(
            self.disableSelection
        )
        self.tableWidget.setColumnHidden(0, 1)
        self.tableWidget.setSortingEnabled(True)

        self.messageBox = QMessageBox(self)
        self.messageBox.setWindowIcon(QIcon("uis/invoice/dokkaebi.png"))
        self.messageBox.setWindowTitle("Fill error")

    def goBackToInvoices(self):
        invoices.showInvocies()
        widget.setCurrentIndex(0)

    def setNewInvoice(self):
        self.newRows = 0
        self.deleted = False

        select = "select max(id) from goods"
        result = dbutil.select(select)

        if result[0][0]:
            newMaxId = int(result[0][0])
        else:
            newMaxId = 0

        self.maxGoodsId = newMaxId

        select = "select max(id) from invoices"
        result = dbutil.select(select)

        if result[0][0]:
            newId = int(result[0][0])
        else:
            newId = 0

        self.currentId = newId + 1

        self.textbox.setText(str(datetime.now()))
        self.dateEdit.setDate(date.today())
        self.date.setText(
            str(datetime.strptime(str(date.today()), "%Y-%m-%d").strftime("%d.%m.%Y"))
        )
        self.tableWidget.setRowCount(0)

        self.uniqueGoods.setText("0")
        self.goods.setText("0")
        self.sum.setText("0")

    def changeInfo(self, index):
        self.newRows = 0
        self.currentId = index
        self.deleted = False

        select = "select max(id) from goods"
        result = dbutil.select(select)
        self.maxGoodsId = result[0][0]

        if not self.maxGoodsId:
            self.maxGoodsId = 0

        select = (
            "select id, invoice_name, date, goods, goods_unique, earning from invoices where id = "
            + index
        )
        result = dbutil.select(select)

        self.textbox.setText(str(result[0][1]))
        self.dateEdit.setDate(datetime.strptime(result[0][2], "%Y-%m-%d"))
        self.date.setText(
            str(datetime.strptime(result[0][2], "%Y-%m-%d").strftime("%d.%m.%Y"))
        )
        self.uniqueGoods.setText(str(result[0][4]) + " positions")
        self.goods.setText(str(result[0][3]))
        self.sum.setText(str(result[0][5]))

        select = (
            "select id, width, height, count, price, total_price from goods where invoice = "
            + index
        )
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
            width = self.tableWidget.item(i, 1)
            height = self.tableWidget.item(i, 2)
            count = self.tableWidget.item(i, 3)
            price = self.tableWidget.item(i, 4)

            if self.upgradedCheck(width, height, count, price):
                for j in range(1, self.tableWidget.columnCount() - 1):
                    self.tableWidget.item(i, j).setBackground(QColor(255, 255, 255))

                count = int(count.text())
                price = float(price.text())

                self.tableWidget.setItem(i, 5, QTableWidgetItem(str(count * price)))

                sum += count * price
                goods += count
                notNullRows += 1
            else:
                for j in range(1, self.tableWidget.columnCount() - 1):
                    if self.tableWidget.item(i, j):
                        self.tableWidget.item(i, j).setBackground(QColor(255, 92, 92))

                self.messageBox.setFont(QFont("Dubai Light", 13))

                self.messageOnCond(
                    0,
                    "Error, you must fill ",
                    " in the row ",
                    " in the row ",
                    width,
                    height,
                    count,
                    price,
                    str(i + 1),
                )

                self.messageBox.exec()

            self.uniqueGoods.setText(str(notNullRows) + " positions")
            self.goods.setText(str(goods))
            self.sum.setText(str(sum))

    def disableSelection(self, selected):
        for i in selected.indexes():
            if self.tableWidget.item(i.row(), i.column()):
                self.tableWidget.item(i.row(), i.column()).setSelected(False)

    def numberCheck(self, number):
        try:
            float(number)
            return True
        except ValueError:
            return False

    def upgradedCheck(self, width, height, count, price):

        widthCon, heightCon, countCon, priceCon = self.firstSubCheck(
            width, height, count, price
        )

        if widthCon and heightCon and countCon and priceCon:
            widthCon, heightCon, countCon, priceCon = self.secondSubCheck(
                width, height, count, price
            )

            if widthCon and heightCon and countCon and priceCon:
                return True

        return False

    def firstSubCheck(self, width, height, count, price):
        return (
            width is not None,
            height is not None,
            count is not None,
            price is not None,
        )

    def secondSubCheck(self, width, height, count, price):
        return (
            self.numberCheck(width.text()),
            self.numberCheck(height.text()),
            count.text().isdigit(),
            self.numberCheck(price.text()),
        )

    def messageOnCond(
        self,
        check,
        messageStart,
        messageEnd,
        messageEndAlt,
        width,
        height,
        count,
        price,
        row,
    ):
        if not check:
            widthCon, heightCon, countCon, priceCon = self.firstSubCheck(
                width, height, count, price
            )

            if widthCon and heightCon and countCon and priceCon:
                self.messageOnCond(
                    1,
                    "Error, ",
                    " must be a float number (1.1, 3, 5.99...) in the row ",
                    " must be an integer number (1, 2, 3..) in the row ",
                    width,
                    height,
                    count,
                    price,
                    row,
                )
                return True
        else:
            widthCon, heightCon, countCon, priceCon = self.secondSubCheck(
                width, height, count, price
            )

        if not widthCon:
            self.messageBox.setText(messageStart + "width" + messageEnd + row)
        elif not heightCon:
            self.messageBox.setText(messageStart + "height" + messageEnd + row)
        elif not countCon:
            self.messageBox.setText(messageStart + "count" + messageEndAlt + row)
        elif not priceCon:
            self.messageBox.setText(messageStart + "price" + messageEnd + row)

    def save(self):
        if (
            self.textbox.toPlainText() != ""
            and self.goods.text() != ""
            and self.uniqueGoods.text() != ""
            and self.sum.text() != ""
        ):
            select = "select max(id) from invoices"
            result = dbutil.select(select)

            if result[0][0]:
                maxInv = int(result[0][0])
            else:
                maxInv = 0

            if int(self.currentId) > int(maxInv) or self.deleted:
                select = (
                    "insert into invoices (id, invoice_name, date, goods, goods_unique, earning) values ("
                    + str(self.currentId)
                    + ", '', '2000-01-01', 0, 0, 0)"
                )
                result = dbutil.select(select)

            self.calculate()

            select = (
                "update invoices set invoice_name = '"
                + self.textbox.toPlainText()
                + "', date = '"
                + self.dateEdit.date().toString("yyyy-MM-dd")
                + "', goods = "
                + self.goods.text()
                + ", goods_unique = "
                + self.uniqueGoods.text().replace(" positions", "")
                + ", earning = "
                + self.sum.text()
                + " where id = "
                + str(self.currentId)
            )
            result = dbutil.select(select)

            ids = []

            for i in range(self.tableWidget.rowCount()):
                if self.upgradedCheck(
                    self.tableWidget.item(i, 1),
                    self.tableWidget.item(i, 2),
                    self.tableWidget.item(i, 3),
                    self.tableWidget.item(i, 4),
                ):
                    ids.append(int(self.tableWidget.item(i, 0).text()))

                    if int(self.tableWidget.item(i, 0).text()) > self.maxGoodsId:
                        select = (
                            "insert into goods (invoice, width, height, count, price, total_price) values ("
                            + str(self.currentId)
                            + ", "
                            + self.tableWidget.item(i, 1).text()
                            + ", "
                            + self.tableWidget.item(i, 2).text()
                            + ", "
                            + self.tableWidget.item(i, 3).text()
                            + ", "
                            + self.tableWidget.item(i, 4).text()
                            + ", "
                            + self.tableWidget.item(i, 5).text()
                            + ")"
                        )
                        result = dbutil.select(select)
                    else:
                        select = (
                            "update goods set width = "
                            + self.tableWidget.item(i, 1).text()
                            + ", height = "
                            + self.tableWidget.item(i, 2).text()
                            + ", count = "
                            + self.tableWidget.item(i, 3).text()
                            + ", price = "
                            + self.tableWidget.item(i, 4).text()
                            + ", total_price = "
                            + self.tableWidget.item(i, 5).text()
                            + " where id = "
                            + self.tableWidget.item(i, 0).text()
                        )
                        result = dbutil.select(select)

            select = "select id from goods where invoice = " + str(self.currentId)
            result = dbutil.select(select)

            array = [a[0] for a in result]
            toDelete = set(array) - set(ids)

            for id in toDelete:
                select = "delete from goods where id = " + str(id)
                result = dbutil.select(select)

        select = "select max(id) from goods"
        result = dbutil.select(select)

        if result[0][0]:
            newMaxId = int(result[0][0])
        else:
            newMaxId = 0

        self.maxGoodsId = newMaxId

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
    plot_type = 0
    isBlocked = True

    def __init__(self):
        super(Plots, self).__init__()
        loadUi_("uis/plots/Plots.ui", self)

        self.timer_id = 0
        self.current_width = self.size().width()
        self.current_height = self.size().height()

        self.radio_Auto.toggle()
        self.goBackToInvoicesButton.clicked.connect(self.goBackToInvoices)
        self.showPlotButton.clicked.connect(self.show_func_pie)
        self.goods_Button.clicked.connect(self.show_func_goods)
        self.earnings_Button.clicked.connect(self.show_func_earnings)
        self.bar_Button.clicked.connect(self.show_func_bar)
        self.pie_Button.clicked.connect(self.show_func_pie)

        self.datePicker1.setDate(date.today() - timedelta(days=30))
        self.datePicker2.setDate(date.today())

        self.messageBox = QMessageBox(self)
        self.messageBox.setWindowIcon(QIcon("uis/invoice/dokkaebi.png"))
        self.messageBox.setWindowTitle("Plot error")

        self.scroll = QScrollArea()

        self.fig, self.ax = plt.subplots()
        _, _ = self.startPlot(0)

    def datesBetween(self, sdate, edate):
        dates = []
        delta = edate - sdate  # as timedelta

        for i in range(delta.days + 1):
            day = sdate + timedelta(days=i)
            dates.append(self.toString(day))

        return dates

    def toDate(self, date):
        return datetime.strptime(date, "%Y-%m-%d")

    def toString(self, date):
        return date.strftime("%Y-%m-%d")

    def radio_buttons(self, x):
        if self.radio_Auto.isChecked():
            if self.plot_type == 4:
                mas = x

                if len(x) > 12:
                    d = ceil(len(x) / 12)
                    mas = x[::d]

                return mas
            else:
                mas = x

                if len(x) > 31:  # для двух
                    a = int(len(x) / 30)
                    mas = x[::a]

                    mas[-1] = mas[-1][13:] + x[-1][:]

                return mas

        elif self.radio_Years.isChecked():
            date1 = self.toString(self.datePicker1.date().toPyDate())
            date2 = self.toString(self.datePicker2.date().toPyDate())
            d = int(date2[:4]) - int(date1[:4])

            year1 = int(date1[:4])

            mas = [x[0]]

            if d > 0:
                mas.append(str(year1 + 1) + "-01-01")

            if d >= 2:
                for i in range(2, d + 1):
                    mas.append(str(year1 + i) + "-01-01")

            if x[-1] not in mas:
                mas.append(x[-1])

            return mas

        elif self.radio_Months.isChecked():
            mas = [x[0]]

            firstDate = self.toDate(x[0]) + relativedelta(months=1)
            firstDateNewMonth = self.toString(firstDate)[:7] + "-01"

            currentDate = self.toDate(firstDateNewMonth)

            while True:
                if currentDate > (self.toDate(x[-1]) - relativedelta(days=1)):
                    break

                mas.append(self.toString(currentDate))
                currentDate += relativedelta(months=1)

            mas.append(x[-1])

            print(mas)
            return mas
        elif self.radio_Weeks.isChecked():
            if self.toDate(x[0]) + relativedelta(days=1) > self.toDate(x[-1]):
                return []
            elif self.toDate(x[0]) + relativedelta(days=1) == self.toDate(x[-1]):
                return [x[0], self.toString(self.toDate(x[0]) + relativedelta(days=1))]

            firstMonday = self.toDate(x[0]) + timedelta(
                days=-self.toDate(x[0]).weekday(), weeks=1
            )

            if firstMonday > self.toDate(x[-1]):
                return [x[0], self.toString(self.toDate(x[-1]))]

            firstMonday = self.toString(firstMonday)

            xDates = [x[0]]
            xDates.extend(x[x.index(firstMonday) : -1 : 7])
            xDates.append(x[-1])

            return xDates

    def startPlot(self, index):
        self.plot_type = index

        if index:
            self.View.deleteLater()

        self.fig, self.ax = plt.subplots()

        self.scene = QtWidgets.QGraphicsScene()
        self.View = QtWidgets.QGraphicsView(self.scene, self.graphicsView)

        self.View.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.View.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        date1 = self.datePicker1.date().toPyDate()
        date2 = self.datePicker2.date().toPyDate() + timedelta(days=1)

        if date1 >= date2:
            return [], []

        return self.radio_buttons(self.datesBetween(date1, date2)), []

    def show_func_goods(self):
        x, y = self.startPlot(1)

        self.show_func_plot(x, y, "goods")

    def show_func_earnings(self):
        x, y = self.startPlot(2)

        self.show_func_plot(x, y, "earning")

    def show_func_plot(self, x, y, subject):
        for i in range(len(x) - 1):
            select = (
                "select sum("
                + subject
                + ") from invoices where date >= '"
                + x[i]
                + "' and date < '"
                + x[i + 1]
                + "'"
            )
            result = dbutil.select(select)

            y.append(result[0][0])

            if not y[i]:
                y[i] = 0

        if len(x) == 0:
            plt.close(self.fig)
            return 0

        xDates = [
            x[0] + " - " + self.toString(self.toDate(x[1]) - relativedelta(days=1))
        ]
        xYears = [x[0][:4]]
        xYearsCount = [0]
        xtickstop = [xDates[-1][5:10] + " - " + xDates[-1][18:]]

        if self.radio_Years.isChecked():
            for i in range(1, len(x)):
                if x[i][:4] not in xYears:
                    xYears.append(x[i][:4])
                    xYearsCount.append(i)

            x = xYears
        elif self.radio_Months.isChecked():
            for i in range(1, len(x)):
                if x[i][:4] not in xYears:
                    xYears.append(x[i][:4])
                    xYearsCount.append(i)

            xtickstop = []
            for i in range(len(x) - 1):
                xtickstop.append(self.toDate(x[i]).strftime("%B"))

            x = x[:-1]
        else:
            for i in range(1, len(x) - 1):
                xDates.append(
                    x[i]
                    + " - "
                    + self.toString(self.toDate(x[i + 1]) - relativedelta(days=1))
                )

                xtickstop.append(xDates[-1][5:10] + " - " + xDates[-1][18:])

                if xDates[i][13:17] not in xYears:
                    xYears.append(xDates[i][13:17])
                    xYearsCount.append(i)

            if xDates[-1][13:17] not in xYears:
                xYears.append(xDates[-1][13:17])
                xYearsCount.append(len(x))

            x = xDates

        if self.radio_Auto.isChecked():
            border = 62
        else:
            border = 30

        if len(x) > border:
            self.messageBox.setFont(QFont("Dubai Light", 13))
            self.messageBox.setText("Too many dates input")
            self.messageBox.exec()

            self.isBlocked = True

            return True

        self.isBlocked = False

        self.instantResize()

        # self.ax.plot(x, y, 'o', color='black', markersize=3)
        self.ax.plot(
            x,
            y,
            color="#6ad487",
            marker=".",
            markerfacecolor="black",
            markeredgecolor="black",
            markeredgewidth=0.5,
            markersize=self.width() / 220,
            rasterized=True,
        )
        # self.ax.plot(x, y, color='#6ad487')

        if not self.radio_Years.isChecked():
            self.ax.set_xticks(x, labels=xtickstop)

            self.ax_t = self.ax.secondary_xaxis("top")
            self.ax_t.minorticks_on()
            self.ax_t.xaxis.set_minor_locator(ticker.NullLocator())
            self.ax_t.set_xticks(xYearsCount, labels=xYears)

            self.ax_t.tick_params(axis="x", direction="inout")

            self.ax_t.tick_params(
                axis="both",
                which="major",
                direction="inout",
                length=10,
                width=1,
                color="black",
                pad=10,
                labelsize=10,
                labelcolor="black",
                labelrotation=45,
            )

        self.endPlot()

    def show_func_bar(self):
        _, _ = self.startPlot(3)

        select = (
            """select goods.width, goods.height, goods.total_price from goods inner join invoices on invoices.id 
                 = goods.invoice where date >= '"""
            + self.toString(self.datePicker1.date().toPyDate())
            + "' and date < '"
            + self.toString(self.datePicker2.date().toPyDate() + relativedelta(days=1))
            + "'"
        )

        result = dbutil.select(select)

        mul = []
        for i in result:
            mul.append([i[0] * i[1], i[2]])

        if len(mul) == 0:
            plt.close(self.fig)

            self.messageBox.setFont(QFont("Dubai Light", 13))
            self.messageBox.setText(
                f"There's no goods in this period ({self.datePicker1.date().toPyDate()} - {self.datePicker2.date().toPyDate()})"
            )
            self.messageBox.exec()

            self.isBlocked = True

            return True

        mul.sort()

        if len(mul) < 1:
            return True

        b = [mul[0]]

        for i in range(1, len(mul)):
            if mul[i][0] in list(np.array(b)[:, 0]):
                b[-1][1] += mul[i][1]
            else:
                b.append([mul[i][0], mul[i][1]])

        self.instantResize()

        self.ax.bar(list(range(len(b))), np.array(b)[:, 1], zorder=3)
        plt.xticks(list(range(len(b))), labels=np.array(b)[:, 0])

        self.endPlot()

    def show_func_pie(self):
        x, y = self.startPlot(4)

        if len(x) == 0:
            plt.close(self.fig)
            return 0

        for i in range(len(x) - 1):
            select = (
                "select sum(earning) from invoices where date >= '"
                + x[i]
                + "' and date < '"
                + x[i + 1]
                + "'"
            )
            result = dbutil.select(select)
            y.append(result[0][0])

            if not y[i]:
                y[i] = 0

        self.instantResize()

        if sum(y) < 1:
            self.messageBox.setFont(QFont("Dubai Light", 13))
            self.messageBox.setText(
                f"There's no goods in this period ({self.datePicker1.date().toPyDate()} - {self.datePicker2.date().toPyDate()})"
            )
            self.messageBox.exec()

            self.isBlocked = True

            return True

        if len(x) > 15:
            self.messageBox.setFont(QFont("Dubai Light", 13))
            self.messageBox.setText("Too many dates input")
            self.messageBox.exec()

            self.isBlocked = True

            return True

        self.isBlocked = False

        self.ax.pie(
            y,
            shadow=False,
            wedgeprops={"linewidth": 3},
            colors=[
                "#6cc399",
                "#ffc658",
                "#ab55a0",
                "#46bcd6",
                "#fcda54",
                "#cf4f9a",
                "#44a3d3",
                "#fee854",
                "#e94f81",
                "#458bc9",
                "#f8ee5b",
                "#f05759",
                "#4b6db4",
                "#d2de54",
                "#f37658",
            ],
        )
        #
        xYearsCount = [0]
        xYears = [x[0][:4]]
        xtickstop = []
        xDates = [
            x[0] + " - " + self.toString(self.toDate(x[1]) - relativedelta(days=1))
        ]

        if self.radio_Months.isChecked():
            for i in range(1, len(x)):
                if x[i][:4] not in xYears:
                    xYears.append(x[i][:4])
                    xYearsCount.append(i)

            xtickstop = []
            for i in range(len(x) - 1):
                xtickstop.append(self.toDate(x[i]).strftime("%B"))

            if self.toDate(x[-2]).strftime("%B") != self.toDate(x[-1]).strftime("%B"):
                xtickstop.append(self.toDate(x[-1]).strftime("%B"))

            for i in range(len(xYearsCount)):
                xtickstop[xYearsCount[i]] = str(
                    xYears[i] + ": " + xtickstop[xYearsCount[i]]
                )
        elif self.radio_Years.isChecked():
            for i in range(1, len(x)):
                if x[i][:4] not in xYears:
                    xYears.append(x[i][:4])
                    xYearsCount.append(i)
            xtickstop = xYears
        else:
            for i in range(1, len(x) - 1):
                xDates.append(
                    x[i]
                    + " - "
                    + self.toString(self.toDate(x[i + 1]) - relativedelta(days=1))
                )

                xtickstop.append(xDates[-1][5:10] + " - " + xDates[-1][18:])

                if xDates[i][13:17] not in xYears:
                    xYears.append(xDates[i][13:17])
                    xYearsCount.append(i)

            if xDates[-1][13:17] not in xYears:
                xYears.append(xDates[-1][13:17])
                xYearsCount.append(len(x))

            xDatesc = []
            for i in xDates:
                xDatesc.append(i[5:10] + " - " + i[18:23])

            xDatesc[0] = xDates[0][:4] + ": " + xDatesc[0]

            for i in range(1, len(xYearsCount) - 1):
                xDatesc[xYearsCount[i] + 1] = str(
                    xYears[i] + ": " + xDatesc[xYearsCount[i] + 1]
                )

            if len(xDatesc) > 1:
                if xYearsCount[-1] == len(xDatesc) - 1:
                    xDatesc[xYearsCount[-1]] = str(
                        xYears[-1] + ": " + xDatesc[xYearsCount[-1]]
                    )
                elif len(xYearsCount) > 1:
                    xDatesc[xYearsCount[-1] + 1] = str(
                        xYears[-1] + ": " + xDatesc[xYearsCount[-1] + 1]
                    )

            xtickstop = xDatesc

        self.ax.legend(
            xtickstop, loc="center left", bbox_to_anchor=(1, 0.5), frameon=False
        )

        self.endPlot()

    def endPlot(self):
        self.ax.grid(c="#dadada", which="major")
        self.ax.grid(
            c="#f0f0f0", which="minor", axis="y", linestyle="--", linewidth=1, zorder=0
        )

        self.ax.tick_params(
            axis="x",
            which="major",
            direction="inout",
            length=5,
            width=1,
            color="black",
            pad=5,
            labelsize=9,
            labelcolor="black",
            labelrotation=80,
        )

        self.ax.tick_params(
            axis="y",
            which="major",
            direction="inout",
            length=5,
            width=1,
            color="black",
            pad=5,
            labelsize=10,
            labelcolor="black",
            labelrotation=0,
        )

        self.ax.minorticks_on()
        self.ax.xaxis.set_minor_locator(ticker.NullLocator())

        canvas = FigureCanvas(self.fig)
        proxy_widget = QtWidgets.QGraphicsProxyWidget()
        proxy_widget.setWidget(canvas)
        self.scene.addItem(proxy_widget)

        if self.plot_type != 4:
            self.View.resize(ceil(self.width() - 200), ceil(self.height()) - 25)
        else:
            self.View.resize(ceil((self.width() - 200)), ceil(self.height()) - 25)

        self.fig.tight_layout()
        self.View.show()
        plt.close(self.fig)

    def resizeEvent(self, event):
        self.killTimer(self.timer_id)

        width_dif = self.size().width() / self.current_width
        height_dif = self.size().height() / self.current_height

        if width_dif + height_dif != 2:
            self.current_width *= width_dif
            self.current_height *= height_dif

            if self.plot_type != 4:
                self.View.resize(
                    ceil(self.current_width - 200), ceil(self.current_height) - 25
                )
            else:
                self.View.resize(
                    ceil((self.current_width - 200)), ceil(self.current_height) - 25
                )

            self.View.scale(1 + 1 * (width_dif - 1), 1 + 1 * (height_dif - 1))

            self.timer_id = self.startTimer(300)

    def timerEvent(self, event):
        self.plotResize()
        # print("resize")
        self.killTimer(self.timer_id)

    def plotResize(self):
        if not self.isBlocked:
            if self.plot_type == 1:
                self.show_func_goods()
            elif self.plot_type == 2:
                self.show_func_earnings()
            elif self.plot_type == 3:
                self.show_func_bar()
            elif self.plot_type == 4:
                self.show_func_pie()

    def instantResize(self):
        if self.plot_type != 4:
            self.fig.set_figwidth((self.width() - 270) / self.fig.dpi)

            self.fig.set_figheight((self.height() - 25) / self.fig.dpi)
        else:
            self.fig.set_figwidth(
                int((self.width() - 270 / 960 * self.width()) / self.fig.dpi) + 0.5
            )

            self.fig.set_figheight((self.height()) / self.fig.dpi)

    def goBackToInvoices(self):
        widget.setCurrentIndex(0)


class Reports(QDialog):
    def __init__(self):
        super(Reports, self).__init__()
        loadUi_("uis/reports/Reports.ui", self)
        self.goBackToInvoicesButton.clicked.connect(self.goBackToInvoices)
        self.showReportsButton.clicked.connect(self.showReports)

        self.tableWidget.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch
        )
        self.tableWidget.setSortingEnabled(True)

        second_date = date.today()
        first_date = date.today() - timedelta(days=30)
        self.datePicker1.setDate(first_date)
        self.datePicker2.setDate(second_date)

        self.showReports()

    def showReports(self):
        date1 = self.datePicker1.date().toString("yyyy-MM-dd")
        date2 = self.datePicker2.date().toString("yyyy-MM-dd")

        select = (
            "select sum(count), sum(total_price) from goods inner join invoices on goods.invoice = invoices.id where date between '"
            + date1
            + "' and '"
            + date2
            + "'"
        )
        result = dbutil.select(select)

        self.goodsLabel.setText(str(result[0][0]))
        self.sumLabel.setText(str(result[0][1]))

        select = (
            "select width, height, sum(count), sum(total_price) from goods inner join invoices on goods.invoice = invoices.id where date between '"
            + date1
            + "' and '"
            + date2
            + "'group by width, height"
        )
        result = dbutil.select(select)

        self.tableWidget.setRowCount(len(result))

        for i in range(len(result)):
            for j in range(4):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(result[i][j])))

    def goBackToInvoices(self):
        widget.setCurrentIndex(0)


class DBUtil:
    def __init__(self):
        self.connection = sqlite3.connect("db/Accounting.db")
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

widget.resize(960, 620)
widget.setWindowTitle("Invoices")
widget.setWindowIcon(QIcon("melusi.png"))
widget.show()

sys.exit(app.exec())
dbutil.connection.close()
