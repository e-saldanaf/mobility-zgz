from sqlalchemy import create_engine, text
import pandas as pd
import logging

class BiziLoader:
    def __init__(self, connection_uri: str):
        self.engine = create_engine(connection_uri)

    def upsert_data(self, df: pd.DataFrame, table_name: str):
        if df.empty:
            return

        with self.engine.begin() as connection:
            connection.execute(text(f"CREATE TEMP TABLE temp_{table_name} (LIKE {table_name})"))
            df.to_sql(f"temp_{table_name}", con=connection, if_exists="append", index=False)

            upsert_query = text(f"""
                INSERT INTO {table_name} (id, title, bikes, slots, lat, lon, api_updated_at, created_at, modified_at, action)
                SELECT id, title, bikes, slots, lat, lon, api_updated_at, created_at, modified_at, 'INSERT'
                FROM temp_{table_name}
                ON CONFLICT (id) DO UPDATE SET
                    bikes = EXCLUDED.bikes,
                    slots = EXCLUDED.slots,
                    api_updated_at = EXCLUDED.api_updated_at,
                    modified_at = EXCLUDED.modified_at,
                    action = 'UPDATE';
            """)
            connection.execute(upsert_query)
            logging.info(f"Successfully loaded {len(df)} rows.")