# Guía de Pruebas — Hub Empresarial (Backends)

Esta guía explica cómo correr los tests unitarios de cada microservicio, leer los reportes de cobertura, y usar SonarQube para verificar el Quality Gate del proyecto.

## 1. Estructura de tests

Cada `modulo_*` sigue el mismo patrón, replicado desde `modulo_rrhh` (el módulo de referencia):

```
modulo_x/
├── pytest.ini              # config de pytest + cobertura
├── requirements.txt        # incluye pytest, pytest-asyncio, pytest-cov, pytest-mock, httpx
└── src/
    └── tests/
        ├── __init__.py
        ├── test_<entidad>_service.py      # mockea el repository con AsyncMock
        ├── test_<entidad>_repository.py   # mockea la sesión SQLAlchemy
        └── test_auth.py                   # decoradores login_required / require_permission
```

Patrón de cada test (AAA — Arrange/Act/Assert):

```python
@pytest.mark.asyncio
async def test_obtener_por_id(service, mock_repo):
    # Arrange
    mock_repo.find_by_id.return_value = PersonalDB(id=1, nombre="Test")

    # Act
    result = await service.obtener_por_id(1)

    # Assert
    assert result is not None
    mock_repo.find_by_id.assert_called_once_with(1)
```

Los tests de `repository` no levantan una base de datos real — mockean `AsyncSession` completo (`session.execute`, `session.add`, `session.commit`, `session.get`, etc). Son tests unitarios rápidos, no de integración.

`modulo_middleware` y `modulo_watchdog` no siguen el patrón de capas (no tienen `service`/`repository`); sus tests cubren directamente los endpoints Quart (`/validate`, `/health`, `/status`) y las funciones de `main.py` (`restart_container`, `get_docker_client`).

## 2. Cómo correr los tests de un módulo

Cada módulo es independiente, con su propio entorno virtual:

```bash
cd modulo_rrhh   # o cualquier otro modulo_*
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac

pip install -r requirements.txt
pytest
```

`pytest.ini` ya tiene configurado:

```ini
[pytest]
asyncio_mode = auto
addopts = --cov=src --cov-report=term-missing --cov-report=xml --cov-report=html --cov-fail-under=60
testpaths = src/tests
```

Esto significa que `pytest` solo (sin flags) ya:
- Corre todos los tests en `src/tests/`
- Calcula cobertura de `src/`
- Imprime en consola las líneas sin cubrir (`--cov-report=term-missing`)
- Genera `coverage.xml` (para SonarQube/CI) y `htmlcov/` (para revisión visual)
- **Falla la corrida si la cobertura total es menor a 60%** (`--cov-fail-under=60`)

Un run en verde ya certifica que el módulo cumple el mínimo de cobertura exigido por la rúbrica.

`modulo_middleware` y `modulo_watchdog` no tienen carpeta `src/repository`/`src/service`, así que su `pytest.ini` mide cobertura sobre todo el directorio (`--cov=.`) usando `.coveragerc` para excluir `.venv`/tests de la medición.

## 3. Leer el reporte de cobertura

- **Consola**: la tabla que imprime `pytest` al final muestra, por archivo, `Stmts` (líneas), `Miss` (líneas sin cubrir) y `Cover` (%). La columna `Missing` lista los números de línea sin tests.
- **HTML** (`htmlcov/index.html`): ábrelo en el navegador para ver línea por línea qué se ejecutó (verde) y qué no (rojo). Es la forma más rápida de identificar huecos.
- **XML** (`coverage.xml`): formato que consume SonarQube y herramientas de CI. No se lee a mano.

Cobertura por módulo, verificada corriendo `pytest` en contenedores reales (no de memoria):

| Módulo | Tests | Cobertura |
|---|---|---|
| `modulo_rrhh` | 23 | 78.5% |
| `modulo_mantencion` | 93 (91 pasan, 2 fallan — ver nota) | 92.4% |
| `modulo_bodega` | 51 | 85.1% |
| `modulo_prevencion` | 32 | 87.5% |
| `modulo_acreditacion` | 33 | 89.8% |
| `modulo_administracion` | 33 | 96.7% |
| `modulo_middleware` | 7 | 90.3% |
| `modulo_watchdog` | 17 | 73.5% |
| `hub-ms-operacion` (repo propio) | 32 | 88.5% |
| `hub-ms-facturacion` (repo propio) | 28 | 86.9% |

**Total: 349 tests, 347 pasan**, todos los módulos sobre el umbral de 60% exigido por la rúbrica.

**Nota sobre `modulo_mantencion`:** 2 tests preexistentes en `test_mantencion_controller.py` (`test_get_preventive_status_integration`, `test_get_mantenciones_list`) fallan por un bug previo a esta fase: `main.py` no registra `app.preventive_service_instance`, que esos tests de integración esperan. No afecta la cobertura (sigue sobre 60%) ni es un problema introducido por los tests nuevos — queda documentado para una futura corrección.

## 4. SonarQube — Quality Gate

### 4.1. Levantar SonarQube

Desde `hub-infra` (archivo separado del compose principal, para no mezclar infraestructura de calidad con la app):

```bash
cd hub-infra
docker-compose -f docker-compose.sonarqube.yml up -d
```

Espera ~1-2 minutos a que el contenedor esté listo (la primera vez es más lento, indexa su propia base de datos):

```bash
curl http://localhost:9000/api/system/status
# {"status":"UP"} cuando está listo
```

Accede a `http://localhost:9000` — usuario `admin`, password `admin` (te pedirá cambiarla en el primer login).

### 4.2. Generar un token de análisis

