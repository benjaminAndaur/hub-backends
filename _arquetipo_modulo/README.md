# Arquetipo de módulo (equivalente a Maven Archetype)

Plantilla [cookiecutter](https://cookiecutter.readthedocs.io/) que genera un `modulo_*` nuevo, ya pre-configurado con la estructura de capas estándar del Hub Empresarial (`models/repository/service/controller/utils`), Dockerfile, `pytest.ini`, y Swagger (`quart-schema`) activado de fábrica.

## Uso

Desde la raíz de `hub-backends`:

```bash
pip install cookiecutter
python scaffold.py
```

Cookiecutter pregunta de forma interactiva:

| Campo | Ejemplo | Para qué se usa |
|---|---|---|
| `module_name` | `Calidad` | Nombre legible → genera `modulo_calidad/` |
| `entity_name` | `Auditoria` | Nombre de la clase/entidad principal (`AuditoriaDB`, `AuditoriaRepository`, ...) |
| `port` | `8000` | Puerto interno del Dockerfile/uvicorn |

Genera el módulo completo en el directorio actual, verificado en esta sesión con `module_name=Calidad`, `entity_name=Auditoria`:

```
modulo_calidad/
├── Dockerfile
├── main.py                  # QuartSchema activado, Swagger en /docs
├── pytest.ini
├── requirements.txt
└── src/
    ├── models/auditoria_db.py
    ├── repository/auditoria_repository.py
    ├── service/auditoria_service.py
    ├── controller/auditoria_controller.py
    ├── utils/auth.py
    └── tests/test_auditoria_service.py
```

## Qué incluye

- **Repository + Service + Controller** ya conectados (mismo patrón que el resto de `hub-backends`).
- **Auth**: `login_required` / `require_permission` copiados del resto del Hub.
- **Swagger**: `QuartSchema(app, swagger_ui_path="/docs")` en `main.py` — el módulo generado expone `/docs` sin configuración adicional.
- **Tests base** del Service (4 tests, patrón AAA, mock del repository con `AsyncMock`).

## Qué falta completar manualmente (honesto, no es magia)

El arquetipo deja la **estructura**, no el **dominio**. Después de generarlo:

1. Reemplazar los campos de `{entidad}_db.py` por los reales (el arquetipo solo pone `nombre` + `creado_en` de ejemplo).
2. Completar el `controller` y el `repository` con tests propios — verificado en esta sesión: el módulo recién generado pasa sus 4 tests base pero queda en **~53% de cobertura** (el controller, sin tests aún, arrastra el promedio bajo el umbral de 60% configurado en `pytest.ini`). Es esperado: el desarrollador debe agregar tests de controller/repository específicos de la entidad real antes de integrar el módulo al stack.
3. Agregar el servicio al `docker-compose.yml` de `hub-infra` y su ruta en `nginx.conf` (no lo hace el arquetipo — son cambios en otro repo).

## Por qué cookiecutter y no un script bash a mano

Cookiecutter resuelve los placeholders Jinja2 (`{{cookiecutter.entity_name}}`) en **nombres de archivo y contenido** de forma consistente, evitando errores manuales de copy-paste (que es como históricamente se crearon los módulos de este proyecto, con inconsistencias entre módulos como resultado). Es el equivalente directo a `mvn archetype:generate`.
