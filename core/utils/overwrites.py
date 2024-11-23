import typing as ty

from PyQt6.QtWidgets import QDialog
from PyQt6.uic import loadUi


def loadUi_(
    uifile: str, baseinstance: QDialog | None = None, package: str | None = None
) -> None:
    _: ty.Any = loadUi(uifile, baseinstance, package if package else "")
