from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from src.models.producto_db import ProductoDB
from src.models.solicitud_db import SolicitudBodegaDB
from src.service.solicitud_service import SolicitudService


@pytest.fixture
def mock_solicitud_repo():
    return AsyncMock()


@pytest.fixture
def mock_producto_repo():
    return AsyncMock()


@pytest.fixture
def service(mock_solicitud_repo, mock_producto_repo):
    return SolicitudService(mock_solicitud_repo, mock_producto_repo)


@pytest.mark.asyncio
async def test_crear_solicitud_creates_with_estado_pendiente(service, mock_solicitud_repo):
    # Arrange
    data = {
        "area_solicitante": "Mantencion",
        "usuario_solicitante": "Juan",
        "detalles_json": [{"producto_id": 1, "cantidad": 2}],
        "comentarios": "Urgente",
    }
    creada = SolicitudBodegaDB(
        id=1,
        area_solicitante="Mantencion",
        usuario_solicitante="Juan",
        estado="Pendiente",
        fecha_solicitud=datetime(2024, 1, 1),
        detalles_json=[{"producto_id": 1, "cantidad": 2}],
        comentarios="Urgente",
    )
    mock_solicitud_repo.create.return_value = creada

    # Act
    result = await service.crear_solicitud(data)

    # Assert
    assert result["estado"] == "Pendiente"
    assert result["area_solicitante"] == "Mantencion"
    mock_solicitud_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_crear_solicitud_uses_default_values_when_missing(service, mock_solicitud_repo):
    # Arrange
    creada = SolicitudBodegaDB(
        id=1,
        area_solicitante="Desconocida",
        usuario_solicitante="Desconocido",
        estado="Pendiente",
        fecha_solicitud=datetime(2024, 1, 1),
        detalles_json=[],
        comentarios="",
    )
    mock_solicitud_repo.create.return_value = creada

    # Act
    result = await service.crear_solicitud({})

    # Assert
    assert result["area_solicitante"] == "Desconocida"
    assert result["usuario_solicitante"] == "Desconocido"


@pytest.mark.asyncio
async def test_obtener_todas_returns_formatted_list(service, mock_solicitud_repo):
    # Arrange
    mock_solicitud_repo.get_all.return_value = [
        SolicitudBodegaDB(
            id=1,
            area_solicitante="Mantencion",
            usuario_solicitante="Juan",
            estado="Pendiente",
            fecha_solicitud=datetime(2024, 1, 1),
            detalles_json=[],
        )
    ]

    # Act
    result = await service.obtener_todas()

    # Assert
    assert len(result) == 1
    assert result[0]["id"] == 1
    mock_solicitud_repo.get_all.assert_called_once()


@pytest.mark.asyncio
async def test_entregar_solicitud_descuenta_stock_y_marca_entregada(
    service, mock_solicitud_repo, mock_producto_repo
):
    # Arrange
    solicitud = SolicitudBodegaDB(
        id=1,
        area_solicitante="Mantencion",
        usuario_solicitante="Juan",
        estado="Pendiente",
        fecha_solicitud=datetime(2024, 1, 1),
        detalles_json=[{"producto_id": 10, "cantidad": 2}],
    )
    mock_solicitud_repo.get_by_id.return_value = solicitud
    producto = ProductoDB(id=10, nombre="Filtro", precio=10.5, stock=5)
    mock_producto_repo.get_by_id.return_value = producto
    actualizada = SolicitudBodegaDB(
        id=1,
        area_solicitante="Mantencion",
        usuario_solicitante="Juan",
        estado="Entregada",
        fecha_solicitud=datetime(2024, 1, 1),
        detalles_json=[{"producto_id": 10, "cantidad": 2}],
    )
    mock_solicitud_repo.update.return_value = actualizada

    # Act
    result = await service.entregar_solicitud(1)

    # Assert
    assert producto.stock == 3
    assert result["estado"] == "Entregada"
    mock_solicitud_repo.update.assert_called_once_with(1, {"estado": "Entregada"})


@pytest.mark.asyncio
async def test_entregar_solicitud_raises_when_no_encontrada(service, mock_solicitud_repo):
    # Arrange
    mock_solicitud_repo.get_by_id.return_value = None

    # Act / Assert
    with pytest.raises(ValueError, match="Solicitud no encontrada"):
        await service.entregar_solicitud(999)


