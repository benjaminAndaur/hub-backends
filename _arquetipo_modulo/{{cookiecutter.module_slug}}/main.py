import asyncio
import os
from quart import Quart, g
from quart_cors import cors
from quart_schema import QuartSchema
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.repository.{{cookiecutter.entity_slug}}_repository import {{cookiecutter.entity_name}}Repository
from src.service.{{cookiecutter.entity_slug}}_service import {{cookiecutter.entity_name}}Service
from src.controller.{{cookiecutter.entity_slug}}_controller import create_{{cookiecutter.entity_slug}}_blueprint

app = Quart(__name__)
app = cors(app, allow_origin="*",
           allow_headers=["Content-Type", "Authorization"],
           allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

QuartSchema(
    app,
    info={"title": "{{cookiecutter.module_name}}", "version": "1.0"},
    swagger_ui_path="/docs",
)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://admin:admin123@db-global:5432/asdf_db")

_engine = None
_async_session = None
_loop = None


def get_async_session():
    global _engine, _async_session
    if _async_session is None:
        _engine = create_async_engine(DATABASE_URL, echo=True)
        _async_session = async_sessionmaker(_engine, expire_on_commit=False)
    return _async_session()


@app.before_serving
async def setup_db():
    global _engine, _async_session, _loop
    current_loop = asyncio.get_running_loop()
    if _engine is None or _loop != current_loop:
        _engine = create_async_engine(DATABASE_URL, pool_size=10, max_overflow=20, pool_pre_ping=True, echo=False)
        _async_session = async_sessionmaker(_engine, expire_on_commit=False)
        _loop = current_loop

        from src.models.base import Base
        from src.models.{{cookiecutter.entity_slug}}_db import {{cookiecutter.entity_name}}DB  # noqa: F401

    retries = 10
    while retries > 0:
        try:
            async with _engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("Successfully connected to database.")
            break
        except Exception as e:
            retries -= 1
            print(f"Database connection failed. Retrying... ({retries} left). Error: {e}")
            if retries == 0:
                raise e
            await asyncio.sleep(5)


@app.before_request
async def inject_dependencies():
    session = get_async_session()
    repo = {{cookiecutter.entity_name}}Repository(session)
    service = {{cookiecutter.entity_name}}Service(repo)
    g.service = service
    g.current_session = session


@app.after_request
async def cleanup(response):
    if hasattr(g, 'current_session'):
        await g.current_session.close()
    return response


@app.errorhandler(Exception)
async def handle_exception(e):
    app.logger.error(f"Global error in {{cookiecutter.module_name}}: {str(e)}")
    return {"error": "Internal Server Error", "message": str(e)}, 500


bp = create_{{cookiecutter.entity_slug}}_blueprint(type('ServiceProxy', (), {
    'crear': lambda self, data: g.service.crear(data),
    'obtener_todos': lambda self: g.service.obtener_todos(),
    'obtener_por_id': lambda self, id: g.service.obtener_por_id(id),
    'actualizar': lambda self, id, data: g.service.actualizar(id, data),
    'eliminar': lambda self, id: g.service.eliminar(id),
})())

app.register_blueprint(bp, url_prefix='/api/v1/{{cookiecutter.entity_table}}')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port={{cookiecutter.port}})
