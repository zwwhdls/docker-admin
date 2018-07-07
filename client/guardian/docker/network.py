from guardian.util.error import BaseError
from .manager import BaseMode, BaseManager


class NetworkError(BaseError):
    pass


class NetworkModel(BaseMode):
    FIELDS = ["id", "name", "containers"]

    def __init__(self, model):
        super(NetworkModel, self).__init__(model)

        self.id = model.id
        self.name = model.name
        self.containers = model.containers


class NetworkManager(BaseManager):
    ERROR_MODEL = NetworkError

    def __init__(self, manager):
        super(NetworkManager, self).__init__(manager)

        self.collection = self.client.networks
        self.model = NetworkModel

    def list(self, names=None, ids=None, get_all=False):
        kwargs = dict()
        if not get_all:
            kwargs['filters'] = {
                "labels": ["Guardian=network"],
            }
        if names:
            kwargs['names'] = names
        if ids:
            kwargs['ids'] = ids
        return [self.model(n) for n in self.collection.list(**kwargs)]

    def create(self, name, *args, **kwargs):
        labels = kwargs.get("labels", {})
        labels.update({
            "Guardian": "network",
            "GuardianNetwork": name,
        })
        kwargs['labels'] = labels
        return self.model(self.collection.create(name, *args, **kwargs))
