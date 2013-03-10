from fabric.api import *

env.hosts = ['django@beta.partici.pe:17566']

def git_pull():
    run("cd /home/django/participe/MVP/; git pull origin master")

def install_requirements():
    with cd("/home/django/participe/MVP"):
        run("source /home/django/participe/ve/bin/activate; pip install -r requirements.txt")

def stop_all():
    sudo("service nginx stop")
    sudo("service supervisor stop")

def start_all():
    sudo("service nginx start")
    sudo("service supervisor start")

def schema_migration():
    with settings(warn_only=True):
        run("source /home/django/participe/ve/bin/activate && /home/django/participe/MVP/manage.py syncdb")
        run("source /home/django/participe/ve/bin/activate && /home/django/participe/MVP/manage.py schemamigration account --auto")
        run("source /home/django/participe/ve/bin/activate && /home/django/participe/MVP/manage.py schemamigration organization --auto")
        run("source /home/django/participe/ve/bin/activate && /home/django/participe/MVP/manage.py schemamigration challenge --auto")
        run("source /home/django/participe/ve/bin/activate && /home/django/participe/MVP/manage.py migrate account ")
        run("source /home/django/participe/ve/bin/activate && /home/django/participe/MVP/manage.py migrate organization")
        run("source /home/django/participe/ve/bin/activate && /home/django/participe/MVP/manage.py migrate challenge")

def get_text():
    with cd("/home/django/participe/MVP/participe"):
        run("source /home/django/participe/ve/bin/activate && ../manage.py compilemessages")

def deploy():
    stop_all()
    git_pull()
    install_requirements()
    schema_migration()
    get_text()
    start_all()

