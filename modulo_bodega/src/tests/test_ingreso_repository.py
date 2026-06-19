import pytest
from unittest.mock import AsyncMock, MagicMock
from src.repository.ingreso_repository import IngresoRepository
from src.models.ingreso_db import IngresoBodegaDB


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def repository(mock_session):
    return IngresoRepository(mock_session)


@pytest.mark.asyncio
async def test_create_adds_commits_and_refreshes(repository, mock_session):
    # Arrange
    obj = IngresoBodegaDB(usuario_entrega="JUAN", usuario_recepcion="PEDRO", n_documento="123")

    # Act
    result = await repository.create(obj)

    # Assert
    mock_session.add.assert_called_once_with(obj)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(obj)
    assert result is obj


@pytest.mark.asyncio
async def test_get_all_returns_list(repository, mock_session):
    # Arrange
    expected = [IngresoBodegaDB(id=1, usuario_entrega="JUAN", n_documento="123")]
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
    expected = IngresoBodegaDB(id=1, usuario_entrega="JUAN", n_documento="123")
    mock_session.get.return_value = expected

    # Act
    result = await repository.get_by_id(1)

    # Assert
    assert result is expected
    mock_session.get.assert_called_once_with(IngresoBodegaDB, 1)


@pytest.mark.asyncio
async def test_get_by_id_returns_none_when_missing(repository, mock_session):
    # Arrange
    mock_session.get.return_value = None

    # Act
    result = await repository.get_by_id(999)

    # Assert
    assert result is None