@pytest.mark.asyncio
async def test_entregar_solicitud_raises_when_ya_entregada(service, mock_solicitud_repo):
    # Arrange
    solicitud = SolicitudBodegaDB(
        id=1,
        area_solicitante="Mantencion",
        usuario_solicitante="Juan",
        estado="Entregada",
        fecha_solicitud=datetime(2024, 1, 1),
        detalles_json=[],
    )
    mock_solicitud_repo.get_by_id.return_value = solicitud

    # Act / Assert
    with pytest.raises(ValueError, match="ya ha sido entregada"):
        await service.entregar_solicitud(1)


@pytest.mark.asyncio
async def test_entregar_solicitud_raises_when_producto_no_existe(
    service, mock_solicitud_repo, mock_producto_repo
):
    # Arrange
    solicitud = SolicitudBodegaDB(
        id=1,
        area_solicitante="Mantencion",
        usuario_solicitante="Juan",
        estado="Pendiente",
        fecha_solicitud=datetime(2024, 1, 1),
        detalles_json=[{"producto_id": 99, "cantidad": 2}],
    )
    mock_solicitud_repo.get_by_id.return_value = solicitud
    mock_producto_repo.get_by_id.return_value = None

    # Act / Assert
    with pytest.raises(ValueError, match="no existe"):
        await service.entregar_solicitud(1)


@pytest.mark.asyncio
async def test_entregar_solicitud_raises_when_stock_insuficiente(
    service, mock_solicitud_repo, mock_producto_repo
):
    # Arrange
    solicitud = SolicitudBodegaDB(
        id=1,
        area_solicitante="Mantencion",
        usuario_solicitante="Juan",
        estado="Pendiente",
        fecha_solicitud=datetime(2024, 1, 1),
        detalles_json=[{"producto_id": 10, "cantidad": 5}],
    )
    mock_solicitud_repo.get_by_id.return_value = solicitud
    producto = ProductoDB(id=10, nombre="Filtro", precio=10.5, stock=1)
    mock_producto_repo.get_by_id.return_value = producto

    # Act / Assert
    with pytest.raises(ValueError, match="Stock insuficiente"):
        await service.entregar_solicitud(1)


@pytest.mark.asyncio
async def test_rechazar_solicitud_marca_rechazada(service, mock_solicitud_repo):
    # Arrange
    solicitud = SolicitudBodegaDB(
        id=1,
        area_solicitante="Mantencion",
        usuario_solicitante="Juan",
        estado="Pendiente",
        fecha_solicitud=datetime(2024, 1, 1),
        detalles_json=[],
    )
    mock_solicitud_repo.get_by_id.return_value = solicitud
    actualizada = SolicitudBodegaDB(
        id=1,
        area_solicitante="Mantencion",
        usuario_solicitante="Juan",
        estado="Rechazada",
        fecha_solicitud=datetime(2024, 1, 1),
        detalles_json=[],
    )
    mock_solicitud_repo.update.return_value = actualizada

    # Act
    result = await service.rechazar_solicitud(1)

    # Assert
    assert result["estado"] == "Rechazada"
    mock_solicitud_repo.update.assert_called_once_with(1, {"estado": "Rechazada"})


@pytest.mark.asyncio
async def test_rechazar_solicitud_raises_when_no_encontrada(service, mock_solicitud_repo):
    # Arrange
    mock_solicitud_repo.get_by_id.return_value = None

    # Act / Assert
    with pytest.raises(ValueError, match="Solicitud no encontrada"):
        await service.rechazar_solicitud(999)


@pytest.mark.asyncio
async def test_rechazar_solicitud_raises_when_ya_entregada(service, mock_solicitud_repo):
    # Arrange
    solicitud = SolicitudBodegaDB(
        id=1,
        area_solicitante="Mantencion",
        usuario_solicitante="Juan",
        estado="Entregada",
        fecha_solicitud=datetime(2024, 1, 1),
        detalles_json=[],
    )
    mock_solicitud_repo.get_by_id.return_value = solicitud

    # Act / Assert
    with pytest.raises(ValueError, match="ya entregada"):
        await service.rechazar_solicitud(1)
