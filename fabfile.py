from fabric.api import *

env.hosts = ['django@beta.partici.pe:17566']

def git_pull():
    run("cd /home/django/participe/MVP/; git pull origin master")

def stop_all():
    sudo("service nginx stop")
    sudo("service supervisor stop")

def start_all():
    sudo("service nginx start")
    sudo("service supervisor start")

def schema_migration():
    with settings(warn_only=True):
        run("/home/django/participe/MVP/manage.py schemamigration account --auto")
        run("/home/django/participe/MVP/manage.py schemamigration organization --auto")
        run("/home/django/participe/MVP/manage.py schemamigration challenge --auto")
        run("/home/django/participe/MVP/manage.py migrate account ")
        run("/home/django/participe/MVP/manage.py migrate organization")
        run("/home/django/participe/MVP/manage.py migrate challenge")

def deploy():
    stop_all()
    git_pull()
    schema_migration()
    start_all()

