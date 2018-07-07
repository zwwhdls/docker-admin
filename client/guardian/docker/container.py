import string
import random
from docker.errors import APIError

from guardian.util.error import BaseError
from .manager import BaseMode, BaseManager


class ContainerError(BaseError):
    pass


class ContainerModel(BaseMode):
    FIELDS = ['id', 'image', 'labels', 'status', 'cmd']

    def __init__(self, model):
        super(ContainerModel, self).__init__(model)

        self.id = model.id
        self.image = model.image
        self.labels = model.labels
        self.status = model.status
        self.cmd = ""


class ContainerManager(BaseManager):
    ERROR_MODEL = ContainerError

    def __init__(self, manager):
        super(ContainerManager, self).__init__(manager)

        self.collection = self.client.containers
        self.model = ContainerModel

    def run(self, image, name=None, command=None, ports=None, network=None,
            volumes=None, working_dir=None, remove=False, **kwargs):
        if not name:
            name = "hdls_{}".format(
                "".join(random.sample(string.ascii_lowercase, 8)))
        labels = kwargs.get("labels", {})
        labels.update({
            "Guardian": "container",
            "GuardianContainer": name,
        })
        kwargs['name'] = name
        kwargs['detach'] = True
        kwargs['labels'] = labels
        kwargs['restart_policy'] = {"Name": "always", "MaximumRetryCount": 10}

        try:
            return self.model(self.collection.run(
                image, command=command, ports=ports, network=network,
                volumes=volumes, working_dir=working_dir, remove=remove, **kwargs))
        except APIError as e:
            raise ContainerError("Run container error: {}".format(e))

    def list(self, get_all=False, **kwargs):
        filters = kwargs.get("filters", {})
        if not get_all:
            filters.update({
                "label": "Guardian=container"
            })
        try:
            return [self.model(ctn)
                    for ctn in self.collection.list(all=True, filters=filters, **kwargs)]
        except APIError as e:
            raise ContainerError("Run container error: {}".format(e))
