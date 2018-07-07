from flask import Blueprint

from guardian.service import ServiceManager

service_bp = Blueprint("service_v1", __name__, url_prefix="/v1/service")


@service_bp.route("/<service_name>/config-file", methods=['POST'])
def upload_service_config_file(service_name):
    manager = ServiceManager(service_name)


@service_bp.route("/<service_name>/up", methods=['POST'])
def up_compose_service(service_name):
    manager = ServiceManager(service_name)


@service_bp.route("/<service_name>/down", methods=['POST'])
def down_compose_service(service_name):
    manager = ServiceManager(service_name)
