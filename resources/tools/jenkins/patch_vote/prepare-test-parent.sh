cd "$vpp_dir"
rm -rf csit_new
mkdir -p csit_new
for filename in output.xml log.html report.html; do
    mv csit/$filename csit_new/$filename
done
bash "$script_dir/parse.sh" csit_new
# TODO: Also handle archive/ and make job archive everything useful.
( cd "$csit_dir" && git reset --hard HEAD && git clean -dffx )
cp build_parent/*.deb csit/
# Create symlinks so that if job fails on robot test, results can be archived.
ln -s csit csit_parent
