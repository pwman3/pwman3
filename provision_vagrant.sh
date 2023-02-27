#!/usr/bin/env bash

apt-get install -y debconf-utils
export TERM=linux
export DEBIAN_FRONTEND=noninteractive
echo 'debconf debconf/frontend select noninteractive' | debconf-set-selections

locale-gen "en_US.UTF-8"

dpkg-reconfigure --frontend=noninteractiv locales

debconf-set-selections <<< 'mysql-server-5.6 mysql-server/root_password password toor'
debconf-set-selections <<< 'mysql-server-5.6 mysql-server/root_password_again password toor'

echo "LC_ALL=en_US.UTF-8" >> /etc/environment
echo "LANG=en_US.UTF-8" >> /etc/environment

PACKAGES="python-psycopg2 sqlite3 git python3-pip \
postgresql-server-dev-9.5 postgresql \
postgresql-contrib \
python-dev python3-dev libffi-dev \
postgresql python3-psycopg2 build-essential \
mysql-server-5.7
"

apt-get update
apt-get install -y ${PACKAGES}

PYTHON_PACKAGES="psycopg2 pymysql pymongo pexpect coverage pew"

sudo pip3 install ${PYTHON_PACKAGES}

# install mongodb
curl -fsSL https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -

echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list

apt-get update
apt-get install -y mongodb-org
systemctl start mongod

cd /home/vagrant
if [ ! -d pwman3 ]; then
	git clone https://github.com/pwman3/pwman3.git
	chown vagrant:vagrant -R pwman3
fi

# setup mysql
mysql -e 'CREATE DATABASE IF NOT EXISTS pwmantest' -uroot --password=toor
mysql -e "create user 'pwman'@'localhost' IDENTIFIED BY '123456'" -uroot --password=toor
mysql -e "grant all on pwmantest.* to 'pwman'@'localhost';" -uroot --password=toor

# setup postgresql
sudo -u postgres psql -c "CREATE USER tester WITH PASSWORD '123456';" -U postgres
sudo -u postgres psql -c 'create database pwman;' -U postgres
sudo -u postgres psql -c 'grant ALL ON DATABASE pwman to tester' -U postgres

# setup mongodb
mongo < /home/vagrant/pwman3/tests/init_mongo.js