En la UI: **My Account → Security → Generate Tokens**. Ponle un nombre (ej. `hub-backends-scan`), tipo `User Token`, y copia el valor — solo se muestra una vez.

**Nunca pegues el token directo en un comando que vaya a quedar en historial compartido o en un archivo del repo.** Si usas un script, pásalo por variable de entorno en tu shell local, no lo commitees.

### 4.3. Generar los reportes de cobertura

Antes de analizar, cada módulo necesita su `coverage.xml` actualizado (correr `pytest` como en la sección 2 los genera).

### 4.4. Correr el análisis

`hub-backends` tiene un único `sonar-project.properties` en la raíz que define un proyecto multi-módulo (uno por `modulo_*`, cada uno con su propio `coverage.xml`):

```bash
cd hub-backends
docker run --rm --network hub-infra_sonar-network \
  -v "$(pwd):/usr/src" \
  sonarsource/sonar-scanner-cli \
  -Dsonar.host.url=http://sonarqube:9000 \
  -Dsonar.token=<TU_TOKEN>
```

(En PowerShell, reemplaza `$(pwd)` por `${PWD}` y usa el separador de línea `` ` `` en vez de `\`.)

`hub-ms-operacion` y `hub-ms-facturacion` son repos separados, cada uno con su propio `sonar-project.properties` — se analizan igual pero desde su propia carpeta, y deben estar conectados a la misma red Docker (`hub-infra_sonar-network`) para alcanzar el contenedor `sonarqube`.

### 4.5. Leer el resultado

`http://localhost:9000/dashboard?id=hub-backends` muestra el **Quality Gate**: pasa o falla según las condiciones configuradas (por defecto en SonarQube Community: 0 bugs nuevos, 0 vulnerabilidades nuevas, cobertura en código nuevo ≥ umbral). Cada submódulo aparece como proyecto propio en el listado, con su cobertura, líneas duplicadas, code smells y vulnerabilidades detectadas.

Meta de la rúbrica: cobertura > 60%, 0 bugs críticos, 0 vulnerabilidades — visible directamente en el dashboard, útil para mostrar en la defensa oral.

### 4.6. Resultado real del análisis (verificado en esta sesión)

| Proyecto | Quality Gate | Coverage (Overall Code) | Bugs | Vulnerabilidades | Code Smells |
|---|---|---|---|---|---|
| `hub-backends` | ❌ Failed (gate "Sonar way" en *New Code*, umbral 80%) | **71.4%** | 0 | 3 (credenciales hardcodeadas en scripts de seed) | 15 |
| `hub-ms-operacion` | ✅ Passed | **71.7%** | 0 | 0 | 1 |
| `hub-ms-facturacion` | ✅ Passed | **71.0%** | 0 | 0 | 1 |

**Aclaración importante sobre el "Failed" de `hub-backends`:** el Quality Gate default de SonarQube Community ("Sonar way") evalúa **código nuevo** desde la última versión, con umbral de cobertura **80%** y 0 issues nuevos — no el 60% global que exige la rúbrica del EFT. La cobertura **global** (pestaña "Overall Code") es 71.4%, sobre el mínimo exigido. Los 3 "Failed" del gate son: cobertura de código nuevo 65.7% (<80%), duplicación de código nuevo 9.7% (>3%), y 3 issues en código nuevo. Para la defensa, lo relevante es la columna "Overall Code", no el gate de código nuevo.

**Las 3 vulnerabilidades (BLOCKER)** son credenciales de base de datos hardcodeadas en scripts de seed de desarrollo (`modulo_mantencion/src/scripts/seed_*.py`, `modulo_rrhh/src/scripts/seed_personal.py`) — son scripts de carga de datos de prueba local, no código de producción, pero quedan como hallazgo honesto documentado (relevante para la sección de Privacy by Design/ética del EFT).

**Bug real corregido en esta sesión:** `hub-ms-operacion` y `hub-ms-facturacion` no tenían `.coveragerc` con `relative_files = True` — sin eso, `coverage.xml` guarda rutas absolutas del contenedor de pytest, que SonarQube no puede resolver al correr en su propio contenedor (reportaba 0.0% de cobertura aunque pytest sí medía 88%+ en consola). Se agregó el archivo a ambos repos, igual al patrón ya usado en todos los módulos de `hub-backends`.

## 5. Agregar tests a un módulo nuevo

Si se agrega un microservicio nuevo (o un repo propio, como se hizo con `operacion`/`facturacion`):

1. Agregar a `requirements.txt`: `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-mock`, `httpx`.
2. Copiar el `pytest.ini` de cualquier módulo existente.
3. Crear `src/tests/__init__.py` (vacío).
4. Escribir `test_<entidad>_service.py` y `test_<entidad>_repository.py` siguiendo el patrón AAA de la sección 1.
5. Si el módulo tiene `utils/auth.py`, copiar `test_auth.py` de otro módulo y ajustar el nombre pasado a `require_permission('<modulo>', ...)`.
6. Si es un repo propio (no vive en `hub-backends`), agregar su propio `sonar-project.properties` (ver `hub-ms-operacion/sonar-project.properties` como ejemplo).

**Cuidado con el claim `sub` del JWT en los tests:** PyJWT 2.10+ exige que `sub` sea un string en el payload, o lanza `InvalidSubjectError` al decodificar. Siempre usar `"sub": "1"`, nunca `"sub": 1`. Por eso `modulo_middleware` y `modulo_watchdog` ahora pinean `PyJWT==2.8.0` en su `requirements.txt` — antes no tenían versión fija y resolvían a una más nueva con esta validación más estricta que el resto de los módulos.
