from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.models.solicitud_db import SolicitudBodegaDB
from src.repository.solicitud_repository import SolicitudRepository


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def repository(mock_session):
    return SolicitudRepository(mock_session)


@pytest.mark.asyncio
async def test_create_adds_commits_and_refreshes(repository, mock_session):
    # Arrange
    obj = SolicitudBodegaDB(
        area_solicitante="Mantencion",
        usuario_solicitante="Juan",
        estado="Pendiente",
        detalles_json=[{"producto_id": 1, "cantidad": 2}],
    )

    # Act
    result = await repository.create(obj)

    # Assert
    mock_session.add.assert_called_once_with(obj)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(obj)
    assert result is obj


@pytest.mark.asyncio
async def test_get_all_returns_list_ordered_by_fecha(repository, mock_session):
    # Arrange
    expected = [
        SolicitudBodegaDB(
            id=1,
            area_solicitante="Mantencion",
            usuario_solicitante="Juan",
            estado="Pendiente",
            fecha_solicitud=datetime(2024, 1, 1),
            detalles_json=[],
        )
    ]
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = expected
    execute_result = MagicMock()
    execute_result.scalars.return_value = scalars_mock
    mock_session.execute.return_value = execute_result

    # Act
    result = await repository.get_all()

    # Assert
    assert result == expected
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_id_returns_match(repository, mock_session):
    # Arrange
    expected = SolicitudBodegaDB(
        id=1,
        area_solicitante="Mantencion",
        usuario_solicitante="Juan",
        estado="Pendiente",
        detalles_json=[],
    )
    mock_session.get.return_value = expected

    # Act
    result = await repository.get_by_id(1)

    # Assert
    assert result is expected
    mock_session.get.assert_called_once_with(SolicitudBodegaDB, 1)


@pytest.mark.asyncio
async def test_get_by_id_returns_none_when_missing(repository, mock_session):
    # Arrange
    mock_session.get.return_value = None

    # Act
    result = await repository.get_by_id(999)

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_update_with_existing_solicitud_updates_fields_and_commits(repository, mock_session):
    # Arrange
    existing = SolicitudBodegaDB(
        id=1,
        area_solicitante="Mantencion",
        usuario_solicitante="Juan",
        estado="Pendiente",
        detalles_json=[],
    )
    mock_session.get.return_value = existing

    # Act
    result = await repository.update(1, {"estado": "Entregada"})

    # Assert
    assert result.estado == "Entregada"
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(existing)


@pytest.mark.asyncio
async def test_update_with_missing_solicitud_returns_none(repository, mock_session):
    # Arrange
    mock_session.get.return_value = None

    # Act
    result = await repository.update(999, {"estado": "Entregada"})

    # Assert
    assert result is None
    mock_session.commit.assert_not_called()
