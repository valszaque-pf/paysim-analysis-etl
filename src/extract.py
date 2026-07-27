#!/usr/bin/env python3
"""
Lee un archivo CSV en memoria, lo transforma 
a un archivo .parquet y lo guarda.
"""

# imports
import logging

import duckdb

from src.paths import CSV_PATH, RAW_PATH, ensure_directories
from src.utils import logging_config

logger = logging.getLogger(__name__)


# funciones
def extract() -> None:
    """
    lee el archivo CSV original en memoria 
    
    y lo extrae como un archivo .parquet
    """
    if not CSV_PATH.is_file():
        logger.error("No existe el archivo CSV en la ruta")
        raise FileNotFoundError("Archivo no encontrado")

    with duckdb.connect() as conn:
        logger.info(f"Extrayendo desde {CSV_PATH}")

        conn.execute(f"""
            COPY (
                SELECT *
                FROM read_csv_auto('{CSV_PATH}')
            )
            TO '{RAW_PATH}'
            (FORMAT PARQUET, COMPRESSION SNAPPY)
        """)
        
        logger.info(f"Extracción completada, archivo guardado en {RAW_PATH}")
            

# orquestador
def main() -> None:
    """
    triggerea la función definida previamente 
    
    cuando el script es ejecutado en terminal
    """
    logging_config()
    ensure_directories()
    
    extract()
    
    
if __name__ == "__main__":
    main()