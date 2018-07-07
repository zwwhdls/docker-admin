import time
import json
import requests
import logging
import urllib.parse as url_util
from requests.adapters import HTTPAdapter

from guardian.config import get_agent_config

LOG = logging.getLogger(__name__)
DEFAULT_HEADERS = {
    'User-Agent': "Guardian Client",
    'Accept-Encoding': ', '.join(('gzip', 'deflate')),
    'Accept': '*/*',
    'Connection': 'keep-alive',
}


class BaseClient(requests.Session):
    def __init__(self, base_url, headers=None):
        super(BaseClient, self).__init__()

        self.base_url = base_url

        self.headers = DEFAULT_HEADERS
        if headers and isinstance(headers, dict):
            self.headers.update(headers)

        self.mount('https://', HTTPAdapter(max_retries=3))
        self.mount('http://', HTTPAdapter(max_retries=3))

    def url(self, path):
        return url_util.urljoin(self.base_url, path)


class MasterProxy(BaseClient):
    def __init__(self, headers):
        super(MasterProxy, self).__init__(
            get_agent_config("AGENT_URL"), headers)


class MasterClient(BaseClient):
    def __init__(self):
        master_url = get_agent_config("master_url")
        token = get_agent_config("agent_token")
        headers = dict(Authorization=token)
        super(MasterClient, self).__init__(master_url, headers)

    def send_heartbeat(self):
        _send = True
        _srv_time = 0
        while _send and _srv_time < 5:
            rsp = self.post(self.url("/node/heartbeat"),
                            json=dict(msg="What can I do for you?", time=time.time()))
            if not rsp.ok:
                return False
            if rsp.status_code == 200:
                content = rsp.json()
                cmd_id, content = self._handle_cmd(self._get_cmd_content(content))
                self._cmd_callback(cmd_id, content)
                _srv_time += 1
                time.sleep(1)
            if rsp.status_code == 204:
                _send = False
        return True

    def _cmd_callback(self, cmd_id, content):
        rsp = self.post(self.url("/node/cmd/{}".format(cmd_id)), json=content)
        return rsp.ok

    @staticmethod
    def _get_cmd_content(json_rsp):
        content = json_rsp['content']

        # todo Decrypt content

        return content

    def _handle_cmd(self, content):
        """
        If master can not access agent
        agent will get cmd from master when send heartbeat
        :param content:
        :return:
        """
        try:
            cmd_id = content['cmd_id']
            path = content['path']
            method = content['method']
            headers = content['headers']
            body = content.get('body')
        except KeyError as e:
            LOG.error("Handle cmd from {}, key error: {}".format(
                self.base_url, e))
            return
        proxy = MasterProxy(headers)
        method_handle = proxy.__getattribute__(str(method).lower())
        if body:
            body = json.dumps(body)
        else:
            body = None
        rsp = method_handle(proxy.url(path), data=body)
        content = {
            "body": rsp.json(),
            "headers": rsp.headers,
            "status_code": rsp.status_code,
        }
        return cmd_id, content
