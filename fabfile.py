from fabric.api import *

env.hosts = ['participe@participe.ch']


def git_pull():
    run("cd /home/participe/MVP/; git pull origin master")


def install_requirements():
    with cd("/home/participe/MVP"):
        run("source /home/participe/venv/bin/activate; pip install -r requirements.txt")


def stop_all():
    sudo("service nginx stop")
    sudo("service supervisor stop")


def start_all():
    sudo("service nginx start")
    sudo("service supervisor start")


def schema_migration():
    with settings(warn_only=True):
        run("source /home/participe/venv/bin/activate && /home/participe/MVP/manage.py syncdb")
        run("source /home/participe/venv/bin/activate && /home/participe/MVP/manage.py schemamigration account --auto")
        run("source /home/participe/venv/bin/activate && /home/participe/MVP/manage.py schemamigration organization --auto")
        run("source /home/participe/venv/bin/activate && /home/participe/MVP/manage.py schemamigration challenge --auto")
        run("source /home/participe/venv/bin/activate && /home/participe/MVP/manage.py migrate account ")
        run("source /home/participe/venv/bin/activate && /home/participe/MVP/manage.py migrate organization")
        run("source /home/participe/venv/bin/activate && /home/participe/MVP/manage.py migrate challenge")


def get_text():
    with cd("/home/participe/MVP/participe"):
        run("source /home/participe/venv/bin/activate && ../manage.py compilemessages")


def deploy():
    stop_all()
    git_pull()
    install_requirements()
    schema_migration()
    get_text()
    start_all()

