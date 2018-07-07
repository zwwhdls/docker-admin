from flask_script import Manager

from guardian.app import create_app
from guardian.util.install import Installer

app = create_app()
manager = Manager(app)


@manager.command
def install(install_token):
    """
    Install docker-proxy agent from master.
    """
    installer = Installer(install_token)
    installer.install()


@manager.command
def start():
    """
    Run agent.
    :return:
    """


if __name__ == "__main__":
    manager.run()
