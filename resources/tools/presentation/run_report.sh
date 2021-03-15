#!/bin/bash

set -x

RELEASE=$1

# set default values in config array
typeset -A CFG
typeset -A DIR

DIR[WORKING]=_tmp
CFG[BLD_LATEX]=1

# Install system dependencies
sudo apt-get -y update
sudo apt-get -y install libxml2 libxml2-dev libxslt-dev build-essential \
    zlib1g-dev unzip

if [[ ${CFG[BLD_LATEX]} -eq 1 ]] ;
then
    export DEBIAN_FRONTEND=noninteractive
    sudo apt-get -y install xvfb texlive-latex-recommended \
        texlive-fonts-recommended texlive-fonts-extra texlive-latex-extra latexmk wkhtmltopdf inkscape
    sudo sed -i.bak 's/^\(main_memory\s=\s\).*/\110000000/' /usr/share/texlive/texmf-dist/web2c/texmf.cnf
fi

# Create working directories
mkdir ${DIR[WORKING]}

# Create virtual environment
virtualenv -p $(which python3) ${DIR[WORKING]}/env
source ${DIR[WORKING]}/env/bin/activate

# FIXME: Temporary hack until all docker dns will be solved
echo "nameserver 172.17.0.1" > /etc/resolv.conf

# Install python dependencies:
pip3 install -r requirements.txt

export PYTHONPATH=`pwd`:`pwd`/../../../:`pwd`/../../libraries/python

python pal.py \
    --specification specification.yaml \
    --release ${RELEASE} \
    --week "09" \
    --logging INFO \
    --force

RETURN_STATUS=$(echo $?)
exit ${RETURN_STATUS}
