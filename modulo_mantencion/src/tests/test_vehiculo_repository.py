from unittest.mock import AsyncMock, MagicMock

import pytest

from src.models.vehiculo import VehiculoCreate, VehiculoUpdate
from src.models.vehiculo_db import VehiculoDB
from src.repository.vehiculo_repository import VehiculoRepository


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def repository(mock_session):
    return VehiculoRepository(mock_session)


@pytest.mark.asyncio
async def test_create_adds_commits_and_refreshes(repository, mock_session):
    # Arrange
    data = VehiculoCreate(patente="ABCD12", modelo="Camion")

    # Act
    result = await repository.create(data)

    # Assert
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()
    assert isinstance(result, VehiculoDB)
    assert result.patente == "ABCD12"


@pytest.mark.asyncio
async def test_get_by_id_returns_match(repository, mock_session):
    # Arrange
    expected = VehiculoDB(id=1, patente="ABCD12")
    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = expected
    mock_session.execute.return_value = execute_result

    # Act
    result = await repository.get_by_id(1)

    # Assert
    assert result is expected
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_id_returns_none_when_missing(repository, mock_session):
    # Arrange
    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = execute_result

    # Act
    result = await repository.get_by_id(999)

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_get_all_returns_list(repository, mock_session):
    # Arrange
    expected = [VehiculoDB(id=1, patente="ABCD12"), VehiculoDB(id=2, patente="EFGH34")]
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
async def test_update_sets_fields_and_commits(repository, mock_session):
    # Arrange
    db_obj = VehiculoDB(id=1, patente="ABCD12", estado="Disponible")
    update_data = VehiculoUpdate(estado="Ocupado")

    # Act
    result = await repository.update(db_obj, update_data)

    # Assert
    assert result.estado == "Ocupado"
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(db_obj)


@pytest.mark.asyncio
async def test_delete_calls_session_delete_and_commit(repository, mock_session):
    # Arrange
    db_obj = VehiculoDB(id=1, patente="ABCD12")

    # Act
    await repository.delete(db_obj)

    # Assert
    mock_session.delete.assert_called_once_with(db_obj)
    mock_session.commit.assert_called_once()
