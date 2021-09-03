if [[ "$#" != "1" ]]; then
    echo "Use precisely one argument!"
fi

#arg="$(cat "$1" | sed -iE 's#[ _]#\[ _\]?#g')"
arg="${1//[ _]/\[ _\]\\?}"
echo grep -rin --color "${arg}"
grep -rin --color "${arg}"
