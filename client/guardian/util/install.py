import json
import time
import logging
import base64
from aead import AEAD

from guardian.docker import DockerManager
from guardian.config import SECRET_KEY, DOCKER_SOCK, CONFIG_FILE_DIR, \
    CONFIG_FILE_PATH, LOG_FILE_DIR, SERVICE_FILE_DIR

LOG = logging.getLogger("Installer")
TOKEN_SERIALIZER = AEAD(base64.urlsafe_b64encode(str(SECRET_KEY).encode()[:32]))


class InstallError(Exception):
    pass


class Installer:

    def __init__(self, install_token):
        self.install_token = install_token
        self.docker_manager = DockerManager()

    def install(self):
        LOG.info("Start install agent")
        self._render_config_file()
        LOG.info("Write config to {}".format(CONFIG_FILE_PATH))
        service_id = self._create_agent_service()
        LOG.info("Create agent finish.")
        self._check_service_status(service_id)
        LOG.info("Install success.")

    def _render_config_file(self):
        LOG.info("Pares Install Token.")
        data = self._pares_token(self.install_token)
        with open(CONFIG_FILE_PATH, "w") as f:
            f.write(json.dumps(data))
        LOG.info("Master Url: {}".format(data['master_url']))
        LOG.info("Agent Id: {}".format(data['agent_id']))

    def _get_current_image(self):
        client = self.docker_manager.container
        ctn = client.list(get_all=True)
        for c in ctn:
            if not str(c.cmd).startswith("python service.py install"):
                continue
            return c.image

    def _create_service(self, docker_image):
        client = self.docker_manager.container
        cmd = "python service.py start"
        ports = {'18080/tcp': 5000}
        volumes = {
            # task log dir
            LOG_FILE_DIR: {
                'bind': LOG_FILE_DIR,
                'mode': 'rw',
            },
            # config file dir
            CONFIG_FILE_DIR: {
                'bind': CONFIG_FILE_DIR,
                'mode': 'rw',
            },
            # service file dir
            SERVICE_FILE_DIR: {
                'bind': SERVICE_FILE_DIR,
                'mode': 'rw',
            },
            # docker sock path
            DOCKER_SOCK: {
                'bind': DOCKER_SOCK,
                'mode': 'rw',
            }
        }
        ctn = client.run(docker_image, command=cmd, ports=ports, volumes=volumes)
        return ctn.id

    def _check_service_status(self, service_id):
        LOG.info("Ready to check service status, sleep 5s")
        time.sleep(5)
        client = self.docker_manager.container
        ctn = client.get(service_id)
        return ctn.status == "running"

    def _create_agent_service(self):
        docker_image = self._get_current_image()
        LOG.info("Get Agent image: {}".format(docker_image))
        service_id = self._create_service(docker_image)
        LOG.info("Run Agent: {}".format(service_id))
        return service_id

    @staticmethod
    def _pares_token(install_token):
        try:
            payload = TOKEN_SERIALIZER.decrypt(install_token, b"docker-proxy")
            payload = json.loads(payload.decode())
            if not payload.get("agent_id"):
                raise ValueError("agent info not found")
        except ValueError:
            raise InstallError("Install token is wrong.")
        return dict(
            master_url=payload['master_url'],
            agent_token=payload['agent_token'],
            agent_id=payload['agent_id'],
        )
