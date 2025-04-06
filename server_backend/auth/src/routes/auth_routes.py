from flask import Blueprint, request, jsonify
from src.services.auth_service import login_user, generate_token
from src.services.auth_service import register_user
from src.services.auth_service import initiate_password_reset
from src.services.auth_service import reset_password_by_token
from jwt import ExpiredSignatureError, InvalidTokenError
import jwt
from src.config.config import Config


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "oks"}), 200

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON requerido"}), 400

    username = data.get('username')
    password = data.get('password')
    ip = request.remote_addr

    if not username or not password:
        return jsonify({"error": "username y password son requeridos"}), 400

    result, status = login_user(username, password, ip)
    return jsonify(result), status

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    nombre = data.get("nombre")
    password = data.get("password")
    ip = request.remote_addr

    if not all([email, nombre, password]):
        return {"error": "Faltan campos requeridos"}, 400

    result, status = register_user(email, nombre, password, ip)
    return result, status

@auth_bp.route('/validate', methods=['POST'])
def validate_token():


    data = request.get_json()
    token = data.get("token")

    if not token:
        return jsonify({"error": "Token requerido"}), 400

    try:
        decoded = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
        return jsonify({"valid": True, "username": decoded.get("sub")}), 200
    except ExpiredSignatureError:
        return jsonify({"valid": False, "error": "Token expirado"}), 401
    except InvalidTokenError:
        return jsonify({"valid": False, "error": "Token inválido"}), 401

@auth_bp.route('/recover', methods=['POST'])
def recover():
    # TODO verificar cuand una username tenga un user con un proceso abierto y bloquear el intento de mas de tres veces 

    data = request.get_json()
    username = data.get("username")
    ip = request.remote_addr
    if not username:
        return jsonify({"error": "username requerido"}), 400

    result, status = initiate_password_reset(username,ip)
    return jsonify(result), status


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    

    token = request.args.get("token")
    data = request.get_json()
    new_password = data.get("new_password") if data else None

    if not token or not new_password:
        return jsonify({"error": "token en la URL y nueva contraseña en el body son requeridos"}), 400

    result, status = reset_password_by_token(token, new_password)
    return jsonify(result), status
