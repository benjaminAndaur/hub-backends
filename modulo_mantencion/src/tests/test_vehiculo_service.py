from unittest.mock import AsyncMock

import pytest

from src.models.vehiculo import VehiculoCreate, VehiculoResponse, VehiculoUpdate
from src.models.vehiculo_db import VehiculoDB
from src.service.vehiculo_service import VehiculoService


@pytest.fixture
def mock_vehiculo_repo():
    return AsyncMock()


@pytest.fixture
def service(mock_vehiculo_repo):
    return VehiculoService(mock_vehiculo_repo)


@pytest.mark.asyncio
async def test_create_vehiculo_returns_response(service, mock_vehiculo_repo):
    # Arrange
    data = VehiculoCreate(patente="ABCD12", modelo="Camion")
    mock_vehiculo_repo.create.return_value = VehiculoDB(
        id=1, patente="ABCD12", modelo="Camion", estado="Disponible"
    )

    # Act
    result = await service.create_vehiculo(data)

    # Assert
    assert isinstance(result, VehiculoResponse)
    assert result.id == 1
    assert result.patente == "ABCD12"
    mock_vehiculo_repo.create.assert_called_once_with(data)


@pytest.mark.asyncio
async def test_get_vehiculo_returns_response_when_found(service, mock_vehiculo_repo):
    # Arrange
    mock_vehiculo_repo.get_by_id.return_value = VehiculoDB(
        id=1, patente="ABCD12", estado="Disponible"
    )

    # Act
    result = await service.get_vehiculo(1)

    # Assert
    assert result is not None
    assert result.id == 1
    mock_vehiculo_repo.get_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_get_vehiculo_returns_none_when_missing(service, mock_vehiculo_repo):
    # Arrange
    mock_vehiculo_repo.get_by_id.return_value = None

    # Act
    result = await service.get_vehiculo(999)

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_get_all_vehiculos_returns_list(service, mock_vehiculo_repo):
    # Arrange
    mock_vehiculo_repo.get_all.return_value = [
        VehiculoDB(id=1, patente="ABCD12", estado="Disponible"),
        VehiculoDB(id=2, patente="EFGH34", estado="Disponible"),
    ]

    # Act
    result = await service.get_all_vehiculos(limit=50, offset=0)

    # Assert
    assert len(result) == 2
    mock_vehiculo_repo.get_all.assert_called_once_with(50, 0)


@pytest.mark.asyncio
async def test_get_all_vehiculos_returns_empty_list(service, mock_vehiculo_repo):
    # Arrange
    mock_vehiculo_repo.get_all.return_value = []

    # Act
    result = await service.get_all_vehiculos()

    # Assert
    assert result == []


@pytest.mark.asyncio
async def test_update_vehiculo_returns_response_when_found(service, mock_vehiculo_repo):
    # Arrange
    mock_vehiculo_repo.get_by_id.return_value = VehiculoDB(
        id=1, patente="ABCD12", estado="Disponible"
    )
    mock_vehiculo_repo.update.return_value = VehiculoDB(id=1, patente="ABCD12", estado="Ocupado")

    # Act
    result = await service.update_vehiculo(1, VehiculoUpdate(estado="Ocupado"))

    # Assert
    assert result is not None
    assert result.estado == "Ocupado"
    mock_vehiculo_repo.update.assert_called_once()


@pytest.mark.asyncio
async def test_update_vehiculo_returns_none_when_missing(service, mock_vehiculo_repo):
    # Arrange
    mock_vehiculo_repo.get_by_id.return_value = None

    # Act
    result = await service.update_vehiculo(999, VehiculoUpdate(estado="Ocupado"))

    # Assert
    assert result is None
    mock_vehiculo_repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_delete_vehiculo_returns_true_when_found(service, mock_vehiculo_repo):
    # Arrange
    db_obj = VehiculoDB(id=1, patente="ABCD12", estado="Disponible")
    mock_vehiculo_repo.get_by_id.return_value = db_obj

    # Act
    result = await service.delete_vehiculo(1)

    # Assert
    assert result is True
    mock_vehiculo_repo.delete.assert_called_once_with(db_obj)


@pytest.mark.asyncio
async def test_delete_vehiculo_returns_false_when_missing(service, mock_vehiculo_repo):
    # Arrange
    mock_vehiculo_repo.get_by_id.return_value = None

    # Act
    result = await service.delete_vehiculo(999)

    # Assert
    assert result is False
    mock_vehiculo_repo.delete.assert_not_called()
