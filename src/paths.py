#!/usr/bin/env python3
"""
Contiene las rutas utilizadas a través de todo el programa
y crea los directorios del proyecto completo.
"""

# imports
import logging
from pathlib import Path

from src.utils import logging_config

logger = logging.getLogger(__name__)

# constantes
## sube a raíz del proyecto desde la carpeta /src/
ROOT = Path(__file__).resolve().parent.parent

## carpetas de datos y consultas
DATA_DIR        = ROOT / "data"
CSV_DIR         = DATA_DIR / "csv"
RAW_DIR         = DATA_DIR / "raw"
TRANSFORMED_DIR = DATA_DIR / "transformed"
SQL_DIR         = ROOT / "SQL"

## outputs de gráficos y cuadernos
REPORTS_DIR     = ROOT / "reports"
NOTEBOOKS_DIR   = ROOT / "notebooks"

## archivos concretos
CSV_PATH        = CSV_DIR / "PS_20174392719_1491204439457_log.csv"
RAW_PATH        = RAW_DIR  / "paysim_raw.parquet"
CLEAN_PATH      = TRANSFORMED_DIR / "paysim_clean.parquet"


# funciones
def ensure_directories() -> None:
    """
    Crea los directorios faltantes en caso de ser necesario.
    """
    logger.info("Creando directorios...")
    
    for directory in (
        DATA_DIR, 
        CSV_DIR, 
        RAW_DIR, 
        TRANSFORMED_DIR, 
        REPORTS_DIR, 
        NOTEBOOKS_DIR
    ):
        directory.mkdir(parents=True, exist_ok=True)


# orquestador
def main() -> None:
    """
    triggerea la función definida previamente 
    
    cuando el script es ejecutado en terminal
    """
    logging_config()
    
    ensure_directories()


if __name__ == "__main__":
    main()