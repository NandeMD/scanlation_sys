from sqlalchemy import create_engine, MetaData, Table, select, insert, update, delete, desc, text, and_
from sqlalchemy.engine.base import Engine
from sqlalchemy.engine.cursor import LegacyCursorResult
from sqlalchemy.sql.selectable import Select
from typing import Optional, Union
from .models import Chapters, PayPeriods


class ChapterEngine:
    def __init__(self) -> None:
        # Generate chapters.db tables from chapters_db_tables.sql
        self.ENGINE = create_engine("sqlite:///chs/chapters.db")
        
        self.conn: Optional[Engine] = None
        
        self.metadata_chapters: Optional[MetaData] = None
        self.metadata_pay_periods: Optional[MetaData] = None
        self.metadata_sqliteseq: Optional[MetaData] = None
        
        self.chapters: Optional[Table] = None
        self.pay_periods: Optional[Table] = None
        self.sqliteseq: Optional[Table] = None
        
    def connect(self):
        self.conn = self.ENGINE.connect()
        self.metadata_chapters = MetaData()
        self.metadata_pay_periods = MetaData()
        self.metadata_sqliteseq = MetaData()
        
        self.chapters = Table("chapters", self.metadata_chapters, autoload=True, autoload_with=self.ENGINE)
        self.pay_periods = Table("pay_periods", self.metadata_pay_periods, autoload=True, autoload_with=self.ENGINE)
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
    
    def select_last_period_chapters(self, last_period_stamp: float):
        query: Select = select(self.chapters).where(self.chapters.columns.created_at >= last_period_stamp)
        result_proxy: LegacyCursorResult = self.conn.execute(query)
        return result_proxy.fetchall()
    
    def select_chapters_by_period(self, period_start: float, period_end: Optional[float]):
        query: Optional[Select] = None
        if period_end is not None and period_end > 0:
            query: Select = select(self.chapters).where(and_(self.chapters.columns.created_at <= period_end, self.chapters.columns.created_at >= period_start))
        else:
            query: Select = select(self.chapters).where(and_(self.chapters.columns.created_at >= period_start))
        
        result_proxy: LegacyCursorResult = self.conn.execute(query)
        return result_proxy.fetchall()
    
    def insert_chapter(self, serie_id: int, serie_name: str, chapter_num: float, creator_id: int, creator_name: str, created_at: float):
        values = {      
            "serie_id":       serie_id,
            "serie_name":     serie_name,
            "chapter_num":    chapter_num,
            "creator_id":     creator_id,
            "creator_name":   creator_name,
            "created_at":     created_at
        }
        
        query = insert(self.chapters)
        self.conn.execute(query, values)
    
    def insert_pay_period(self, creator_id: int, creator_name: str, created_at: float):
        values = {
            "creator_id":     creator_id,
            "creator_name":   creator_name,
            "created_at":     created_at
        }
        
        query = insert(self.pay_periods)
        self.conn.execute(query, values)
        
    def delete_row(self, tbl: Table, row_id):
        query = delete(tbl).where(tbl.columns.id == row_id)
        self.conn.execute(query)
        
    def update_columns(self, model: Union[Chapters, PayPeriods], tbl: Table):
        opts = {}
        
        for key, value in model.dict().items():
            if value is not None:
                opts[key] = value
                
        query = update(tbl).values(opts).where(tbl.columns.id == model.id)
        self.conn.execute(query)
        
    def delete_all(self, tbl: Table):
        query = delete(tbl)
        self.conn.execute(query)
        
        query2 = update(self.sqliteseq).values({"seq": 0}).where(self.sqliteseq.columns.name == tbl.name)
        self.conn.execute(query2)
        
    def check_if_chapter_exists(self, serie_id: int, chapter_num: float):
        query: Select = select(self.chapters).where(
            and_(
                self.chapters.columns.serie_id == serie_id,
                self.chapters.columns.chapter_num == chapter_num
            )
        )
        result_proxy: LegacyCursorResult = self.conn.execute(query)
        return result_proxy.fetchall()
    
    def select_period_by_timestamp(self, timestamp: float):
        query1: Select = select(self.pay_periods).where(
            and_(
                timestamp > self.pay_periods.columns.created_at,
                timestamp < self.pay_periods.columns.closed_at
            )
        )
        
        result_proxy: LegacyCursorResult = self.conn.execute(query1)
        results = result_proxy.fetchall()
        
        if len(results) == 0:
            query2: Select = select(self.pay_periods).where(
                timestamp > self.pay_periods.columns.created_at
            )
            
            result_proxy: LegacyCursorResult = self.conn.execute(query1)
            results = result_proxy.fetchall()
        
        return results
    
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

    def between_2_dates(self, lower_bound: int, upper_bound: int):
        query = text(
            f"SELECT * FROM chapters WHERE "
            f"tl_at BETWEEN {lower_bound} AND {upper_bound} OR "
            f"pr_at BETWEEN {lower_bound} AND {upper_bound} OR "
            f"clnr_at BETWEEN {lower_bound} AND {upper_bound} OR "
            f"ts_at BETWEEN {lower_bound} AND {upper_bound} OR "
            f"qc_at BETWEEN {lower_bound} AND {upper_bound}"
        )
        result = self.conn.execute(query)
        return result.fetchall()
    
    def filter_by_many(self, params: str, table_name: str, count: int):
        parameters = params.split("|")

        query = text(f"SELECT * FROM {table_name} WHERE {' and '.join(parameters)}")
        result = self.conn.execute(query)
        return result.fetchmany(count)
    