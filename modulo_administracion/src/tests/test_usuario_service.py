import jwt
import pytest
from unittest.mock import AsyncMock
from src.service.usuario_service import UsuarioService, SECRET_KEY, ALGORITHM
from src.models.usuario_db import UsuarioDB


@pytest.fixture
def mock_usuario_repo():
    return AsyncMock()


@pytest.fixture
def service(mock_usuario_repo):
    return UsuarioService(mock_usuario_repo)


@pytest.mark.asyncio
async def test_crear_usuario_con_email_duplicado_lanza_value_error(service, mock_usuario_repo):
    # Arrange
    mock_usuario_repo.get_by_email.return_value = UsuarioDB(
        id=1, nombre="JUAN PEREZ", email="juan@asdf.cl", password_hash="hashed123"
    )
    data = {"nombre": "Juan Perez", "email": "juan@asdf.cl", "password": "secret123"}

    # Act / Assert
    with pytest.raises(ValueError, match="El email ya está registrado."):
        await service.crear_usuario(data)

    mock_usuario_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_crear_usuario_exitoso_hashea_password_y_nunca_la_guarda_en_texto_plano(service, mock_usuario_repo):
    # Arrange
    mock_usuario_repo.get_by_email.return_value = None
    mock_usuario_repo.create = AsyncMock(side_effect=lambda usuario: usuario)
    data = {"nombre": "Juan Perez", "email": "juan@asdf.cl", "password": "secret123", "permisos": {"rrhh": "view"}}

    # Act
    result = await service.crear_usuario(data)

    # Assert
    mock_usuario_repo.create.assert_called_once()
    creado: UsuarioDB = mock_usuario_repo.create.call_args[0][0]
    assert creado.password_hash != "secret123"
    assert creado.password_hash.startswith("$2b$")  # bcrypt hash prefix
    assert service.verify_password("secret123", creado.password_hash) is True
    assert result["email"] == "juan@asdf.cl"
    assert "password" not in result
    assert "password_hash" not in result


@pytest.mark.asyncio
async def test_crear_usuario_sin_password_usa_default_123456(service, mock_usuario_repo):
    # Arrange
    mock_usuario_repo.get_by_email.return_value = None
    mock_usuario_repo.create = AsyncMock(side_effect=lambda usuario: usuario)
    data = {"nombre": "Juan Perez", "email": "juan@asdf.cl"}

    # Act
    await service.crear_usuario(data)

    # Assert
    creado: UsuarioDB = mock_usuario_repo.create.call_args[0][0]
    assert service.verify_password("123456", creado.password_hash) is True


@pytest.mark.asyncio
async def test_obtener_todos(service, mock_usuario_repo):
    # Arrange
    mock_usuario_repo.get_all.return_value = [
        UsuarioDB(id=1, nombre="JUAN PEREZ", email="juan@asdf.cl", password_hash="hashed123", permisos={})
    ]

    # Act
    result = await service.obtener_todos()

    # Assert
    assert len(result) == 1
    assert result[0]["email"] == "juan@asdf.cl"
    mock_usuario_repo.get_all.assert_called_once()


@pytest.mark.asyncio
async def test_obtener_por_id_encontrado(service, mock_usuario_repo):
    # Arrange
    mock_usuario_repo.get_by_id.return_value = UsuarioDB(
        id=1, nombre="JUAN PEREZ", email="juan@asdf.cl", password_hash="hashed123", permisos={}
    )

    # Act
    result = await service.obtener_por_id(1)

    # Assert
    assert result is not None
    assert result["id"] == 1
    mock_usuario_repo.get_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_obtener_por_id_no_encontrado(service, mock_usuario_repo):
    # Arrange
    mock_usuario_repo.get_by_id.return_value = None

    # Act
    result = await service.obtener_por_id(999)

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_actualizar_usuario_con_cambio_de_password_hashea_y_elimina_campo_plano(service, mock_usuario_repo):
    # Arrange
    actualizado = UsuarioDB(id=1, nombre="JUAN PEREZ", email="juan@asdf.cl", password_hash="nuevo_hash", permisos={})
    mock_usuario_repo.update.return_value = actualizado
    data = {"password": "nueva_clave"}

    # Act
    result = await service.actualizar_usuario(1, data)

    # Assert
    assert result is not None
    mock_usuario_repo.update.assert_called_once()
    call_id, call_data = mock_usuario_repo.update.call_args[0]
    assert call_id == 1
    assert "password" not in call_data
    assert "password_hash" in call_data
    assert call_data["password_hash"] != "nueva_clave"
    assert service.verify_password("nueva_clave", call_data["password_hash"]) is True


