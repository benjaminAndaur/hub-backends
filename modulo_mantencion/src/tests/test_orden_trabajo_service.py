from unittest.mock import AsyncMock

import pytest

from src.models.orden_trabajo_db import OrdenTrabajoDB, OrdenTrabajoRepuestoDB
from src.service.orden_trabajo_service import OrdenTrabajoService


@pytest.fixture
def mock_ot_repo():
    return AsyncMock()


@pytest.fixture
def service(mock_ot_repo):
    return OrdenTrabajoService(mock_ot_repo)


@pytest.mark.asyncio
async def test_crear_ot_creates_and_returns_summary(service, mock_ot_repo):
    # Arrange
    data = {"mantencion_id": 1, "mecanico_id": 2}
    mock_ot_repo.create_ot.return_value = OrdenTrabajoDB(
        id=1, mantencion_id=1, mecanico_id=2, estado="Abierta"
    )

    # Act
    result = await service.crear_ot(data)

    # Assert
    assert result == {"id": 1, "mantencion_id": 1, "mecanico_id": 2, "estado": "Abierta"}
    mock_ot_repo.create_ot.assert_called_once()
    created_arg = mock_ot_repo.create_ot.call_args[0][0]
    assert created_arg.mantencion_id == 1
    assert created_arg.mecanico_id == 2


@pytest.mark.asyncio
async def test_agregar_repuesto_ot_creates_and_returns_summary(service, mock_ot_repo):
    # Arrange
    mock_ot_repo.create_ot_repuesto.return_value = OrdenTrabajoRepuestoDB(
        id=1, ot_id=5, producto_id=10, cantidad_solicitada=3
    )

    # Act
    result = await service.agregar_repuesto_ot(5, 10, 3)

    # Assert
    assert result == {"id": 1, "ot_id": 5, "producto_id": 10, "cantidad_solicitada": 3}
    mock_ot_repo.create_ot_repuesto.assert_called_once()
    created_arg = mock_ot_repo.create_ot_repuesto.call_args[0][0]
    assert created_arg.ot_id == 5
    assert created_arg.producto_id == 10
    assert created_arg.cantidad_solicitada == 3


@pytest.mark.asyncio
async def test_solicitar_devolucion_repuesto_returns_summary_when_found(service, mock_ot_repo):
    # Arrange
    mock_ot_repo.update_ot_repuesto.return_value = OrdenTrabajoRepuestoDB(
        id=1, ot_id=5, producto_id=10, estado_devolucion="Pendiente"
    )

    # Act
    result = await service.solicitar_devolucion_repuesto(1, 2)

    # Assert
    assert result == {"id": 1, "estado_devolucion": "Pendiente"}
    mock_ot_repo.update_ot_repuesto.assert_called_once_with(
        1, {"cantidad_devuelta": 2, "estado_devolucion": "Pendiente"}
    )


@pytest.mark.asyncio
async def test_solicitar_devolucion_repuesto_returns_error_when_not_found(service, mock_ot_repo):
    # Arrange
    mock_ot_repo.update_ot_repuesto.return_value = None

    # Act
    result = await service.solicitar_devolucion_repuesto(999, 2)

    # Assert
    assert result == {"error": "Repuesto en OT no encontrado"}
