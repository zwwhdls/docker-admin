from flask import Blueprint, jsonify

from guardian.node import NodeManager

node_bp = Blueprint("node_v1", __name__, url_prefix="/v1/node")
node_manager = NodeManager()


@node_bp.route("/info", methods=["GET"])
def get_node_info():
    return jsonify(node_manager.base_info)


@node_bp.route("/health", methods=["GET"])
def get_node_health():
    return jsonify({"status": node_manager.health})


@node_bp.route("/load", methods=["GET"])
def get_node_load():
    return jsonify(node_manager.load)
