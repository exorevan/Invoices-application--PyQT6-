import sys
import typing as ty

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication

from core.lib.handlers.handler_interface import Handler
from core.lib.handlers.pages.invoice import InvoicePage
from core.lib.handlers.pages.invoices import InvoicesPage
from core.lib.handlers.pages.plots import PlotsPage
from core.lib.handlers.pages.reports import ReportsPage
from core.lib.utils.database_util import DBUtil


@ty.final
class MainApplication(Handler):
    def __init__(self) -> None:
        self.handler_name = "Main Application"

    @classmethod
    def run(cls) -> ty.NoReturn:
        dbutil: DBUtil = DBUtil()

        try:
            app: QApplication = QApplication(sys.argv)
            widget: QtWidgets.QStackedWidget = QtWidgets.QStackedWidget()

            invoices: InvoicesPage = InvoicesPage(widget, dbutil)
            invoice: InvoicePage = InvoicePage(widget, dbutil)
            plots: PlotsPage = PlotsPage(widget, dbutil)
            reports: ReportsPage = ReportsPage(widget, dbutil)

            _ = widget.addWidget(invoices)
            _ = widget.addWidget(invoice)
            _ = widget.addWidget(plots)
            _ = widget.addWidget(reports)

            _ = invoice.backToInvoices.connect(invoices.showInvoices)

            widget.show()

            sys.exit(app.exec())
        finally:
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
