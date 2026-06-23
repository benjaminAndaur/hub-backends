# hub-backends

Microservicios backend (Python/Quart) del Hub Empresarial. Cada módulo es una API independiente que comparte la misma base de datos PostgreSQL (`asdf_db`) pero se despliega como contenedor propio.

Repos relacionados:
- [`hub-frontends`](https://github.com/benjaminAndaur/hub-frontends) — frontends React/Vite
- [`hub-infra`](https://github.com/benjaminAndaur/hub-infra) — nginx, base de datos y `docker-compose.yml`
- [`hub-ms-operacion`](https://github.com/benjaminAndaur/hub-ms-operacion) — microservicio de Viajes/Operaciones, extraído de este monorepo con **base de datos propia** (Database per Service)
- [`hub-ms-facturacion`](https://github.com/benjaminAndaur/hub-ms-facturacion) — microservicio de Facturación, extraído de este monorepo con **base de datos propia** (Database per Service)
- [`hub-bff`](https://github.com/benjaminAndaur/hub-bff) — BFF (NestJS) que agrega datos de `hub-ms-operacion` + `hub-ms-facturacion` con Circuit Breaker

## Módulos incluidos

| Módulo | Puerto interno | Dominio |
|---|---|---|
| `modulo_middleware` | 8009 | Validación de JWT (interno, sin frontend) |
| `modulo_administracion` | 8007 | Usuarios y permisos |
| `modulo_rrhh` | 8000 | Personal / RRHH |
| `modulo_mantencion` | 8000 | Mantención de vehículos |
| `modulo_acreditacion` | 8000 | Acreditación de clientes |
| `modulo_bodega` | 8000 | Bodega / Inventario |
| `modulo_prevencion` | 8000 | Prevención / Incidentes |
| `modulo_watchdog` | 8008 | Monitoreo y reinicio automático de microservicios |

> `modulo_operacion` y `modulo_facturacion` ya no viven en este repo: se migraron a [`hub-ms-operacion`](https://github.com/benjaminAndaur/hub-ms-operacion) y [`hub-ms-facturacion`](https://github.com/benjaminAndaur/hub-ms-facturacion) respectivamente, cada uno con su propia base de datos PostgreSQL aislada (patrón **Database per Service**). El resto de los módulos de esta tabla sigue compartiendo `asdf_db`.

## Cómo ejecutar un módulo individual

```bash
cd modulo_rrhh   # o cualquier otro modulo_*
pip install -r requirements.txt

# Variables de entorno requeridas
export DATABASE_URL=postgresql+asyncpg://admin:admin123@localhost:5432/asdf_db
export JWT_SECRET=super-secret-key-123

uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

> Para levantar el stack completo (todos los módulos + frontends + nginx + base de datos), usar `docker-compose up --build` desde el repo [`hub-infra`](https://github.com/benjaminAndaur/hub-infra).

## Arquitectura de cada módulo

```
modulo_x/
├── main.py              # entrypoint Quart; @app.before_request inyecta repo/service/sesión BD en g{}
├── Dockerfile
├── requirements.txt
└── src/
    ├── models/
    │   ├── {entidad}.py       # Pydantic: {Entidad}Create, {Entidad}Update, {Entidad}Response
    │   └── {entidad}_db.py    # ORM SQLAlchemy (Base)
    ├── repository/
    │   └── {entidad}_repository.py   # solo consultas async, sin lógica de negocio
    ├── service/
    │   └── {entidad}_service.py      # lógica de negocio; orquesta repositorios
    ├── controller/
    │   └── {entidad}_controller.py   # Blueprint Quart; valida Pydantic; llama g.service
    └── utils/
        └── auth.py        # decoradores @login_required y @require_permission
```

- Todas las operaciones de BD son asíncronas (SQLAlchemy 2.0 async + asyncpg).
- Las tablas se crean con `Base.metadata.create_all()` al arrancar — **no hay migraciones**.
- No hay FK entre tablas de módulos distintos (por diseño). Las referencias cruzadas se guardan como ID externo + valor denormalizado (ej: `viaje.conductor_id` + `viaje.conductor_nombre`), para permitir despliegue independiente.

## Autenticación y permisos

1. `POST /api/v1/administracion/login` (única ruta pública) retorna un JWT con `{sub, email, rol, permisos: {modulo: "none"|"view"|"edit"}}`.
2. El gateway Nginx valida el JWT en cada request vía `auth_request` contra `modulo_middleware`.
3. El middleware devuelve `X-User-ID`, `X-User-Role`, `X-User-Email` como headers.
4. Cada controlador usa `@login_required` + `@require_permission('modulo', 'view'|'edit')` para autorizar.

## Lógica de negocio destacada

**`modulo_mantencion`:**
- Al crear una `mantencion`, el `vehiculo.estado` cambia automáticamente a `"BLOQUEADO POR MANTENCIÓN PREVENTIVA"` o `"BLOQUEADO POR MANTENCIÓN CORRECTIVA"` (lógica en `MantencionService`).
- Al marcar la mantención como `"Completada"`, el vehículo vuelve a `"Disponible"`.
- Incluye un worker async (`PreventiveService.start_worker()`) que monitorea templates y crea `mantenciones` automáticamente según condiciones programadas. El estado se persiste en BD.

**`modulo_watchdog`:**
- Corre un thread daemon (`monitor_loop()`) que cada 30s hace `GET /health` a cada microservicio.
- Si un servicio falla 2 checks consecutivos, reinicia el contenedor vía Docker API (`/var/run/docker.sock`).
- `GET /status` (requiere permiso `administracion edit`) expone el estado de todos los servicios.

## Variables de entorno

| Variable | Valor en dev |
|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://admin:admin123@db-global:5432/asdf_db` |
| `JWT_SECRET` | `super-secret-key-123` |

## Tests

Todos los módulos activos (`modulo_middleware`, `modulo_administracion`, `modulo_rrhh`, `modulo_mantencion`, `modulo_acreditacion`, `modulo_bodega`, `modulo_prevencion`, `modulo_watchdog`) tienen tests en `src/tests/` (pytest + pytest-asyncio, mockeando repos/sesión con `AsyncMock`). `sonar-project.properties` (raíz del repo) importa el reporte `coverage.xml` para SonarQube — ver `GUIA_PRUEBAS.md` para el flujo completo de cómo correr `pytest --cov` en cada `modulo_*` y generar/leer los reportes.

## Patrones de diseño

- **Repository**: en todos los módulos (`src/repository/`) — ver [`PATRONES_DE_DISENO.md`](../PATRONES_DE_DISENO.md) en la raíz del proyecto.
- **Factory Method**: `modulo_prevencion/src/notificaciones/` — `NotificadorFactory.crear(nivel_gravedad)` decide qué notificador instanciar (`NotificacionUrgente`/`Estandar`/`Registro`) sin que `IncidenteService` conozca las clases concretas.
- **Circuit Breaker**: implementado en [`hub-bff`](https://github.com/benjaminAndaur/hub-bff) (único lugar del sistema con llamadas HTTP a otros microservicios propios).

## Industrialización

**Linting (equivalente a Checkstyle):** Ruff + Black, configurados en `pyproject.toml` (raíz del repo).
```bash
./lint.sh   # ruff check + black --check sobre todo el repo
```

**Swagger/OpenAPI (contratos de API):** `quart-schema` expuesto en `modulo_rrhh` y `modulo_operacion`/`hub-ms-operacion` (mínimo de 2 módulos exigido por la rúbrica) — `GET /docs` (Swagger UI) y `GET /openapi.json` en cada uno. Activado con una línea en `main.py`:
```python
QuartSchema(app, info={"title": "RRHH", "version": "1.0"}, swagger_ui_path="/docs")
```

**Arquetipo de módulo (equivalente a Maven Archetype):** `_arquetipo_modulo/` — plantilla cookiecutter que genera un `modulo_*` nuevo con las 4 capas, Dockerfile, tests base y Swagger ya activado. Ver [`_arquetipo_modulo/README.md`](./_arquetipo_modulo/README.md).
```bash
pip install cookiecutter
python scaffold.py
```

**Documentación HTML (equivalente a Javadoc):** docstrings en services/repositories + [`pdoc`](https://pdoc.dev/) genera la documentación navegable.
```bash
pip install pdoc
pdoc --output-dir docs src.service src.repository src.controller src.utils.auth   # desde cada modulo_*/
```

Ver [`EQUIVALENCIAS_TECNOLOGICAS.md`](../EQUIVALENCIAS_TECNOLOGICAS.md) en la raíz del proyecto para el mapeo completo Java→Python/Node de cada requisito.
