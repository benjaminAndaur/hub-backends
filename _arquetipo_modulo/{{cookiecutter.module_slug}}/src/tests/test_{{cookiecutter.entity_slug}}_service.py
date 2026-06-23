import pytest
from datetime import datetime
from unittest.mock import AsyncMock

from src.service.{{cookiecutter.entity_slug}}_service import {{cookiecutter.entity_name}}Service
from src.models.{{cookiecutter.entity_slug}}_db import {{cookiecutter.entity_name}}DB


@pytest.fixture
def mock_repo():
    return AsyncMock()


@pytest.fixture
def service(mock_repo):
    return {{cookiecutter.entity_name}}Service(mock_repo)


def _con_id_y_fecha(obj):
    obj.id = 1
    obj.creado_en = datetime(2024, 1, 1)
    return obj


@pytest.mark.asyncio
async def test_crear_retorna_response_dto(service, mock_repo):
    # Arrange
    data = {"nombre": "Ejemplo"}
    mock_repo.create = AsyncMock(side_effect=_con_id_y_fecha)

    # Act
    result = await service.crear(data)

    # Assert
    assert result.id == 1
    assert result.nombre == "Ejemplo"
    mock_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_obtener_todos_retorna_lista(service, mock_repo):
    # Arrange
    mock_repo.get_all.return_value = [
        {{cookiecutter.entity_name}}DB(id=1, nombre="Ejemplo", creado_en=datetime(2024, 1, 1))
    ]

    # Act
    results = await service.obtener_todos()

    # Assert
    assert len(results) == 1
    assert results[0].nombre == "Ejemplo"


@pytest.mark.asyncio
async def test_obtener_por_id_retorna_none_si_no_existe(service, mock_repo):
    # Arrange
    mock_repo.get_by_id.return_value = None

    # Act
    result = await service.obtener_por_id(999)

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_eliminar_delega_en_repository(service, mock_repo):
    # Arrange
    mock_repo.delete.return_value = True

    # Act
    result = await service.eliminar(1)

    # Assert
    assert result is True
    mock_repo.delete.assert_called_once_with(1)
