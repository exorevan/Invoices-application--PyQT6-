from datetime import date, datetime

from PyQt6 import QtWidgets
from PyQt6.QtGui import QFont, QColor, QIcon
from PyQt6.QtWidgets import QDialog, QTableWidgetItem, QMessageBox
from PyQt6.uic import loadUi


class InvoicePage(QDialog):
    currentId = 0
    newRows = 0
    maxGoodsId = 0
    deleted = False

    def __init__(self, widget, dbutil):
        super(InvoicePage, self).__init__()
        loadUi("uis/invoice/Invoice.ui", self)

        self.widget = widget
        self.dbutil = dbutil

        self.goBackToInvoicesButton.clicked.connect(self.goBackToInvoices)
        self.addRowButton.clicked.connect(self.addRow)
        self.deleteRowButton.clicked.connect(self.deleteRow)
        self.calculateButton.clicked.connect(self.calculate)
        self.saveButton.clicked.connect(self.save)
        self.deleteButton.clicked.connect(self.delete)

        self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tableWidget.selectionModel().selectionChanged.connect(self.disableSelection)
        self.tableWidget.setColumnHidden(0, 1)
        self.tableWidget.setSortingEnabled(True)

        self.messageBox = QMessageBox(self)
        self.messageBox.setWindowIcon(QIcon('uis/invoice/dokkaebi.png'))
        self.messageBox.setWindowTitle('Fill error')

    def goBackToInvoices(self):
        #invoices.showInvocies()
        self.widget.setCurrentIndex(0)

    def setNewInvoice(self):
        self.newRows = 0
        self.deleted = False

        select = "select max(id) from goods"
        result = self.dbutil.select(select)

        if result[0][0]:
            newMaxId = int(result[0][0])
        else:
            newMaxId = 0

        self.maxGoodsId = newMaxId

        select = "select max(id) from invoices"
        result = self.dbutil.select(select)

        if result[0][0]:
            newId = int(result[0][0])
        else:
            newId = 0

        self.currentId = newId + 1

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
        result = self.dbutil.select(select)
        self.maxGoodsId = result[0][0]

        if not self.maxGoodsId:
            self.maxGoodsId = 0

        select = "select id, invoice_name, date, goods, goods_unique, earning from invoices where id = " + index
        result = self.dbutil.select(select)

        self.textbox.setText(str(result[0][1]))
        self.dateEdit.setDate(datetime.strptime(result[0][2], '%Y-%m-%d'))
        self.date.setText(str(datetime.strptime(result[0][2], '%Y-%m-%d').strftime('%d.%m.%Y')))
        self.uniqueGoods.setText(str(result[0][4]) + " positions")
        self.goods.setText(str(result[0][3]))
        self.sum.setText(str(result[0][5]))

        select = "select id, width, height, count, price, total_price from goods where invoice = " + index
        result = self.dbutil.select(select)

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

                self.messageBox.setFont(QFont('Dubai Light', 13))

                self.messageOnCond(0, "Error, you must fill ", " in the row ", ' in the row ', width, height, count,
                                   price, str(i + 1))

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

        widthCon, heightCon, countCon, priceCon = self.firstSubCheck(width, height, count, price)

        if widthCon and heightCon and countCon and priceCon:
            widthCon, heightCon, countCon, priceCon = self.secondSubCheck(width, height, count, price)

            if widthCon and heightCon and countCon and priceCon:
                return True

        return False

    def firstSubCheck(self, width, height, count, price):
        return width is not None, height is not None, count is not None, price is not None

    def secondSubCheck(self, width, height, count, price):
        return self.numberCheck(width.text()), self.numberCheck(height.text()), count.text().isdigit(), \
               self.numberCheck(price.text())

    def messageOnCond(self, check, messageStart, messageEnd, messageEndAlt, width, height, count, price, row):
        if not check:
            widthCon, heightCon, countCon, priceCon = self.firstSubCheck(width, height, count, price)

            if widthCon and heightCon and countCon and priceCon:
                self.messageOnCond(1, "Error, ", " must be a float number (1.1, 3, 5.99...) in the row ",
                                   " must be an integer number (1, 2, 3..) in the row ", width, height, count, price,
                                   row)
                return True
        else:
            widthCon, heightCon, countCon, priceCon = self.secondSubCheck(width, height, count, price)

        if not widthCon:
            self.messageBox.setText(messageStart + "width" + messageEnd + row)
        elif not heightCon:
            self.messageBox.setText(messageStart + "height" + messageEnd + row)
        elif not countCon:
            self.messageBox.setText(messageStart + "count" + messageEndAlt + row)
        elif not priceCon:
            self.messageBox.setText(messageStart + "price" + messageEnd + row)

    def save(self):
        if self.textbox.toPlainText() != "" and self.goods.text() != '' and self.uniqueGoods.text() != '' and self.sum.text() != '':
            select = "select max(id) from invoices"
            result = self.dbutil.select(select)

            if result[0][0]:
                maxInv = int(result[0][0])
            else:
                maxInv = 0

            if int(self.currentId) > int(maxInv) or self.deleted:
                select = "insert into invoices (id, invoice_name, date, goods, goods_unique, earning) values (" + str(
                    self.currentId) + ", '', '2000-01-01', 0, 0, 0)"
                result = self.dbutil.select(select)

            self.calculate()

            select = f"update invoices set invoice_name = '{self.textbox.toPlainText()}', date = '{self.dateEdit.date().toString('yyyy-MM-dd')}', goods = {self.goods.text()}, goods_unique = {self.uniqueGoods.text().replace(' positions', '')}, earning = {self.sum.text()} where id = {self.currentId}"
            result = self.dbutil.select(select)

            ids = []

            for i in range(self.tableWidget.rowCount()):
                if self.upgradedCheck(self.tableWidget.item(i, 1), self.tableWidget.item(i, 2),
                                      self.tableWidget.item(i, 3),
                                      self.tableWidget.item(i, 4)):
                    ids.append(int(self.tableWidget.item(i, 0).text()))

                    if int(self.tableWidget.item(i, 0).text()) > self.maxGoodsId:
                        select = f"insert into goods (invoice, width, height, count, price, total_price) values ({self.currentId}, {self.tableWidget.item(i, 1).text()}, {self.tableWidget.item(i, 2).text()}, {self.tableWidget.item(i, 3).text()}, {self.tableWidget.item(i, 4).text()}, {self.tableWidget.item(i, 5).text()})"
                        result = self.dbutil.select(select)
                    else:
                        select = f"update goods set width = {self.tableWidget.item(i, 1).text()}, height = {self.tableWidget.item(i, 2).text()}, count = {self.tableWidget.item(i, 3).text()}, price = {self.tableWidget.item(i, 4).text()}, total_price = {self.tableWidget.item(i, 5).text()} where id = {self.tableWidget.item(i, 0).text()}"
                        result = self.dbutil.select(select)

            select = f"select id from goods where invoice = {self.currentId}"
            result = self.dbutil.select(select)

            array = [a[0] for a in result]
            toDelete = set(array) - set(ids)

            for id in toDelete:
                select = f"delete from goods where id = {id}"
                result = self.dbutil.select(select)

        select = "select max(id) from goods"
        result = self.dbutil.select(select)

        if result[0][0]:
            newMaxId = int(result[0][0])
        else:
            newMaxId = 0

        self.maxGoodsId = newMaxId

        self.deleted = False

    def delete(self):
        self.deleted = True

        select = "delete from goods where invoice = " + str(self.currentId)
        result = self.dbutil.select(select)

        select = "delete from invoices where id = " + str(self.currentId)
        result = self.dbutil.select(select)

        select = "select max(id) from goods"
        result = self.dbutil.select(select)
        self.maxGoodsId = result[0][0]
