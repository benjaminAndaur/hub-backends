import pytest
from datetime import date
from unittest.mock import AsyncMock, MagicMock
from src.repository.acreditacion_repository import AcreditacionRepository
from src.models.acreditacion_db import Cliente, Requerimiento, Acreditacion, TipoSujeto


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def repository(mock_session):
    return AcreditacionRepository(mock_session)


# --- Cliente Repository ---

@pytest.mark.asyncio
async def test_create_cliente_adds_commits_and_refreshes(repository, mock_session):
    # Arrange
    data = {"nombre": "Cliente Uno", "rut": "76.123.456-7", "contacto": "contacto@cliente.cl"}

    # Act
    result = await repository.create_cliente(data)

    # Assert
    mock_session.add.assert_called_once()
    added_obj = mock_session.add.call_args[0][0]
    assert isinstance(added_obj, Cliente)
    assert added_obj.nombre == "Cliente Uno"
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(added_obj)
    assert result is added_obj


@pytest.mark.asyncio
async def test_get_all_clientes_returns_list(repository, mock_session):
    # Arrange
    expected = [Cliente(id=1, nombre="Cliente Uno", rut="76.123.456-7")]
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = expected
    execute_result = MagicMock()
    execute_result.scalars.return_value = scalars_mock
    mock_session.execute.return_value = execute_result

    # Act
    result = await repository.get_all_clientes()

    # Assert
    assert result == expected
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_cliente_by_id_returns_match(repository, mock_session):
    # Arrange
    expected = Cliente(id=1, nombre="Cliente Uno", rut="76.123.456-7")
    mock_session.get.return_value = expected

    # Act
    result = await repository.get_cliente_by_id(1)

    # Assert
    assert result is expected
    mock_session.get.assert_called_once_with(Cliente, 1)


@pytest.mark.asyncio
async def test_get_cliente_by_id_returns_none_when_missing(repository, mock_session):
    # Arrange
    mock_session.get.return_value = None

    # Act
    result = await repository.get_cliente_by_id(999)

    # Assert
    assert result is None


# --- Requerimiento Repository ---

@pytest.mark.asyncio
async def test_create_requerimiento_adds_commits_and_refreshes(repository, mock_session):
    # Arrange
    data = {"cliente_id": 1, "nombre": "Requerimiento Uno", "tipo_sujeto": TipoSujeto.PERSONAL}

    # Act
    result = await repository.create_requerimiento(data)

    # Assert
    mock_session.add.assert_called_once()
    added_obj = mock_session.add.call_args[0][0]
    assert isinstance(added_obj, Requerimiento)
    assert added_obj.cliente_id == 1
    assert added_obj.tipo_sujeto == TipoSujeto.PERSONAL
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(added_obj)
    assert result is added_obj


@pytest.mark.asyncio
async def test_get_requerimientos_by_cliente_returns_list(repository, mock_session):
    # Arrange
    expected = [Requerimiento(id=1, cliente_id=1, nombre="Requerimiento Uno", tipo_sujeto=TipoSujeto.PERSONAL)]
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = expected
    execute_result = MagicMock()
    execute_result.scalars.return_value = scalars_mock
    mock_session.execute.return_value = execute_result

    # Act
    result = await repository.get_requerimientos_by_cliente(1)

    # Assert
    assert result == expected
    mock_session.execute.assert_called_once()


# --- Acreditacion Repository ---

@pytest.mark.asyncio
async def test_create_acreditacion_converts_date_strings_and_persists(repository, mock_session):
    # Arrange
    data = {
        "requerimiento_id": 1,
        "sujeto_id": 10,
        "fecha_emision": "2026-01-01",
        "fecha_vencimiento": "2027-01-01",
    }

    # Act
    result = await repository.create_acreditacion(data)

    # Assert
    mock_session.add.assert_called_once()
    added_obj = mock_session.add.call_args[0][0]
    assert isinstance(added_obj, Acreditacion)
    assert added_obj.fecha_emision == date(2026, 1, 1)
    assert added_obj.fecha_vencimiento == date(2027, 1, 1)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(added_obj)
    assert result is added_obj


