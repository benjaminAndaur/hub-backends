import pytest

from src.notificaciones.notificador import (
    NotificacionEstandar,
    NotificacionRegistro,
    NotificacionUrgente,
)
from src.notificaciones.notificador_factory import NotificadorFactory


def test_crear_devuelve_notificacion_urgente_para_gravedad_alta():
    # Act
    notificador = NotificadorFactory.crear("Alta")

    # Assert
    assert isinstance(notificador, NotificacionUrgente)


def test_crear_devuelve_notificacion_estandar_para_gravedad_media():
    # Act
    notificador = NotificadorFactory.crear("Media")

    # Assert
    assert isinstance(notificador, NotificacionEstandar)


def test_crear_devuelve_notificacion_registro_para_gravedad_baja():
    # Act
    notificador = NotificadorFactory.crear("Baja")

    # Assert
    assert isinstance(notificador, NotificacionRegistro)


def test_crear_lanza_error_para_gravedad_desconocida():
    # Act / Assert
    with pytest.raises(ValueError):
        NotificadorFactory.crear("Critica")


@pytest.mark.asyncio
async def test_notificacion_urgente_retorna_resumen_con_canales():
    # Arrange
    notificador = NotificadorFactory.crear("Alta")
    incidente = type("Incidente", (), {"id": 1, "titulo": "Caida de altura"})()

    # Act
    resultado = await notificador.notificar(incidente)

    # Assert
    assert resultado["tipo"] == "urgente"
    assert resultado["canales"] == ["email", "sms", "whatsapp"]
    assert resultado["incidente_id"] == 1


@pytest.mark.asyncio
async def test_notificacion_registro_no_usa_canales():
    # Arrange
    notificador = NotificadorFactory.crear("Baja")
    incidente = type("Incidente", (), {"id": 2, "titulo": "Derrame menor"})()

    # Act
    resultado = await notificador.notificar(incidente)

    # Assert
    assert resultado["tipo"] == "registro"
    assert resultado["canales"] == []
