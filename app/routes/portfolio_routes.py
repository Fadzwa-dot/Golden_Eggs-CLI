from flask import Blueprint, request, jsonify
from app.service.portfolio_service import PortfolioService

portfolio_bp = Blueprint("portfolio", __name__, url_prefix="/api/portfolios")
svc = PortfolioService()


def _portfolio_to_dict(p):
    return {
        "id": p.id,
        "name": getattr(p, "name", None),
        "description": getattr(p, "description", None),
        "owner_username": getattr(p, "owner_username", None),
    }


@portfolio_bp.route("/", methods=["GET"])
def list_portfolios():
    owner = request.args.get("owner")
    if owner:
        portfolios = svc.get_portfolios_by_username(owner)
    else:
        # Return all portfolios when no owner filter provided
        portfolios = svc.list_all_portfolios()
    return jsonify([_portfolio_to_dict(p) for p in portfolios])


@portfolio_bp.route("/<int:portfolio_id>", methods=["GET"])
def get_portfolio(portfolio_id):
    owner = request.args.get("owner")
    if not owner:
        return jsonify({"error": "owner query parameter required"}), 400
    p = svc.get_portfolio(owner, portfolio_id)
    if not p:
        return jsonify({"error": "portfolio not found"}), 404
    # include investments if present
    investments = []
    try:
        for inv in getattr(p, "investments", []) or []:
            investments.append({
                "id": getattr(inv, "id", None),
                "security_ticker": getattr(inv, "security_ticker", None),
                "quantity": getattr(inv, "quantity", None),
                "purchase_price": getattr(inv, "purchase_price", None),
            })
    except Exception:
        investments = []
    result = _portfolio_to_dict(p)
    result["investments"] = investments
    return jsonify(result)


@portfolio_bp.route("/", methods=["POST"])
def create_portfolio():
    data = request.get_json() or {}
    name = data.get("name")
    description = data.get("description", "")
    owner = data.get("owner")
    if not name or not owner:
        return jsonify({"error": "name and owner are required"}), 400
    try:
        p = svc.create_portfolio(owner, name, description)
        return jsonify(_portfolio_to_dict(p)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@portfolio_bp.route("/<int:portfolio_id>", methods=["DELETE"])
def delete_portfolio(portfolio_id):
    owner = request.args.get("owner")
    if not owner:
        return jsonify({"error": "owner query parameter required"}), 400
    try:
        svc.delete_portfolio(owner, portfolio_id)
        return jsonify({"message": "deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@portfolio_bp.route("/<int:portfolio_id>/add", methods=["POST"])
def add_investment(portfolio_id):
    data = request.get_json() or {}
    owner = data.get("owner")
    ticker = data.get("ticker")
    quantity = data.get("quantity")
    purchase_price = data.get("purchase_price")
    if not owner or not ticker or quantity is None or purchase_price is None:
        return jsonify({"error": "owner, ticker, quantity, purchase_price required"}), 400
    try:
        inv = svc.add_investment(owner, portfolio_id, ticker, int(quantity), float(purchase_price))
        return jsonify({"id": getattr(inv, "id", None)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@portfolio_bp.route("/<int:portfolio_id>/harvest", methods=["POST"])
def harvest_investment(portfolio_id):
    data = request.get_json() or {}
    owner = data.get("owner")
    ticker = data.get("ticker")
    quantity = data.get("quantity")
    sale_price = data.get("sale_price")
    if not owner or not ticker or quantity is None or sale_price is None:
        return jsonify({"error": "owner, ticker, quantity, sale_price required"}), 400
    try:
        proceeds = svc.harvest_investment(owner, portfolio_id, ticker, int(quantity), float(sale_price))
        return jsonify({"proceeds": proceeds}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
