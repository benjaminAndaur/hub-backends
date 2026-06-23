#!/bin/bash
# Equivalente a "make lint" / Checkstyle: corre Ruff (errores/estilo) y
# Black (formato) contra todo hub-backends. Falla si hay algo por corregir.
set -e
echo "==> ruff check"
ruff check .
echo "==> black --check"
black --check .
echo "OK: lint limpio"
