set -exu

# docs contains too many wide formatted tables.
# .txt contains lines with wide URLs.
lines=`grep -rn ".\{81\}" resources tests \
| fgrep -v .svg | fgrep -v .txt | tee lines.log | wc -l`
if [ "$lines" != "0" ]; then
    echo "Long lines detected: $lines"
    ## TODO: Enable when output size does more good than harm.
    # cat lines.log
    echo
    echo "Line length checker: FAIL"
    exit 1
fi

echo
echo "Line length checker: PASS"
