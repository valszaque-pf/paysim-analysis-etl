#!/usr/bin/env python3
"""
Recibe el dataframe paysim crudo, aplica las transformaciones
necesarias para su validación y lo guarda como .parquet
"""

# imports
import logging

import pandas as pd

from src.paths import CLEAN_PATH, RAW_PATH, ensure_directories
from src.utils import logging_config, snake_case

logger = logging.getLogger(__name__)


# constantes
MONEY_COLUMNS = [
    "amount",
    "oldbalance_orig",
    "newbalance_orig",
    "oldbalance_dest",
    "newbalance_dest"
]


# funciones
def transform(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica la cadena de transformaciones raw -> wrangling.
    """
    transformations = (
        df
        .pipe(
            snake_case
        )
        .rename(
            columns={"oldbalance_org": "oldbalance_orig"}
        )        
        .assign(
            hour_of_day=(df["step"] - 1) % 24
        )
        .assign(
            simulation_day=((df["step"] - 1) // 24) + 1
        )
        .round(
            dict.fromkeys(MONEY_COLUMNS, 2)
        )
        .astype(
            {"is_fraud": bool, "is_flagged_fraud": bool}
        )
    )   
    return transformations


def save_transformed(df: pd.DataFrame) -> None:
    """
    Guarda el DataFrame de transform en formato parquet
    """
    df.to_parquet(CLEAN_PATH, index=False)
    logger.info(f"Transformación completada, archivo guardado en {CLEAN_PATH}")


# orquestador
def main() -> pd.DataFrame:
    """
    triggerea la función definida previamente 
    
    cuando el script es ejecutado en terminal
    """
    logging_config()
    ensure_directories()
    
    paysim_processed = transform(pd.read_parquet(RAW_PATH))
    
    save_transformed(paysim_processed)
    
    logger.info(f"archivo correctamente guardado en {CLEAN_PATH}")
    
    return paysim_processed
    
       
if __name__ == "__main__":
    main()