nfs-kernel-server install:
  pkg.installed:
    - skip_verify: True
    - refresh: False
    - name: nfs-kernel-server
