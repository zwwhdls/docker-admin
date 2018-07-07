from flask import Blueprint, jsonify, request

from guardian.docker import DockerManager
from guardian.util.decorator import parameter_validator

docker_bp = Blueprint("docker_v1", __name__, url_prefix="/v1/docker")

PULL_IMAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "repository": {"type": "string"},
        "tag": {"type": "string"},
        "auth_config": {
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "password": {"type": "string"},
            },
            "required": ['username', 'password'],
        },
    },
    "required": ['repository']
}
RUN_CONTAINER_SCHEMA = {
    "type": "object",
    "properties": {
        "image": {"type": "string"},
        "name": {"type": "string"},
        "command": {"type": "string"},
        "working_dir": {"type": "string"},
        "remove": {"type": "boolean"},
        "network": {"type": "string"},
        "ports": {"type": "object"},
        "volume": {"type": "object"},
    },
    "required": ['image']
}
CREATE_VOLUME_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
    },
    "required": ["name"]
}
CREATE_NETWORK_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
    }
}


@docker_bp.route("/info", methods=['GET'])
def get_docker_info():
    manager = DockerManager()
    info = manager.info()
    return jsonify(info.render())


@docker_bp.route("/images", methods=['GET'])
def get_docker_images():
    manager = DockerManager()
    client = manager.image
    images = client.list()
    return jsonify([i.render() for i in images])


@docker_bp.route("/images", methods=['POST'])
@parameter_validator(PULL_IMAGE_SCHEMA)
def pull_docker_images():
    manager = DockerManager()
    client = manager.image
    data = request.json
    repository = data['repository']
    tag = data.get("tag") or "latest"
    auth_config = data.get("auth_config")
    image = client.pull(repository=repository, tag=tag, auth_config=auth_config)
    return jsonify(image.render())


@docker_bp.route("/containers", methods=['GET'])
def get_docker_container():
    manager = DockerManager()
    client = manager.container
    ctn = client.list()
    return jsonify([c.render() for c in ctn])


@docker_bp.route("/containers", methods=['POST'])
@parameter_validator(RUN_CONTAINER_SCHEMA)
def run_docker_container():
    manager = DockerManager()
    client = manager.container
    data = request.json
    image = data["image"]
    cmd = data.get("command")
    ports = data.get("ports")
    network = data.get("network")
    volume = data.get("volume")
    remove = data.get("remove") or False
    working_dir = data.get("working_dir")
    name = data.get("name")
    ctn = client.run(image=image, name=name, command=cmd,
                     ports=ports, network=network, volumes=volume,
                     remove=remove, working_dir=working_dir)
    return jsonify(ctn.render())


@docker_bp.route("/networks", methods=['GET'])
def get_docker_networks():
    manager = DockerManager()
    client = manager.network
    nets = client.list()
    return jsonify([n.render() for n in nets])


@docker_bp.route("/networks", methods=['POST'])
@parameter_validator(CREATE_NETWORK_SCHEMA)
def create_docker_networks():
    manager = DockerManager()
    client = manager.network
    data = request.json
    net = client.create(data['name'])
    return jsonify(net.render())


@docker_bp.route("/volumes", methods=['GET'])
def get_docker_networks():
    manager = DockerManager()
    client = manager.volume
    vs = client.list()
    return jsonify([v.render() for v in vs])


@docker_bp.route("/volumes", methods=['POST'])
@parameter_validator(CREATE_VOLUME_SCHEMA)
def create_docker_networks():
    manager = DockerManager()
    client = manager.volume
    data = request.json
    volume = client.create(name=data.get("name"))
    return jsonify(volume.render())
