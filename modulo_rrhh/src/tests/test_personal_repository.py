from unittest.mock import AsyncMock, MagicMock

import pytest

from src.models.personal_db import PersonalDB
from src.repository.personal_repository import PersonalRepository


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def repository(mock_session):
    return PersonalRepository(mock_session)


@pytest.mark.asyncio
async def test_save_adds_commits_and_refreshes(repository, mock_session):
    # Arrange
    obj = PersonalDB(nombre="JUAN", apellido1="PEREZ", rut="123", cargo="Chofer", base="Lampa")

    # Act
    result = await repository.save(obj)

    # Assert
    mock_session.add.assert_called_once_with(obj)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(obj)
    assert result is obj


@pytest.mark.asyncio
async def test_find_all_returns_list(repository, mock_session):
    # Arrange
    expected = [
        PersonalDB(id=1, nombre="JUAN", apellido1="PEREZ", rut="123", cargo="Chofer", base="Lampa")
    ]
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = expected
    execute_result = MagicMock()
    execute_result.scalars.return_value = scalars_mock
    mock_session.execute.return_value = execute_result

    # Act
    result = await repository.find_all()

    # Assert
    assert result == expected
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_find_by_id_returns_match(repository, mock_session):
    # Arrange
    expected = PersonalDB(
        id=1, nombre="JUAN", apellido1="PEREZ", rut="123", cargo="Chofer", base="Lampa"
    )
    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = expected
    mock_session.execute.return_value = execute_result

    # Act
    result = await repository.find_by_id(1)

    # Assert
    assert result is expected


@pytest.mark.asyncio
async def test_find_by_id_returns_none_when_missing(repository, mock_session):
    # Arrange
    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = execute_result

    # Act
    result = await repository.find_by_id(999)

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_update_with_data_executes_update_and_commits(repository, mock_session):
    # Arrange
    updated = PersonalDB(
        id=1, nombre="JUAN", apellido1="PEREZ", rut="123", cargo="Mecanico", base="Lampa"
    )
    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = updated
    mock_session.execute.return_value = execute_result

    # Act
    result = await repository.update(1, {"cargo": "Mecanico", "motivo": None})

    # Assert
    assert mock_session.execute.call_count == 2  # update statement + find_by_id refresh
    mock_session.commit.assert_called_once()
    assert result is updated


@pytest.mark.asyncio
async def test_update_with_only_none_values_skips_update_statement(repository, mock_session):
    # Arrange
    existing = PersonalDB(
        id=1, nombre="JUAN", apellido1="PEREZ", rut="123", cargo="Chofer", base="Lampa"
    )
    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = existing
    mock_session.execute.return_value = execute_result

    # Act
    result = await repository.update(1, {"motivo": None})

    # Assert
    mock_session.commit.assert_not_called()
    assert result is existing


@pytest.mark.asyncio
async def test_delete_returns_true_when_row_removed(repository, mock_session):
    # Arrange
    execute_result = MagicMock()
    execute_result.rowcount = 1
    mock_session.execute.return_value = execute_result

    # Act
    result = await repository.delete(1)

    # Assert
    mock_session.commit.assert_called_once()
    assert result is True


@pytest.mark.asyncio
async def test_delete_returns_false_when_no_row_removed(repository, mock_session):
    # Arrange
    execute_result = MagicMock()
    execute_result.rowcount = 0
    mock_session.execute.return_value = execute_result

    # Act
    result = await repository.delete(999)

    # Assert
    assert result is False
