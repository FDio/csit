#!/bin/bash
#set -xeuf -o pipefail
set -x

#sudo apt-get -y install libpython2.7-dev

rm -f priv_key
cat > priv_key <<EOF
-----BEGIN RSA PRIVATE KEY-----
MIIEpgIBAAKCAQEAwUDlTpzSHpwLQotZOFS4AgcPNEWCnP1AB2hWFmvI+8Kah/gb
v8ruZU9RqhPs56tyKzxbhvNkY4VbH5F1GilHZu3mLqzM4KfghMmaeMEjO1T7BYYd
vuBfTvIluljfQ2vAlnYrDwn+ClxJk81m0pDgvrLEX4qVVh2sGh7UEkYy5r82DNa2
4VjzPB1J/c8a9zP8FoZUhYIzF4FLvRMjUADpbMXgJMsGpaZLmz95ap0Eot7vb1Cc
1LvF97iyBCrtIOSKRKA50ZhLGjMKmOwnYU+cP5718tbproDVi6VJOo7zeuXyetMs
8YBl9kWblWG9BqP9jctFvsmi5G7hXgq1Y8u+DwIDAQABAoIBAQC/W4E0DHjLMny7
0bvw2YKzD0Zw3fttdB94tkm4PdZv5MybooPnsAvLaXVV0hEdfVi5kzSWNl/LY/tN
EP1BgGphc2QgB59/PPxGwFIjDCvUzlsZpynBHe+B/qh5ExNQcVvsIOqWI7DXlXaN
0i/khOzmJ6HncRRah1spKimYRsaUUDskyg7q3QqMWVaqBbbMvLs/w7ZWd/zoDqCU
MY/pCI6hkB3QbRo0OdiZLohphBl2ShABTwjvVyyKL5UA4jAEneJrhH5gWVLXnfgD
p62W5CollKEYblC8mUkPxpP7Qo277zw3xaq+oktIZhc5SUEUd7nJZtNqVAHqkItW
79VmpKyxAoGBAPfU+kqNPaTSvp+x1n5sn2SgipzDtgi9QqNmC4cjtrQQaaqI57SG
OHw1jX8i7L2G1WvVtkHg060nlEVo5n65ffFOqeVBezLVJ7ghWI8U+oBiJJyQ4boD
GJVNsoOSUQ0rtuGd9eVwfDk3ol9aCN0KK53oPfIYli29pyu4l095kg11AoGBAMef
bPEMBI/2XmCPshLSwhGFl+dW8d+Klluj3CUQ/0vUlvma3dfBOYNsIwAgTP0iIUTg
8DYE6KBCdPtxAUEI0YAEAKB9ry1tKR2NQEIPfslYytKErtwjAiqSi0heM6+zwEzu
f54Z4oBhsMSL0jXoOMnu+NZzEc6EUdQeY4O+jhjzAoGBAIogC3dtjMPGKTP7+93u
UE/XIioI8fWg9fj3sMka4IMu+pVvRCRbAjRH7JrFLkjbUyuMqs3Arnk9K+gbdQt/
+m95Njtt6WoFXuPCwgbM3GidSmZwYT4454SfDzVBYScEDCNm1FuR+8ov9bFLDtGT
D4gsngnGJj1MDFXTxZEn4nzZAoGBAKCg4WmpUPaCuXibyB+rZavxwsTNSn2lJ83/
sYJGBhf/raiV/FLDUcM1vYg5dZnu37RsB/5/vqxOLZGyYd7x+Jo5HkQGPnKgNwhn
g8BkdZIRF8uEJqxOo0ycdOU7n/2O93swIpKWo5LIiRPuqqzj+uZKnAL7vuVdxfaY
qVz2daMPAoGBALgaaKa3voU/HO1PYLWIhFrBThyJ+BQSQ8OqrEzC8AnegWFxRAM8
EqrzZXl7ACUuo1dH0Eipm41j2+BZWlQjiUgq5uj8+yzy+EU1ZRRyJcOKzbDACeuD
BpWWSXGBI5G4CppeYLjMUHZpJYeX1USULJQd2c4crLJKb76E8gz3Z9kN
-----END RSA PRIVATE KEY-----
EOF

chmod 600 priv_key
ls -la

#git clone ssh://rotterdam-jobbuilder@gerrit.fd.io:29418/vpp
#
#cd vpp/build-root
#./bootstrap.sh
#make PLATFORM=vpp TAG=vpp_debug install-deb
#
#ls -la

#VIRL_VMS="10.30.51.53,10.30.51.51,10.30.51.52"
#IFS=',' read -ra ADDR <<< "${VIRL_VMS}"
#
function ssh_do() {
    echo
    echo "### "  ssh $@
    ssh -i priv_key -o StrictHostKeyChecking=no $@
}

#for addr in "${ADDR[@]}"; do
#    echo
#    echo ${addr}
#    echo
#
#    ssh_do cisco@${addr} hostname || true
#    ssh_do cisco@${addr} "ifconfig -a" || true
#    ssh_do cisco@${addr} "lspci -Dnn | grep 0200" || true
#    ssh_do cisco@${addr} "free -m" || true
#    ssh_do cisco@${addr} "cat /proc/meminfo" || true
#    ssh_do cisco@${addr} "dpkg -l vpp\*" || true
#    ssh_do cisco@${addr} "lshw -c network" || true
#    ssh_do cisco@${addr} "sudo -S sh -c 'echo exec show  hardware | vpp_api_test '"
#done


#ssh_do cisco@10.30.51.73 "sudo apt-get -y install python-virtualenv python-dev"
#ssh_do cisco@10.30.51.73 "lspci -vmmks 0000:00:04.0"

#ssh_do cisco@10.30.51.72 "sudo -S sh -c 'echo exec show  hardware | vpp_api_test '"
#ssh_do cisco@10.30.51.71 "sudo -S sh -c 'echo exec show  hardware | vpp_api_test '"


#echo Virtualenv install
#VE_DIR=`pwd`/build
#export PYTHONPATH=${VE_DIR}/lib/python2.7/site-packages
#
#curl -O https://pypi.python.org/packages/source/v/virtualenv/virtualenv-14.0.6.tar.gz
#tar -zxf virtualenv-14.0.6.tar.gz
#cd virtualenv-14.0.6
#
#python setup.py install --prefix=${VE_DIR}
#
#cd ..
#${VE_DIR}/bin/virtualenv env

virtualenv env
. env/bin/activate

echo pip install
pip install -r requirements.txt

#PYTHONPATH=`pwd` pybot -L TRACE -v TOPOLOGY_PATH:topologies/available/virl.yaml --exitonfailure --exitonerror --skipteardownonexit tests
PYTHONPATH=`pwd` pybot -L TRACE -v TOPOLOGY_PATH:topologies/available/virl.yaml --exclude PERFTEST tests

