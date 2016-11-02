#/bin/bash

export PYTHONPATH=`pwd`

virtualenv env
source env/bin/activate

pip install -r requirements.txt

mkdir gen_docs

PYTHON_MODULES=$(ls -la resources/libraries/python/*.py | cut -d "/" -f 4 | cut -d "." -f 1)

mkdir gen_docs/python
for module in ${PYTHON_MODULES}; do
    python -m robot.libdoc resources.libraries.python.${module} gen_docs/python/${module}.html
done

ROBOT_MODULES=$(ls -la resources/libraries/robot/*.robot | cut -d "/" -f 4 | cut -d "." -f 1)

mkdir gen_docs/robot
for module in ${ROBOT_MODULES}; do
    python -m robot.libdoc resources/libraries/robot/${module}.robot gen_docs/robot/${module}.html
done

python -m robot.testdoc tests/ gen_docs/tests.html
