from sqlalchemy import create_engine, text
import pandas as pd
import logging

ALLOWED_TABLES = {"bizi_stations"}

class BiziLoader:
    def __init__(self, connection_uri: str):
        self.engine = create_engine(connection_uri)

    def upsert_data(self, df: pd.DataFrame, table_name: str):
        if df.empty:
            return

        if table_name not in ALLOWED_TABLES:
            raise ValueError(f"Table '{table_name}' is not allowed. Must be one of: {ALLOWED_TABLES}")

        columns = [c for c in df.columns if c != "action"]
        col_list = ", ".join(columns)
        excluded_updates = ",\n                    ".join(
            f"{c} = EXCLUDED.{c}"
            for c in columns
            if c not in ("id", "created_at")
        )

        with self.engine.begin() as connection:
            connection.execute(text(f"DROP TABLE IF EXISTS temp_{table_name}"))
            connection.execute(text(f"CREATE TEMP TABLE temp_{table_name} (LIKE {table_name})"))
            df.to_sql(f"temp_{table_name}", con=connection, if_exists="append", index=False)

            upsert_query = text(f"""
                INSERT INTO {table_name} ({col_list}, action)
                SELECT {col_list}, 'INSERT'
                FROM temp_{table_name}
                ON CONFLICT (id) DO UPDATE SET
                    {excluded_updates},
                    action = 'UPDATE';
            """)
            connection.execute(upsert_query)

            counts = connection.execute(
                text(f"SELECT action, COUNT(*) FROM {table_name} WHERE id IN (SELECT id FROM temp_{table_name}) GROUP BY action")
            ).fetchall()

        summary = {row[0]: row[1] for row in counts}
        logging.info(
            f"Upsert complete for '{table_name}': "
            f"{summary.get('INSERT', 0)} inserted, {summary.get('UPDATE', 0)} updated."
        )