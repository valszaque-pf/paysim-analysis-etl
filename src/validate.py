#!/usr/bin/env python3
"""
Contiene las clases que definen los schemas de validacióm
para datos crudos y limpios.
También contiene las funciones que ejecutan la comparación
de los datos contra el schema.
"""

# imports
import logging

import pandas as pd
import pandera.pandas as pa
from pandera.typing import Series

logger = logging.getLogger(__name__)


# constantes 
ALLOWED_TRANSACTION_TYPES = [
    "CASH_IN", 
    "CASH_OUT", 
    "DEBIT", 
    "PAYMENT", 
    "TRANSFER"
]

# clases y funciones
## clase y función de validación de datos crudos
class RawPaySimSchema(pa.DataFrameModel):
    """
    Contrato de datos para el dataset PaySim en estado crudo
    
    en el que se definen las columnas y sus restricciones.
    """
    step: Series[int] = pa.Field(
        ge=1, 
        le=743,
        description=("estos valores corresponden a la cantidad de horas en 1 mes")
    )
    type: Series[str] = pa.Field(
        isin=ALLOWED_TRANSACTION_TYPES,
        description=("la exploración nos dijo que solo estos tipos de operación existen")
    )
    amount: Series[float] = pa.Field(
        ge=0,
        description=("el valor de cualquier monto de dinero operado no puede ser menor"
                     "que 0")
    )
    oldbalanceOrg: Series[float] = pa.Field(
        ge=0,
        description=("el nombre de esta columna será corregido en la siguiente"
                     "operación de transform")
    )
    newbalanceOrig: Series[float] = pa.Field(
        ge=0,
        description=("esta columna y la anterior trabajan con valores de cuentas, por"
                     "lo que no pueden haber negativos")
    )
    nameOrig: Series[str] = pa.Field(
        description="nombre de la cuenta de origen"
    )
    nameDest: Series[str] = pa.Field(
        description=("en ambas columnas sólo hay nombres de cuentas")
    )
    oldbalanceDest: Series[float] = pa.Field(
        ge=0
    )
    newbalanceDest: Series[float] = pa.Field(
        ge=0,
        description=("ambas columnas trabajan con valores de cuentas, nunca pueden"
                     "haber negativos en ellas")
    )
    isFraud: Series[int] = pa.Field(
        isin=[0, 1]
    )
    isFlaggedFraud: Series[int] = pa.Field(
        isin=[0, 1],
        description=("en ambas columnas sabemos que trabajamos con booleanos, mas"
                     "serán transformados después")
    )
    class Config:
        strict=True 
        coerce=False 


def validate_raw(df: pd.DataFrame) -> pd.DataFrame: 
    """
    Valida el DataFrame crudo con el schema PaySimCrudoSchema.
    """ 
    try: 
        logger.info("Comenzando validación")
        df_valido = RawPaySimSchema.validate(df, lazy=True)
        logger.info("Validación completa sin excepciones")
        return df_valido
        
    except pa.errors.SchemaErrors as err: 
        logger.error(
            "Error de validación de Pandera." 
            f"Se encontraron {len(err.failure_cases)} anomalías."
        )
        logger.error(
            f"\nDetalle de fallas:\n{err.failure_cases.to_string()}"
        )
        raise


## clase y función de validación de datos limpios
class CleanPaySimSchema(pa.DataFrameModel):
    """
    Contrato de datos para el dataset PaySim post-transform
    
    en el que se definen las columnas y sus restricciones.
    """
    step: Series[int] = pa.Field(
        ge=1, 
        le=743,
        description=("cantidad de horas en 1 mes")
    )
    type: Series[str] = pa.Field(
        isin=ALLOWED_TRANSACTION_TYPES,
        description=("tipos de operaciones")
    )
    amount: Series[float] = pa.Field(
        ge=0,
        description=("monto transado")
    )
    oldbalance_orig: Series[float] = pa.Field(
        ge=0,
        description=("balance de la cuenta de origen pre-transacción")
    )
    newbalance_orig: Series[float] = pa.Field(
        ge=0,
        description=("balance de la cuenta de origen post-transacción")
    )
    name_orig: Series[str] = pa.Field(
        description=("nombre cuenta de origen")
    )
    name_dest: Series[str] = pa.Field(
        description=("nombre cuenta de destino")
    )
    oldbalance_dest: Series[float] = pa.Field(
        ge=0,
        description=("balance de la cuenta de destino pre-transacción")
    )
    newbalance_dest: Series[float] = pa.Field(
        ge=0,
        description=("balance de la cuenta de destino post-transacción")
    )
    is_fraud: Series[bool] = pa.Field(
        description=("transacciones que son fraude")
    )
    is_flagged_fraud: Series[bool] = pa.Field(
        description=("transacciones que fueron marcadas como fraude")
    )
    hour_of_day: Series[int] = pa.Field(
        ge=0, 
        le=23,
        description=("representa las 24 horas del día")
    )
    simulation_day: Series[int] = pa.Field(
        ge=1, 
        le=31,
        description=("representa los 31 días de la simulación")
    )
    class Config:
        strict=True
        coerce=False 


def validate_clean(df: pd.DataFrame) -> pd.DataFrame: 
    """
    Valida el DataFrame limpio con el schema PaySimLimpioSchema.
    """ 
    try: 
        logger.info("Comenzando validación")
        df_valido = CleanPaySimSchema.validate(df, lazy=True)
        logger.info("Validación completa sin excepciones")
        return df_valido
        
    except pa.errors.SchemaErrors as err: 
        logger.error(
            "Error de validación de Pandera." 
            f"Se encontraron {len(err.failure_cases)} anomalías."
        )
        logger.error(
            f"\nDetalle de fallas:\n{err.failure_cases.to_string()}"
        )
        raise
