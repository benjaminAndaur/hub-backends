import pytest
from unittest.mock import AsyncMock, MagicMock
from src.service.mantencion_template_service import MantencionTemplateService
from src.models.mantencion_template_db import MantencionTemplateDB


@pytest.fixture
def mock_template_repo():
    return AsyncMock()


@pytest.fixture
def service(mock_template_repo):
    return MantencionTemplateService(mock_template_repo)


@pytest.mark.asyncio
async def test_crear_template_creates_and_returns_summary(service, mock_template_repo):
    # Arrange
    data = {
        "nombre": "Mantención 50.000km",
        "descripcion": "Cambio de aceite y filtros",
        "tareas_json": {"tareas": ["aceite", "filtros"]},
        "repuestos_json_default": {"producto_1": 2}
    }
    mock_template_repo.create.return_value = MantencionTemplateDB(id=1, nombre="Mantención 50.000km")

    # Act
    result = await service.crear_template(data)

    # Assert
    assert result == {"id": 1, "nombre": "Mantención 50.000km"}
    mock_template_repo.create.assert_called_once()
    created_arg = mock_template_repo.create.call_args[0][0]
    assert created_arg.nombre == "Mantención 50.000km"
    assert created_arg.descripcion == "Cambio de aceite y filtros"
    assert created_arg.tareas_json == {"tareas": ["aceite", "filtros"]}
    assert created_arg.repuestos_json_default == {"producto_1": 2}


@pytest.mark.asyncio
async def test_crear_template_with_minimal_data_uses_defaults(service, mock_template_repo):
    # Arrange
    data = {"nombre": "Template Básico"}
    mock_template_repo.create.return_value = MantencionTemplateDB(id=2, nombre="Template Básico")

    # Act
    result = await service.crear_template(data)

    # Assert
    assert result == {"id": 2, "nombre": "Template Básico"}
    created_arg = mock_template_repo.create.call_args[0][0]
    assert created_arg.descripcion is None
    assert created_arg.tareas_json is None
    assert created_arg.repuestos_json_default is None


@pytest.mark.asyncio
async def test_obtener_todos_returns_list_of_summaries(service, mock_template_repo):
    # Arrange
    mock_template_repo.get_all.return_value = [
        MantencionTemplateDB(id=1, nombre="Template A"),
        MantencionTemplateDB(id=2, nombre="Template B"),
    ]

    # Act
    result = await service.obtener_todos()

    # Assert
    assert result == [{"id": 1, "nombre": "Template A"}, {"id": 2, "nombre": "Template B"}]
    mock_template_repo.get_all.assert_called_once()


@pytest.mark.asyncio
async def test_obtener_todos_returns_empty_list_when_no_templates(service, mock_template_repo):
    # Arrange
    mock_template_repo.get_all.return_value = []

    # Act
    result = await service.obtener_todos()

    # Assert
    assert result == []
