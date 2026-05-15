import requests
import logging


class BiziExtractor:
    def __init__(self, api_url: str):
        # Añadimos parámetros de consulta para asegurar el formato JSON
        self.api_url = api_url if "?" in api_url else f"{api_url}?rf=json&start=0&rows=1000"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
        }

    def fetch_data(self) -> list:
        try:
            logging.info(f"Requesting URL: {self.api_url}")
            response = requests.get(self.api_url, headers=self.headers, timeout=20)

            logging.info(f"Response Status: {response.status_code}")

            response.raise_for_status()

            # Si el contenido está vacío, intentamos un fallback sin HTTPS (a veces ocurre en nodos de Zgz)
            if not response.text.strip():
                logging.warning("Empty response received. Retrying with alternative protocol...")
                alt_url = self.api_url.replace("https://", "http://")
                response = requests.get(alt_url, headers=self.headers, timeout=20)

            data = response.json()

            # La API de Zaragoza a menudo devuelve un diccionario con una clave 'result'
            if isinstance(data, dict):
                stations = data.get("result", [])
                logging.info(f"Extracted {len(stations)} stations from dictionary.")
                return stations
            elif isinstance(data, list):
                logging.info(f"Extracted {len(data)} stations from list.")
                return data

            return []

        except Exception as e:
            logging.error(f"Extraction failed: {e}")
            raise