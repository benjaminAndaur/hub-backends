import asyncio
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.models.mantencion_db import MantencionDB
from src.models.vehiculo_db import VehiculoDB
from src.service.preventive_service import PreventiveService


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def session_factory(mock_session):
    @asynccontextmanager
    async def factory():
        yield mock_session

    return factory


@pytest.fixture
def service(session_factory):
    return PreventiveService(session_factory)


@pytest.mark.asyncio
async def test_start_worker_initializes_queue_and_task(service):
    # Arrange
    with patch("src.service.preventive_service.asyncio.create_task") as mock_create_task:
        # Act
        service.start_worker()

        # Assert
        assert service.queue is not None
        assert isinstance(service.queue, asyncio.Queue)
        mock_create_task.assert_called_once()


@pytest.mark.asyncio
async def test_start_worker_does_not_reinitialize_existing_queue(service):
    # Arrange
    with patch("src.service.preventive_service.asyncio.create_task") as mock_create_task:
        service.start_worker()
        existing_queue = service.queue

        # Act
        service.start_worker()

        # Assert
        assert service.queue is existing_queue
        mock_create_task.assert_called_once()


@pytest.mark.asyncio
async def test_enqueue_preventive_puts_item_when_queue_exists(service):
    # Arrange
    service.queue = asyncio.Queue()
    data = {"vehiculo_id": 1, "odometro_actual": 60000}

    # Act
    await service.enqueue_preventive(data)

    # Assert
    assert service.queue.qsize() == 1
    item = await service.queue.get()
    assert item == data


@pytest.mark.asyncio
async def test_enqueue_preventive_does_nothing_when_queue_missing(service):
    # Arrange
    assert service.queue is None

    # Act / Assert (no exception raised)
    await service.enqueue_preventive({"vehiculo_id": 1, "odometro_actual": 1000})
    assert service.queue is None


@pytest.mark.asyncio
async def test_fetch_sitrack_data_returns_list_on_success(service):
    # Arrange
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = [{"assetName": "ABC123", "deviceId": "1", "odometer": 1000}]

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client_cm = AsyncMock()
    mock_client_cm.__aenter__.return_value = mock_client

    with patch("src.service.preventive_service.httpx.AsyncClient", return_value=mock_client_cm):
        # Act
        result = await service.fetch_sitrack_data()

    # Assert
    assert result == [{"assetName": "ABC123", "deviceId": "1", "odometer": 1000}]


@pytest.mark.asyncio
async def test_fetch_sitrack_data_returns_empty_list_when_response_not_list(service):
    # Arrange
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {"unexpected": "shape"}

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client_cm = AsyncMock()
    mock_client_cm.__aenter__.return_value = mock_client

    with patch("src.service.preventive_service.httpx.AsyncClient", return_value=mock_client_cm):
        # Act
        result = await service.fetch_sitrack_data()

    # Assert
    assert result == []


@pytest.mark.asyncio
async def test_fetch_sitrack_data_returns_empty_list_on_exception(service):
    # Arrange
    mock_client_cm = AsyncMock()
    mock_client_cm.__aenter__.side_effect = Exception("network error")

    with patch("src.service.preventive_service.httpx.AsyncClient", return_value=mock_client_cm):
        # Act
        result = await service.fetch_sitrack_data()

    # Assert
    assert result == []


@pytest.mark.asyncio
async def test_get_preventive_status_returns_empty_list_when_no_sitrack_data(service, mock_session):
    # Arrange
    with patch.object(service, "fetch_sitrack_data", AsyncMock(return_value=[])):
        # Act
        result = await service.get_preventive_status()

    # Assert
    assert result == []


