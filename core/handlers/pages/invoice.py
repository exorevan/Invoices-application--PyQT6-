import os
import typing as ty
from datetime import date, datetime

from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import pyqtSignal

from core.db.crud import invoice as crud
from core.db.util import get_application_path
from core.handlers.pages import notification
from core.handlers.pages.notification import NotificationWidget
from core.utils.overwrites import loadUi_


@ty.final
class InvoicePage(QtWidgets.QDialog):
    notification: NotificationWidget | None = None
    widget: QtWidgets.QStackedWidget

    backToInvoices: pyqtSignal = pyqtSignal()

    currentId: int = 0
    newRows: int = 0
    maxGoodsId: int = 0
    deleted: bool = False

    def __init__(self, widget: QtWidgets.QStackedWidget) -> None:
        super(InvoicePage, self).__init__()
        _ = loadUi_(
            uifile=os.path.join(get_application_path(), "uis/invoice/Invoice.ui"),
            baseinstance=self,
        )

        self.widget = widget
        self.installEventFilter(self)

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

        self.messageBox = QtWidgets.QMessageBox(self)
        self.messageBox.setWindowIcon(
            QtGui.QIcon(
                os.path.join(get_application_path(), "uis/invoice/dokkaebi.png")
            )
        )
        self.messageBox.setWindowTitle("Fill error")

    def goBackToInvoices(self) -> None:
        if self.notification and self.notification.isVisible():
            self.notification.start_hide_animation()

        self.widget.setCurrentIndex(0)
        self.backToInvoices.emit()

    def setNewInvoice(self) -> None:
        self.newRows = 0
        self.deleted = False

        goods_result = crud.get_goods_count()[0]

        newMaxId: int = int(goods_result.max_id) if goods_result.max_id else 0

        self.maxGoodsId = newMaxId

        invoices_result = crud.get_invoices_count()[0]

        newId: int = int(invoices_result.max_id) if invoices_result.max_id else 0

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

        goods_count_result = crud.get_goods_count()[0]
        self.maxGoodsId = (
            int(goods_count_result.max_id) if goods_count_result.max_id else 0
        )

        if not self.maxGoodsId:
            self.maxGoodsId = 0

        invoice_result = crud.get_invoice(id=index)[0]

        self.textbox.setText(invoice_result.name)
        self.dateEdit.setDate(datetime.strptime(invoice_result.date, "%d.%m.%Y"))
        self.date.setText(invoice_result.date)
        self.uniqueGoods.setText(invoice_result.goods_unique + " positions")
        self.goods.setText(invoice_result.goods)
        self.sum.setText(invoice_result.earning)

        goods_result = crud.get_goods(id=index)

        self.tableWidget.setRowCount(len(goods_result))
        for i, val in enumerate(goods_result):
            self.tableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem(val.id))
            self.tableWidget.setItem(i, 1, QtWidgets.QTableWidgetItem(val.width))
            self.tableWidget.setItem(i, 2, QtWidgets.QTableWidgetItem(val.height))
            self.tableWidget.setItem(i, 3, QtWidgets.QTableWidgetItem(val.count))
            self.tableWidget.setItem(i, 4, QtWidgets.QTableWidgetItem(val.price))
            self.tableWidget.setItem(i, 5, QtWidgets.QTableWidgetItem(val.total_price))

    def addRow(self) -> None:
        newId: int = int(self.maxGoodsId) + self.newRows + 1
        currentRow: int = self.tableWidget.currentRow()
        self.tableWidget.insertRow(currentRow + 1)
        self.tableWidget.setItem(
            currentRow + 1, 0, QtWidgets.QTableWidgetItem(str(newId))
        )
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
                    self.tableWidget.item(i, j).setBackground(
                        QtGui.QColor(255, 255, 255)
                    )

                count: int = int(count.text())
                price: float = float(price.text())

                value = count * price
                formatted_value = value
                self.tableWidget.setItem(
                    i, 5, QtWidgets.QTableWidgetItem(str(formatted_value))
                )

                sum += float(formatted_value)
                goods += count
                notNullRows += 1
            else:
                for j in range(1, self.tableWidget.columnCount() - 1):
                    if self.tableWidget.item(i, j):
                        self.tableWidget.item(i, j).setBackground(
                            QtGui.QColor(255, 92, 92)
                        )

                self.messageBox.setFont(QtGui.QFont("Dubai Light", 13))

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
            invoices_result = crud.get_invoices_count()[0]

            maxInv: int = int(invoices_result.max_id) if invoices_result.max_id else 0

            if int(self.currentId) > int(maxInv) or self.deleted:
                _ = crud.create_invoice(self.currentId)

            self.calculate()

            _ = crud.update_invoice(
                id=self.currentId,
                name=self.textbox.toPlainText(),
                date=self.dateEdit.date().toPyDate(),
                goods=int(self.goods.text()),
                goods_unique=int(self.uniqueGoods.text().replace(" positions", "")),
                earning=float(self.sum.text()),
            )

            ids = []

            for i in range(self.tableWidget.rowCount()):
                if self.upgradedCheck(
                    self.tableWidget.item(i, 1),
                    self.tableWidget.item(i, 2),
                    self.tableWidget.item(i, 3),
                    self.tableWidget.item(i, 4),
                ):
                    ids.append(self.tableWidget.item(i, 0).text())

                    if int(self.tableWidget.item(i, 0).text()) > self.maxGoodsId:
                        _ = crud.create_good(
                            id=self.currentId,
                            width=self.tableWidget.item(i, 1).text(),
                            height=self.tableWidget.item(i, 2).text(),
                            count=self.tableWidget.item(i, 3).text(),
                            price=self.tableWidget.item(i, 4).text(),
                            total_price=self.tableWidget.item(i, 5).text(),
                        )
                    else:
                        _ = crud.update_good(
                            id=self.tableWidget.item(i, 0).text(),
                            width=self.tableWidget.item(i, 1).text(),
                            height=self.tableWidget.item(i, 2).text(),
                            count=self.tableWidget.item(i, 3).text(),
                            price=self.tableWidget.item(i, 4).text(),
                            total_price=self.tableWidget.item(i, 5).text(),
                        )

            good_result = crud.get_good(id=self.currentId)

            array = [a.id for a in good_result]
            toDelete: set[int] = set(array) - set(ids)

            for id in toDelete:
                _ = crud.delete_good(id=id)

        goods_result = crud.get_goods_count()[0]

        newMaxId: int = int(goods_result.max_id) if goods_result.max_id else 0

        self.maxGoodsId = newMaxId

        self.deleted = False

        self.show_notification(message="Saved succesfully")

    def show_notification(self, message: str) -> None:
        if self.notification is not None:
            # Закрываем предыдущее уведомление
            _ = self.notification.close()

        self.notification = NotificationWidget(message, self)
        self.notification.show()
        # Устанавливаем позицию уведомления
        self.notification.update_position()

    @ty.override
    def resizeEvent(self, a0: QtGui.QResizeEvent | None = None):
        super().resizeEvent(a0)
        if self.notification is not None:
            self.notification.update_position()

    def delete(self):
        self.deleted = True

        result = crud.delete_goods(id=self.currentId)

        result = crud.delete_invoice(id=self.currentId)

        result = crud.get_goods_count()[0]
        self.maxGoodsId = int(result.max_id)
