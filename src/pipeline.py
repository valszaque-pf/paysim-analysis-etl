#!/usr/bin/env python3
"""
Orquestador principal del pipeline ETL del dataset paysim.
"""

# imports
from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass

import pandas as pd

from src.download import download_dataset
from src.extract import extract
from src.load import DEFAULT_BATCH_SIZE, load_paysim
from src.paths import RAW_PATH, ensure_directories
from src.transform import save_transformed, transform
from src.utils import logging_config
from src.validate import validate_clean, validate_raw
from src.migrations import run_migrations

logger = logging.getLogger(__name__)

# clases y funciones
@dataclass(frozen=True)
class PipelineResult:
    """
    Resumen de una ejecución del pipeline.
    """

    loaded_rows: int | None


def run_pipeline(
    *,
    migrate: bool = False,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> PipelineResult:
    """Ejecuta el pipeline ETL.

    Las migraciones de esquema son optativas.
    """
    if batch_size <= 0:
        raise ValueError("batch_size debe ser mayor que cero")

    ensure_directories()

    if migrate:
        run_migrations()
        
    download_dataset()
    extract()

    if not RAW_PATH.is_file():
        raise FileNotFoundError(
            f"No existe el parquet crudo requerido: {RAW_PATH}"
        )

    logger.info("Leyendo y extrayendo datos crudos")
    raw_df = pd.read_parquet(RAW_PATH)
    validated_raw_df = validate_raw(raw_df)

    logger.info("Transformando a datos limpios")
    clean_df = transform(validated_raw_df)
    validated_clean_df = validate_clean(clean_df)
    save_transformed(validated_clean_df)

    logger.info("Iniciando carga a PostgreSQL")
    loaded_rows = load_paysim(batch_size=batch_size)
    logger.info("Carga completada: %s filas", loaded_rows)

    return PipelineResult(
        loaded_rows=loaded_rows
    )


def build_parser() -> argparse.ArgumentParser:
    """
    Construye la interfaz de línea de comandos del pipeline.
    """
    parser = argparse.ArgumentParser(
        description="Ejecuta el pipeline ETL completo de PaySim."
    )
    parser.add_argument(
        "--migrate",
        action="store_true",
        help="Ejecuta 'alembic upgrade head' antes del ETL.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help=(
            "Cantidad de filas por lote durante la carga "
            f"(por defecto: {DEFAULT_BATCH_SIZE})."
        )
    )
    return parser


# orquestador
def main() -> None:
    """
    Procesa argumentos y ejecuta el pipeline desde la terminal.
    """
    logging_config()
    args = build_parser().parse_args()

    try:
        result = run_pipeline(
            migrate=args.migrate,
            batch_size=args.batch_size
        )
    except Exception:
        logger.exception("El pipeline terminó con errores")
        sys.exit(1)

    if result.loaded_rows is None:
        logger.info(
            "Pipeline completado sin carga"
        )
    else:
        logger.info(
            "Pipeline completado: %s filas cargadas",
            result.loaded_rows
        )


if __name__ == "__main__":
    main()
