import typing as ty
from collections.abc import Sequence

import sqlalchemy as sa

from core.datatypes import custom_float
from core.db.tables import Goods, Invoices
from core.db.util import DBUtil


@custom_float
def get_invoice_sum(subject: str, date1: str, date2: str) -> Sequence[sa.RowMapping]:
    query: sa.Select[ty.Any] = sa.Select(
        sa.func.sum(getattr(Invoices, subject)).label("sum")
    ).where(Invoices.date >= date1, Invoices.date < date2)

    return DBUtil.query(query=query)


@custom_float
def get_goods(date1: str, date2: str) -> Sequence[sa.RowMapping]:
    query: sa.Select[ty.Any] = (
        sa.Select(Goods.width, Goods.height, Goods.total_price)
        .select_from(sa.join(Goods, Invoices, Goods.invoice == Invoices.id))
        .where(Invoices.date >= date1, Invoices.date < date2)
    )

    return DBUtil.query(query=query)
