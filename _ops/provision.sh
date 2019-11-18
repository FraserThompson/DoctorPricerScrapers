ssh root@${DP_SERVER} << EOF
    apt-get update
    DEBIAN_FRONTEND=noninteractive apt-get --with-new-pkgs upgrade -y
    adduser --disabled-password --gecos "" fraser
    usermod -a -G docker fraser
    echo 'fraser ALL=NOPASSWD: ALL' >> /etc/sudoers.d/fraser
    mkdir -p /home/fraser/.ssh
    cp /root/.ssh/authorized_keys /home/fraser/.ssh/authorized_keys
    chown fraser:fraser /home/fraser/.ssh/authorized_keys
    ufw allow 80
    ufw allow 443
    ufw deny 2375
    ufw deny 2376
    reboot
EOF