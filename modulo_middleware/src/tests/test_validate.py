from datetime import datetime, timedelta

import jwt
import pytest
from main import SECRET_KEY, app


@pytest.fixture
def client():
    return app.test_client()


def make_token(sub=1, email="user@asdf.cl", rol="admin", expired=False):
    payload = {
        "sub": str(sub),
        "email": email,
        "rol": rol,
        "exp": datetime.utcnow() + (timedelta(minutes=-5) if expired else timedelta(minutes=5)),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


@pytest.mark.asyncio
async def test_health_returns_ok(client):
    # Act
    response = await client.get("/health")

    # Assert
    assert response.status_code == 200
    data = await response.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "middleware"


@pytest.mark.asyncio
async def test_validate_without_authorization_header_returns_401(client):
    # Act
    response = await client.get("/validate")

    # Assert
    assert response.status_code == 401
    data = await response.get_json()
    assert data["error"] == "Missing token"


@pytest.mark.asyncio
async def test_validate_with_malformed_header_returns_401(client):
    # Act
    response = await client.get("/validate", headers={"Authorization": "NotBearer xyz"})

    # Assert
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_validate_with_valid_token_returns_200_and_user_headers(client):
    # Arrange
    token = make_token(sub=42, email="juan@asdf.cl", rol="admin")

    # Act
    response = await client.get("/validate", headers={"Authorization": f"Bearer {token}"})

    # Assert
    assert response.status_code == 200
    data = await response.get_json()
    assert data["status"] == "authorized"
    assert data["user"] == "42"
    assert response.headers["X-User-ID"] == "42"
    assert response.headers["X-User-Role"] == "admin"
    assert response.headers["X-User-Email"] == "juan@asdf.cl"


@pytest.mark.asyncio
async def test_validate_with_expired_token_returns_401(client):
    # Arrange
    token = make_token(expired=True)

    # Act
    response = await client.get("/validate", headers={"Authorization": f"Bearer {token}"})

    # Assert
    assert response.status_code == 401
    data = await response.get_json()
    assert data["error"] == "Token expired"


@pytest.mark.asyncio
async def test_validate_with_invalid_token_returns_401(client):
    # Act
    response = await client.get("/validate", headers={"Authorization": "Bearer not-a-real-token"})

    # Assert
    assert response.status_code == 401
    data = await response.get_json()
    assert data["error"] == "Invalid token"


@pytest.mark.asyncio
async def test_validate_post_method_also_works(client):
    # Arrange
    token = make_token()

    # Act
    response = await client.post("/validate", headers={"Authorization": f"Bearer {token}"})

    # Assert
    assert response.status_code == 200
