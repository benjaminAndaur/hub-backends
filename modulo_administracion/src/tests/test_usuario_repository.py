from unittest.mock import AsyncMock, MagicMock

import pytest
from src.models.usuario_db import UsuarioDB
from src.repository.usuario_repository import UsuarioRepository


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def repository(mock_session):
    return UsuarioRepository(mock_session)


@pytest.mark.asyncio
async def test_create_adds_commits_and_refreshes(repository, mock_session):
    # Arrange
    obj = UsuarioDB(nombre="JUAN PEREZ", email="juan@asdf.cl", password_hash="hashed123")

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
    expected = [
        UsuarioDB(id=1, nombre="JUAN PEREZ", email="juan@asdf.cl", password_hash="hashed123")
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
    expected = UsuarioDB(id=1, nombre="JUAN PEREZ", email="juan@asdf.cl", password_hash="hashed123")
    mock_session.get.return_value = expected

    # Act
    result = await repository.get_by_id(1)

    # Assert
    assert result is expected
    mock_session.get.assert_called_once_with(UsuarioDB, 1)


@pytest.mark.asyncio
async def test_get_by_id_returns_none_when_missing(repository, mock_session):
    # Arrange
    mock_session.get.return_value = None

    # Act
    result = await repository.get_by_id(999)

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_get_by_email_returns_match(repository, mock_session):
    # Arrange
    expected = UsuarioDB(id=1, nombre="JUAN PEREZ", email="juan@asdf.cl", password_hash="hashed123")
    scalars_mock = MagicMock()
    scalars_mock.first.return_value = expected
    execute_result = MagicMock()
    execute_result.scalars.return_value = scalars_mock
    mock_session.execute.return_value = execute_result

    # Act
    result = await repository.get_by_email("juan@asdf.cl")

    # Assert
    assert result is expected
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_email_returns_none_when_missing(repository, mock_session):
    # Arrange
    scalars_mock = MagicMock()
    scalars_mock.first.return_value = None
    execute_result = MagicMock()
    execute_result.scalars.return_value = scalars_mock
    mock_session.execute.return_value = execute_result

    # Act
    result = await repository.get_by_email("nadie@asdf.cl")

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_update_with_existing_user_sets_attrs_and_commits(repository, mock_session):
    # Arrange
    existing = UsuarioDB(
        id=1, nombre="JUAN PEREZ", email="juan@asdf.cl", password_hash="hashed123", estado=True
    )
    mock_session.get.return_value = existing

    # Act
    result = await repository.update(1, {"estado": False})

    # Assert
    assert result is existing
    assert result.estado is False
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(existing)


@pytest.mark.asyncio
async def test_update_ignores_keys_not_present_in_model(repository, mock_session):
    # Arrange
    existing = UsuarioDB(id=1, nombre="JUAN PEREZ", email="juan@asdf.cl", password_hash="hashed123")
    mock_session.get.return_value = existing

    # Act
    result = await repository.update(1, {"campo_inexistente": "valor"})

    # Assert
    assert result is existing
    assert not hasattr(result, "campo_inexistente")
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_returns_none_when_user_missing(repository, mock_session):
    # Arrange
    mock_session.get.return_value = None

    # Act
    result = await repository.update(999, {"estado": False})

    # Assert
    assert result is None
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_delete_returns_true_when_user_removed(repository, mock_session):
    # Arrange
    existing = UsuarioDB(id=1, nombre="JUAN PEREZ", email="juan@asdf.cl", password_hash="hashed123")
    mock_session.get.return_value = existing

    # Act
    result = await repository.delete(1)

    # Assert
    mock_session.delete.assert_called_once_with(existing)
    mock_session.commit.assert_called_once()
    assert result is True


@pytest.mark.asyncio
async def test_delete_returns_false_when_user_missing(repository, mock_session):
    # Arrange
    mock_session.get.return_value = None

    # Act
    result = await repository.delete(999)

    # Assert
    mock_session.delete.assert_not_called()
    assert result is False
