import threading
from docker.errors import APIError

from guardian.util.logger import Logger
from guardian.util.error import BaseError
from .manager import BaseMode, BaseManager


class ImageError(BaseError):
    pass


class ImageModel(BaseMode):
    FIELDS = ['id', 'labels', 'short_id', 'tags']

    def __init__(self, model):
        super(ImageModel, self).__init__(model)

        self.id = model.id
        self.labels = model.labels
        self.short_id = model.short_id
        self.tags = model.tags

    def tag(self, repository, tag=None, **kwargs):
        try:
            return self.model.tag(repository, tag, **kwargs)
        except APIError as e:
            raise ImageError("Create image tag error: {}".format(e))


class RegistryData(BaseMode):
    FIELDS = ['id', 'short_id']

    def __init__(self, model):
        super(RegistryData, self).__init__(model)

        self.id = model.id
        self.short_id = model.short_id


class ImageManager(BaseManager):
    ERROR_MODEL = ImageError

    def __init__(self, manager):
        super(ImageManager, self).__init__(manager)

        self.collection = self.client.images
        self.model = ImageModel

        self.task = None

    def build(self, *args, **kwargs):
        labels = kwargs.get("labels", {})
        labels.update({
            "Guardian": "image",
            "GuardianImageBuild": "true"
        })
        image, log_gen = self.collection.build(*args, **kwargs)
        self._async_record_log(
            Logger("image_build", image.id), log_gen)
        return self.model(image)

    def list(self, name=None, with_layers=False, get_all=True):
        filters = {}
        if not get_all:
            filters['label'] = "GuardianImageBuild"
        try:
            return super(ImageManager, self).list(
                name=name, all=with_layers, filters=filters)
        except APIError as e:
            raise ImageError("List image error: {}".format(e))

    def pull(self, repository, tag=None, auth_config=None, **kwargs):
        if auth_config:
            assert "username" in auth_config
            assert "password" in auth_config
            kwargs['auth_config'] = auth_config
        try:
            return self.model(self.collection.pull(
                repository, tag, **kwargs))
        except APIError as e:
            raise ImageError("Pull image {}:{} error: {}".format(
                repository, tag or "latest", e))

    def push(self, repository, tag=None, auth_config=None, **kwargs):
        if auth_config:
            assert "username" in auth_config
            assert "password" in auth_config
            kwargs['auth_config'] = auth_config
        try:
            self.collection.push(repository, tag=None, **kwargs)
        except APIError as e:
            raise ImageError("Push image {}:{} error: {}".format(
                repository, tag or "latest", e))

    def get_registry_data(self, name):
        return self.model(
            self.collection.get_registry_data(name))

    def _async_record_log(self, logger, log_gen):
        def _record(_logger, _log_gen):
            for row in _log_gen:
                _logger.record(row)

        task = threading.Thread(
            target=_record, args=(logger, log_gen))
        self.task = task
        task.is_alive()

    def wait_task(self):
        task = self.task
        if not task or not task.is_alive():
            return
        task.join()
