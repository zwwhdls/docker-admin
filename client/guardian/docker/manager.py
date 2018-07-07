from docker.errors import APIError


class BaseMode:
    FIELDS = None

    def __init__(self, model):
        self.model = model

    def __getattr__(self, item):
        return self.model.__getattr__(item)

    def render(self):
        data = {}
        for k in self.FIELDS:
            data[k] = self.__getattribute__(k)
        return data


class BaseManager:
    ERROR_MODEL = None

    def __init__(self, docker_manager):
        self.docker_manager = docker_manager
        self.client = self.docker_manager.client

        # Get Collection Obj by type in docker client
        self.collection = None

        # Render docker model from docker-py model
        self.model = None

    def list(self, *args, **kwargs):
        assert self.collection and self.model
        try:
            return [self.model(i)
                    for i in self.collection.list(*args, **kwargs)]
        except APIError as e:
            raise self.ERROR_MODEL("List {} error: {}".format(
                self.model.__class__.__name__, e))

    def get(self, key):
        assert self.collection and self.model
        try:
            return self.model(self.collection.get(key))
        except APIError as e:
            raise self.ERROR_MODEL("Get {} by key {} error: {}".format(
                self.model.__class__.__name__, key, e))

    def create(self, *args, **kwargs):
        assert self.collection and self.model
        try:
            return self.model(self.collection.create(*args, **kwargs))
        except APIError as e:
            raise self.ERROR_MODEL("Create {} error: {}".format(
                self.model.__class__.__name__, e))

    def __getattr__(self, item):
        return self.collection.__getattr__(item)
