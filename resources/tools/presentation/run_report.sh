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
    sudo apt-get -y install xvfb texlive-latex-recommended \
        texlive-fonts-recommended texlive-fonts-extra texlive-latex-extra latexmk wkhtmltopdf inkscape
    sudo sed -i.bak 's/^\(main_memory\s=\s\).*/\110000000/' /usr/share/texlive/texmf-dist/web2c/texmf.cnf
fi

# Create working directories
mkdir ${DIR[WORKING]}

# Create virtual environment
virtualenv -p $(which python3) ${DIR[WORKING]}/env
source ${DIR[WORKING]}/env/bin/activate

# Install python dependencies:
pip3 install -r requirements.txt

export PYTHONPATH=`pwd`:`pwd`/../../../:`pwd`/../../libraries/python

python pal.py \
    --specification specification.yaml \
    --release ${RELEASE} \
<<<<<<< HEAD   (953d13 Report: Fix typo in specification.)
<<<<<<< HEAD   (793b6b Report: Add data)
<<<<<<< HEAD   (b95753 PAL: Fix table data model)
<<<<<<< HEAD   (ede849 Report: Add pdf version)
<<<<<<< HEAD   (35a360 Report: Add data)
=======
<<<<<<< HEAD   (ef4187 Report: Add pdf version)
>>>>>>> CHANGE (68013a Report: Configure report 2001.15)
    --week "13" \
=======
<<<<<<< HEAD   (ede849 Report: Add pdf version)
<<<<<<< HEAD   (d4f9e9 CSIT-1597 API cleanup: acl)
    --week "12" \
=======
=======
<<<<<<< HEAD   (9b9bbb PAL: Fix table data model)
>>>>>>> CHANGE (8f2816 Report: Configure report 2001.16)
    --week "14" \
<<<<<<< HEAD   (b95753 PAL: Fix table data model)
>>>>>>> CHANGE (0ed80e Report: COnfigure reoirt 2001.14)
>>>>>>> CHANGE (bdfc93 Report: COnfigure reoirt 2001.14)
=======
    --week "15" \
>>>>>>> CHANGE (8e601d Report: Configure report 2001.15)
>>>>>>> CHANGE (68013a Report: Configure report 2001.15)
=======
=======
    --week "16" \
>>>>>>> CHANGE (42a491 Report: Configure report 2001.16)
>>>>>>> CHANGE (8f2816 Report: Configure report 2001.16)
=======
    --week "18" \
>>>>>>> CHANGE (dfd4a2 Report: Configure Report 2001.18)
=======
    --week "19" \
>>>>>>> CHANGE (413f1d Report: Configure report 2001.19)
    --logging INFO \
    --force

RETURN_STATUS=$(echo $?)
exit ${RETURN_STATUS}
