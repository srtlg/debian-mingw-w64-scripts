#!/bin/sh
set -e
. "`dirname $0`/00_create_machine.sh"
config=/etc/systemd/nspawn/debian-${release}.nspawn
rm -f $config
systemd-nspawn -D debian-$release sh -c "echo 'deb http://ftp.de.debian.org/debian ${release}-backports main' >> /etc/apt/sources.list"
systemd-nspawn -D debian-$release sh -c "apt-get update && apt-get install -t ${release}-backports cmake"
systemd-nspawn -D debian-$release sh -c "apt-get install --no-install-recommends \
ninja-build python3 \
patch xz-utils sudo pkg-config \
screen \
git \
ca-certificates \
"
# maybe export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt?
systemd-nspawn -D debian-$release sh -c 'update-alternatives --install /usr/bin/python python /usr/bin/python3 1'
systemd-nspawn -D debian-$release sh -c "echo '$SUDO_USER    ALL=(ALL:ALL) NOPASSWD: ALL'  > /etc/sudoers.d/$SUDO_USER"
systemd-nspawn -D debian-$release sh -c "apt-get install --no-install-recommends \
gcc-mingw-w64-x86-64-posix \
g++-mingw-w64-x86-64-posix \
gfortran-mingw-w64-x86-64-posix \
wine64 \
" 
