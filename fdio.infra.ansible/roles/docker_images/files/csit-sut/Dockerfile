FROM base-ubuntu2204:local

COPY supervisord.conf /etc/supervisor/supervisord.conf

CMD ["sh", "-c", "rm -f /dev/shm/db /dev/shm/global_vm /dev/shm/vpe-api; /usr/bin/supervisord -c /etc/supervisor/supervisord.conf; /usr/sbin/sshd -D -p 2222"]