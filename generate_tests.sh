TEST_DIR=./tests
BKP_DIR=./tests_bkp
function generate_tests () {
    set -exuo pipefail
    if [ -d "$BKP_DIR" ] && [ -n "$(ls -A "$BKP_DIR")" ]; then
	#Backup directory already exists with original test cases.
	rm -rf ${TEST_DIR}
	cp -r ${BKP_DIR} ${TEST_DIR}
    else
	#Create new backup dir with name tests_bkp.
	mkdir ${BKP_DIR}
        cp -r ${TEST_DIR}/* ${BKP_DIR}
    fi
    echo "end"
    cmd_line=("find" "${TEST_DIR}" "-type" "f")
    cmd_line+=("-executable" "-name" "*.py")
    # We sort the directories, so log output can be compared between runs.
    file_list=$("${cmd_line[@]}" | sort)

    for gen in ${file_list}; do
        directory="$(dirname "${gen}")"
        filename="$(basename "${gen}")"
        pushd "${directory}"
        ./"${filename}"
        popd
    done
}


generate_tests
