from flask_apscheduler import APScheduler

scheduler = APScheduler()


def send_heartbeat():
    from guardian.util.client import MasterClient
    client = MasterClient()
    client.send_heartbeat()


def prune_docker_file():
    from guardian.docker import DockerManager
    manager = DockerManager()
    manager.prune()

