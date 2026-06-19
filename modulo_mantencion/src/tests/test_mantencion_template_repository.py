import pytest
from unittest.mock import AsyncMock, MagicMock
from src.repository.mantencion_template_repository import MantencionTemplateRepository
from src.models.mantencion_template_db import MantencionTemplateDB


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def repository(mock_session):
    return MantencionTemplateRepository(mock_session)


@pytest.mark.asyncio
async def test_create_adds_commits_and_refreshes(repository, mock_session):
    # Arrange
    template = MantencionTemplateDB(nombre="Template A", descripcion="Desc")

    # Act
    result = await repository.create(template)

    # Assert
    mock_session.add.assert_called_once_with(template)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(template)
    assert result is template


@pytest.mark.asyncio
async def test_get_all_returns_list(repository, mock_session):
    # Arrange
    expected = [MantencionTemplateDB(id=1, nombre="Template A")]
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
    expected = MantencionTemplateDB(id=1, nombre="Template A")
    mock_session.get.return_value = expected

    # Act
    result = await repository.get_by_id(1)

    # Assert
    assert result is expected
    mock_session.get.assert_called_once_with(MantencionTemplateDB, 1)


@pytest.mark.asyncio
async def test_get_by_id_returns_none_when_missing(repository, mock_session):
    # Arrange
    mock_session.get.return_value = None

    # Act
    result = await repository.get_by_id(999)

    # Assert
    assert result is None
