import os
from datetime import date, datetime
from typing import final

from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor, QFont, QIcon
from PyQt6.QtWidgets import QDialog, QMessageBox, QTableWidgetItem

from core.lib.utils.database_util import DBUtil, get_application_path
from core.lib.utils.overwrites import loadUi_


@final
class InvoicePage(QDialog):
    dbutil: DBUtil
    widget: QtWidgets.QStackedWidget

    backToInvoices: pyqtSignal = pyqtSignal()

    currentId: int = 0
    newRows: int = 0
    maxGoodsId: int = 0
    deleted: bool = False

    def __init__(self, widget: QtWidgets.QStackedWidget, dbutil: DBUtil) -> None:
        super(InvoicePage, self).__init__()
        _ = loadUi_(
            uifile=os.path.join(get_application_path(), "uis/invoice/Invoice.ui"),
            baseinstance=self,
        )

        self.widget = widget
        self.dbutil = dbutil

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
        self.messageBox.setWindowIcon(
            QIcon(os.path.join(get_application_path(), "uis/invoice/dokkaebi.png"))
        )
        self.messageBox.setWindowTitle("Fill error")

    def goBackToInvoices(self) -> None:
        self.widget.setCurrentIndex(0)
        self.backToInvoices.emit()

    def setNewInvoice(self) -> None:
        self.newRows = 0
        self.deleted = False

        select = "select max(id) from goods"
        result: list[list[str]] = self.dbutil.select(query=select)

        if result[0][0]:
            newMaxId: int = int(result[0][0])
        else:
            newMaxId = 0

        self.maxGoodsId = newMaxId

        select = "select max(id) from invoices"
        result = self.dbutil.select(query=select)

        if result[0][0]:
            newId: int = int(result[0][0])
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

    def changeInfo(self, index: int) -> None:
        self.newRows = 0
        self.currentId = index
        self.deleted = False

        select = "select max(id) from goods"
        result: list[list[str]] = self.dbutil.select(query=select)
        self.maxGoodsId = int(result[0][0])

        if not self.maxGoodsId:
            self.maxGoodsId = 0

        select: str = (
            f"select id, invoice_name, date, goods, goods_unique, earning from invoices where id = {index}"
        )
        result = self.dbutil.select(query=select)

        self.textbox.setText(str(result[0][1]))
        self.dateEdit.setDate(datetime.strptime(result[0][2], "%Y-%m-%d"))
        self.date.setText(
            str(datetime.strptime(result[0][2], "%Y-%m-%d").strftime(format="%d.%m.%Y"))
        )
        self.uniqueGoods.setText(str(result[0][4]) + " positions")
        self.goods.setText(str(result[0][3]))
        self.sum.setText(str(result[0][5]))

        select = f"select id, width, height, count, price, total_price from goods where invoice = {index}"
        result = self.dbutil.select(select)

        self.tableWidget.setRowCount(len(result))
        for i in range(len(result)):
            for j in range(6):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(result[i][j])))

    def addRow(self) -> None:
        newId: int = int(self.maxGoodsId) + self.newRows + 1
        currentRow: int = self.tableWidget.currentRow()
        self.tableWidget.insertRow(currentRow + 1)
        self.tableWidget.setItem(currentRow + 1, 0, QTableWidgetItem(str(newId)))
        self.newRows += 1

    def deleteRow(self) -> None:
        if self.tableWidget.rowCount() > 0:
            currentRow: int = self.tableWidget.currentRow()

            if currentRow < 0:
                currentRow = 0

            self.tableWidget.removeRow(currentRow)

    def calculate(self) -> None:
        sum = 0
        goods = 0
        notNullRows = 0

        for i in range(self.tableWidget.rowCount()):
            width: int = self.tableWidget.item(i, 1)
            height: int = self.tableWidget.item(i, 2)
            count: int = self.tableWidget.item(i, 3)
            price: int = self.tableWidget.item(i, 4)

            if self.upgradedCheck(width, height, count, price):
                for j in range(1, self.tableWidget.columnCount() - 1):
                    self.tableWidget.item(i, j).setBackground(QColor(255, 255, 255))

                count: int = int(count.text())
                price: float = float(price.text())

                value = count * price
                formatted_value = f"{value:.2f}".rstrip("0").rstrip(".")
                self.tableWidget.setItem(i, 5, QTableWidgetItem(formatted_value))

                sum += float(formatted_value)
                goods += count
                notNullRows += 1
            else:
                for j in range(1, self.tableWidget.columnCount() - 1):
                    if self.tableWidget.item(i, j):
                        self.tableWidget.item(i, j).setBackground(QColor(255, 92, 92))

                self.messageBox.setFont(QFont("Dubai Light", 13))

                _ = self.messageOnCond(
                    check=0,
                    messageStart="Error, you must fill ",
                    messageEnd=" in the row ",
                    messageEndAlt=" in the row ",
                    width=width,
                    height=height,
                    count=count,
                    price=price,
                    row=str(i + 1),
                )

                _ = self.messageBox.exec()

            self.uniqueGoods.setText(str(notNullRows) + " positions")
            self.goods.setText(str(goods))
            self.sum.setText(str(sum))

    def disableSelection(self, selected) -> None:
        for i in selected.indexes():
            if self.tableWidget.item(i.row(), i.column()):
                self.tableWidget.item(i.row(), i.column()).setSelected(False)

    def numberCheck(self, number: str | int | float) -> bool:
        try:
            _ = float(number)
            return True
        except ValueError:
            return False

    def upgradedCheck(self, width: int, height: int, count: int, price: int) -> bool:

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

    def firstSubCheck(
        self,
        width: int | None,
        height: int | None,
        count: int | None,
        price: int | None,
    ) -> tuple[bool, bool, bool, bool]:
        return (
            width is not None,
            height is not None,
            count is not None,
            price is not None,
        )

    def secondSubCheck(
        self, width, height, count, price
    ) -> tuple[bool, bool, bool, bool]:
        return (
            self.numberCheck(number=width.text()),
            self.numberCheck(number=height.text()),
            count.text().isdigit(),
            self.numberCheck(number=price.text()),
        )

    def messageOnCond(
        self,
        check: int,
        messageStart: str,
        messageEnd: str,
        messageEndAlt: str,
        width: int,
        height: int,
        count: int,
        price: int,
        row: int,
    ):
        if not check:
            widthCon, heightCon, countCon, priceCon = self.firstSubCheck(
                width, height, count, price
            )

            if widthCon and heightCon and countCon and priceCon:
                _ = self.messageOnCond(
                    check=1,
                    messageStart="Error, ",
                    messageEnd=" must be a float number (1.1, 3, 5.99...) in the row ",
                    messageEndAlt=" must be an integer number (1, 2, 3..) in the row ",
                    width=width,
                    height=height,
                    count=count,
                    price=price,
                    row=row,
                )
                return True
        else:
            widthCon, heightCon, countCon, priceCon = self.secondSubCheck(
                width, height, count, price
            )

        if not widthCon:
            self.messageBox.setText(f"{messageStart}width{messageEnd}{row}")
        elif not heightCon:
            self.messageBox.setText(f"{messageStart}height{messageEnd}{row}")
        elif not countCon:
            self.messageBox.setText(f"{messageStart}count{messageEnd}{row}")
        elif not priceCon:
            self.messageBox.setText(f"{messageStart}price{messageEnd}{row}")

    def save(self) -> None:
        if (
            self.textbox.toPlainText() != ""
            and self.goods.text() != ""
            and self.uniqueGoods.text() != ""
            and self.sum.text() != ""
        ):
            select = "select max(id) from invoices"
            result = self.dbutil.select(select)

            if result[0][0]:
                maxInv: int = int(result[0][0])
            else:
                maxInv = 0

            if int(self.currentId) > int(maxInv) or self.deleted:
                select: str = (
                    "insert into invoices (id, invoice_name, date, goods, goods_unique, earning) values ("
                    + str(self.currentId)
                    + ", '', '2000-01-01', 0, 0, 0)"
                )
                result = self.dbutil.select(select)

            self.calculate()

            select = f"update invoices set invoice_name = '{self.textbox.toPlainText()}', date = '{self.dateEdit.date().toString('yyyy-MM-dd')}', goods = {self.goods.text()}, goods_unique = {self.uniqueGoods.text().replace(' positions', '')}, earning = {self.sum.text()} where id = {self.currentId}"
            result = self.dbutil.select(select)

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
