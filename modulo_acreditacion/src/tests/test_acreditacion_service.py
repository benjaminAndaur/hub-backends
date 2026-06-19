import pytest
from unittest.mock import AsyncMock
from src.service.acreditacion_service import AcreditacionService
from src.models.acreditacion_db import Cliente, Requerimiento, Acreditacion, TipoSujeto


@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def service(mock_repository):
    return AcreditacionService(mock_repository)


@pytest.mark.asyncio
async def test_create_cliente_delegates_to_repository(service, mock_repository):
    # Arrange
    data = {"nombre": "Cliente Uno", "rut": "76.123.456-7", "contacto": "contacto@cliente.cl"}
    expected = Cliente(id=1, nombre="Cliente Uno", rut="76.123.456-7", contacto="contacto@cliente.cl")
    mock_repository.create_cliente.return_value = expected

    # Act
    result = await service.create_cliente(data)

    # Assert
    assert result is expected
    mock_repository.create_cliente.assert_called_once_with(data)


@pytest.mark.asyncio
async def test_get_all_clientes_delegates_to_repository(service, mock_repository):
    # Arrange
    expected = [Cliente(id=1, nombre="Cliente Uno", rut="76.123.456-7")]
    mock_repository.get_all_clientes.return_value = expected

    # Act
    result = await service.get_all_clientes()

    # Assert
    assert result == expected
    mock_repository.get_all_clientes.assert_called_once()


@pytest.mark.asyncio
async def test_create_requerimiento_delegates_to_repository(service, mock_repository):
    # Arrange
    data = {"cliente_id": 1, "nombre": "Requerimiento Uno", "tipo_sujeto": TipoSujeto.PERSONAL}
    expected = Requerimiento(id=1, cliente_id=1, nombre="Requerimiento Uno", tipo_sujeto=TipoSujeto.PERSONAL)
    mock_repository.create_requerimiento.return_value = expected

    # Act
    result = await service.create_requerimiento(data)

    # Assert
    assert result is expected
    mock_repository.create_requerimiento.assert_called_once_with(data)


@pytest.mark.asyncio
async def test_get_requerimientos_by_cliente_delegates_to_repository(service, mock_repository):
    # Arrange
    expected = [Requerimiento(id=1, cliente_id=1, nombre="Requerimiento Uno", tipo_sujeto=TipoSujeto.PERSONAL)]
    mock_repository.get_requerimientos_by_cliente.return_value = expected

    # Act
    result = await service.get_requerimientos_by_cliente(1)

    # Assert
    assert result == expected
    mock_repository.get_requerimientos_by_cliente.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_create_acreditacion_delegates_to_repository(service, mock_repository):
    # Arrange
    data = {
        "requerimiento_id": 1,
        "sujeto_id": 10,
        "fecha_emision": "2026-01-01",
        "fecha_vencimiento": "2027-01-01",
    }
    expected = Acreditacion(id=1, requerimiento_id=1, sujeto_id=10)
    mock_repository.create_acreditacion.return_value = expected

    # Act
    result = await service.create_acreditacion(data)

    # Assert
    assert result is expected
    mock_repository.create_acreditacion.assert_called_once_with(data)


@pytest.mark.asyncio
async def test_get_acreditaciones_by_sujeto_delegates_to_repository(service, mock_repository):
    # Arrange
    expected = [Acreditacion(id=1, requerimiento_id=1, sujeto_id=10)]
    mock_repository.get_acreditaciones_by_sujeto.return_value = expected

    # Act
    result = await service.get_acreditaciones_by_sujeto(10, TipoSujeto.PERSONAL)

    # Assert
    assert result == expected
    mock_repository.get_acreditaciones_by_sujeto.assert_called_once_with(10, TipoSujeto.PERSONAL)


@pytest.mark.asyncio
async def test_get_acreditaciones_without_filters_delegates_with_none(service, mock_repository):
    # Arrange
    expected = [Acreditacion(id=1, requerimiento_id=1, sujeto_id=10)]
    mock_repository.get_acreditaciones.return_value = expected

    # Act
    result = await service.get_acreditaciones()

    # Assert
    assert result == expected
    mock_repository.get_acreditaciones.assert_called_once_with(None, None)


@pytest.mark.asyncio
async def test_get_acreditaciones_with_sujeto_id_delegates_correctly(service, mock_repository):
    # Arrange
    expected = [Acreditacion(id=1, requerimiento_id=1, sujeto_id=10)]
    mock_repository.get_acreditaciones.return_value = expected

    # Act
    result = await service.get_acreditaciones(sujeto_id=10)

    # Assert
    assert result == expected
    mock_repository.get_acreditaciones.assert_called_once_with(10, None)


@pytest.mark.asyncio
async def test_get_acreditaciones_with_tipo_sujeto_delegates_correctly(service, mock_repository):
    # Arrange
    expected = [Acreditacion(id=1, requerimiento_id=1, sujeto_id=10)]
    mock_repository.get_acreditaciones.return_value = expected

    # Act
    result = await service.get_acreditaciones(tipo_sujeto=TipoSujeto.VEHICULO)

    # Assert
    assert result == expected
    mock_repository.get_acreditaciones.assert_called_once_with(None, TipoSujeto.VEHICULO)


@pytest.mark.asyncio
async def test_get_acreditaciones_with_both_filters_delegates_correctly(service, mock_repository):
    # Arrange
    expected = [Acreditacion(id=1, requerimiento_id=1, sujeto_id=10)]
    mock_repository.get_acreditaciones.return_value = expected

    # Act
    result = await service.get_acreditaciones(sujeto_id=10, tipo_sujeto=TipoSujeto.VEHICULO)

    # Assert
    assert result == expected
    mock_repository.get_acreditaciones.assert_called_once_with(10, TipoSujeto.VEHICULO)
