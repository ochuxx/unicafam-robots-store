from flask import Blueprint, current_app, jsonify, request

from .services.gas_client import post_to_gas

api = Blueprint("api", __name__)


@api.get("/ping")
def ping():
    return jsonify({"message": "pong"})


@api.post("/robots")
def create_robot():
    payload = request.get_json(silent=True) or {}
    if not payload:
        return jsonify({"error": "Missing JSON body"}), 400

    gas_url = current_app.config.get("GAS_URL", "")
    gas_response = post_to_gas(gas_url, payload)

    if gas_response is None:
        return jsonify({"status": "queued", "detail": "GAS_URL not configured"}), 202

    return jsonify({
        "status": "forwarded",
        "gas_status": gas_response.status_code,
    }), 200


@api.post("/echo")
def echo():
    payload = request.get_json(silent=True) or {}
    return jsonify({"received": payload})
