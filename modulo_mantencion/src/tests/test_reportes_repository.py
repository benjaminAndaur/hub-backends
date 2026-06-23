from unittest.mock import AsyncMock, MagicMock

import pytest

from src.models.reportes import ReportesCreate
from src.models.reportes_db import ReportesDB
from src.repository.reportes_repository import ReportesRepository


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def repository(mock_session):
    return ReportesRepository(mock_session)


@pytest.mark.asyncio
async def test_create_adds_commits_and_refreshes(repository, mock_session):
    # Arrange
    data = ReportesCreate(report_id="r1", asset_name="Camion 1")

    # Act
    result = await repository.create(data)

    # Assert
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()
    assert isinstance(result, ReportesDB)
    assert result.report_id == "r1"


@pytest.mark.asyncio
async def test_create_many_adds_all_and_commits(repository, mock_session):
    # Arrange
    data = [ReportesCreate(report_id="r1"), ReportesCreate(report_id="r2")]

    # Act
    result = await repository.create_many(data)

    # Assert
    mock_session.add_all.assert_called_once()
    added_objs = mock_session.add_all.call_args[0][0]
    assert len(added_objs) == 2
    mock_session.commit.assert_called_once()
    assert result == 2


@pytest.mark.asyncio
async def test_get_by_id_returns_match(repository, mock_session):
    # Arrange
    expected = ReportesDB(report_id="r1")
    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = expected
    mock_session.execute.return_value = execute_result

    # Act
    result = await repository.get_by_id("r1")

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
    result = await repository.get_by_id("inexistente")

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_get_all_returns_list(repository, mock_session):
    # Arrange
    expected = [ReportesDB(report_id="r1"), ReportesDB(report_id="r2")]
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
