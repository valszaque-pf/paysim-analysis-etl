#!/usr/bin/env python3
"""
Clases definitorias del schema utilizado para migrar la tabla a
postgreSQL con alembic.
"""

# imports
from __future__ import annotations

from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Identity,
    Index,
    MetaData,
    Numeric,
    SmallInteger,
    Text,
    false,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# clases
class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    })


class PaySim(Base):
    __tablename__ = "paysim"
    __table_args__ = (
        CheckConstraint(
            "amount >= 0",
            name="amount_nonneg"
        ),
        CheckConstraint(
            "hour_of_day BETWEEN 0 AND 23", 
            name="hour_valid"
        ),
        CheckConstraint(
            "type IN ('PAYMENT','TRANSFER','CASH_OUT','CASH_IN','DEBIT')",
            name="type_valid"
        ),
        Index(
            "ix_paysim_name_orig", 
            "name_orig"
        ),
        Index(
            "ix_paysim_name_dest", 
            "name_dest"
        ),
        Index(
            "ix_paysim_is_fraud_true",
            "is_fraud",
            postgresql_where=text("is_fraud = true")
        )
    )
    id: Mapped[int] = mapped_column(
        Identity(), primary_key=True
    )
    step: Mapped[int] = mapped_column(
        SmallInteger, nullable=False
    )
    type: Mapped[str] = mapped_column(        
        Text, nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False
    )
    name_orig: Mapped[str] = mapped_column(
        Text, nullable=False
    )
    oldbalance_orig: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False
    )
    newbalance_orig: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False
    )
    name_dest: Mapped[str] = mapped_column(
        Text, nullable=False
    )
    oldbalance_dest: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False
    )
    newbalance_dest: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False
    )
    is_fraud: Mapped[bool] = mapped_column(
        nullable=False, default=False, server_default=false()
    )
    is_flagged_fraud: Mapped[bool] = mapped_column(
        nullable=False, default=False, server_default=false()
    )
    hour_of_day: Mapped[int] = mapped_column(
        SmallInteger, nullable=False
    )
    simulation_day: Mapped[int] = mapped_column(
        SmallInteger, nullable=False
    )