import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from src.service.reportes_service import ReportesService
from src.models.reportes import ReportesCreate, ReportesResponse


@pytest.fixture
def mock_reportes_repo():
    return AsyncMock()


@pytest.fixture
def service(mock_reportes_repo):
    return ReportesService(mock_reportes_repo)


def make_db_reporte(**overrides):
    base = dict(
        report_id="r1",
        sequential_id=1,
        report_date=None,
        input_date=None,
        device_id=None,
        holder_id=None,
        asset_id=None,
        asset_name=None,
        event_id=None,
        event_name=None,
        gps_validity=None,
        gps_satellites=None,
        gps_dop=None,
        latitude=None,
        longitude=None,
        location=None,
        area_type=None,
        speed=None,
        heading=None,
        odometer=None,
        hourmeter=None,
        total_fuel_used=None,
        obc_hourmeter=None,
        obc_odometer=None,
        parameter_value=None,
        parameter_id=None,
        parameter_name=None,
        ralenti_band_time=None,
        yellow_band_time=None,
        efficient_handling_band_time=None,
        red_band_time=None,
        load_over_75_band_time=None,
        inefficient_cruise_control_band_time=None,
        engine_braking_time=None,
        cartography_limit_speed=None,
        gps_speed=None,
        driver_name=None,
        driver_last_name=None,
        driver_document_type=None,
        driver_document_number=None,
        ignition=None,
        ignition_date=None,
        fecha_registro=datetime(2024, 1, 1),
    )
    base.update(overrides)
    return MagicMock(**base)


@pytest.mark.asyncio
async def test_create_reporte_returns_response(service, mock_reportes_repo):
    # Arrange
    data = ReportesCreate(report_id="r1")
    mock_reportes_repo.create.return_value = make_db_reporte(report_id="r1")

    # Act
    result = await service.create_reporte(data)

    # Assert
    assert isinstance(result, ReportesResponse)
    assert result.report_id == "r1"
    mock_reportes_repo.create.assert_called_once_with(data)


@pytest.mark.asyncio
async def test_create_multiple_reportes_returns_inserted_count(service, mock_reportes_repo):
    # Arrange
    data = [ReportesCreate(report_id="r1"), ReportesCreate(report_id="r2")]
    mock_reportes_repo.create_many.return_value = 2

    # Act
    result = await service.create_multiple_reportes(data)

    # Assert
    assert result == {"inserted": 2}
    mock_reportes_repo.create_many.assert_called_once_with(data)


@pytest.mark.asyncio
async def test_get_reporte_by_id_returns_response_when_found(service, mock_reportes_repo):
    # Arrange
    mock_reportes_repo.get_by_id.return_value = make_db_reporte(report_id="r1")

    # Act
    result = await service.get_reporte_by_id("r1")

    # Assert
    assert result is not None
    assert result.report_id == "r1"
    mock_reportes_repo.get_by_id.assert_called_once_with("r1")


@pytest.mark.asyncio
async def test_get_reporte_by_id_returns_none_when_missing(service, mock_reportes_repo):
    # Arrange
    mock_reportes_repo.get_by_id.return_value = None

    # Act
    result = await service.get_reporte_by_id("inexistente")

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_get_all_reportes_returns_list(service, mock_reportes_repo):
    # Arrange
    mock_reportes_repo.get_all.return_value = [make_db_reporte(report_id="r1"), make_db_reporte(report_id="r2")]

    # Act
    result = await service.get_all_reportes(limit=50, offset=0)

    # Assert
    assert len(result) == 2
    mock_reportes_repo.get_all.assert_called_once_with(50, 0)


@pytest.mark.asyncio
async def test_get_all_reportes_returns_empty_list(service, mock_reportes_repo):
    # Arrange
    mock_reportes_repo.get_all.return_value = []

    # Act
    result = await service.get_all_reportes()

    # Assert
    assert result == []
