import datetime
import typing as ty
from collections.abc import Sequence
from decimal import Decimal
from functools import wraps

from sqlalchemy import RowMapping


class InvoiceFloat:
    value: float | Decimal

    def __init__(self, value: float | Decimal) -> None:
        self.value = value

    @ty.override
    def __str__(self):
        formatted_value = f"{self.value:.2f}".rstrip("0").rstrip(".")
        return formatted_value


record_type = dict[str, bool | int | float | Decimal | str | datetime.datetime | None]


class InvoiceRecord:
    value: record_type

    def __init__(self, value: record_type) -> None:
        self.value = value

    def __getattr__(self, name: str) -> str:
        value = self.value.get(name)

        if value is None:
            return ""

        if isinstance(value, (datetime.date, datetime.datetime)):
            return value.strftime(format="%d.%m.%Y")

        if isinstance(value, (float, Decimal)):
            return f"{value:.2f}".rstrip("0").rstrip(".")

        return str(value)


OuterFetch = Sequence[RowMapping]
InternalFetch = Sequence[InvoiceRecord]
F = ty.TypeVar("F", bound=ty.Callable[..., OuterFetch])


def custom_float(func: F) -> ty.Callable[..., InternalFetch]:
    @wraps(wrapped=func)
    def wrapper(*args, **kwargs) -> InternalFetch:
        result: OuterFetch = func(*args, **kwargs)

        modified_result: list[InvoiceRecord] = []

        for row in result:
            row_dict = dict(row)

            for key, value in row_dict.items():
                row_dict[key] = value

            modified_result.append(InvoiceRecord(row_dict))

        return modified_result

    return wrapper
