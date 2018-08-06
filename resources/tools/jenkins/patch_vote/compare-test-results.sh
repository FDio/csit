cd "$vpp_dir"
rm -rf csit_parent
mkdir -p csit_parent
for filename in output.xml log.html report.html; do
    mv csit/$filename csit_parent/$filename
done
bash "$script_new/parse.sh" csit_parent
virtualenv --system-site-packages "env"
set +u
source "env/bin/activate"
set -u
pip install -r "$script_new/requirements.txt"
python "$script_new/compare.py"
# The exit code affects the vote result.
