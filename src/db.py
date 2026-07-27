#!/usr/bin/env python3
"""
Crea un engine de SQLalchemy a postgreSQL con una conexión psycopg2
o sólo abre la conexión en caso de ser necesario.
"""

# imports
from __future__ import annotations

import os
from functools import cache

import psycopg2
import psycopg2.extensions
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

load_dotenv()


# funciones
def get_db_url() -> str:
    """
    Obtiene y valida la URL de conexión definida en el entorno.
    """
    db_url = os.getenv("DB_URL")

    if not db_url:
        raise ValueError(
            "DB_URL no está definida en el .env."
        )
    return db_url


def get_connection() -> psycopg2.extensions.connection:
    """
    Abre una conexión psycopg2 usando DB_URL.
    """
    db_url = get_db_url()

    if db_url.startswith(
        "postgresql+psycopg2://"
    ):
        db_url = db_url.replace(
            "postgresql+psycopg2://", "postgresql://"
        )
    return psycopg2.connect(db_url)


@cache
def get_engine(echo: bool = False) -> Engine:
    """
    Crea un engine de SQLAlchemy a postgreSQL con psycopg2.
    """

    return create_engine(
        get_db_url(),
        pool_pre_ping=True,
        echo=echo
    )