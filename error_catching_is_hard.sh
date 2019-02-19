set -e
f() {
    set -e
    false  # We want this to die or exit.
    echo "I am alive!"
}
die() {
    echo "I am dead."
    exit 1
}
set -e
f || die
echo "Still alive!"
