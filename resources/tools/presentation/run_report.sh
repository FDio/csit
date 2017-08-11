#!/bin/bash

set -x


# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Get actual date
DATE=$(date -u '+%d-%b-%Y')

# Load configuration
source ${SCRIPT_DIR}/run_report.cfg

# Install system dependencies
#sudo apt-get -y update
#sudo apt-get -y install libxml2 libxml2-dev libxslt-dev build-essential \
#    zlib1g-dev unzip

#if [[ ${CFG[BLD_LATEX]} -eq 1 ]] ;
#then
#    sudo apt-get -y install xvfb texlive-latex-recommended \
#        texlive-fonts-recommended texlive-fonts-extra texlive-latex-extra latexmk wkhtmltopdf
#    sudo sed -i.bak 's/^\(main_memory\s=\s\).*/\110000000/' /usr/share/texlive/texmf-dist/web2c/texmf.cnf
#fi

# Clean-up when finished
#trap 'rm -rf ${DIR[WORKING]}; exit' EXIT
#trap 'rm -rf ${DIR[WORKING]}; exit' ERR

# Create working directories
#mkdir ${DIR[WORKING]}

# Create virtual environment
virtualenv ${DIR[WORKING]}/env
. ${DIR[WORKING]}/env/bin/activate

# Install python dependencies:
pip install -r requirements.txt

export PYTHONPATH=`pwd`

python presentation.py -c configuration.yaml -f -l INFO

# HTML BUILDER
if [[ ${CFG[BLD_HTML]} -eq 1 ]] ;
then
    sphinx-build -v -c . -a -b html -E \
        -D release=$1 -D version="$1 report - $DATE" \
        ${DIR[WORKING,SRC]} ${DIR[BUILD,HTML]}/

    # Patch the CSS for tables layout
    cat - > ${DIR[CSS_PATCH_FILE]} <<"_EOF"
/* override table width restrictions */
@media screen and (min-width: 767px) {
    .wy-table-responsive table td, .wy-table-responsive table th {
        white-space: normal !important;
    }

    .wy-table-responsive {
        font-size: small;
        margin-bottom: 24px;
        max-width: 100%;
        overflow: visible !important;
    }
}
_EOF
fi

