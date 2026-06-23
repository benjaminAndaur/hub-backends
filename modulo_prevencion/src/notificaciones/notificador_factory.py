from src.notificaciones.notificador import (
    INotificador,
    NotificacionEstandar,
    NotificacionRegistro,
    NotificacionUrgente,
)

_NOTIFICADORES_POR_GRAVEDAD = {
    "Alta": NotificacionUrgente,
    "Media": NotificacionEstandar,
    "Baja": NotificacionRegistro,
}


class NotificadorFactory:
    """Factory Method: decide qué estrategia de notificación usar según
    la gravedad del incidente, sin que el código cliente (IncidenteService)
    conozca las clases concretas. Agregar un nuevo nivel de gravedad solo
    requiere sumar una entrada al mapa, sin tocar el resto del sistema (OCP).
    """

    @staticmethod
    def crear(nivel_gravedad: str) -> INotificador:
        clase = _NOTIFICADORES_POR_GRAVEDAD.get(nivel_gravedad)
        if clase is None:
            raise ValueError(f"Nivel de gravedad desconocido: {nivel_gravedad!r}")
        return clase()
