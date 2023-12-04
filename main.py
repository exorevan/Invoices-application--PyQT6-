import sys

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication

from core.lib.handlers.handler_interface import Handler
from core.lib.handlers.pages.invoice import InvoicePage
from core.lib.handlers.pages.invoices import InvoicesPage
from core.lib.handlers.pages.plots import PlotsPage
from core.lib.handlers.pages.reports import ReportsPage
from core.lib.utils.database_util import DBUtil


class MainApplication(Handler):
    def __init__(self):
        self.handler_name = "Main Application"

    @classmethod
    def run(self):
        app = QApplication(sys.argv)
        widget = QtWidgets.QStackedWidget()
        dbutil = DBUtil()

        invoices = InvoicesPage(widget, dbutil)
        invoice = InvoicePage(widget, dbutil)
        plots = PlotsPage(widget, dbutil)
        reports = ReportsPage(widget, dbutil)

        widget.addWidget(invoices)
        widget.addWidget(invoice)
        widget.addWidget(plots)
        widget.addWidget(reports)
        widget.show()

        sys.exit(app.exec())
        dbutil.connection.close()


if __name__ == "__main__":
    """
    Indicies:
        0 - Invoices
        1 - Invoice
        2 - Plots
        3 - Reports
    """

    MainApplication.run()
