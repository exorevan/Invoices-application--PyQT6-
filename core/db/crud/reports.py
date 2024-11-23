import typing as ty
from collections.abc import Sequence

import sqlalchemy as sa

from core.datatypes import custom_float
from core.db.tables import Goods, Invoices
from core.db.util import DBUtil


@custom_float
def get_goods_parameters(date1: str, date2: str) -> Sequence[sa.RowMapping]:
    query: sa.Select[ty.Any] = (
        sa.Select(
            Goods.width,
            Goods.height,
            sa.func.sum(Goods.count).label("count"),
            sa.func.sum(Goods.total_price).label("price"),
        )
        .select_from(sa.join(Goods, Invoices, Goods.invoice == Invoices.id))
        .where(Invoices.date.between(date1, date2))
        .group_by(Goods.width, Goods.height)
    )

    return DBUtil.query(query=query)


@custom_float
def get_goods_summary(date1: str, date2: str) -> Sequence[sa.RowMapping]:
    query: sa.Select[ty.Any] = (
        sa.Select(
            sa.func.sum(Goods.count).label("count"),
            sa.func.sum(Goods.total_price).label("total_price"),
        )
        .select_from(sa.join(Goods, Invoices, Goods.invoice == Invoices.id))
        .where(Invoices.date.between(date1, date2))
    )

    return DBUtil.query(query=query)
