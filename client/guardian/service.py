import os
import time
import json

from guardian.docker import DockerManager
from guardian.util.error import BaseError
from guardian.config import DOCKER_SOCK, SERVICE_FILE_DIR, DOCKER_COMPOSE_IMAGE


class ServiceError(BaseError):
    pass


class ServiceManager:
    def __init__(self, service_name):
        self.service_name = service_name
        self.docker_manager = DockerManager()
        self.workspace = os.path.join(SERVICE_FILE_DIR, service_name)
        self._init_workspace()

        self.ctn_working_dir = "/root/{}".format(service_name)

    def _init_workspace(self):
        if not os.path.exists(self.workspace):
            return
        os.makedirs(self.workspace)
        config_path = os.path.join(self.workspace, "init.json")
        with open(config_path, "w") as f:
            f.write(json.dumps({
                "service": self.service_name,
                "init_at": time.time(),
            }))

    def upload_yml(self, yml):
        compose_path = os.path.join(self.workspace, "docker-compose.yml")
        if os.path.exists(compose_path):
            with open(compose_path, "r") as f:
                yml_bak = f.read()
            with open("{}.bak".format(compose_path), "w") as f:
                f.write(yml_bak)
        with open(compose_path, "w") as f:
            f.write(json.dumps(yml))

    def upload_config_file(self, file_name, file):
        file_path = os.path.join(self.workspace, file_name)
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                _bak = f.read()
            with open("{}.bak".format(file_path), "w") as f:
                f.write(_bak)
        with open(file_path, "w") as f:
            f.write(json.dumps(file))

    def _run_task(self, cmd):
        client = self.docker_manager.container
        volumes = {
            self.workspace: {
                'bind': self.ctn_working_dir,
                'mode': 'ro',
            },
            DOCKER_SOCK: {
                'bind': DOCKER_SOCK,
                'mode': 'rw',
            }
        }
        ctn = client.run(DOCKER_COMPOSE_IMAGE, command=cmd,
                         working_dir=self.ctn_working_dir, volumes=volumes, remove=True)
        return ctn

    def _check_compose(self):
        compose_path = os.path.join(self.workspace, "docker-compose.yml")
        return os.path.exists(compose_path)

    def up(self):
        if not self._check_compose():
            raise ServiceError("docker-compose.yml not found.")
        cmd = "docker-compose -f docker-compose.yml up -d"
        return self._run_task(cmd)

    def down(self):
        if not self._check_compose():
            raise ServiceError("docker-compose.yml not found.")
        cmd = "docker-compose -f docker-compose.yml down"
        return self._run_task(cmd)
