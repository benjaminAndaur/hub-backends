from quart import Blueprint, request, jsonify

from src.utils.auth import login_required, require_permission


def create_{{cookiecutter.entity_slug}}_blueprint(service):
    bp = Blueprint('{{cookiecutter.entity_slug}}', __name__)

    @bp.route('/health', methods=['GET'])
    async def health():
        return jsonify({"status": "ok", "service": "{{cookiecutter.module_slug}}"}), 200

    @bp.route('/{{cookiecutter.entity_table}}', methods=['POST'])
    @login_required
    @require_permission('{{cookiecutter.permission_key}}', 'edit')
    async def crear():
        data = await request.get_json()
        creado = await service.crear(data)
        return jsonify(creado.model_dump(mode="json")), 201

    @bp.route('/{{cookiecutter.entity_table}}', methods=['GET'])
    @login_required
    @require_permission('{{cookiecutter.permission_key}}', 'view')
    async def obtener_todos():
        entidades = await service.obtener_todos()
        return jsonify([e.model_dump(mode="json") for e in entidades])

    @bp.route('/{{cookiecutter.entity_table}}/<int:id>', methods=['GET'])
    @login_required
    @require_permission('{{cookiecutter.permission_key}}', 'view')
    async def obtener_por_id(id):
        entidad = await service.obtener_por_id(id)
        if entidad is None:
            return jsonify({"error": "No encontrado"}), 404
        return jsonify(entidad.model_dump(mode="json"))

    @bp.route('/{{cookiecutter.entity_table}}/<int:id>', methods=['PUT'])
    @login_required
    @require_permission('{{cookiecutter.permission_key}}', 'edit')
    async def actualizar(id):
        data = await request.get_json()
        actualizado = await service.actualizar(id, data)
        if actualizado is None:
            return jsonify({"error": "No encontrado"}), 404
        return jsonify(actualizado.model_dump(mode="json"))

    @bp.route('/{{cookiecutter.entity_table}}/<int:id>', methods=['DELETE'])
    @login_required
    @require_permission('{{cookiecutter.permission_key}}', 'edit')
    async def eliminar(id):
        eliminado = await service.eliminar(id)
        if not eliminado:
            return jsonify({"error": "No encontrado"}), 404
        return '', 204

    return bp
