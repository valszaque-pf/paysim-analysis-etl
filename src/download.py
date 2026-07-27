#!/usr/bin/env python3
"""
Descarga y descomprime el dataset PaySim desde kaggle.
"""

from __future__ import annotations

import logging
import shutil
import zipfile
from pathlib import Path

import kagglehub

from src.paths import CSV_DIR, CSV_PATH, ensure_directories
from src.utils import logging_config

logger = logging.getLogger(__name__)


# funciones
def decompress_dataset(archive_path: Path) -> Path:
    """
    Extrae el CSV y elimina el ZIP mediante reemplazo atómico.
    """
    temporary_path = CSV_PATH.with_suffix(".csv.tmp")

    try:
        with zipfile.ZipFile(archive_path) as archive:
            matches = [
                entry
                for entry in archive.infolist()
                if not entry.is_dir()
                and Path(entry.filename).name == CSV_PATH.name
            ]

            if len(matches) != 1:
                raise FileNotFoundError(
                    f"No se encontró exactamente un {CSV_PATH.name} "
                    f"dentro de {archive_path}"
                )

            logger.info("Descomprimiendo %s", matches[0].filename)

            with (
                archive.open(matches[0]) as source,
                temporary_path.open("wb") as destination,
            ):
                shutil.copyfileobj(source, destination)

        temporary_path.replace(CSV_PATH)

    finally:
        temporary_path.unlink(missing_ok=True)

    logger.info("CSV descomprimido en %s", CSV_PATH)
    return CSV_PATH


def download_dataset(force_download: bool = False) -> Path:
    """
    Descarga PaySim y devuelve la ruta al CSV descomprimido.
    """
    if CSV_PATH.is_file() and not force_download:
        if zipfile.is_zipfile(CSV_PATH):
            return decompress_dataset(CSV_PATH)

        logger.info("Reutilizando dataset existente en %s", CSV_PATH)
        return CSV_PATH

    logger.info("Descargando dataset desde Kaggle")

    downloaded_path = Path(
        kagglehub.dataset_download(
            "ealaxi/paysim1",
            path=CSV_PATH.name,
            output_dir=str(CSV_DIR),
            force_download=force_download,
        )
    )

    if zipfile.is_zipfile(downloaded_path):
        return decompress_dataset(downloaded_path)

    return CSV_PATH

# orquestador
def main() -> None:
    """
    triggerea la función definida previamente 
    
    cuando el script es ejecutado en terminal
    """
    logging_config()
    ensure_directories()
    
    download_dataset()
    
    
if __name__ == "__main__":
    main()