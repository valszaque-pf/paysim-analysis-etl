#!/usr/bin/env python3
"""
Lee el .parquet post-transform en batches con pyarrow,
lo serializa a un buffer CSV en memoria 
y lo carga a Postgres vía COPY FROM STDIN.
"""

# imports
from __future__ import annotations

import argparse
import io
import logging
import sys
from collections.abc import Iterator
from pathlib import Path

import pandas as pd
import psycopg2.extensions
import pyarrow.parquet as pq
from psycopg2 import sql

from src.db import get_connection
from src.paths import CLEAN_PATH, ensure_directories
from src.schema import PaySim
from src.utils import logging_config

logger = logging.getLogger(__name__)


# constantes
TABLE = PaySim.__table__
TABLE_NAME: str = TABLE.name
TABLE_COLUMNS: list[str] = [
    column.name for column in TABLE.columns if column.name != "id"
]
DEFAULT_BATCH_SIZE: int = 200_000


# funciones
def truncate_table(
    cursor: psycopg2.extensions.cursor, table: str
) -> None:
    """
    Vacía la tabla antes de la carga completa.
    """
    query = sql.SQL(
        "TRUNCATE TABLE {table} RESTART IDENTITY"
    ).format(
        table=sql.Identifier(table)
    )
    cursor.execute(query)

    
def read_parquet_batches(
    path: Path, batch_size: int = DEFAULT_BATCH_SIZE
) -> Iterator[pd.DataFrame]:
    """
    Itera el parquet por batches usando pyarrow.
    """
    parquet_file = pq.ParquetFile(path)
    for batch in parquet_file.iter_batches(batch_size=batch_size):
        yield batch.to_pandas()


def chunk_to_csv_buffer(
    df: pd.DataFrame, columns: list[str]
) -> io.StringIO:
    """
    Reordena el DataFrame según el orden de columnas 
    
    de la tabla y lo serializa a un buffer CSV en memoria.
    """
    buffer = io.StringIO()
    df[columns].to_csv(
        buffer, 
        index=False, 
        header=False
    )
    buffer.seek(0)
    return buffer

    
def copy_chunk(
    cursor: psycopg2.extensions.cursor,
    buffer: io.StringIO,
    table: str,
    columns: list[str],
) -> None:
    """
    Ejecuta COPY FROM STDIN contra Postgres con el 
    
    buffer CSV en memoria de chunk_to_csv_buffer.
    """
    query = sql.SQL(
        "COPY {table} ({columns}) FROM STDIN WITH (FORMAT csv)"
    ).format(
        table=sql.Identifier(table),
        columns=sql.SQL(", ").join(sql.Identifier(col) for col in columns),
    )
    cursor.copy_expert(sql=query, file=buffer)


def load_paysim(
    path: Path = CLEAN_PATH, batch_size: int = DEFAULT_BATCH_SIZE
) -> int:
    """
    Orquesta el load del parquet post-transform a Postgres.

    Retorna el total de filas cargadas. Si falla la función no retorna.
    """
    if batch_size <= 0:
        raise ValueError("batch_size debe ser mayor que cero.")

    conn = get_connection()
    total_rows = 0
    chunk_num = 0

    try:
        with conn:
            with conn.cursor() as cursor:
                truncate_table(cursor, TABLE_NAME)

                for chunk_num, df in enumerate(
                    read_parquet_batches(path, batch_size), start=1
                ):
                    buffer = chunk_to_csv_buffer(
                        df, TABLE_COLUMNS
                    )
                    
                    copy_chunk(
                        cursor, buffer, TABLE_NAME, TABLE_COLUMNS
                    )

                    total_rows += len(df)
                    logger.info(
                        f"Chunk {chunk_num}: {len(df)} filas"
                    )

    except Exception:
        logger.error(
            f"Load abortado en el chunk {chunk_num}. Rollback completo"
        )
        raise
        
    finally:
        conn.close()

    return total_rows


# orquestador
def main() -> None:
    """
    ejecuta el orquestador load_paysim en CLI 
    
    con parámetros opcionales de batch size.
    """
    logging_config()
    ensure_directories()
    
    parser = argparse.ArgumentParser(
        description="Carga masiva de PaySim a Postgres."
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE
    )
    args = parser.parse_args()
    
    try:
        total = load_paysim(
            path=CLEAN_PATH, batch_size=args.batch_size
        )
        logger.info(
            f"Éxito: {total} filas cargadas"
        )
        
    except Exception as e: 
        logger.error(f"Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()