#!/usr/bin/env bash

function prepare() {
    export TERM=linux
    export DEBIAN_FRONTEND=noninteractive
    #
    apt-get install -y debconf-utils
    #
    echo 'debconf debconf/frontend select noninteractive' | debconf-set-selections
    #
    locale-gen "en_US.UTF-8"
    #
    dpkg-reconfigure --frontend=noninteractiv locales
    #
    debconf-set-selections <<< 'mysql-server-5.6 mysql-server/root_password password toor'
    debconf-set-selections <<< 'mysql-server-5.6 mysql-server/root_password_again password toor'
    #
    echo "LC_ALL=en_US.UTF-8" >> /etc/environment
    echo "LANG=en_US.UTF-8" >> /etc/environment
}

function install_deps() {
    local PACKAGES="python-psycopg2 sqlite3 git \
    postgresql-server-dev-all postgresql \
    postgresql-contrib python3-venv \
    python-dev python3-dev libffi-dev \
    postgresql python3-psycopg2 build-essential \
    mariadb-server mongodb
    "
    #
    apt-get update
    apt-get install -y ${PACKAGES}
}

function install_python_packages() {
   local PYTHON_PACKAGES="psycopg2 pymysql pymongo pexpect coverage pew"
   if [ ! -f  /usr/local/bin/pip3 ]; then
       wget https://bootstrap.pypa.io/get-pip.py
       sudo python3 get-pip.py
   fi
   #
   #
   sudo pip3 install ${PYTHON_PACKAGES}
}


function start_databases() {
   for db in mongodb mariadb postgresql; do
       systemctl start $db
   done
}


function setup_databases() {
    ## setup mysql
    mysql -e 'CREATE DATABASE IF NOT EXISTS pwmantest' -uroot --password=toor
    mysql -e "create user 'pwman'@'localhost' IDENTIFIED BY '123456'" -uroot --password=toor
    mysql -e "grant all on pwmantest.* to 'pwman'@'localhost';" -uroot --password=toor
    #
    ## setup postgresql

    local POSTGRES_USER=postgres;
    local POSTGRES_DB=pwman

    sudo -u postgres psql -v ON_ERROR_STOP=1 <<-EOSQL
CREATE DATABASE $POSTGRES_DB;
CREATE USER tester WITH PASSWORD '123456';
GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO tester;
EOSQL

## setup mongodb
mongo < tests/init_mongo.js
}
#


function main(){
    prepare
    install_deps
    install_python_packages
    start_databases
    setup_databases
}

# This line and the if condition bellow allow sourcing the script without executing
# the main function
(return 0 2>/dev/null) && sourced=1 || sourced=0

if [[ $sourced == 1 ]]; then
    set +e
    echo "You can now use any of these functions:"
    echo ""
    typeset -F

    #typeset -F |  cut -d" " -f 3
else
    set -eu
	cd /vagrant
    main "$@"
fi

# vi: sts=4 ts=4 sw=4 ai