@pytest.mark.asyncio
async def test_get_preventive_status_marks_existing_vehicle_needing_mantencion(
    service, mock_session
):
    # Arrange
    vehiculo = VehiculoDB(id=1, patente="ABC123", device_id=1, estado="Disponible")

    with (
        patch.object(
            service,
            "fetch_sitrack_data",
            AsyncMock(return_value=[{"assetName": "ABC123", "deviceId": "1", "odometer": 60000}]),
        ),
        patch("src.service.preventive_service.VehiculoRepository") as MockVehiculoRepo,
        patch("src.service.preventive_service.MantencionRepository") as MockMantencionRepo,
    ):

        mock_vehiculo_repo = MockVehiculoRepo.return_value
        mock_vehiculo_repo.get_all = AsyncMock(return_value=[vehiculo])

        mock_mantencion_repo = MockMantencionRepo.return_value
        mock_mantencion_repo.get_latest_for_vehiculo = AsyncMock(return_value=None)

        with patch.object(service, "enqueue_preventive", AsyncMock()) as mock_enqueue:
            # Act
            result = await service.get_preventive_status()

    # Assert
    assert len(result) == 1
    assert result[0]["patente"] == "ABC123"
    assert result[0]["necesita_mantencion"] is True
    assert result[0]["diferencia"] == 60000
    mock_enqueue.assert_called_once_with({"vehiculo_id": 1, "odometro_actual": 60000})
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_get_preventive_status_does_not_need_mantencion_when_diferencia_is_small(
    service, mock_session
):
    # Arrange
    vehiculo = VehiculoDB(id=1, patente="ABC123", device_id=1, estado="Disponible")
    last_mantencion = MantencionDB(
        id=1, vehiculo_id=1, mecanico_id=1, tipo="Preventiva", odometro=59000
    )

    with (
        patch.object(
            service,
            "fetch_sitrack_data",
            AsyncMock(return_value=[{"assetName": "ABC123", "deviceId": "1", "odometer": 60000}]),
        ),
        patch("src.service.preventive_service.VehiculoRepository") as MockVehiculoRepo,
        patch("src.service.preventive_service.MantencionRepository") as MockMantencionRepo,
    ):

        mock_vehiculo_repo = MockVehiculoRepo.return_value
        mock_vehiculo_repo.get_all = AsyncMock(return_value=[vehiculo])

        mock_mantencion_repo = MockMantencionRepo.return_value
        mock_mantencion_repo.get_latest_for_vehiculo = AsyncMock(return_value=last_mantencion)

        with patch.object(service, "enqueue_preventive", AsyncMock()) as mock_enqueue:
            # Act
            result = await service.get_preventive_status()

    # Assert
    assert len(result) == 1
    assert result[0]["necesita_mantencion"] is False
    assert result[0]["diferencia"] == 1000
    mock_enqueue.assert_not_called()


@pytest.mark.asyncio
async def test_get_preventive_status_creates_new_vehicle_when_not_found(service, mock_session):
    # Arrange
    with (
        patch.object(
            service,
            "fetch_sitrack_data",
            AsyncMock(return_value=[{"assetName": "NEW123", "deviceId": "5", "odometer": 100}]),
        ),
        patch("src.service.preventive_service.VehiculoRepository") as MockVehiculoRepo,
        patch("src.service.preventive_service.MantencionRepository") as MockMantencionRepo,
    ):

        mock_vehiculo_repo = MockVehiculoRepo.return_value
        mock_vehiculo_repo.get_all = AsyncMock(return_value=[])

        mock_mantencion_repo = MockMantencionRepo.return_value
        mock_mantencion_repo.get_latest_for_vehiculo = AsyncMock(return_value=None)

        # Act
        result = await service.get_preventive_status()

    # Assert
    mock_session.add.assert_called_once()
    added_vehiculo = mock_session.add.call_args[0][0]
    assert added_vehiculo.patente == "NEW123"
    assert added_vehiculo.device_id == 5
    assert len(result) == 1
    assert result[0]["patente"] == "NEW123"


