#!/bin/sh
set -e
. "`dirname $0`/00_create_machine.sh"
[ -e "/home/$USER/nspawn" ] || ( echo "expecting ~/nspawn shared directory" && exit 1 )
config=/etc/systemd/nspawn/debian-${release}.nspawn
#rm -f $config
# or useradd -m -s /bin/bash $USER
systemd-nspawn -D debian-$release sh -c "passwd; adduser $USER; passwd $USER"
cat>$config<<EOF
[Network]
VirtualEthernet=no
[Files]
Bind=/home/$USER/nspawn:/home/$USER/nspawn:idmap
EOF
systemd-nspawn -D debian-$release sh -c "touch /etc/default/locale"
