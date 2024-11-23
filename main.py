import sys
import typing as ty

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication

from core.handlers.handler_interface import Handler
from core.handlers.pages.invoice import InvoicePage
from core.handlers.pages.invoices import InvoicesPage
from core.handlers.pages.plots import PlotsPage
from core.handlers.pages.reports import ReportsPage
from core.db.util import DBUtil


@ty.final
class MainApplication(Handler):
    def __init__(self) -> None:
        self.handler_name = "Main Application"

    @classmethod
    def run(cls) -> ty.NoReturn:
        DBUtil.setup()

        app: QApplication = QApplication(sys.argv)
        widget: QtWidgets.QStackedWidget = QtWidgets.QStackedWidget()

        invoices: InvoicesPage = InvoicesPage(widget)
        invoice: InvoicePage = InvoicePage(widget)
        plots: PlotsPage = PlotsPage(widget)
        reports: ReportsPage = ReportsPage(widget)

        _ = widget.addWidget(invoices)
        _ = widget.addWidget(invoice)
        _ = widget.addWidget(plots)
        _ = widget.addWidget(reports)

        _ = invoice.backToInvoices.connect(invoices.showInvoices)

        widget.show()

        sys.exit(app.exec())


if __name__ == "__main__":
    """
    Indicies:
        0 - Invoices
        1 - Invoice
        2 - Plots
        3 - Reports
    """

    MainApplication.run()
