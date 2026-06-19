import pytest
from unittest.mock import AsyncMock, MagicMock
from src.repository.producto_repository import ProductoRepository
from src.models.producto_db import ProductoDB


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def repository(mock_session):
    return ProductoRepository(mock_session)


@pytest.mark.asyncio
async def test_create_adds_commits_and_refreshes(repository, mock_session):
    # Arrange
    obj = ProductoDB(nombre="Filtro de aceite", precio=10.5, stock=5)

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
    expected = [ProductoDB(id=1, nombre="Filtro de aceite", precio=10.5, stock=5)]
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
    expected = ProductoDB(id=1, nombre="Filtro de aceite", precio=10.5, stock=5)
    mock_session.get.return_value = expected

    # Act
    result = await repository.get_by_id(1)

    # Assert
    assert result is expected
    mock_session.get.assert_called_once_with(ProductoDB, 1)


@pytest.mark.asyncio
async def test_get_by_id_returns_none_when_missing(repository, mock_session):
    # Arrange
    mock_session.get.return_value = None

    # Act
    result = await repository.get_by_id(999)

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_update_with_existing_producto_updates_fields_and_commits(repository, mock_session):
    # Arrange
    existing = ProductoDB(id=1, nombre="Filtro de aceite", precio=10.5, stock=5)
    mock_session.get.return_value = existing

    # Act
    result = await repository.update(1, {"stock": 8})

    # Assert
    assert result.stock == 8
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(existing)


@pytest.mark.asyncio
async def test_update_with_missing_producto_returns_none(repository, mock_session):
    # Arrange
    mock_session.get.return_value = None

    # Act
    result = await repository.update(999, {"stock": 8})

    # Assert
    assert result is None
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_update_ignores_unknown_fields(repository, mock_session):
    # Arrange
    existing = ProductoDB(id=1, nombre="Filtro de aceite", precio=10.5, stock=5)
    mock_session.get.return_value = existing

    # Act
    result = await repository.update(1, {"campo_inexistente": "valor"})

    # Assert
    assert not hasattr(result, "campo_inexistente")
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_returns_true_when_producto_removed(repository, mock_session):
    # Arrange
    existing = ProductoDB(id=1, nombre="Filtro de aceite", precio=10.5, stock=5)
    mock_session.get.return_value = existing

    # Act
    result = await repository.delete(1)

    # Assert
    mock_session.delete.assert_called_once_with(existing)
    mock_session.commit.assert_called_once()
    assert result is True


@pytest.mark.asyncio
async def test_delete_returns_false_when_producto_missing(repository, mock_session):
    # Arrange
    mock_session.get.return_value = None

    # Act
    result = await repository.delete(999)

    # Assert
    mock_session.delete.assert_not_called()
    assert result is False
