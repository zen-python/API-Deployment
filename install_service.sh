#!/bin/bash
cp deploy_socket_server.py /usr/local/bin
cp deploysocket.sh /etc/init.d
update-rc.d deploysocket.sh defaults
/etc/init.d/deploysocket.sh start
/etc/init.d/deploysocket.sh status