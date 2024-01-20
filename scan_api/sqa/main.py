from sqlalchemy import create_engine, MetaData, Table, select, insert, update, delete, desc, text
from sqlalchemy.engine.base import Engine
from sqlalchemy.engine.cursor import LegacyCursorResult
from sqlalchemy.sql.selectable import Select
from sqlalchemy.exc import IntegrityError
from requests.exceptions import MissingSchema, ConnectionError
from .models import Options, Optional


class DataEngine:
    def __init__(self):
        # Generate series.db tables from series_db_tables.sql
        self.ENGINE = create_engine("sqlite:///sqa/series.db")

        self.conn: Optional[Engine] = None
        self.metadata: Optional[MetaData] = None
        self.series: Optional[Table] = None

    def connect(self):
        self.conn = self.ENGINE.connect()
        self.metadata = MetaData()
        self.series = Table("series", self.metadata, autoload=True, autoload_with=self.ENGINE)

    def disconnect(self):
        self.conn.close()

    def select_all(self):
        query: Select = select(self.series)
        result_proxy: LegacyCursorResult = self.conn.execute(query)
        return result_proxy.fetchall()

    def select_many(self, count):
        query: Select = select(self.series)
        result_proxy: LegacyCursorResult = self.conn.execute(query)
        return result_proxy.fetchmany(count)

    def insert_row(
            self,
            name: str,
            image_url: str,
            source_url: str,
            base_url: str,
            source_chap: float,
            base_chap: float,
            role_id: int,
            channel_id: int,
            lchurl: str,
            main_cat: int,
            tl: int,
            pr: int,
            lr: int,
            clnr: int,
            tser: int,
            qcer: int
    ):
        values_list = {
            "name": name,
            "image_url": image_url,
            "source_url": source_url,
            "base_url": base_url,
            "source_chap": source_chap,
            "base_chap": base_chap,
            "role_id": role_id,
            "channel_id": channel_id,
            "discord_last_sent": 0,
            "last_chapter_url": lchurl,
            "main_category": main_cat,
            "current_category": main_cat,
            "tl": tl,
            "pr": pr,
            "lr": lr,
            "clnr": clnr,
            "tser": tser,
            "qcer": qcer,
        }

        query = insert(self.series)
        self.conn.execute(query, values_list)

    def update_columns(self, model: Options):
        opts = {}

        for key, value in model.dict().items():
            if value is not None:
                opts[key] = value

        if model.dict().get("main_category"):
            opts["current_category"] = model.dict().get("main_category")

        query = update(self.series).values(opts).where(self.series.columns.id == model.id)
        self.conn.execute(query)

    def delete_row(self, ehehe):
        query = delete(self.series).where(self.series.columns.id == ehehe)
        self.conn.execute(query)

    def order_by(self, param: str, mode: str):
        query = ""

        if mode == "desc":
            query = text(f"SELECT * FROM series ORDER BY {param} DESC")
        else:
            query = text(f"SELECT * FROM series ORDER BY {param}")

        result = self.conn.execute(query)

        return result.fetchall()

    def order_by_many(self, count, param, mode):
        query = ""

        if mode == "desc":
            query = text(f"SELECT * FROM series ORDER BY {param} DESC LIMIT {count}")
        else:
            query = text(f"SELECT * FROM series ORDER BY {param} LIMIT {count}")

        result = self.conn.execute(query)

        return result.fetchmany(count)

    def filter_by(self, params: str):
        parameters = params.split("|")
        params_arr = []

        for param in parameters:
            x = param.split("=")
            x1 = x[1] if x[1].isnumeric() else f"'{x[1]}'"
            params_arr.append(f"{x[0]}={x1}")

        query = text(f"SELECT * FROM series WHERE {' and '.join(params_arr)}")
        result = self.conn.execute(query)
        return result.fetchall()

    def get_homepage(self):
        query = text("SELECT id, name, image_url, source_url, base_url, source_chap, base_chap, waiting_pr, pred, cleaned, completed, role_id, channel_id FROM series")
        result = self.conn.execute(query)

        series = {
            "series": [
                {
                    "id": serie[0],
                    "name": serie[1],
                    "image_url": serie[2],
                    "source_url": serie[3],
                    "base_url": serie[4],
                    "source_chap": serie[5],
                    "base_chap": serie[6],
                    "waiting_pr": serie[7],
                    "pred": serie[8],
                    "cleaned": serie[9],
                    "completed": serie[10],
                    "role_id": serie[11],
                    "channel_id": serie[12]
                } for serie in result.fetchall()
            ]
        }

        return series

    def get_personnel_page(self):
        query = "SELECT id, name, role_id, channel_id, main_category, current_category, tl, pr, clnr, tser FROM series"
        result = self.conn.execute(query)

        series = {
            "series": [
                {
                    "id": serie[0],
                    "name": serie[1],
                    "role_id": serie[2],
                    "channel_id": serie[3],
                    "main_category": serie[4],
                    "current_category": serie[5],
                    "tl": serie[6],
                    "pr": serie[7],
                    "clnr": serie[8],
                    "tser": serie[9]
                } for serie in result.fetchall()
            ]
        }

        return series


if __name__ == "__main__":
    pass

