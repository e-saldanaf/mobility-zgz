import pandas as pd
import logging
from datetime import datetime, timezone


class BiziTransformer:
    @staticmethod
    def clean_data(raw_data: list) -> pd.DataFrame:
        if not raw_data:
            logging.warning("No data to transform.")
            return pd.DataFrame()

        try:
            # En lugar de usar posiciones, extraemos los campos por nombre.
            # La API de Zaragoza usa estos nombres internos en su JSON:
            rows = []
            for item in raw_data:
                # Extraemos la fecha del diccionario 'lastUpdated'
                raw_date = item.get('lastUpdated', '')

                rows.append({
                    'id': item.get('id'),
                    'title': item.get('title'),
                    'bikes': item.get('bicisDisponibles'),
                    'slots': item.get('anclajesDisponibles'),
                    'api_updated_at': raw_date,
                    'lon': item.get('geometry', {}).get('coordinates', [0, 0])[0],
                    'lat': item.get('geometry', {}).get('coordinates', [0, 0])[1]
                })

            df = pd.DataFrame(rows)

            # Limpieza y tipado
            df['id'] = pd.to_numeric(df['id']).astype(int)
            df['bikes'] = pd.to_numeric(df['bikes']).fillna(0).astype(int)
            df['slots'] = pd.to_numeric(df['slots']).fillna(0).astype(int)
            df['api_updated_at'] = pd.to_datetime(df['api_updated_at'], errors='coerce')
            df['lon'] = pd.to_numeric(df['lon'])
            df['lat'] = pd.to_numeric(df['lat'])

            # Auditoría
            now = datetime.now(timezone.utc)
            df['created_at'] = now
            df['modified_at'] = now
            

            logging.info(f"Transformation successful: {len(df)} rows processed by field names.")
            return df

        except Exception as e:
            logging.error(f"Transformation logic failed: {e}")
            raise