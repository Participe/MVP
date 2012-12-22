It provides information on how to configure the Django/Python development
environment from scratch on a bare operating system.
Guide was based on bitter experience.
The basis is taken of so-called "Amazon Linux AMI". Where it is possible,
examples on using "yum" (Fedora/Redhat/CentOS) and "apt-get" (Debian/Ubuntu)
package managers are provided. Otherwise, follow the installation instructions.

0. Presets: 

        sudo <yum|apt-get> install gcc
        sudo <yum|apt-get> install python-setuptools

        sudo yum install python-setuptools-devel
    or  ...

        sudo yum install python-devel
    or  sudo apt-get install python-dev
    
1. Installing and configuring PostgreSQL (optional: use SQLite instead):
1.1 Install PostgreSQL:

        sudo yum install postgresql postgresql-server postgresql-devel
    or  sudo apt-get install postgresql libpq-dev

1.2 Create PostgreSQL data directory:

        sudo chkconfig postgresql on
        sudo service postgresql initdb
        sudo service postgresql start

1.3 Create PostgreSQL user account. It can be created, but it would be good
    to change a password:
 
        sudo adduser postgres
        sudo passwd postgres
        ...
        
1.4 Grant your local user with privileges. To do this, change user to
    'postgres' and set-up 'pg_hba.conf':

        su -- postgres
        cd /usr/share/pgsql
        sudo cp pg_hba.conf.sample pg_hba.conf
        sudo <vi|nano> pg_hba.conf
    
    After set-up 'pg_hba.conf' should contain following:
    
        local   all         postgres                          trust
        local   all         <YOUR_USERNAME>                   trust

        # TYPE  DATABASE    USER        CIDR-ADDRESS          METHOD
        # "local" is for Unix domain socket connections only
        local   all         all                               md5
        # IPv4 local connections:
        host    all         all         127.0.0.1/32          md5
        # IPv6 local connections:
        host    all         all         ::1/128               md5
        
    Don't forget to replace <YOUR_USERNAME> with your local username and
    restart PostgreSQL server:
    
        sudo service postgresql restart

1.5 Go back to your account (press <Ctrl+D>) and create database:

        createdb <db_name>
        psql <db_name>

2. Installing / upgrading git:
2.1 Easiest way, but there's no warranty that you'll obtain latest version
    (>=1.7.10):

        sudo <yum|apt-get> install git

2.2 Hardest way:

        sudo apt-get install expat openssl zlib1g zlib1g-dev gettext
        sudo apt-get install libcurl4-gnutls-dev
        sudo apt-get install libexpat1-dev
    
        git clone git://git.kernel.org/pub/scm/git/git.git
        cd git/
        sudo make prefix=/usr all
        sudo make prefix=/usr install
    
3. Installing dependencies for PIL (Python image libraries):
3.1 Mandatory:

        sudo <yum|apt-get> install libjpeg 

        sudo yum install libjpeg-devel
    or  sudo apt-get install libjpeg-dev

        sudo yum install freetype-devel  
    or  sudo apt-get install libfreetype6-dev
    
3.2 Optional (if PIL were installed before libjpeg*):

        pip uninstall pil
        pip install pil --upgrade

4. Installing Virtual Environment and project dependencies:

        sudo easy_install virtualenv
        cd <PATH_TO_PROJECT>
        virtualenv ve --no-site-packages
        . ve/bin/activate
        pip install -r requirements.txt
        
5. Serving Django/Python with uWSGI/Nginx.
5.1 First of all (at Amazon AWS management console):
5.1.1 Launch instance.
5.1.2 Allocate <ElasticIP> and associate it with instance.
5.1.3 Configure Security Groups, i.e. open ports (e.g. SSH, all TCP, all UDP,
    all ICMP, HTTP, HTTPS).
5.1.4 Create <SSH-Keypair> and store it somewhere on computer.
5.2 Register (buy) domain name (e.g. <example.com>) at DNS registrar
    (e.g. 'godaddy.com' or 'name.com') and associate <*.example.com> with
    <ElasticIP> (type A).
5.3 Connect to instance via SSH, e.g.

        ssh -i <PATH_TO_SSH-Keypair> ec2-user@107.21.220.121

5.4 Now, inside instance, clone project into working directory and do all steps
    on system setup (install and configure PostgreSQL, virtual environment and
    project dependencies). Checkout if Django server is running on localhost.
5.5 Installation and configuration of uWSGI/Nginx. Originally taken from here 
    http://posterous.adambard.com/start-to-finish-serving-mysql-backed-django-w
5.5.1 Configure <PATH_TO_PROJECT/wsgi.py>:

        import os

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "participe.settings")

        from django.core.wsgi import get_wsgi_application
        application = get_wsgi_application()

5.5.2 Install uWSGI:

        sudo pip install uwsgi

5.5.3 Install and configure Nginx according to Adam's blog.
5.5.4 Create and configure our configuration file, e.g.

        sudo nano /opt/nginx/sites-enabled/mvp
    
    In my case it looks like:

        upstream mvp {
	        server unix://tmp/uwsgi_mvp.sock;
        }
        server{
       	    listen 80;
            server_name ec2-107-21-220-121.compute-1.amazonaws.com \
                    <example.com> <www.example.com>;
            access_log /home/ec2-user/logs/access.log;
            error_log /home/ec2-user/logs/error.log;
            location /site_media {
                root /home/ec2-user/www/mvp/participe/media/;
            }
	        location / {
                uwsgi_pass     unix:///tmp/uwsgi_mvp.sock;
                include        uwsgi_params;
            }
        }

    And finally:

        sudo /etc/init.d/nginx restart
        cd /home/ec2-user/www/mvp
        . ve/bin/activate
        sudo uwsgi --home /home/ec2-user/www/mvp/participe/ 
                   --socket /tmp/uwsgi_mvp.sock
                   --chmod-socket 
                   --module wsgi 
                   --pythonpath /home/ec2-user/www/mvp/partice
                   -H /home/ec2-user/www/mvp/ve
                   --logto /var/log/uwsgi.log
                   
5.5.6 To run daemonized uWSGI, create configuration file, e.g.:

        sudo nano /etc/init/uwsgi.conf

    In my case it looks like ("exec ..." all in one line):
    
        description "uWSGI server"

        start on runlevel [2345]
        stop on runlevel [!2345]

        respawn
        exec /usr/bin/uwsgi \
            --home /home/ec2-user/www/mvp/participe/ \
            --socket /tmp/uwsgi_mvp.sock \
            --chmod-socket \
            --module wsgi \
            --pythonpath /home/ec2-user/www/mvp/participe \
            -H /home/ec2-user/www/mvp/ve/ \
            --logto /var/log/uwsgi.log \
            --chdir /home/ec2-user/www/mvp/

    Run/terminate daemonized uWSGI:

        sudo start uwsgi
        sudo stop uwsgi

6. Django Social Auth (follow 
    https://django-social-auth.readthedocs.org/en/latest/index.html)
6.1 Facebook
6.1.1 Go to http://developers.facebook.com/setup/, create <App> 
    (Website with Facebook Login) and sign-up as developer.
    Obtain <AppID> and <AppSecret>. Go to [Edit App] and fill up field
    "Website with Facebook Login" with URL to your site, e.g.
    "http://www.example.com". From now Facebook should allow authorization
    request from domain <www.example.com>.
6.1.2 Learn about permissions
    https://developers.facebook.com/docs/concepts/login/permissions-login-dialog/

