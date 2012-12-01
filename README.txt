1. Installing / upgrading git:
1.1 Easiest way, but there's no warranty that you'll obtain latest version (>=1.7.10):

    sudo apt-get install git
    
1.2 Hardest way:

    sudo apt-get install expat openssl zlib1g zlib1g-dev gettext
    sudo apt-get install libcurl4-gnutls-dev
    sudo apt-get install libexpat1-dev
    
    git clone git://git.kernel.org/pub/scm/git/git.git
    cd git/
    sudo make prefix=/usr all
    sudo make prefix=/usr install
    
1. Installing Virtual Environment and project dependencies:

    cd <PROJECT_PATH>
    virtualenv ve --no-site-packages
    . ve/bin/activate
    pip install -r requirements.txt
