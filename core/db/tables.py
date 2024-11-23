import datetime
import typing as ty

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import DeclarativeMeta, Mapped, declarative_base, mapped_column

Base: DeclarativeMeta = declarative_base()


@ty.final
class Goods(Base):
    __tablename__ = "goods"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, unique=True, nullable=False
    )
    invoice: Mapped[int] = mapped_column(ForeignKey("invoices.id"), nullable=False)
    width: Mapped[float] = mapped_column(Numeric, nullable=False)
    height: Mapped[float] = mapped_column(Numeric, nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Numeric, nullable=False)
    total_price: Mapped[float] = mapped_column(Numeric, nullable=False)


@ty.final
class Info(Base):
    __tablename__ = "info"

    invoices: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, unique=True, nullable=False
    )
    goods: Mapped[int] = mapped_column(Integer)
    packs: Mapped[int] = mapped_column(Integer)


@ty.final
class Invoices(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, unique=True, nullable=False
    )
    invoice_name: Mapped[str] = mapped_column(Text, nullable=False)
    date: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )
    goods: Mapped[int] = mapped_column(Integer, nullable=False)
    goods_unique: Mapped[int] = mapped_column(Integer)
    earning: Mapped[float] = mapped_column(Numeric, nullable=False)


@ty.final
class Packs(Base):
    __tablename__ = "packs"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, unique=True, nullable=False
    )
    pack_name: Mapped[str] = mapped_column(Text, nullable=False)
