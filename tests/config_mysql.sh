#!/bin/bash
mysql -u root -p << END
create database pwmantest;
create user 'pwman'@'localhost' IDENTIFIED BY '123456';
grant all on pwmantest.* to 'pwman'@'localhost';
END
