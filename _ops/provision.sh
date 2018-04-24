ssh root@${DP_SERVER} << EOF
    apt-get update
    DEBIAN_FRONTEND=noninteractive apt-get upgrade -y
    adduser --disabled-password --gecos "" fraser
    usermod -a -G docker fraser
    mkdir -p /home/fraser/.ssh
    cp /root/.ssh/authorized_keys /home/fraser/.ssh/authorized_keys
    chown fraser:fraser /home/fraser/.ssh/authorized_keys
    reboot
EOF