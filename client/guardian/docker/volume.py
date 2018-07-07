import random
import string

from guardian.util.error import BaseError
from .manager import BaseMode, BaseManager


class VolumeError(BaseError):
    pass


class VolumeModel(BaseMode):
    FIELDS = []

    def __init__(self, model):
        super(VolumeModel, self).__init__(model)

        self.id = model.id
        self.name = model.name


class VolumeManager(BaseManager):
    ERROR_MODEL = VolumeError

    def __init__(self, manager):
        super(VolumeManager, self).__init__(manager)

        self.collection = self.client.volumes
        self.model = VolumeModel

    def list(self, get_all=False):
        kwargs = dict()
        if not get_all:
            kwargs['filters'] = {
                "labels": ["Guardian=volume"]
            }
        return [self.model(v) for v in self.collection.list(**kwargs)]

    def create(self, name=None, *args, **kwargs):
        if not name:
            name = "hdls" + "".join(
                random.sample(string.ascii_lowercase, 8))
        labels = kwargs.get("labels", {})
        labels.update({
            "Guardian": "volume",
            "GuardianVolume": name,
        })
        kwargs['labels'] = labels
        return self.model(self.collection.create(name, *args, **kwargs))
