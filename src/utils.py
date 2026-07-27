#!/usr/bin/env python3
"""
Aparejo de funciones para manipular strings,
dataframes, configurar logging, etc.
"""

# imports
import logging
import re

import pandas as pd


# funciones
def to_snake_case(name: str) -> str:
    """
    Aplica snake_case a un string
    """
    name = re.sub(
        r'([a-z0-9])([A-Z])', 
        r'\1_\2', 
        name
    )
    name = re.sub(
        r'([A-Z]+)([A-Z][a-z])', 
        r'\1_\2',
        name
    )
    name = re.sub(
        r"[\s-]+", 
        "_",
        name
    )
    name = re.sub(
        r"[^a-zA-Z0-9_áéíóúÁÉÍÓÚüÜñÑ]", 
        "", 
        name
    )
    name = re.sub(
        r"_+", 
        "_", 
        name
    )
    name = name.lower()
    
    return name.strip("_")


def snake_case(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convierte los nombres de columna de un DataFrame con to_snake_case
    """
    df.columns = [to_snake_case(col) for col in df.columns]
    
    return df

    
def logging_config() -> None:
    """
    Configuración global de logging
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )
