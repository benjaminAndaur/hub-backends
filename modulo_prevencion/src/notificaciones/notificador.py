from abc import ABC, abstractmethod


class INotificador(ABC):
    """Interfaz común para cualquier estrategia de aviso de un incidente."""

    @abstractmethod
    async def notificar(self, incidente) -> dict:
        """Ejecuta el aviso y devuelve un resumen de lo realizado."""
        raise NotImplementedError


class NotificacionUrgente(INotificador):
    """Incidentes de gravedad Alta: aviso inmediato y multi-canal (simulado)."""

    async def notificar(self, incidente) -> dict:
        canales = ["email", "sms", "whatsapp"]
        print(
            f"[URGENTE] Incidente #{incidente.id} ({incidente.titulo}) "
            f"notificado por {', '.join(canales)}"
        )
        return {"tipo": "urgente", "canales": canales, "incidente_id": incidente.id}


class NotificacionEstandar(INotificador):
    """Incidentes de gravedad Media: aviso por un solo canal (simulado)."""

    async def notificar(self, incidente) -> dict:
        canales = ["email"]
        print(f"[ESTANDAR] Incidente #{incidente.id} ({incidente.titulo}) notificado por email")
        return {"tipo": "estandar", "canales": canales, "incidente_id": incidente.id}


class NotificacionRegistro(INotificador):
    """Incidentes de gravedad Baja: solo queda registrado, sin aviso activo."""

    async def notificar(self, incidente) -> dict:
        print(
            f"[REGISTRO] Incidente #{incidente.id} ({incidente.titulo}) registrado sin aviso activo"
        )
        return {"tipo": "registro", "canales": [], "incidente_id": incidente.id}
