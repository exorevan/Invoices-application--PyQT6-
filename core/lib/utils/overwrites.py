from PyQt6.QtWidgets import QDialog
from PyQt6.uic import loadUi


def loadUi_(
    uifile: str, baseinstance: QDialog | None = None, package: str = ""
) -> None:
    loadUi(uifile, baseinstance, package)
