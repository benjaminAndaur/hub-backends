from sqlalchemy import Column, Integer, String, DateTime
import datetime

from src.models.base import Base


class {{cookiecutter.entity_name}}DB(Base):
    """Modelo ORM (SQLAlchemy) de {{cookiecutter.entity_name}}.

    Plantilla generada por el arquetipo de módulo (_arquetipo_modulo).
    Reemplaza estos campos por los reales de tu entidad.
    """

    __tablename__ = "{{cookiecutter.entity_table}}"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    creado_en = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
