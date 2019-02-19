# What is the output of this bash script?
set -e
function f() {
    set -e
    false
    echo "inside"
}
f || echo "$?"
echo "after or"
f
echo "after direct"
