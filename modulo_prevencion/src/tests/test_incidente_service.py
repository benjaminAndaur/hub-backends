import pytest
from datetime import datetime
from unittest.mock import AsyncMock
from src.service.incidente_service import IncidenteService
from src.models.incidente_db import IncidenteDB


@pytest.fixture
def mock_incidente_repo():
    return AsyncMock()


@pytest.fixture
def service(mock_incidente_repo):
    return IncidenteService(mock_incidente_repo)


def _with_id_and_fecha(obj):
    obj.id = 1
    obj.fecha = datetime(2024, 1, 1)
    return obj


@pytest.mark.asyncio
async def test_crear_incidente_returns_response_dto(service, mock_incidente_repo):
    # Arrange
    data = {"titulo": "Caida de altura", "descripcion": "Trabajador resbalo", "nivel_gravedad": "Alta"}
    mock_incidente_repo.create = AsyncMock(side_effect=_with_id_and_fecha)

    # Act
    result = await service.crear_incidente(data)

    # Assert
    assert result.id == 1
    assert result.titulo == "Caida de altura"
    assert result.nivel_gravedad == "Alta"
    mock_incidente_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_obtener_todos_returns_list(service, mock_incidente_repo):
    # Arrange
    mock_incidente_repo.get_all.return_value = [
        IncidenteDB(id=1, titulo="Caida de altura", nivel_gravedad="Alta", fecha=datetime(2024, 1, 1))
    ]

    # Act
    results = await service.obtener_todos()

    # Assert
    assert len(results) == 1
    assert results[0].titulo == "Caida de altura"
    mock_incidente_repo.get_all.assert_called_once()


@pytest.mark.asyncio
async def test_obtener_todos_returns_empty_list_when_no_data(service, mock_incidente_repo):
    # Arrange
    mock_incidente_repo.get_all.return_value = []

    # Act
    results = await service.obtener_todos()

    # Assert
    assert results == []


@pytest.mark.asyncio
async def test_obtener_por_id_returns_dto_when_found(service, mock_incidente_repo):
    # Arrange
    mock_incidente_repo.get_by_id.return_value = IncidenteDB(
        id=1, titulo="Caida de altura", nivel_gravedad="Alta", fecha=datetime(2024, 1, 1)
    )

    # Act
    result = await service.obtener_por_id(1)

    # Assert
    assert result is not None
    assert result.id == 1
    mock_incidente_repo.get_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_obtener_por_id_returns_none_when_missing(service, mock_incidente_repo):
    # Arrange
    mock_incidente_repo.get_by_id.return_value = None

    # Act
    result = await service.obtener_por_id(999)

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_actualizar_incidente_returns_dto_when_found(service, mock_incidente_repo):
    # Arrange
    mock_incidente_repo.update.return_value = IncidenteDB(
        id=1, titulo="Caida de altura", nivel_gravedad="Media", fecha=datetime(2024, 1, 1)
    )

    # Act
    result = await service.actualizar_incidente(1, {"nivel_gravedad": "Media"})

    # Assert
    assert result.nivel_gravedad == "Media"
    mock_incidente_repo.update.assert_called_once_with(1, {"nivel_gravedad": "Media"})


@pytest.mark.asyncio
async def test_actualizar_incidente_returns_none_when_missing(service, mock_incidente_repo):
    # Arrange
    mock_incidente_repo.update.return_value = None

    # Act
    result = await service.actualizar_incidente(999, {"nivel_gravedad": "Media"})

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_eliminar_incidente_delegates_to_repository(service, mock_incidente_repo):
    # Arrange
    mock_incidente_repo.delete.return_value = True

    # Act
    result = await service.eliminar_incidente(1)

    # Assert
    assert result is True
    mock_incidente_repo.delete.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_eliminar_incidente_returns_false_when_not_found(service, mock_incidente_repo):
    # Arrange
    mock_incidente_repo.delete.return_value = False

    # Act
    result = await service.eliminar_incidente(999)

    # Assert
    assert result is False
