from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import docker
import jwt
import main
import pytest
from main import app, get_docker_client, restart_container
from src.utils.auth import SECRET_KEY


@pytest.fixture
def client():
    return app.test_client()


def make_token(permisos=None, expired=False):
    payload = {
        "sub": "1",
        "email": "admin@asdf.cl",
        "permisos": permisos or {"administracion": "view"},
        "exp": datetime.utcnow() + (timedelta(minutes=-5) if expired else timedelta(minutes=5)),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


@pytest.mark.asyncio
async def test_health_returns_monitored_services_count(client):
    # Act
    response = await client.get("/health")

    # Assert
    assert response.status_code == 200
    data = await response.get_json()
    assert data["status"] == "healthy"
    assert data["monitored_services"] == len(main.SERVICES_TO_MONITOR)


@pytest.mark.asyncio
async def test_status_without_token_returns_401(client):
    # Act
    response = await client.get("/status")

    # Assert
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_status_with_permission_returns_services_state(client):
    # Arrange
    token = make_token(permisos={"administracion": "view"})

    # Act
    response = await client.get("/status", headers={"Authorization": f"Bearer {token}"})

    # Assert
    assert response.status_code == 200
    data = await response.get_json()
    assert "services" in data
    assert "failures" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_status_without_permission_returns_403(client):
    # Arrange
    token = make_token(permisos={"administracion": "none"})

    # Act
    response = await client.get("/status", headers={"Authorization": f"Bearer {token}"})

    # Assert
    assert response.status_code == 403


def test_get_docker_client_returns_client_on_success():
    # Arrange
    with patch("docker.from_env") as mock_from_env:
        mock_from_env.return_value = MagicMock()

        # Act
        result = get_docker_client()

        # Assert
        assert result is not None
        mock_from_env.assert_called_once()


def test_get_docker_client_returns_none_on_failure():
    # Arrange
    with patch("docker.from_env", side_effect=Exception("docker daemon unreachable")):
        # Act
        result = get_docker_client()

        # Assert
        assert result is None


def test_restart_container_calls_restart_on_found_container():
    # Arrange
    mock_client = MagicMock()
    mock_container = MagicMock()
    mock_client.containers.get.return_value = mock_container

    # Act
    restart_container(mock_client, "ms_rrhh")

    # Assert
    mock_client.containers.get.assert_called_once_with("ms_rrhh")
    mock_container.restart.assert_called_once()


def test_restart_container_handles_not_found_without_raising():
    # Arrange
    mock_client = MagicMock()
    mock_client.containers.get.side_effect = docker.errors.NotFound("not found")

    # Act / Assert (no exception propagates)
    restart_container(mock_client, "ms_inexistente")


def test_restart_container_handles_generic_exception_without_raising():
    # Arrange
    mock_client = MagicMock()
    mock_client.containers.get.side_effect = Exception("unexpected docker error")

    # Act / Assert (no exception propagates)
    restart_container(mock_client, "ms_rrhh")