@pytest.mark.asyncio
async def test_get_preventive_status_skips_items_without_patente_or_device_id(
    service, mock_session
):
    # Arrange
    with (
        patch.object(
            service,
            "fetch_sitrack_data",
            AsyncMock(
                return_value=[
                    {"assetName": None, "deviceId": "5", "odometer": 100},
                    {"assetName": "ABC123", "deviceId": None, "odometer": 100},
                ]
            ),
        ),
        patch("src.service.preventive_service.VehiculoRepository") as MockVehiculoRepo,
        patch("src.service.preventive_service.MantencionRepository") as MockMantencionRepo,
    ):

        mock_vehiculo_repo = MockVehiculoRepo.return_value
        mock_vehiculo_repo.get_all = AsyncMock(return_value=[])

        mock_mantencion_repo = MockMantencionRepo.return_value
        mock_mantencion_repo.get_latest_for_vehiculo = AsyncMock(return_value=None)

        # Act
        result = await service.get_preventive_status()

    # Assert
    assert result == []
    mock_session.add.assert_not_called()


@pytest.mark.asyncio
async def test_process_queue_creates_mantencion_for_queued_item(service):
    """Testea la lógica interna del worker (un solo ciclo), sin ejecutar el while True real."""
    # Arrange
    service.queue = asyncio.Queue()
    await service.queue.put({"vehiculo_id": 1, "odometro_actual": 60000})

    mock_session = AsyncMock()

    @asynccontextmanager
    async def factory():
        yield mock_session

    service.session_factory = factory

    mock_mantencion_repo = AsyncMock()

    call_count = {"n": 0}

    async def fake_wait_for(coro, timeout):
        call_count["n"] += 1
        if call_count["n"] == 1:
            return await coro
        raise asyncio.CancelledError()

    with (
        patch(
            "src.service.preventive_service.MantencionRepository", return_value=mock_mantencion_repo
        ),
        patch("src.service.preventive_service.asyncio.wait_for", side_effect=fake_wait_for),
    ):
        # Act
        with pytest.raises(asyncio.CancelledError):
            await service._process_queue()

    # Assert
    mock_mantencion_repo.create.assert_called_once()
    created_arg = mock_mantencion_repo.create.call_args[0][0]
    assert created_arg.vehiculo_id == 1
    assert created_arg.odometro == 60000
    assert created_arg.tipo == "Preventiva"


@pytest.mark.asyncio
async def test_process_queue_continues_on_timeout(service):
    """Si la cola está vacía (TimeoutError), el worker debe seguir sin lanzar excepción."""
    # Arrange
    service.queue = asyncio.Queue()
    call_count = {"n": 0}

    async def fake_wait_for(coro, timeout):
        call_count["n"] += 1
        coro.close()  # evita warning de coroutine nunca esperada (queue.get() descartado)
        if call_count["n"] == 1:
            raise asyncio.TimeoutError()
        raise asyncio.CancelledError()

    with patch("src.service.preventive_service.asyncio.wait_for", side_effect=fake_wait_for):
        # Act
        with pytest.raises(asyncio.CancelledError):
            await service._process_queue()

    # Assert
    assert call_count["n"] == 2


@pytest.mark.asyncio
async def test_process_queue_logs_and_continues_on_generic_exception(service):
    """Si ocurre un error inesperado procesando un item, el worker no debe propagar la excepción."""
    # Arrange
    call_count = {"n": 0}

    async def fake_wait_for(coro, timeout):
        call_count["n"] += 1
        if call_count["n"] == 1:
            # Item inválido (falta 'odometro_actual') -> KeyError dentro del try del worker real
            return await coro
        raise asyncio.CancelledError()

    service.queue = asyncio.Queue()
    await service.queue.put({"vehiculo_id": 1})  # falta 'odometro_actual' a propósito

    with patch("src.service.preventive_service.asyncio.wait_for", side_effect=fake_wait_for):
        # Act
        with pytest.raises(asyncio.CancelledError):
            await service._process_queue()

    # Assert: el segundo wait_for (timeout/cancel) fue alcanzado, lo que prueba que
    # la excepción genérica del primer ciclo fue capturada y el loop continuó.
    assert call_count["n"] == 2
