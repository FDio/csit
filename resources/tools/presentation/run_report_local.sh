#!/bin/bash

# set -x

usage()
{
  cat <<EOF
usage: run_report_local [OPTION]

Options:
  -h; --help             Display this help and exit.
  -f; --file             Input XML file to be processed.
  -d; --directory        Directory with input XML files to be processed.
  -r; --release          Release string (optional).
  -w; --week             Release week (optional).
  -i; --no-dependencies  Do not install dependencies.
  -l; --install-latex    Instal Latex.
EOF
}

filename=""
directoryname=""
release="master"
week="1"
cfg_install_dependencies=1
cfg_install_latex=0

while [ "$1" != "" ]; do
    case $1 in
        -f | --file )               shift
                                    filename=$1
                                    ;;
        -d | --directory )          shift
                                    directoryname=$1
                                    ;;
        -r | --release )            shift
                                    release=$1
                                    ;;
        -w | --week )               shift
                                    week=$1
                                    ;;
        -i | --no-dependencies )    cfg_install_dependencies=0
                                    ;;
        -l | --install-latex )      cfg_install_latex=1
                                    ;;
        -h | --help )               usage
                                    exit 1
                                    ;;
        * )                         usage
                                    exit 1
    esac
    shift
done

echo "Parameters:"
echo "  Input file:           " ${filename}
echo "  Input directory:      " ${directoryname}
echo "  Report release:       " ${release}
echo "  Report week:          " ${week}
echo "  Install dependencies: " ${cfg_install_dependencies}
echo "  Install Latex:        " ${cfg_install_latex}

if [[ $filename == "" && $directoryname == "" ]]; then
    echo "ERROR: The input directory or file is required."
    usage
    exit 1
fi

# set default values in config array
typeset -A CFG
typeset -A DIR

DIR[WORKING]=_tmp

# Install system dependencies
if [[ ${cfg_install_dependencies} -eq 1 ]] ;
then
sudo apt-get -y update
sudo apt-get -y install libxml2 libxml2-dev libxslt-dev build-essential \
    zlib1g-dev unzip
fi

if [[ ${cfg_install_latex} -eq 1 ]] ;
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

# Show help so you know the meaning of all parameters
python pal.py --help

if [[ ${filename} != "" ]]; then
    python pal.py \
        --specification specification_local.yaml \
        --release ${release} \
        --week ${week} \
        --logging INFO \
        --force \
        --input-file ${filename}
fi

if [[ ${directoryname} != "" ]]; then
    python pal.py \
        --specification specification_local.yaml \
        --release ${release} \
        --week ${week} \
        --logging INFO \
        --force \
        --input-directory ${directoryname}
fi

RETURN_STATUS=$(echo $?)
exit ${RETURN_STATUS}
