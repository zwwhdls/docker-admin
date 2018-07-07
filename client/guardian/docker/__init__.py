import docker

from guardian.config import DOCKER_SOCK


class DockerInfoModel:

    def __init__(self, info):
        pass

    def render(self):
        pass


class DockerManager:

    def __init__(self):
        self.client = docker.DockerClient(base_url=DOCKER_SOCK)

    @property
    def container(self):
        from .container import ContainerManager
        return ContainerManager(self)

    @property
    def image(self):
        from .image import ImageManager
        return ImageManager(self)

    @property
    def network(self):
        from .network import NetworkManager
        return NetworkManager(self)

    @property
    def volume(self):
        from .volume import VolumeManager
        return VolumeManager(self)

    def info(self):
        pass

    def prune(self):
        pass
