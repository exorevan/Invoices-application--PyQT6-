import datetime
import typing as ty
from collections.abc import Sequence

import sqlalchemy as sa

from core.datatypes import custom_float
from core.db.tables import Goods, Invoices
from core.db.util import DBUtil


def create_good(
    id: int, width: float, height: float, count: int, price: float, total_price: float
) -> None:
    query: sa.Insert[ty.Any] = sa.Insert(Goods).values(
        invoice=id,
        width=width,
        height=height,
        count=count,
        price=price,
        total_price=total_price,
    )

    return DBUtil.execute(query=query)


def create_invoice(id: int) -> None:
    query: sa.Insert[ty.Any] = sa.Insert(Invoices).values(
        id=id,
        invoice_name="",
        date=datetime.datetime(2000, 1, 1),
        goods=0,
        goods_unique=0,
        earning=0,
    )

    return DBUtil.execute(query=query)


def delete_good(id: int) -> None:
    query: sa.Delete[ty.Any] = sa.Delete(Goods).where(Goods.id == id)

    return DBUtil.execute(query=query)


def delete_goods(id: int) -> None:
    query: sa.Delete[ty.Any] = sa.Delete(Goods).where(Goods.invoice == id)

    return DBUtil.execute(query=query)


def delete_invoice(id: int) -> None:
    query: sa.Delete[ty.Any] = sa.Delete(Invoices).where(Invoices.id == id)

    return DBUtil.execute(query=query)


@custom_float
def get_good(id: int) -> Sequence[sa.RowMapping]:
    query: sa.Select[ty.Any] = sa.Select(Goods.id).where(Goods.invoice == id)

    return DBUtil.query(query=query)


@custom_float
def get_goods(id: int) -> Sequence[sa.RowMapping]:
    query: sa.Select[ty.Any] = sa.Select(
        Goods.id, Goods.width, Goods.height, Goods.count, Goods.price, Goods.total_price
    ).where(Goods.invoice == id)

    return DBUtil.query(query=query)


@custom_float
def get_goods_count() -> Sequence[sa.RowMapping]:
    query: sa.Select[ty.Any] = sa.Select(sa.func.max(Goods.id).label("max_id"))

    return DBUtil.query(query=query)


@custom_float
def get_invoice(id: int) -> Sequence[sa.RowMapping]:
    query: sa.Select[ty.Any] = sa.Select(
        Invoices.id,
        Invoices.invoice_name.label("name"),
        Invoices.date,
        Invoices.goods,
        Invoices.goods_unique,
        Invoices.earning,
    ).where(Invoices.id == id)

    return DBUtil.query(query=query)


@custom_float
def get_invoices_count() -> Sequence[sa.RowMapping]:
    query: sa.Select[ty.Any] = sa.Select(sa.func.max(Invoices.id).label("max_id"))

    return DBUtil.query(query=query)


def update_invoice(
    id: int, name: str, date: str, goods: int, goods_unique: int, earning: float
) -> None:
    query: sa.Update[ty.Any] = (
        sa.Update(Invoices)
        .where(Invoices.id == id)
        .values(
            invoice_name=name,
            date=date,
            goods=goods,
            goods_unique=goods_unique,
            earning=earning,
        )
    )

    return DBUtil.execute(query=query)


def update_good(
    id: int, width: float, height: float, count: int, price: float, total_price: float
) -> None:
    query: sa.Update[ty.Any] = (
        sa.Update(Goods)
        .where(Goods.id == id)
        .values(
            width=width,
            height=height,
            count=count,
            price=price,
            total_price=total_price,
        )
    )

    return DBUtil.execute(query=query)
