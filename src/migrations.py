#!/usr/bin/env python3
"""
Centralizador de función de migración
para pipeline.py
"""

# imports
import logging

from alembic import command
from alembic.config import Config

from src.paths import ROOT

logger = logging.getLogger(__name__)

# funciones
def run_migrations() -> None:
    """
    Crea o actualiza el esquema de PostgreSQL hasta la revisión
    
    más reciente definida con Alembic.
    """
    alembic_config = Config(str(ROOT / "alembic.ini"))
    alembic_config.set_main_option(
        "script_location", str(ROOT / "migrations")
    )
    alembic_config.attributes["configure_logging"] = False

    logger.info("Aplicando migraciones de base de datos")

    try:
        command.upgrade(alembic_config, "head")
        
    except UnicodeDecodeError as err:
        logger.error("UnicodeDecodeError encontrado en %s", err)
        raise RuntimeError(
            "Alembic no pudo completar la migración. "
            "Revisar configuración de PostgreSQL."
        ) from None
        
    logger.info("Migraciones aplicadas correctamente")