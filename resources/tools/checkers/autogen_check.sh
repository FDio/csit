set -exu

for gen in `find ./tests -type f -executable -name '*.py'`; do
    directory=`dirname "$gen"`
    filename=`basename "$gen"`
    ( cd "$directory" && PYTHONPATH="$PYTHONPATH" ./"$filename" )
done

lines=`git diff | tee autogen.log | wc -l`
if [ "$lines" != "0" ]; then
    echo "Autogeneration conflict diff nonzero: $lines"
    # TODO: Disable if output size does more harm than good.
    cat autogen.log
    echo
    echo "Autogen checker: FAIL"
    exit 1
fi

echo
echo "Autogen checker: PASS"
