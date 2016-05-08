/nfs:
  file.directory:
    - user: root
    - group: root
    - mode: 755

/nfs/scratch:
  file.directory:
    - user: root
    - group: root
    - mode: 1777

/nfs/ro:
  file.directory:
    - user: virl
    - group: virl
    - mode: 755

/etc/exports:
  file.managed:
    - mode: 644
    - template: jinja
    - source: "salt://ckoester/nfs-server/files/exports"

nfs_server_running:
  service.running:
    - name: nfs-kernel-server

update_exports:
  cmd.run:
    - name: exportfs -ra