@pytest.mark.asyncio
async def test_create_acreditacion_without_date_fields_persists_normally(repository, mock_session):
    # Arrange
    data = {"requerimiento_id": 1, "sujeto_id": 10}

    # Act
    result = await repository.create_acreditacion(data)

    # Assert
    added_obj = mock_session.add.call_args[0][0]
    assert added_obj.fecha_emision is None
    assert added_obj.fecha_vencimiento is None
    assert result is added_obj


@pytest.mark.asyncio
async def test_create_acreditacion_with_empty_date_strings_skips_conversion(repository, mock_session):
    # Arrange
    data = {"requerimiento_id": 1, "sujeto_id": 10, "fecha_emision": "", "fecha_vencimiento": ""}

    # Act
    result = await repository.create_acreditacion(data)

    # Assert
    added_obj = mock_session.add.call_args[0][0]
    assert added_obj.fecha_emision == ""
    assert added_obj.fecha_vencimiento == ""
    assert result is added_obj


@pytest.mark.asyncio
async def test_create_acreditacion_with_date_objects_skips_conversion(repository, mock_session):
    # Arrange
    data = {
        "requerimiento_id": 1,
        "sujeto_id": 10,
        "fecha_emision": date(2026, 1, 1),
        "fecha_vencimiento": date(2027, 1, 1),
    }

    # Act
    result = await repository.create_acreditacion(data)

    # Assert
    added_obj = mock_session.add.call_args[0][0]
    assert added_obj.fecha_emision == date(2026, 1, 1)
    assert added_obj.fecha_vencimiento == date(2027, 1, 1)
    assert result is added_obj


@pytest.mark.asyncio
async def test_get_acreditaciones_by_sujeto_returns_list(repository, mock_session):
    # Arrange
    expected = [Acreditacion(id=1, requerimiento_id=1, sujeto_id=10)]
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = expected
    execute_result = MagicMock()
    execute_result.scalars.return_value = scalars_mock
    mock_session.execute.return_value = execute_result

    # Act
    result = await repository.get_acreditaciones_by_sujeto(10, TipoSujeto.PERSONAL)

    # Assert
    assert result == expected
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_acreditaciones_without_filters_returns_list(repository, mock_session):
    # Arrange
    expected = [Acreditacion(id=1, requerimiento_id=1, sujeto_id=10)]
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = expected
    execute_result = MagicMock()
    execute_result.scalars.return_value = scalars_mock
    mock_session.execute.return_value = execute_result

    # Act
    result = await repository.get_acreditaciones()

    # Assert
    assert result == expected
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_acreditaciones_with_sujeto_id_filters_query(repository, mock_session):
    # Arrange
    expected = [Acreditacion(id=1, requerimiento_id=1, sujeto_id=10)]
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = expected
    execute_result = MagicMock()
    execute_result.scalars.return_value = scalars_mock
    mock_session.execute.return_value = execute_result

    # Act
    result = await repository.get_acreditaciones(sujeto_id=10)

    # Assert
    assert result == expected
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_acreditaciones_with_tipo_sujeto_filters_query(repository, mock_session):
    # Arrange
    expected = [Acreditacion(id=1, requerimiento_id=1, sujeto_id=10)]
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = expected
    execute_result = MagicMock()
    execute_result.scalars.return_value = scalars_mock
    mock_session.execute.return_value = execute_result

    # Act
    result = await repository.get_acreditaciones(tipo_sujeto=TipoSujeto.VEHICULO)

    # Assert
    assert result == expected
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_acreditaciones_with_both_filters_returns_list(repository, mock_session):
    # Arrange
    expected = [Acreditacion(id=1, requerimiento_id=1, sujeto_id=10)]
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = expected
    execute_result = MagicMock()
    execute_result.scalars.return_value = scalars_mock
    mock_session.execute.return_value = execute_result

    # Act
    result = await repository.get_acreditaciones(sujeto_id=10, tipo_sujeto=TipoSujeto.VEHICULO)

    # Assert
    assert result == expected
    mock_session.execute.assert_called_once()
