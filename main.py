import os
import logging
import sys
from dotenv import load_dotenv
from src.extract import BiziExtractor
from src.transform import BiziTransformer
from src.load import BiziLoader

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



def main():
    load_dotenv()

    API_URL = "https://www.zaragoza.es/sede/servicio/urbanismo-infraestructuras/estacion-bicicleta.json"
    DB_URI = os.getenv("DATABASE_URL")
    TABLE_NAME = "bizi_stations"

    from_date = sys.argv[1] if len(sys.argv) > 1 else None
    to_date = sys.argv[2] if len(sys.argv) > 2 else None

    logging.info("Starting ETL Process for Bizi Stations Data from_date: %s, to_date: %s", from_date, to_date)

    try:
        # E - Extract
        extractor = BiziExtractor(API_URL)
        data = extractor.fetch_data()

        if not data:
            logging.error("No data received from API. Pipeline stopping.")
            return

        # T - Transform
        transformer = BiziTransformer()
        df = transformer.clean_data(data)

        if df.empty:
            logging.error("Dataframe is empty after transformation. Pipeline stopping.")
            return

        # L - Load
        loader = BiziLoader(DB_URI)
        loader.upsert_data(df, TABLE_NAME)

        logging.info("ETL Process finished successfully and data loaded to Supabase.")

    except Exception as e:
        logging.error(f"Pipeline failed: {e}")


if __name__ == "__main__":
    main()