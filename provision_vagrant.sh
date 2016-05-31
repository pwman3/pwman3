#!/usr/bin/env bash
export DEBIAN_FRONTEND=noninteractive

sudo locale-gen "en_US.UTF-8"
sudo dpkg-reconfigure locales

echo "LC_ALL=en_US.UTF-8" >> /etc/environment
echo "LANG=en_US.UTF-8" >> /etc/environment

PACKAGES="python-psycopg2 sqlite3 git postgresql-server-dev-9.3 \
python-dev python3-dev \
postgresql-9.3 python3-psycopg2 mysql-server-5.6 build-essential"


apt-get update
apt-get install -y ${PACKAGES}

if [ ! -f  /usr/local/bin/pip ]; then
    wget https://bootstrap.pypa.io/get-pip.py
	sudo python get-pip.py
fi

if [ ! -f  /usr/local/bin/pip3 ]; then
	sudo python3 get-pip.py
fi

sudo mysqladmin -u root password toor

PYTHON_PACKAGES="psycopg2 pymysql pymongo==2.8 pexpect coverage unittest2 \
virtualenvwrapper"

sudo pip3 install ${PYTHON_PACKAGES}
sudo pip install ${PYTHON_PACKAGES}

# install mongodb

sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
echo "deb http://repo.mongodb.org/apt/ubuntu \
	"$(lsb_release -sc)"/mongodb-org/3.0 multiverse" \
	| sudo tee /etc/apt/sources.list.d/mongodb-org-3.1.list

sudo apt-get update
sudo apt-get install -y mongodb-org

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
#mongo pwmantest --eval 'db.addUser("tester", "12345678");'


