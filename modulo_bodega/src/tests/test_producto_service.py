from unittest.mock import AsyncMock

import pytest

from src.models.producto_db import ProductoDB
from src.service.producto_service import ProductoService


@pytest.fixture
def mock_producto_repo():
    return AsyncMock()


@pytest.fixture
def service(mock_producto_repo):
    return ProductoService(mock_producto_repo)


def _with_id(obj):
    obj.id = 1
    return obj


@pytest.mark.asyncio
async def test_crear_producto_returns_response_dto(service, mock_producto_repo):
    # Arrange
    data = {
        "nombre": "Filtro de aceite",
        "descripcion": "Filtro estandar",
        "precio": 10.5,
        "stock": 5,
    }
    mock_producto_repo.create = AsyncMock(side_effect=_with_id)

    # Act
    result = await service.crear_producto(data)

    # Assert
    assert result.id == 1
    assert result.nombre == "Filtro de aceite"
    assert result.stock == 5
    mock_producto_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_obtener_todos_returns_list(service, mock_producto_repo):
    # Arrange
    mock_producto_repo.get_all.return_value = [
        ProductoDB(id=1, nombre="Filtro de aceite", precio=10.5, stock=5)
    ]

    # Act
    results = await service.obtener_todos()

    # Assert
    assert len(results) == 1
    assert results[0].nombre == "Filtro de aceite"
    mock_producto_repo.get_all.assert_called_once()


@pytest.mark.asyncio
async def test_obtener_por_id_returns_dto_when_found(service, mock_producto_repo):
    # Arrange
    mock_producto_repo.get_by_id.return_value = ProductoDB(
        id=1, nombre="Filtro", precio=10.5, stock=5
    )

    # Act
    result = await service.obtener_por_id(1)

    # Assert
    assert result is not None
    assert result.id == 1
    mock_producto_repo.get_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_obtener_por_id_returns_none_when_missing(service, mock_producto_repo):
    # Arrange
    mock_producto_repo.get_by_id.return_value = None

    # Act
    result = await service.obtener_por_id(999)

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_actualizar_producto_returns_dto_when_found(service, mock_producto_repo):
    # Arrange
    mock_producto_repo.update.return_value = ProductoDB(id=1, nombre="Filtro", precio=10.5, stock=8)

    # Act
    result = await service.actualizar_producto(1, {"stock": 8})

    # Assert
    assert result.stock == 8
    mock_producto_repo.update.assert_called_once_with(1, {"stock": 8})


@pytest.mark.asyncio
async def test_actualizar_producto_returns_none_when_missing(service, mock_producto_repo):
    # Arrange
    mock_producto_repo.update.return_value = None

    # Act
    result = await service.actualizar_producto(999, {"stock": 8})

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_eliminar_producto_delegates_to_repository(service, mock_producto_repo):
    # Arrange
    mock_producto_repo.delete.return_value = True

    # Act
    result = await service.eliminar_producto(1)

    # Assert
    assert result is True
    mock_producto_repo.delete.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_eliminar_producto_returns_false_when_not_found(service, mock_producto_repo):
    # Arrange
    mock_producto_repo.delete.return_value = False

    # Act
    result = await service.eliminar_producto(999)

    # Assert
    assert result is False


@pytest.mark.asyncio
async def test_verificar_devolucion_repuesto_increases_stock(service, mock_producto_repo):
    # Arrange
    producto = ProductoDB(id=1, nombre="Filtro", precio=10.5, stock=5)
    mock_producto_repo.get_by_id.return_value = producto
    mock_producto_repo.update.return_value = ProductoDB(id=1, nombre="Filtro", precio=10.5, stock=8)

    # Act
    result = await service.verificar_devolucion_repuesto(1, 3)

    # Assert
    mock_producto_repo.update.assert_called_once_with(1, {"stock": 8})
    assert result.stock == 8


@pytest.mark.asyncio
async def test_verificar_devolucion_repuesto_returns_none_when_producto_missing(
    service, mock_producto_repo
):
    # Arrange
    mock_producto_repo.get_by_id.return_value = None

    # Act
    result = await service.verificar_devolucion_repuesto(999, 3)

    # Assert
    assert result is None
    mock_producto_repo.update.assert_not_called()
