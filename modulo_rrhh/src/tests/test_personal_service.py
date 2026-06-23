from unittest.mock import AsyncMock

import pytest

from src.models.personal_db import PersonalDB
from src.service.personal_service import PersonalService


@pytest.fixture
def mock_personal_repo():
    return AsyncMock()


@pytest.fixture
def service(mock_personal_repo):
    return PersonalService(mock_personal_repo)


@pytest.mark.asyncio
async def test_crear_nuevo_empleado_normalizes_data(service, mock_personal_repo):
    # Arrange
    data = {
        "nombre": "juan",
        "apellido1": "perez",
        "nombre2": "antonio",
        "apellido2": "gonzalez",
        "rut": "12.345.678-k",
        "cargo": "Mecánico",
        "base": "Casa Matriz",
    }

    # Mock repository save to return a PersonalDB instance
    mock_personal_repo.save = AsyncMock(side_effect=lambda x: x)

    # Act
    result = await service.crear_nuevo_empleado(data)

    # Assert
    assert result.nombre == "JUAN"
    assert result.apellido1 == "PEREZ"
    assert result.nombre2 == "ANTONIO"
    assert result.apellido2 == "GONZALEZ"
    assert result.rut == "12345678-K"
    mock_personal_repo.save.assert_called_once()


@pytest.mark.asyncio
async def test_obtener_todos(service, mock_personal_repo):
    # Arrange
    mock_personal_repo.find_all.return_value = [
        PersonalDB(id=1, nombre="JUAN", apellido1="PEREZ", rut="123")
    ]

    # Act
    results = await service.obtener_todos()

    # Assert
    assert len(results) == 1
    assert results[0].nombre == "JUAN"
    mock_personal_repo.find_all.assert_called_once()


@pytest.mark.asyncio
async def test_obtener_por_id(service, mock_personal_repo):
    # Arrange
    mock_personal_repo.find_by_id.return_value = PersonalDB(id=1, nombre="Test")

    # Act
    result = await service.obtener_por_id(1)

    # Assert
    assert result is not None
    assert result.id == 1
    mock_personal_repo.find_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_obtener_por_id_returns_none_when_missing(service, mock_personal_repo):
    # Arrange
    mock_personal_repo.find_by_id.return_value = None

    # Act
    result = await service.obtener_por_id(999)

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_actualizar_personal_delegates_to_repository(service, mock_personal_repo):
    # Arrange
    mock_personal_repo.update.return_value = PersonalDB(id=1, nombre="JUAN", cargo="Mecanico")

    # Act
    result = await service.actualizar_personal(1, {"cargo": "Mecanico"})

    # Assert
    assert result.cargo == "Mecanico"
    mock_personal_repo.update.assert_called_once_with(1, {"cargo": "Mecanico"})


@pytest.mark.asyncio
async def test_eliminar_personal_delegates_to_repository(service, mock_personal_repo):
    # Arrange
    mock_personal_repo.delete.return_value = True

    # Act
    result = await service.eliminar_personal(1)

    # Assert
    assert result is True
    mock_personal_repo.delete.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_eliminar_personal_returns_false_when_not_found(service, mock_personal_repo):
    # Arrange
    mock_personal_repo.delete.return_value = False

    # Act
    result = await service.eliminar_personal(999)

    # Assert
    assert result is False
