#!/bin/sh
set -e
[ `id -u` = 0 ] || (echo "run as root" && exit 1)
cd /var/lib/machines/
release=bullseye
if [ -e debian-$release ]
then
	echo 'machine exists, doing nothing'
else
	debootstrap --include=dbus-broker,systemd-container --components=main,universe \
	  $release debian-$release http://ftp.de.debian.org/debian
fi
