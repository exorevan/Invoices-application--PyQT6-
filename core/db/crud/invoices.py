import typing as ty
from collections.abc import Sequence

import sqlalchemy as sa

from core.datatypes import custom_float
from core.db.tables import Invoices
from core.db.util import DBUtil


@custom_float
def get_invoices(date1: str, date2: str) -> Sequence[sa.RowMapping]:
    query: sa.Select[ty.Any] = sa.Select(
        Invoices.id,
        Invoices.date,
        Invoices.invoice_name.label("name"),
        Invoices.goods,
        Invoices.earning,
    ).where(Invoices.date >= date1, Invoices.date <= date2)

    return DBUtil.query(query=query)
