from datetime import date
from unittest.mock import AsyncMock

import pytest

from src.models.ingreso_db import IngresoBodegaDB
from src.service.ingreso_service import IngresoService


@pytest.fixture
def mock_ingreso_repo():
    return AsyncMock()


@pytest.fixture
def service(mock_ingreso_repo):
    return IngresoService(mock_ingreso_repo)


def _with_id(obj):
    obj.id = 1
    return obj


@pytest.mark.asyncio
async def test_crear_ingreso_returns_response_dto(service, mock_ingreso_repo):
    # Arrange
    data = {
        "usuario_entrega": "JUAN",
        "usuario_recepcion": "PEDRO",
        "tipo_doc_origen": "OC",
        "n_documento": "123",
        "fecha_requerimiento": date(2024, 1, 1),
        "descripcion": "Repuestos varios",
    }
    mock_ingreso_repo.create = AsyncMock(side_effect=_with_id)

    # Act
    result = await service.crear_ingreso(data)

    # Assert
    assert result.id == 1
    assert result.usuario_entrega == "JUAN"
    assert result.n_documento == "123"
    mock_ingreso_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_obtener_todos_returns_list(service, mock_ingreso_repo):
    # Arrange
    mock_ingreso_repo.get_all.return_value = [
        IngresoBodegaDB(id=1, usuario_entrega="JUAN", n_documento="123")
    ]

    # Act
    results = await service.obtener_todos()

    # Assert
    assert len(results) == 1
    assert results[0].usuario_entrega == "JUAN"
    mock_ingreso_repo.get_all.assert_called_once()


@pytest.mark.asyncio
async def test_obtener_todos_returns_empty_list_when_no_data(service, mock_ingreso_repo):
    # Arrange
    mock_ingreso_repo.get_all.return_value = []

    # Act
    results = await service.obtener_todos()

    # Assert
    assert results == []
