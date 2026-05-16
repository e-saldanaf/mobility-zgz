# Mobility Zaragoza - Bizi ETL

Este proyecto es un pipeline **ETL (Extract, Transform, Load)** desarrollado en Python que extrae información en tiempo real sobre el estado de las estaciones de bicicletas públicas (Bizi) del Ayuntamiento de Zaragoza, procesa los datos y los almacena en una base de datos (Supabase / PostgreSQL) para su posterior análisis.

## 🚀 Arquitectura del Proyecto

El proceso se divide en tres fases principales:

1. **Extract (`src/extract.py`)**: Se conecta a la API abierta del Ayuntamiento de Zaragoza para obtener el JSON con el estado actual de todas las estaciones.
2. **Transform (`src/transform.py`)**: Limpia, normaliza y formatea los datos obtenidos (ej. estacionamientos disponibles, bicicletas libres, coordenadas).
3. **Load (`src/load.py`)**: Realiza un *upsert* (actualiza si existe, inserta si es nuevo) de los datos en la tabla `bizi_stations` en la base de datos de destino.

## 🛠️ Tecnologías Utilizadas

- **Python 3.x**
- **Pandas** (Transformación de datos)
- **SQLAlchemy / Psycopg** (Conexión a base de datos)
- **Supabase** (Base de datos PostgreSQL recomendada)
- **Requests** (Llamadas a la API)

## ⚙️ Configuración y Uso

### 1. Preparar el entorno e instalar dependencias

Te recomendamos usar un entorno virtual (como tu entorno `data-engineer` de conda):

```bash
# Activar entorno
conda activate data-engineer

# Instalar los requerimientos
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

Asegúrate de tener un archivo llamado `.env` en la raíz del proyecto que contenga la URI de tu base de datos:

```env
DATABASE_URL="postgresql://usuario:contraseña@host:puerto/nombre_bd"
```

### 3. Ejecutar el Pipeline

Para iniciar el proceso de extracción, transformación y carga, simplemente ejecuta el script principal:

```bash
python main.py
```

Si todo funciona correctamente, verás en consola los logs detallando cuántas estaciones se han procesado y confirmando la carga de datos.

## 📡 Fuente de Datos
Los datos son extraídos en tiempo real del servicio de Infraestructuras y Urbanismo de la [API de Datos Abiertos del Ayuntamiento de Zaragoza](https://www.zaragoza.es/sede/portal/datos-abiertos/).