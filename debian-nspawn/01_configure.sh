#!/bin/sh
set -e
. "`dirname $0`/00_create_machine.sh"
config=/etc/systemd/nspawn/debian-${release}.nspawn
rm -f $config
systemd-nspawn -D debian-$release sh -c "touch /etc/default/locale"
