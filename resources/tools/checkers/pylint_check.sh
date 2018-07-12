set -exu

PYTHONPATH=`pwd` pylint --rcfile=pylint.cfg resources/ tests/ > pylint.log
## TODO: Enable when output size does more good than harm.
# cat pylint.log

echo
echo "Pylint checker: see pylint.log"
