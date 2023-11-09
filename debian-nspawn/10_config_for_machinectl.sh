#!/bin/sh
set -e
. "`dirname $0`/00_create_machine.sh"
shared_directory="/home/$SUDO_USER/nspawn"
[ -e "$shared_directory" ] || ( echo "expecting $shared_directory shared directory" && exit 1 )
config=/etc/systemd/nspawn/debian-${release}.nspawn
rm -f $config
# or useradd -m -s /bin/bash $USER
cat>$config<<EOF
[Network]
VirtualEthernet=no
[Files]
Bind=$shared_directory:$shared_directory:idmap
EOF
