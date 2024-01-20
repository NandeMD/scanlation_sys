from sqlalchemy import create_engine, MetaData, Table, select, insert, update, delete, desc, text, and_
from sqlalchemy.engine.base import Engine
from sqlalchemy.engine.cursor import LegacyCursorResult
from sqlalchemy.sql.selectable import Select
from typing import Optional, Union, Type
from .models import SpeedrunWorks, SpeedrunSeries, SR, Work
from sqlalchemy.engine import Row


import arrow


class SpeedrunsEngine:
    def __init__(self) -> None:
        # Generate speedruns.db tables from speedruns_db_tables.sql
        self.ENGINE = create_engine("sqlite:///speedruns/speedruns.db")

        self.conn: Optional[Engine] = None

        self.metadata_sr_series: Optional[MetaData] = None
        self.metadata_sr_works: Optional[MetaData] = None
        self.metadata_sqliteseq: Optional[MetaData] = None

        self.sr_series: Optional[Table] = None
        self.sr_works: Optional[Table] = None
        self.sqliteseq: Optional[Table] = None

    def connect(self):
        self.ENGINE.connect()
        self.metadata_sr_series = MetaData()
        self.metadata_sr_works = MetaData()
        self.metadata_sqliteseq = MetaData()

        self.sr_series = Table("sr_series", self.metadata_sr_series, autoload=True, autoload_with=self.ENGINE)
        self.sr_works = Table("sr_works", self.metadata_sr_works, utoload=True, autoload_with=self.ENGINE)
        self.sqliteseq = Table("sqlite_sequence", self.metadata_sqliteseq, autoload=True, autoload_with=self.ENGINE)

    def disconnect(self):
        self.conn.close()

    def select_all(self, tbl: Table):
        query: Select = select(tbl)
        result_proxy: LegacyCursorResult = self.conn.execute(query)
        return result_proxy.fetchall()

    def select_many(self, tbl: Table, count: int):
        query: Select = select(tbl)
        result_proxy: LegacyCursorResult = self.conn.execute(query)
        return result_proxy.fetchmany(count)

    def select_by_id(self, tbl: Table, row_id: int):
        query: Select = select(tbl).where(tbl.columns.id == row_id)
        result_proxy: LegacyCursorResult = self.conn.execute(query)
        return result_proxy.fetchall()

    def insert_sr_serie(self, serie_id: int, serie_name: str, creator_id: int, creator_name: str, created_at: int, is_manga: bool, duration: int, fee: float):
        values = {
            "serie_id": serie_id,
            "serie_name": serie_name,
            "creator_id": creator_id,
            "creator_name": creator_name,
            "created_at": created_at,
            "is_manga": 1 if is_manga else 0,
            "duration": duration,
            "fee": fee
        }

        query = insert(self.sr_series)
        self.conn.execute(query, values)

    def insert_sr_work(self, creator_id: int, creator_name: str, created_at: int, work_type: int):
        values = {
            "creator_id": creator_id,
            "creator_name": creator_name,
            "created_at": created_at,
            "work_type": work_type
        }

        query = insert(self.sr_works)
        self.conn.execute(query, values)

    def delete_row(self, tbl: Table, row_id):
        query = delete(tbl).where(tbl.columns.id == row_id)
        self.conn.execute(query)

    def delete_all(self, tbl: Table):
        query = delete(tbl)
        self.conn.execute(query)

        query2 = update(self.sqliteseq).values({"seq": 0}).where(self.sqliteseq.columns.name == tbl.name)
        self.conn.execute(query2)

    def order_by_(self, param: str, mode: str, table_name: str):
        query = ""

        if mode == "desc":
            query = text(f"SELECT * FROM {table_name} ORDER BY {param} DESC")
        else:
            query = text(f"SELECT * FROM {table_name} ORDER BY {param}")

        result = self.conn.execute(query)

        return result.fetchall()

    def order_by_many(self, param: str, mode: str, table_name: str, count: int):
        query = ""

        if mode == "desc":
            query = text(f"SELECT * FROM {table_name} ORDER BY {param} DESC")
        else:
            query = text(f"SELECT * FROM {table_name} ORDER BY {param}")

        result = self.conn.execute(query)

        return result.fetchmany(count)

    def filter_by(self, params: str, table_name: str):
        parameters = params.split("|")

        query = text(f"SELECT * FROM {table_name} WHERE {' and '.join(parameters)}")
        result = self.conn.execute(query)
        return result.fetchall()

    def filter_by_many(self, params: str, table_name: str, count: int):
        parameters = params.split("|")

        query = text(f"SELECT * FROM {table_name} WHERE {' and '.join(parameters)}")
        result = self.conn.execute(query)
        return result.fetchmany(count)

    def update_columns(self, model: Union[SpeedrunWorks, SpeedrunSeries], tbl: Table):
        opts = {}

        for key, value in model.dict().items():
            if value is not None:
                opts[key] = value

        query = update(tbl).values(opts).where(tbl.columns.id == model.id)
        self.conn.execute(query)

    @staticmethod
    def _match_sr_with_work(l_series: list[Row], l_works: list[Row]):
        srs = [SR.from_orm(o) for o in l_series]
        works = [Work.from_orm(o) for o in l_works]

        for s in srs:
            for i in range(len(works)-1, -1, -1):
                if works[i].sr_id == s.id:
                    s.works.append(works[i])
                    works.remove(works[i])

        return srs

    def get_all_and_match(self):
        sr_series = self.select_all(self.sr_series)
        sr_works = self.select_all(self.sr_works)

        return self._match_sr_with_work(sr_series, sr_works)

    def get_active_and_match(self):
        today = int(arrow.utcnow().timestamp())
        sr_series = self.filter_by(f"created_at + duration * 3600 > {today}", "sr_series")
        sr_works = self.select_all(self.sr_works)

        return self._match_sr_with_work(sr_series, sr_works)

    def get_single_sr_from_id(self, sr_id: int):
        sr_serie = self.filter_by(f"id == {sr_id}", "sr_series")[0]
        sr_works = self.filter_by(f"sr_id == {sr_id}", "sr_works")

        ser = SR.from_orm(sr_serie)
        works = [Work.from_orm(o) for o in sr_works]
        ser.works = works

        return ser

