#!/usr/bin/env python3
"""Genera un nuevo modulo_* a partir del arquetipo (_arquetipo_modulo/).

Uso:
    python scaffold.py
    (responde las preguntas interactivas de cookiecutter: module_name,
    entity_name, port, etc. Genera el módulo en el directorio actual.)

Equivalente conceptual a un Maven Archetype: en vez de escribir a mano
main.py + las 4 capas + Dockerfile + tests para cada microservicio nuevo,
se genera todo pre-configurado y consistente con el resto del Hub.
"""

from cookiecutter.main import cookiecutter

if __name__ == "__main__":
    cookiecutter("_arquetipo_modulo")
