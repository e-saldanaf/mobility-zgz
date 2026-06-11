from sqlalchemy import create_engine, text
import pandas as pd
import logging

ALLOWED_TABLES = {"bizi_stations"}


class BiziLoader:
    def __init__(self, connection_uri: str):
        self.engine = create_engine(connection_uri)

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
                text(f"CREATE TEMP TABLE {staging_table} (LIKE {table_name}) ON COMMIT DROP")
            )
            df.to_sql(staging_table, con=connection, if_exists="append", index=False)

            upsert_query = text(f"""
                INSERT INTO {table_name} ({col_list})
                SELECT {col_list} FROM {staging_table}
                ON CONFLICT (id) DO UPDATE SET {set_clause}
                RETURNING (xmax = 0) AS inserted;
            """)
            results = connection.execute(upsert_query).fetchall()

        inserted = sum(1 for row in results if row.inserted)
        updated = len(results) - inserted

        logging.info(
            f"Upsert complete for '{table_name}': "
            f"{inserted} inserted, {updated} updated, {len(results)} total."
        )