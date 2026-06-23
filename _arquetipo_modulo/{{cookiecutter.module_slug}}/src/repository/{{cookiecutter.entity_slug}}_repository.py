from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.{{cookiecutter.entity_slug}}_db import {{cookiecutter.entity_name}}DB


class {{cookiecutter.entity_name}}Repository:
    """Patrón Repository: única capa que conoce SQLAlchemy.

    El Service nunca debe importar `sqlalchemy` directamente — solo
    habla con los métodos de este repositorio, lo que permite mockear
    la persistencia en tests sin levantar una base de datos real.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def check_db_health(self):
        from sqlalchemy import text
        await self.session.execute(text("SELECT 1"))
        return True

    async def create(self, entidad: {{cookiecutter.entity_name}}DB) -> {{cookiecutter.entity_name}}DB:
        self.session.add(entidad)
        await self.session.commit()
        await self.session.refresh(entidad)
        return entidad

    async def get_all(self) -> list[{{cookiecutter.entity_name}}DB]:
        result = await self.session.execute(select({{cookiecutter.entity_name}}DB))
        return result.scalars().all()

    async def get_by_id(self, id: int) -> {{cookiecutter.entity_name}}DB:
        return await self.session.get({{cookiecutter.entity_name}}DB, id)

    async def update(self, id: int, data: dict) -> {{cookiecutter.entity_name}}DB:
        entidad = await self.get_by_id(id)
        if entidad:
            for key, value in data.items():
                if hasattr(entidad, key):
                    setattr(entidad, key, value)
            await self.session.commit()
            await self.session.refresh(entidad)
        return entidad

    async def delete(self, id: int) -> bool:
        entidad = await self.get_by_id(id)
        if entidad:
            await self.session.delete(entidad)
            await self.session.commit()
            return True
        return False
