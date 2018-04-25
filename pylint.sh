# This script assumes requirements.txt are installed,
# presumably into a virtualenv.
# Also, this only works when started from repo root directory.

PYTHONPATH=`pwd` pylint --rcfile=pylint.cfg resources/
