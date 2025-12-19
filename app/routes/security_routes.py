from flask import Blueprint, jsonify
from app.service.security_service import SecurityService

security_bp = Blueprint("security", __name__, url_prefix="/api/securities")
svc = SecurityService()


def _sec_to_dict(s):
    return {"ticker": s.ticker, "name": getattr(s, "name", None), "price": getattr(s, "price", None)}


@security_bp.route("/", methods=["GET"])
def list_securities():
    secs = svc.list_securities()
    return jsonify([_sec_to_dict(s) for s in secs])
