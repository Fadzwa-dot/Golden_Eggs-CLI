from flask import Blueprint, request, jsonify
from app.service.user_service import UserService

user_bp = Blueprint("users", __name__, url_prefix="/api/users")
svc = UserService()


def _user_to_dict(u):
    return {
        "username": u.username,
        "first_name": getattr(u, "first_name", None),
        "last_name": getattr(u, "last_name", None),
        "balance": getattr(u, "balance", None),
        "role": getattr(u, "role", None),
    }


@user_bp.route("/", methods=["GET"])
def list_users():
    users = svc.list_users()
    return jsonify([_user_to_dict(u) for u in users])


@user_bp.route("/<username>", methods=["GET"])
def get_user(username):
    users = svc.list_users()
    for u in users:
        if u.username == username:
            return jsonify(_user_to_dict(u))
    return jsonify({"error": "user not found"}), 404


@user_bp.route("/", methods=["POST"])
def create_user():
    data = request.get_json() or {}
    try:
        user = svc.create_user(
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            username=data.get("username"),
            password=data.get("password"),
            balance=float(data.get("balance", 0.0)),
            role=data.get("role", "customer"),
        )
        return jsonify(_user_to_dict(user)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@user_bp.route("/<username>", methods=["DELETE"])
def delete_user(username):
    try:
        svc.delete_user(username)
        return jsonify({"message": f"User {username} deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
