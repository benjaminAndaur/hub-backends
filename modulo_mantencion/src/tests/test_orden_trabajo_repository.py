from unittest.mock import AsyncMock, MagicMock

import pytest

from src.models.orden_trabajo_db import OrdenTrabajoDB, OrdenTrabajoRepuestoDB
from src.repository.orden_trabajo_repository import OrdenTrabajoRepository


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def repository(mock_session):
    return OrdenTrabajoRepository(mock_session)


@pytest.mark.asyncio
async def test_create_ot_adds_commits_and_refreshes(repository, mock_session):
    # Arrange
    ot = OrdenTrabajoDB(mantencion_id=1, mecanico_id=2)

    # Act
    result = await repository.create_ot(ot)

    # Assert
    mock_session.add.assert_called_once_with(ot)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(ot)
    assert result is ot


@pytest.mark.asyncio
async def test_create_ot_repuesto_adds_commits_and_refreshes(repository, mock_session):
    # Arrange
    repuesto = OrdenTrabajoRepuestoDB(ot_id=1, producto_id=2, cantidad_solicitada=3)

    # Act
    result = await repository.create_ot_repuesto(repuesto)

    # Assert
    mock_session.add.assert_called_once_with(repuesto)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(repuesto)
    assert result is repuesto


@pytest.mark.asyncio
async def test_get_all_ots_returns_list(repository, mock_session):
    # Arrange
    expected = [OrdenTrabajoDB(id=1, mantencion_id=1, mecanico_id=2)]
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = expected
    execute_result = MagicMock()
    execute_result.scalars.return_value = scalars_mock
    mock_session.execute.return_value = execute_result

    # Act
    result = await repository.get_all_ots()

    # Assert
    assert result == expected
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_ot_by_id_returns_match(repository, mock_session):
    # Arrange
    expected = OrdenTrabajoDB(id=1, mantencion_id=1, mecanico_id=2)
    mock_session.get.return_value = expected

    # Act
    result = await repository.get_ot_by_id(1)

    # Assert
    assert result is expected
    mock_session.get.assert_called_once_with(OrdenTrabajoDB, 1)


@pytest.mark.asyncio
async def test_get_ot_by_id_returns_none_when_missing(repository, mock_session):
    # Arrange
    mock_session.get.return_value = None

    # Act
    result = await repository.get_ot_by_id(999)

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_get_repuestos_by_ot_returns_list(repository, mock_session):
    # Arrange
    expected = [OrdenTrabajoRepuestoDB(id=1, ot_id=5, producto_id=10)]
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = expected
    execute_result = MagicMock()
    execute_result.scalars.return_value = scalars_mock
    mock_session.execute.return_value = execute_result

    # Act
    result = await repository.get_repuestos_by_ot(5)

    # Assert
    assert result == expected
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_update_ot_sets_fields_and_commits_when_found(repository, mock_session):
    # Arrange
    ot = OrdenTrabajoDB(id=1, mantencion_id=1, mecanico_id=2, estado="Abierta")
    mock_session.get.return_value = ot

    # Act
    result = await repository.update_ot(1, {"estado": "Cerrada"})

    # Assert
    assert result.estado == "Cerrada"
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(ot)


@pytest.mark.asyncio
async def test_update_ot_ignores_unknown_fields(repository, mock_session):
    # Arrange
    ot = OrdenTrabajoDB(id=1, mantencion_id=1, mecanico_id=2, estado="Abierta")
    mock_session.get.return_value = ot

    # Act
    result = await repository.update_ot(1, {"campo_inexistente": "valor"})

    # Assert
    assert not hasattr(result, "campo_inexistente")
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_ot_returns_none_when_not_found(repository, mock_session):
    # Arrange
    mock_session.get.return_value = None

    # Act
    result = await repository.update_ot(999, {"estado": "Cerrada"})

    # Assert
    assert result is None
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_update_ot_repuesto_sets_fields_and_commits_when_found(repository, mock_session):
    # Arrange
    repuesto = OrdenTrabajoRepuestoDB(id=1, ot_id=5, producto_id=10, estado_devolucion="Ninguna")
    mock_session.get.return_value = repuesto

    # Act
    result = await repository.update_ot_repuesto(1, {"estado_devolucion": "Pendiente"})

    # Assert
    assert result.estado_devolucion == "Pendiente"
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(repuesto)


@pytest.mark.asyncio
async def test_update_ot_repuesto_returns_none_when_not_found(repository, mock_session):
    # Arrange
    mock_session.get.return_value = None

    # Act
    result = await repository.update_ot_repuesto(999, {"estado_devolucion": "Pendiente"})

    # Assert
    assert result is None
    mock_session.commit.assert_not_called()
