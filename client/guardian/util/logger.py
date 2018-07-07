import os
import time

from guardian.config import LOG_FILE_DIR


class Logger:

    def __init__(self, action_type, resource_id):
        self.action_type = action_type
        self.resource_id = resource_id
        file_name = "{}_{}_{}.log".format(
            action_type, resource_id, time.time())
        self.log_file = os.path.join(LOG_FILE_DIR, file_name.lower())

    def record(self, message):
        self._handle(message)

    def _handle(self, row):
        self.__write_file(row)
        self.__push_stream(row)

    def __write_file(self, row):
        with open(self.log_file) as f:
            f.write(row)

    def __push_stream(self, row):
        pass
