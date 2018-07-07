import time

CACHE_TIME = 30


class NodeManager:
    def __init__(self):
        self._load = {
            "cpu": 0,
            "total_mem": 0,
            "used_mem": 0,
        }
        self.expiration = 0
        self.node_info = self._get_node_info()

    def _get_node_info(self):
        return dict()

    def _update_cpu_info(self):
        if int(time.time()) < self.expiration:
            return
        self.expiration = int(time.time()) + CACHE_TIME

    def _update_mem_info(self):
        if int(time.time()) < self.expiration:
            return
        self.expiration = int(time.time()) + CACHE_TIME

    @property
    def load(self):
        self._update_cpu_info()
        self._update_mem_info()
        return self._load

    @property
    def base_info(self):
        return self.node_info

    @property
    def health(self):
        return "health"
