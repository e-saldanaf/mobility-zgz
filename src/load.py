from sqlalchemy import create_engine, text
import pandas as pd
import logging
import os

ALLOWED_TABLES = {"bizi_stations"}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUERIES_DIR = os.path.join(BASE_DIR, "query", "postgresql", "upsert", "bizi_stations")


class BiziLoader:
    def __init__(self, connection_uri: str):
        self.engine = create_engine(connection_uri)

    @staticmethod
    def _load_sql(filename: str) -> str:
        path = os.path.join(QUERIES_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def upsert_data(self, df: pd.DataFrame, table_name: str) -> None:
        if df.empty:
            logging.info(f"Upsert skipped for '{table_name}': empty DataFrame.")
            return
        if table_name not in ALLOWED_TABLES:
            raise ValueError(
                f"Table '{table_name}' is not allowed. Must be one of: {ALLOWED_TABLES}"
            )

        columns = list(df.columns)
        col_list = ", ".join(columns)
        set_clause = ", ".join(
            f"{c} = EXCLUDED.{c}"
            for c in columns
            if c not in ("id", "created_at")
        )
        staging_table = f"stg_{table_name}"

        with self.engine.begin() as connection:
            connection.execute(
                text(self._load_sql("create_temp_table.sql").format(staging_table=staging_table, table_name=table_name))
            )
            df.to_sql(staging_table, con=connection, if_exists="append", index=False)

            upsert_query = self._load_sql("upsert.sql").format(
                table_name=table_name,
                col_list=col_list,
                set_clause=set_clause,
                staging_table=staging_table,
            )
            results = connection.execute(text(upsert_query)).fetchall()

        inserted = sum(1 for row in results if row.inserted)
        updated = len(results) - inserted

        logging.info(
            f"Upsert complete for '{table_name}': "
            f"{inserted} inserted, {updated} updated, {len(results)} total."
        )