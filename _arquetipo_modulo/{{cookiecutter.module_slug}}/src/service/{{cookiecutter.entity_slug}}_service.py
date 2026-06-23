from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

from src.repository.{{cookiecutter.entity_slug}}_repository import {{cookiecutter.entity_name}}Repository
from src.models.{{cookiecutter.entity_slug}}_db import {{cookiecutter.entity_name}}DB


class {{cookiecutter.entity_name}}DTO(BaseModel):
    nombre: str


class {{cookiecutter.entity_name}}ResponseDTO({{cookiecutter.entity_name}}DTO):
    id: int
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)


class {{cookiecutter.entity_name}}Service:
    """Lógica de negocio de {{cookiecutter.entity_name}}.

    Orquesta el Repository pero no conoce SQLAlchemy ni detalles de
    persistencia — solo objetos de dominio y DTOs Pydantic.
    """

    def __init__(self, repository: {{cookiecutter.entity_name}}Repository):
        self.repository = repository

    async def check_db_health(self) -> bool:
        try:
            await self.repository.check_db_health()
            return True
        except Exception:
            return False

    async def crear(self, data: dict) -> {{cookiecutter.entity_name}}ResponseDTO:
        dto = {{cookiecutter.entity_name}}DTO(**data)
        nuevo = {{cookiecutter.entity_name}}DB(**dto.model_dump())
        creado = await self.repository.create(nuevo)
        return {{cookiecutter.entity_name}}ResponseDTO.model_validate(creado)

    async def obtener_todos(self) -> List[{{cookiecutter.entity_name}}ResponseDTO]:
        entidades = await self.repository.get_all()
        return [{{cookiecutter.entity_name}}ResponseDTO.model_validate(e) for e in entidades]

    async def obtener_por_id(self, id: int) -> Optional[{{cookiecutter.entity_name}}ResponseDTO]:
        entidad = await self.repository.get_by_id(id)
        if entidad:
            return {{cookiecutter.entity_name}}ResponseDTO.model_validate(entidad)
        return None

    async def actualizar(self, id: int, data: dict) -> Optional[{{cookiecutter.entity_name}}ResponseDTO]:
        actualizado = await self.repository.update(id, data)
        if actualizado:
            return {{cookiecutter.entity_name}}ResponseDTO.model_validate(actualizado)
        return None

    async def eliminar(self, id: int) -> bool:
        return await self.repository.delete(id)
