import logging
import os
import sys
import typing as ty
from pathlib import Path
from uu import Error

import sqlalchemy as sa

from conf.config import DEFAULT_DB_PATH
from core.db import tables


def get_application_path() -> str:
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    else:
        return ""


class DBUtil:
    engine: sa.Engine
    metadata: sa.MetaData

    engine = sa.create_engine(f"sqlite:///{DEFAULT_DB_PATH}")
    metadata = tables.Base.metadata

    @classmethod
    def setup(cls) -> None:
        db_path = Path(DEFAULT_DB_PATH)

        db_exists = os.path.exists(db_path)

        if not db_exists:
            cls.metadata.create_all(cls.engine)
            logging.info(msg="Database and tables created successfully.")

        else:
            logging.info(msg="Connected to existing database.")

    @classmethod
    def execute(
        cls,
        query: sa.Delete[ty.Any] | sa.Insert[ty.Any] | sa.Update[ty.Any],
    ):
        try:
            with cls.engine.connect() as connection:
                _ = connection.execute(query)
                connection.commit()

        except Exception as e:
            logging.error(msg=f"Error executing select query: {e}")
            raise Error(f"Error executing select query: {e}")

    @classmethod
    def query(
        cls,
        query: sa.Select[ty.Any],
    ):
        try:
            with cls.engine.connect() as connection:
                result: sa.CursorResult[ty.Any] = connection.execute(query)

            return result.mappings().all()

        except Exception as e:
            logging.error(msg=f"Error executing select query: {e}")
            raise Error(f"Error executing select query: {e}")
