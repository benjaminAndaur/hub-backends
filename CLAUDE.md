# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Flujo de Git (GitFlow)

Este repo (y los otros dos del Hub: `hub-infra`, `hub-frontends`) usa **GitFlow**. Reglas:

- `main` — solo recibe merges desde `develop` o `release/*`. Representa lo desplegable/estable. **Nunca commitear directo aquí.**
- `develop` — rama de integración. Todo el trabajo nuevo (fixes, features) se commitea o mergea aquí primero.
- `feature/*`, `fix/*` — ramas de trabajo creadas desde `develop`, mergeadas de vuelta a `develop`.
- `release/*` — ramas de preparación de release creadas desde `develop`, mergeadas a `main` y de vuelta a `develop`.
- `hotfix/*` — para bugs urgentes en producción: se crean desde `main`, se mergean a **ambos** `main` y `develop`.

Antes de empezar a trabajar, verificar en qué rama se está parado (`git branch --show-current`). Si hay cambios sin commitear directo en `main`, moverlos a `develop` (o a una rama `fix/*`/`feature/*` desde `develop`) antes de commitear.

## Resumen del proyecto

Microservicios backend (Python/Quart) del Hub Empresarial. Cada módulo es una API independiente que comparte la misma base de datos PostgreSQL (`asdf_db`) pero se despliega como contenedor propio. Ver `README.md` para el detalle de módulos, arquitectura por capas (`models/repository/service/controller`), autenticación JWT y variables de entorno.

Repos relacionados: [`hub-infra`](https://github.com/benjaminAndaur/hub-infra) (nginx, base de datos, `docker-compose.yml`), [`hub-frontends`](https://github.com/benjaminAndaur/hub-frontends).
