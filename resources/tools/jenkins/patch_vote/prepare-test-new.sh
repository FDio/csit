cd $vpp_dir
rm -rf build_parent
mv build-root build_parent
rm -f csit/*.deb
cp build_new/*.deb csit/
# Create symlinks so that if job fails on robot test, results can be archived.
ln -s csit csit_new
