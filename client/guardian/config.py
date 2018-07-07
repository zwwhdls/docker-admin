import json


class ConfigError(Exception):
    pass


# Docker config
DOCKER_SOCK = "unix:///var/run/docker.sock"

# Agent config
CONFIG_FILE = {}
CONFIG_FILE_DIR = "/etc/DockerProxy"
CONFIG_FILE_PATH = "/etc/DockerProxy/agent.conf"
LOG_FILE_DIR = "/var/log/DockerProxy"
SECRET_KEY = "DANGEROUS"

# Service config
SERVICE_FILE_DIR = "/var/DockerProxy/service"
DOCKER_COMPOSE_IMAGE = ""

# Job config
SCHEDULER_JOBS = [
    {
        'id': 'send_heartbeat_job',
        'func': 'guardian.job.task:send_heartbeat',
        'args': None,
        'trigger': 'interval',
        'seconds': 30
    },
    {
        'id': 'prune_docker_file_job',
        'func': 'guardian.job.task:prune_docker_file',
        'args': None,
        'trigger': 'interval',
        'seconds': 60 * 60 * 24
    },
]


def get_agent_config(config_name, default=None):
    global CONFIG_FILE
    if not CONFIG_FILE:
        with open(CONFIG_FILE_PATH) as f:
            _config = f.read()
        try:
            _config = json.loads(_config)
        except ValueError:
            pass
        CONFIG_FILE = _config
    if config_name in CONFIG_FILE or default:
        return CONFIG_FILE.get(config_name) or default
    raise ConfigError("Config {} not found".format(config_name))