@pytest.mark.asyncio
async def test_actualizar_usuario_sin_cambio_de_password_no_modifica_data(service, mock_usuario_repo):
    # Arrange
    actualizado = UsuarioDB(id=1, nombre="JUAN PEREZ", email="juan@asdf.cl", password_hash="hashed123", permisos={})
    mock_usuario_repo.update.return_value = actualizado
    data = {"nombre": "Juan Perez Actualizado"}

    # Act
    result = await service.actualizar_usuario(1, data)

    # Assert
    assert result is not None
    mock_usuario_repo.update.assert_called_once_with(1, {"nombre": "Juan Perez Actualizado"})


@pytest.mark.asyncio
async def test_actualizar_usuario_retorna_none_cuando_no_existe(service, mock_usuario_repo):
    # Arrange
    mock_usuario_repo.update.return_value = None

    # Act
    result = await service.actualizar_usuario(999, {"nombre": "Nadie"})

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_eliminar_usuario_delegates_to_repository(service, mock_usuario_repo):
    # Arrange
    mock_usuario_repo.delete.return_value = True

    # Act
    result = await service.eliminar_usuario(1)

    # Assert
    assert result is True
    mock_usuario_repo.delete.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_eliminar_usuario_returns_false_when_not_found(service, mock_usuario_repo):
    # Arrange
    mock_usuario_repo.delete.return_value = False

    # Act
    result = await service.eliminar_usuario(999)

    # Assert
    assert result is False


@pytest.mark.asyncio
async def test_login_exitoso_retorna_token_valido_y_actualiza_ultima_conexion(service, mock_usuario_repo):
    # Arrange
    password_hash = service.hash_password("secret123")
    usuario = UsuarioDB(
        id=1, nombre="JUAN PEREZ", email="juan@asdf.cl", password_hash=password_hash,
        permisos={"rrhh": "edit"}
    )
    mock_usuario_repo.get_by_email.return_value = usuario
    mock_usuario_repo.update.return_value = usuario

    # Act
    result = await service.login("juan@asdf.cl", "secret123")

    # Assert
    assert "token" in result
    assert result["user"]["email"] == "juan@asdf.cl"
    assert result["user"]["id"] == 1

    payload = jwt.decode(result["token"], SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "1"
    assert payload["email"] == "juan@asdf.cl"
    assert payload["permisos"] == {"rrhh": "edit"}
    assert "exp" in payload

    mock_usuario_repo.update.assert_called_once()
    update_id, update_data = mock_usuario_repo.update.call_args[0]
    assert update_id == 1
    assert "ultima_conexion" in update_data


@pytest.mark.asyncio
async def test_login_con_email_inexistente_lanza_value_error(service, mock_usuario_repo):
    # Arrange
    mock_usuario_repo.get_by_email.return_value = None

    # Act / Assert
    with pytest.raises(ValueError, match="Credenciales inválidas"):
        await service.login("nadie@asdf.cl", "cualquier_clave")

    mock_usuario_repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_login_con_password_incorrecta_lanza_value_error(service, mock_usuario_repo):
    # Arrange
    password_hash = service.hash_password("secret123")
    usuario = UsuarioDB(id=1, nombre="JUAN PEREZ", email="juan@asdf.cl", password_hash=password_hash, permisos={})
    mock_usuario_repo.get_by_email.return_value = usuario

    # Act / Assert
    with pytest.raises(ValueError, match="Credenciales inválidas"):
        await service.login("juan@asdf.cl", "clave_incorrecta")

    mock_usuario_repo.update.assert_not_called()
